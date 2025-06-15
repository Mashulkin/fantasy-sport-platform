"""
Match odds and betting data models.

Stores betting odds for football matches from various sources
for analysis and decision-making support.
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class MatchOdds(Base, TimestampMixin):
    """
    Betting odds for football matches.
    
    Stores various betting market odds including match outcome,
    goals totals, and clean sheet markets from different sources.
    """
    __tablename__ = "match_odds"

    id = Column(Integer, primary_key=True, index=True)
    home_team_id = Column(Integer, ForeignKey("teams.id"))
    away_team_id = Column(Integer, ForeignKey("teams.id"))
    match_date = Column(DateTime)
    league = Column(String(50))
    
    # Match outcome odds
    home_win = Column(Float)
    draw = Column(Float)
    away_win = Column(Float)
    
    # Goals markets
    over_2_5 = Column(Float)    # Over 2.5 goals
    under_2_5 = Column(Float)   # Under 2.5 goals
    over_1_5 = Column(Float)    # Over 1.5 goals
    under_1_5 = Column(Float)   # Under 1.5 goals
    
    # Clean sheet markets
    home_clean_sheet = Column(Float)
    away_clean_sheet = Column(Float)
    
    # Metadata
    odds_source = Column(String(50))    # Source bookmaker or API
    parsed_at = Column(DateTime)        # When odds were collected
    
    # Relationships
    home_team = relationship(
        "Team", 
        foreign_keys=[home_team_id], 
        back_populates="home_matches"
    )
    away_team = relationship(
        "Team", 
        foreign_keys=[away_team_id], 
        back_populates="away_matches"
    )
