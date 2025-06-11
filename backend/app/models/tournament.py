from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date, JSON, Text, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin
import enum


class TournamentType(str, enum.Enum):
    H2H = "H2H"
    CLASSIC = "CLASSIC"
    CUSTOM = "CUSTOM"


class Tournament(Base, TimestampMixin):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    tournament_type = Column(Enum(TournamentType, name='tournament_type_enum'))
    platform = Column(String(20))  # Data source platform
    start_date = Column(Date)
    end_date = Column(Date)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    settings = Column(JSON)
    """
    Example settings:
    {
        "scoring_system": "FPL",
        "max_players_per_team": 3,
        "budget": 100.0,
        "transfers_per_week": 2,
        "chip_usage": ["wildcard", "bench_boost", "triple_captain"],
        "h2h_settings": {
            "points_for_win": 3,
            "points_for_draw": 1,
            "points_for_loss": 0
        }
    }
    """
    
    # Relationships
    creator = relationship("User")
    participants = relationship("TournamentParticipant", back_populates="tournament", cascade="all, delete-orphan")


class TournamentParticipant(Base, TimestampMixin):
    __tablename__ = "tournament_participants"

    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    team_name = Column(String(100))
    external_team_id = Column(String(100))  # ID on external platform
    
    # Relationships
    tournament = relationship("Tournament", back_populates="participants")
    user = relationship("User")
