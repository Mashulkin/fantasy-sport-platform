from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Date, Boolean, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class PlayerStats(Base, TimestampMixin):
    __tablename__ = "player_stats"

    id = Column(Integer, primary_key=True, index=True)
    player_profile_id = Column(Integer, ForeignKey("player_platform_profiles.id"))
    gameweek = Column(Integer)
    match_date = Column(Date)
    opponent_team_id = Column(Integer, ForeignKey("teams.id"))
    is_home = Column(Boolean)
    
    # Basic stats (common across all platforms)
    minutes_played = Column(Integer, default=0)
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    clean_sheets = Column(Integer, default=0)
    goals_conceded = Column(Integer, default=0)
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    points = Column(Float)
    
    # Extended stats in JSON
    extended_stats = Column(JSON)
    """
    Example extended_stats:
    {
        "shots": 3,
        "shots_on_target": 2,
        "key_passes": 1,
        "tackles": 4,
        "interceptions": 2,
        "penalties_won": 0,
        "penalties_missed": 0,
        "bonus": 2,
        "bps": 28,
        "influence": "24.5",
        "creativity": "18.3",
        "threat": "45.0",
        "ict_index": "8.8",
        "fouls_drawn": 2,
        "fouls_committed": 1,
        "blocked_shots": 1,
        "clearances": 3,
        "successful_dribbles": 2,
        "aerial_duels_won": 1
    }
    """
    
    data_source = Column(String(50))
    parsed_at = Column(DateTime)
    
    # Relationships
    player_profile = relationship("PlayerPlatformProfile", back_populates="stats")
    opponent_team = relationship("Team")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    player_profile_id = Column(Integer, ForeignKey("player_platform_profiles.id"))
    cost = Column(Float)
    ownership_percent = Column(Float, nullable=True)
    recorded_at = Column(DateTime)
    
    # Relationships
    player_profile = relationship("PlayerPlatformProfile", back_populates="price_history")
