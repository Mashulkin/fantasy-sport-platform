"""
Player statistics and price history models.

Tracks player performance data and pricing changes over time
across different fantasy platforms and gameweeks.
"""

from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey, DateTime, Date, 
    Boolean, JSON
)
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class PlayerStats(Base, TimestampMixin):
    """
    Player performance statistics for specific matches/gameweeks.
    
    Stores both basic stats (goals, assists) and extended platform-specific
    metrics in JSON format for flexibility across different platforms.
    """
    __tablename__ = "player_stats"

    id = Column(Integer, primary_key=True, index=True)
    player_profile_id = Column(Integer, ForeignKey("player_platform_profiles.id"))
    gameweek = Column(Integer)
    match_date = Column(Date)
    opponent_team_id = Column(Integer, ForeignKey("teams.id"))
    is_home = Column(Boolean)
    
    # Basic statistics (common across platforms)
    minutes_played = Column(Integer, default=0)
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    clean_sheets = Column(Integer, default=0)
    goals_conceded = Column(Integer, default=0)
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    points = Column(Float)                      # Platform-specific points
    
    # Extended platform-specific statistics stored as JSON
    extended_stats = Column(JSON)
    
    data_source = Column(String(50))            # Source platform/API
    parsed_at = Column(DateTime)
    
    # Relationships
    player_profile = relationship("PlayerPlatformProfile", back_populates="stats")
    opponent_team = relationship("Team")


class PriceHistory(Base):
    """
    Historical pricing data for player platform profiles.
    
    Tracks price changes and ownership fluctuations over time
    for analysis and decision-making support.
    """
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    player_profile_id = Column(Integer, ForeignKey("player_platform_profiles.id"))
    cost = Column(Float)
    ownership_percent = Column(Float, nullable=True)
    recorded_at = Column(DateTime)
    
    # Relationships
    player_profile = relationship("PlayerPlatformProfile", back_populates="price_history")
