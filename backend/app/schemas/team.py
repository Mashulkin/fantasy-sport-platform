"""
Pydantic schemas for team data models.

Defines request/response schemas for team information
and team management operations.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class TeamBase(BaseModel):
    """Base schema for team information."""
    name: str
    abbreviation: Optional[str] = None
    league: Optional[str] = None


class TeamCreate(TeamBase):
    """Schema for creating new teams."""
    pass


class TeamUpdate(TeamBase):
    """Schema for updating existing teams."""
    name: Optional[str] = None


class Team(TeamBase):
    """Schema for team response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
