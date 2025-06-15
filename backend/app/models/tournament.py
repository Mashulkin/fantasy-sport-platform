"""
Tournament and competition models.

Manages fantasy tournament data including participants,
settings, and different tournament types across platforms.
"""

from sqlalchemy import (
    Column, Integer, String, ForeignKey, Boolean, Date, 
    JSON, Text, Enum
)
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin
import enum


class TournamentType(str, enum.Enum):
    """Available tournament types."""
    H2H = "H2H"         # Head-to-head format
    CLASSIC = "CLASSIC" # Classic league format
    CUSTOM = "CUSTOM"   # Custom tournament rules


class Tournament(Base, TimestampMixin):
    """
    Fantasy tournament or league configuration.
    
    Stores tournament metadata, rules, and settings for
    various types of fantasy competitions.
    """
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    tournament_type = Column(Enum(TournamentType, name='tournament_type_enum'))
    platform = Column(String(20))      # Source platform for data
    start_date = Column(Date)
    end_date = Column(Date)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    settings = Column(JSON)             # Tournament-specific configuration
    
    # Relationships
    creator = relationship("User")
    participants = relationship(
        "TournamentParticipant", 
        back_populates="tournament", 
        cascade="all, delete-orphan"
    )


class TournamentParticipant(Base, TimestampMixin):
    """
    Tournament participation record.
    
    Links users to tournaments with their team information
    and external platform identifiers.
    """
    __tablename__ = "tournament_participants"

    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    team_name = Column(String(100))
    external_team_id = Column(String(100))  # ID on external platform
    
    # Relationships
    tournament = relationship("Tournament", back_populates="participants")
    user = relationship("User")
