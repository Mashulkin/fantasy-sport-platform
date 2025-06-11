from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Team(Base, TimestampMixin):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    abbreviation = Column(String(10))
    league = Column(String(50))
    
    # Relationships
    player_profiles = relationship("PlayerPlatformProfile", back_populates="team")
    home_matches = relationship("MatchOdds", foreign_keys="MatchOdds.home_team_id", back_populates="home_team")
    away_matches = relationship("MatchOdds", foreign_keys="MatchOdds.away_team_id", back_populates="away_team")
