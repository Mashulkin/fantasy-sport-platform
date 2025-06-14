"""
Player models for multi-platform fantasy sports data.

Defines player entities with platform-specific profiles to handle
different fantasy platforms having different player representations.
"""

from sqlalchemy import (
    Column, Integer, String, Date, ForeignKey, Boolean, Float, 
    UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Player(Base, TimestampMixin):
    """
    Core player model representing real-world football players.
    
    Contains platform-agnostic player information like name and birth date.
    Platform-specific data is stored in PlayerPlatformProfile.
    """
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    web_name = Column(String(100))      # Display name for web interfaces
    date_of_birth = Column(Date, nullable=True)
    nationality = Column(String(50), nullable=True)
    
    # Relationships
    platform_profiles = relationship(
        "PlayerPlatformProfile", 
        back_populates="player", 
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        UniqueConstraint(
            'first_name', 'last_name', 'date_of_birth', 
            name='_player_uc'
        ),
    )


class PlayerPlatformProfile(Base, TimestampMixin):
    """
    Platform-specific player profile and statistics.
    
    Each player can have multiple profiles for different fantasy platforms
    (FPL, Fanteam, etc.) with platform-specific pricing, positions, and stats.
    """
    __tablename__ = "player_platform_profiles"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    platform = Column(String(20), nullable=False)  # Platform identifier
    platform_player_id = Column(String(50))        # Player ID on platform
    custom_name = Column(String(100))               # Platform display name
    team_id = Column(Integer, ForeignKey("teams.id"))
    player_position = Column(String(10))            # Position on platform
    current_cost = Column(Float)                    # Current price/cost
    ownership_percent = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # FPL-specific fields
    status = Column(String(20), nullable=True)      # a=available, i=injured, etc.
    form = Column(Float, nullable=True)             # Recent form rating
    total_points = Column(Integer, nullable=True)   # Season total points
    event_points = Column(Integer, nullable=True)   # Latest gameweek points
    
    # Relationships
    player = relationship("Player", back_populates="platform_profiles")
    team = relationship("Team", back_populates="player_profiles")
    price_history = relationship(
        "PriceHistory", 
        back_populates="player_profile", 
        cascade="all, delete-orphan"
    )
    stats = relationship(
        "PlayerStats", 
        back_populates="player_profile", 
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        UniqueConstraint(
            'platform', 'platform_player_id', 
            name='_platform_player_uc'
        ),
        CheckConstraint(
            "platform IN ('FPL', 'FANTEAM', 'SORARE', 'FANTON')", 
            name='valid_platform'
        ),
        CheckConstraint(
            "player_position IN ('GK', 'DEF', 'MID', 'FWD')", 
            name='valid_position'
        ),
    )


class Platform:
    """Constants for supported fantasy platforms."""
    FPL = "FPL"
    FANTEAM = "FANTEAM"
    SORARE = "SORARE"
    FANTON = "FANTON"


class Position:
    """Constants for player positions."""
    GK = "GK"    # Goalkeeper
    DEF = "DEF"  # Defender
    MID = "MID"  # Midfielder
    FWD = "FWD"  # Forward
