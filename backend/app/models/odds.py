from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class MatchOdds(Base, TimestampMixin):
    __tablename__ = "match_odds"

    id = Column(Integer, primary_key=True, index=True)
    home_team_id = Column(Integer, ForeignKey("teams.id"))
    away_team_id = Column(Integer, ForeignKey("teams.id"))
    match_date = Column(DateTime)
    league = Column(String(50))
    
    # Odds
    home_win = Column(Float)
    draw = Column(Float)
    away_win = Column(Float)
    over_2_5 = Column(Float)
    under_2_5 = Column(Float)
    over_1_5 = Column(Float)
    under_1_5 = Column(Float)
    home_clean_sheet = Column(Float)
    away_clean_sheet = Column(Float)
    
    # Metadata
    odds_source = Column(String(50))
    parsed_at = Column(DateTime)
    
    # Relationships
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_matches")
