"""
Pydantic schemas for player data models.

Defines request/response schemas for player information,
platform profiles, and team associations.
"""

from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel


class PlayerBase(BaseModel):
    """Base schema for player information."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    web_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = None


class PlayerCreate(PlayerBase):
    """Schema for creating new players."""
    pass


class PlayerUpdate(PlayerBase):
    """Schema for updating existing players."""
    pass


class Player(PlayerBase):
    """Schema for player response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TeamBase(BaseModel):
    """Base schema for team information in player context."""
    id: int
    name: str
    abbreviation: Optional[str] = None
    league: Optional[str] = None
    
    class Config:
        from_attributes = True


class PlayerPlatformProfileBase(BaseModel):
    """Base schema for player platform profiles."""
    platform: str
    platform_player_id: Optional[str] = None
    custom_name: Optional[str] = None
    player_position: Optional[str] = None
    current_cost: Optional[float] = None
    ownership_percent: Optional[float] = None
    is_active: bool = True
    status: Optional[str] = None
    form: Optional[float] = None
    total_points: Optional[int] = None
    event_points: Optional[int] = None


class PlayerPlatformProfile(PlayerPlatformProfileBase):
    """Schema for player platform profile response."""
    id: int
    player_id: int
    team_id: Optional[int] = None
    team: Optional[TeamBase] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PlayerWithProfiles(Player):
    """Schema for player with all platform profiles."""
    platform_profiles: List[PlayerPlatformProfile] = []
    
    class Config:
        from_attributes = True
