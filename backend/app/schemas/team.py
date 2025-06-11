from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class TeamBase(BaseModel):
    name: str
    abbreviation: Optional[str] = None
    league: Optional[str] = None


class TeamCreate(TeamBase):
    pass


class TeamUpdate(TeamBase):
    name: Optional[str] = None


class Team(TeamBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
