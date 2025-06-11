import csv
import io
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.player import Player, PlayerPlatformProfile, Platform, Position
from app.models.team import Team


class CSVImportService:
    """Сервис для импорта данных из CSV файлов"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def import_fpl_players(self, csv_content: str) -> Dict[str, Any]:
        """Импорт игроков FPL из CSV"""
        reader = csv.DictReader(io.StringIO(csv_content))
        
        imported = 0
        errors = []
        
        for row in reader:
            try:
                # Получаем или создаем команду
                team = self._get_or_create_team(
                    row.get('Team', ''),
                    row.get('Abbr', '')
                )
                
                # Получаем или создаем игрока
                player = self._get_or_create_player(
                    row.get('firstName', ''),
                    row.get('lastName', ''),
                    row.get('webName', '')
                )
                
                # Обновляем профиль на платформе
                self._update_platform_profile(
                    player,
                    team,
                    Platform.FPL,
                    row.get('id', ''),
                    row.get('Pos', ''),
                    float(row.get('Cost', 0)),
                    float(row.get('Select', 0)) if row.get('Select') else None
                )
                
                imported += 1
                
            except Exception as e:
                errors.append(f"Row {reader.line_num}: {str(e)}")
                
        self.db.commit()
        
        return {
            "imported": imported,
            "errors": errors
        }
    
    def _get_or_create_team(self, name: str, abbr: str) -> Team:
        """Получить или создать команду"""
        if not name:
            return None
            
        team = self.db.query(Team).filter(Team.name == name).first()
        if not team:
            team = Team(
                name=name,
                abbreviation=abbr,
                league='Premier League'
            )
            self.db.add(team)
            self.db.flush()
            
        return team
    
    def _get_or_create_player(self, first_name: str, last_name: str, web_name: str) -> Player:
        """Получить или создать игрока"""
        player = self.db.query(Player).filter(
            Player.first_name == first_name,
            Player.last_name == last_name
        ).first()
        
        if not player:
            player = Player(
                first_name=first_name,
                last_name=last_name,
                web_name=web_name
            )
            self.db.add(player)
            self.db.flush()
            
        return player
    
    def _update_platform_profile(
        self, 
        player: Player, 
        team: Team,
        platform: Platform,
        platform_id: str,
        position: str,
        cost: float,
        ownership: float = None
    ):
        """Обновить профиль игрока на платформе"""
        position_map = {
            'GK': Position.GK,
            'G': Position.GK,
            'D': Position.DEF,
            'DEF': Position.DEF,
            'M': Position.MID,
            'MID': Position.MID,
            'F': Position.FWD,
            'FWD': Position.FWD,
        }
        
        profile = self.db.query(PlayerPlatformProfile).filter(
            PlayerPlatformProfile.platform == platform,
            PlayerPlatformProfile.platform_player_id == platform_id
        ).first()
        
        if not profile:
            profile = PlayerPlatformProfile(
                player_id=player.id,
                platform=platform,
                platform_player_id=platform_id,
                team_id=team.id if team else None,
                player_position=position_map.get(position),
                current_cost=cost,
                ownership_percent=ownership,
                is_active=True
            )
            self.db.add(profile)
        else:
            profile.team_id = team.id if team else None
            profile.player_position = position_map.get(position)
            profile.current_cost = cost
            if ownership is not None:
                profile.ownership_percent = ownership
