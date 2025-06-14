"""
Team model for sports teams across different platforms.

Represents football clubs/teams that players belong to,
with support for multiple leagues and competitions.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Team(Base, TimestampMixin):
    """
    Sports team model for player affiliations.
    
    Represents real-world football teams that players belong to.
    Used across different fantasy platforms for consistent team data.
    """
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # Full team name
    abbreviation = Column(String(10))           # Short code (e.g., "ARS", "CHE")
    league = Column(String(50))                 # League/competition name
    
    # Relationships
    player_profiles = relationship("PlayerPlatformProfile", back_populates="team")
    home_matches = relationship(
        "MatchOdds", 
        foreign_keys="MatchOdds.home_team_id", 
        back_populates="home_team"
    )
    away_matches = relationship(
        "MatchOdds", 
        foreign_keys="MatchOdds.away_team_id", 
        back_populates="away_team"
    )
