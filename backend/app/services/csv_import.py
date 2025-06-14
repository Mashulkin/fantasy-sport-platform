"""
CSV import service for bulk data loading.

Provides utilities for importing player and team data from CSV files
with validation and error handling.
"""

import csv
import io
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.player import Player, PlayerPlatformProfile, Platform, Position
from app.models.team import Team


class CSVImportService:
    """
    Service for importing data from CSV files.
    
    Handles CSV parsing, data validation, and database operations
    for bulk data import operations.
    """
    
    def __init__(self, db: Session):
        """
        Initialize CSV import service.
        
        Args:
            db: Database session for import operations
        """
        self.db = db
        
    def import_fpl_players(self, csv_content: str) -> Dict[str, Any]:
        """
        Import FPL player data from CSV content.
        
        Processes CSV data to create or update player records,
        team assignments, and platform profiles.
        
        Args:
            csv_content: CSV file content as string
            
        Returns:
            Dict containing import statistics and error details
        """
        reader = csv.DictReader(io.StringIO(csv_content))
        
        imported = 0
        errors = []
        
        for row_num, row in enumerate(reader, start=1):
            try:
                # Process team information
                team = self._get_or_create_team(
                    row.get('Team', ''),
                    row.get('Abbr', '')
                )
                
                # Process player information
                player = self._get_or_create_player(
                    row.get('firstName', ''),
                    row.get('lastName', ''),
                    row.get('webName', '')
                )
                
                # Update platform profile
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
                errors.append(f"Row {row_num}: {str(e)}")
                
        self.db.commit()
        
        return {
            "imported": imported,
            "errors": errors
        }
    
    def _get_or_create_team(self, name: str, abbr: str) -> Team:
        """
        Get existing team or create new one.
        
        Args:
            name: Full team name
            abbr: Team abbreviation
            
        Returns:
            Team: Team database object
        """
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
    
    def _get_or_create_player(
        self, 
        first_name: str, 
        last_name: str, 
        web_name: str
    ) -> Player:
        """
        Get existing player or create new one.
        
        Args:
            first_name: Player's first name
            last_name: Player's last name
            web_name: Display name for web interfaces
            
        Returns:
            Player: Player database object
        """
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
        platform: str,
        platform_id: str,
        position: str,
        cost: float,
        ownership: float = None
    ):
        """
        Update or create platform profile for player.
        
        Args:
            player: Player database object
            team: Team database object
            platform: Platform identifier
            platform_id: Player ID on the platform
            position: Player position code
            cost: Current player cost/price
            ownership: Ownership percentage (optional)
        """
        # Map position strings to standard codes
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
        
        # Find or create platform profile
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
            # Update existing profile
            profile.team_id = team.id if team else None
            profile.player_position = position_map.get(position)
            profile.current_cost = cost
            if ownership is not None:
                profile.ownership_percent = ownership
