import os
import sys
import csv
from datetime import datetime
from typing import Dict, Any, List
import httpx

from app.parsers.base import BaseParser
from app.models.player import Player, PlayerPlatformProfile, Platform, Position
from app.models.team import Team
from app.models.stats import PriceHistory
from sqlalchemy import and_


class FPLPlayersParser(BaseParser):
    """Парсер игроков FPL"""
    
    API_URL = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    
    async def parse(self) -> Dict[str, Any]:
        """Получение данных с API FPL"""
        self.log("Fetching data from FPL API...")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.API_URL)
            
            if response.status_code != 200:
                raise Exception(f"API returned status code: {response.status_code}")
                
            data = response.json()
            self.log(f"Received {len(data['elements'])} players")
            
            return data
    
    async def save_to_db(self, data: Dict[str, Any]) -> None:
        """Сохранение данных в БД"""
        # Сначала обновляем команды и получаем маппинг
        team_mapping = await self._update_teams(data['teams'])
        
        # Затем обновляем игроков
        await self._update_players(data['elements'], team_mapping)
        
    async def _update_teams(self, teams_data: List[Dict]) -> None:
        """Обновление команд"""
        self.log("Updating teams...")
        
        team_mapping = {}
        
        for team_data in teams_data:
            # Проверяем существует ли команда
            team = self.db.query(Team).filter(
                Team.name == team_data['name']
            ).first()
            
            if not team:
                team = Team(
                    name=team_data['name'],
                    abbreviation=team_data.get('short_name', ''),
                    league='Premier League'
                )
                self.db.add(team)
                self.log(f"Added new team: {team.name}")
            else:
                team.abbreviation = team_data.get('short_name', '')
            
            # Сохраняем маппинг ID -> team для быстрого доступа
            team_mapping[team_data['id']] = team
                
        self.db.commit()
        return team_mapping
    
    async def _update_players(self, players_data: List[Dict], team_mapping: Dict) -> None:
        """Обновление игроков"""
        self.log("Updating players...")
        
        position_map = {
            1: 'GK',
            2: 'DEF', 
            3: 'MID',
            4: 'FWD'
        }
        
        for player_data in players_data:
            try:
                # Пропускаем недоступных игроков (status == 'u')
                if player_data.get('status') == 'u':
                    continue
                
                # Получаем команду из маппинга
                team = team_mapping.get(player_data['team'])
                
                if not team:
                    self.log(f"Team not found for player {player_data['web_name']}", "WARNING")
                    continue
                
                # Извлекаем все необходимые данные как в вашем парсере
                real_player_id = str(player_data['code'])  # Это важный ID игрока в реальности
                first_name = player_data['first_name']
                last_name = player_data['second_name']  
                web_name = player_data['web_name']
                position = position_map.get(player_data['element_type'])
                status = player_data.get('status', 'a')  # a, i, d, s
                current_price = player_data['now_cost'] / 10
                ownership = float(player_data.get('selected_by_percent', 0))
                form = float(player_data.get('form', 0))
                total_points = player_data.get('total_points', 0)
                event_points = player_data.get('event_points', 0)
                season_player_id = str(player_data['id'])  # ID на платформе FPL
                
                # Ищем или создаем игрока
                player = self.db.query(Player).filter(
                    and_(
                        Player.first_name == first_name,
                        Player.last_name == last_name
                    )
                ).first()
                
                if not player:
                    player = Player(
                        first_name=first_name,
                        last_name=last_name,
                        web_name=web_name
                    )
                    self.db.add(player)
                    self.db.flush()
                else:
                    # Обновляем web_name если изменился
                    player.web_name = web_name
                
                # Обновляем или создаем профиль на платформе
                profile = self.db.query(PlayerPlatformProfile).filter(
                    and_(
                        PlayerPlatformProfile.platform == Platform.FPL,
                        PlayerPlatformProfile.platform_player_id == season_player_id
                    )
                ).first()
                
                if not profile:
                    profile = PlayerPlatformProfile(
                        player_id=player.id,
                        platform=Platform.FPL,
                        platform_player_id=season_player_id,  # ID на FPL
                        custom_name=web_name,
                        team_id=team.id,
                        player_position=position,
                        current_cost=current_price,
                        ownership_percent=ownership,
                        is_active=status != 'u',
                        status=status,
                        form=form,
                        total_points=total_points,
                        event_points=event_points
                    )
                    self.db.add(profile)
                    self.db.flush()
                else:
                    # Обновляем все данные
                    profile.team_id = team.id
                    profile.player_position = position
                    profile.current_cost = current_price
                    profile.ownership_percent = ownership
                    profile.is_active = status != 'u'
                    profile.custom_name = web_name
                    profile.status = status
                    profile.form = form
                    profile.total_points = total_points
                    profile.event_points = event_points
                
                # Добавляем запись в историю цен только если изменилась цена или ownership
                last_price = self.db.query(PriceHistory).filter(
                    PriceHistory.player_profile_id == profile.id
                ).order_by(PriceHistory.recorded_at.desc()).first()
                
                if not last_price or last_price.cost != current_price or last_price.ownership_percent != ownership:
                    price_history = PriceHistory(
                        player_profile_id=profile.id,
                        cost=current_price,
                        ownership_percent=ownership,
                        recorded_at=datetime.now()
                    )
                    self.db.add(price_history)
                
                self.records_processed += 1
                
                # Логируем каждого 100-го игрока для отслеживания прогресса
                if self.records_processed % 100 == 0:
                    self.log(f"Processed {self.records_processed} players...")
                
            except Exception as e:
                self.log(f"Error processing player {player_data.get('web_name', 'Unknown')}: {str(e)}", "ERROR")
                continue
        
        self.db.commit()
        self.log(f"Updated {self.records_processed} players")


class FPLOwnershipParser(BaseParser):
    """Парсер для обновления ownership"""
    
    API_URL = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    
    async def parse(self) -> Dict[str, Any]:
        """Получение данных ownership"""
        async with httpx.AsyncClient() as client:
            response = await client.get(self.API_URL)
            return response.json()
    
    async def save_to_db(self, data: Dict[str, Any]) -> None:
        """Обновление ownership в БД"""
        for player_data in data['elements']:
            if player_data.get('status') == 'u':
                continue
                
            profile = self.db.query(PlayerPlatformProfile).filter(
                and_(
                    PlayerPlatformProfile.platform == Platform.FPL,
                    PlayerPlatformProfile.platform_player_id == str(player_data['id'])
                )
            ).first()
            
            if profile:
                profile.ownership_percent = float(player_data.get('selected_by_percent', 0))
                self.records_processed += 1
        
        self.db.commit()
        self.log(f"Updated ownership for {self.records_processed} players")
