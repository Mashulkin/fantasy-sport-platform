# Import all models here to ensure they are registered with SQLAlchemy
from app.models.user import User
from app.models.team import Team
from app.models.player import Player, PlayerPlatformProfile, Platform, Position
from app.models.stats import PlayerStats, PriceHistory
from app.models.tournament import Tournament, TournamentParticipant, TournamentType
from app.models.parser import ParserConfig, ParserLog
from app.models.odds import MatchOdds

__all__ = [
    "User",
    "Team",
    "Player",
    "PlayerPlatformProfile",
    "Platform",
    "Position",
    "PlayerStats",
    "PriceHistory",
    "Tournament",
    "TournamentParticipant",
    "TournamentType",
    "ParserConfig",
    "ParserLog",
    "MatchOdds"
]
