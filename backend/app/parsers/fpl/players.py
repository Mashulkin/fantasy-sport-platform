"""
Fantasy Premier League (FPL) data parsers.

This module contains parsers for fetching player data, team information,
and ownership statistics from the official FPL API.
"""

import os
import sys
import csv
from datetime import datetime
from typing import Dict, Any, List
import httpx
from sqlalchemy import and_

from app.parsers.base import BaseParser
from app.models.player import Player, PlayerPlatformProfile, Platform, Position
from app.models.team import Team
from app.models.stats import PriceHistory


class FPLPlayersParser(BaseParser):
    """
    Parser for FPL player data and team information.
    
    Fetches complete player roster with statistics, prices, and team data
    from the FPL bootstrap-static API endpoint.
    """
    
    API_URL = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    
    async def parse(self) -> Dict[str, Any]:
        """
        Fetch player and team data from FPL API.
        
        Returns:
            Dict[str, Any]: Complete FPL data including players and teams
        """
        self.log("Fetching data from FPL API...")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.API_URL)
            
            if response.status_code != 200:
                raise Exception(f"API returned status code: {response.status_code}")
                
            data = response.json()
            self.log(f"Received {len(data['elements'])} players")
            
            return data
    
    async def save_to_db(self, data: Dict[str, Any]) -> None:
        """
        Save FPL data to database.
        
        Updates teams first to establish foreign key relationships,
        then processes players with their platform profiles.
        
        Args:
            data: FPL API response data
        """
        # Update teams and get ID mapping
        team_mapping = await self._update_teams(data['teams'])
        
        # Update players with team references
        await self._update_players(data['elements'], team_mapping)
        
    async def _update_teams(self, teams_data: List[Dict]) -> Dict[int, Team]:
        """
        Update team information in database.
        
        Args:
            teams_data: List of team data from FPL API
            
        Returns:
            Dict[int, Team]: Mapping of FPL team ID to Team objects
        """
        self.log("Updating teams...")
        
        team_mapping = {}
        
        for team_data in teams_data:
            # Find or create team
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
                # Update abbreviation if changed
                team.abbreviation = team_data.get('short_name', '')
            
            # Store mapping for player processing
            team_mapping[team_data['id']] = team
                
        self.db.commit()
        return team_mapping
    
    async def _update_players(
        self, 
        players_data: List[Dict], 
        team_mapping: Dict[int, Team]
    ) -> None:
        """
        Update player information and platform profiles.
        
        Args:
            players_data: List of player data from FPL API
            team_mapping: Mapping of FPL team IDs to Team objects
        """
        self.log("Updating players...")
        
        # Map FPL position IDs to standard position codes
        position_map = {
            1: 'GK',   # Goalkeeper
            2: 'DEF',  # Defender
            3: 'MID',  # Midfielder
            4: 'FWD'   # Forward
        }
        
        for player_data in players_data:
            try:
                # Skip unavailable players
                if player_data.get('status') == 'u':
                    continue
                
                # Get team from mapping
                team = team_mapping.get(player_data['team'])
                if not team:
                    self.log(
                        f"Team not found for player {player_data['web_name']}", 
                        "WARNING"
                    )
                    continue
                
                # Extract player data
                player_info = self._extract_player_info(player_data, position_map)
                
                # Find or create player record
                player = self._get_or_create_player(player_info)
                
                # Update platform profile
                self._update_platform_profile(player, team, player_info)
                
                # Update price history if needed
                self._update_price_history(player_info)
                
                self.records_processed += 1
                
                # Log progress every 100 players
                if self.records_processed % 100 == 0:
                    self.log(f"Processed {self.records_processed} players...")
                
            except Exception as e:
                self.log(
                    f"Error processing player {player_data.get('web_name', 'Unknown')}: {str(e)}", 
                    "ERROR"
                )
                continue
        
        self.db.commit()
        self.log(f"Updated {self.records_processed} players")
    
    def _extract_player_info(self, player_data: Dict, position_map: Dict) -> Dict:
        """
        Extract and normalize player information from API response.
        
        Args:
            player_data: Raw player data from FPL API
            position_map: Mapping of position IDs to position codes
            
        Returns:
            Dict: Normalized player information
        """
        return {
            'real_player_id': str(player_data['code']),
            'first_name': player_data['first_name'],
            'last_name': player_data['second_name'],
            'web_name': player_data['web_name'],
            'position': position_map.get(player_data['element_type']),
            'status': player_data.get('status', 'a'),
            'current_price': player_data['now_cost'] / 10,  # Convert from pence
            'ownership': float(player_data.get('selected_by_percent', 0)),
            'form': float(player_data.get('form', 0)),
            'total_points': player_data.get('total_points', 0),
            'event_points': player_data.get('event_points', 0),
            'season_player_id': str(player_data['id']),
            'team': player_data['team']
        }
    
    def _get_or_create_player(self, player_info: Dict) -> Player:
        """
        Find existing player or create new one.
        
        Args:
            player_info: Normalized player information
            
        Returns:
            Player: Player database object
        """
        player = self.db.query(Player).filter(
            and_(
                Player.first_name == player_info['first_name'],
                Player.last_name == player_info['last_name']
            )
        ).first()
        
        if not player:
            player = Player(
                first_name=player_info['first_name'],
                last_name=player_info['last_name'],
                web_name=player_info['web_name']
            )
            self.db.add(player)
            self.db.flush()
        else:
            # Update web_name if changed
            player.web_name = player_info['web_name']
        
        return player
    
    def _update_platform_profile(
        self, 
        player: Player, 
        team: Team, 
        player_info: Dict
    ) -> PlayerPlatformProfile:
        """
        Update or create FPL platform profile for player.
        
        Args:
            player: Player database object
            team: Team database object
            player_info: Normalized player information
            
        Returns:
            PlayerPlatformProfile: Updated profile object
        """
        profile = self.db.query(PlayerPlatformProfile).filter(
            and_(
                PlayerPlatformProfile.platform == Platform.FPL,
                PlayerPlatformProfile.platform_player_id == player_info['season_player_id']
            )
        ).first()
        
        if not profile:
            profile = PlayerPlatformProfile(
                player_id=player.id,
                platform=Platform.FPL,
                platform_player_id=player_info['season_player_id'],
                custom_name=player_info['web_name'],
                team_id=team.id,
                player_position=player_info['position'],
                current_cost=player_info['current_price'],
                ownership_percent=player_info['ownership'],
                is_active=player_info['status'] != 'u',
                status=player_info['status'],
                form=player_info['form'],
                total_points=player_info['total_points'],
                event_points=player_info['event_points']
            )
            self.db.add(profile)
            self.db.flush()
        else:
            # Update all profile fields
            profile.team_id = team.id
            profile.player_position = player_info['position']
            profile.current_cost = player_info['current_price']
            profile.ownership_percent = player_info['ownership']
            profile.is_active = player_info['status'] != 'u'
            profile.custom_name = player_info['web_name']
            profile.status = player_info['status']
            profile.form = player_info['form']
            profile.total_points = player_info['total_points']
            profile.event_points = player_info['event_points']
        
        return profile
    
    def _update_price_history(self, player_info: Dict) -> None:
        """
        Add price history record if price or ownership changed.
        
        Args:
            player_info: Normalized player information
        """
        profile = self.db.query(PlayerPlatformProfile).filter(
            and_(
                PlayerPlatformProfile.platform == Platform.FPL,
                PlayerPlatformProfile.platform_player_id == player_info['season_player_id']
            )
        ).first()
        
        if not profile:
            return
        
        # Check if price or ownership changed
        last_price = self.db.query(PriceHistory).filter(
            PriceHistory.player_profile_id == profile.id
        ).order_by(PriceHistory.recorded_at.desc()).first()
        
        current_price = player_info['current_price']
        current_ownership = player_info['ownership']
        
        if (not last_price or 
            last_price.cost != current_price or 
            last_price.ownership_percent != current_ownership):
            
            price_history = PriceHistory(
                player_profile_id=profile.id,
                cost=current_price,
                ownership_percent=current_ownership,
                recorded_at=datetime.now()
            )
            self.db.add(price_history)


class FPLOwnershipParser(BaseParser):
    """
    Lightweight parser for updating FPL player ownership percentages.
    
    Used for frequent ownership updates without full player data refresh.
    """
    
    API_URL = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    
    async def parse(self) -> Dict[str, Any]:
        """
        Fetch ownership data from FPL API.
        
        Returns:
            Dict[str, Any]: FPL API response with ownership data
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(self.API_URL)
            return response.json()
    
    async def save_to_db(self, data: Dict[str, Any]) -> None:
        """
        Update ownership percentages for existing players.
        
        Args:
            data: FPL API response data
        """
        for player_data in data['elements']:
            # Skip unavailable players
            if player_data.get('status') == 'u':
                continue
                
            # Find existing platform profile
            profile = self.db.query(PlayerPlatformProfile).filter(
                and_(
                    PlayerPlatformProfile.platform == Platform.FPL,
                    PlayerPlatformProfile.platform_player_id == str(player_data['id'])
                )
            ).first()
            
            if profile:
                profile.ownership_percent = float(
                    player_data.get('selected_by_percent', 0)
                )
                self.records_processed += 1
        
        self.db.commit()
        self.log(f"Updated ownership for {self.records_processed} players")
