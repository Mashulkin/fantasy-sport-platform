from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, Float, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Player(Base, TimestampMixin):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    web_name = Column(String(100))
    date_of_birth = Column(Date, nullable=True)
    nationality = Column(String(50), nullable=True)
    
    # Relationships
    platform_profiles = relationship("PlayerPlatformProfile", back_populates="player", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('first_name', 'last_name', 'date_of_birth', name='_player_uc'),
    )


class PlayerPlatformProfile(Base, TimestampMixin):
    __tablename__ = "player_platform_profiles"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    platform = Column(String(20), nullable=False)  # 'FPL', 'FANTEAM', 'SORARE', 'FANTON'
    platform_player_id = Column(String(50))  # ID игрока на платформе (важно!)
    custom_name = Column(String(100))  # web_name для отображения
    team_id = Column(Integer, ForeignKey("teams.id"))
    player_position = Column(String(10))  # 'GK', 'DEF', 'MID', 'FWD' - позиция на конкретной платформе
    current_cost = Column(Float)
    ownership_percent = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Дополнительные поля для FPL
    status = Column(String(20), nullable=True)  # 'a' - available, 'i' - injured, 'd' - doubtful, 's' - suspended
    form = Column(Float, nullable=True)  # Форма игрока
    total_points = Column(Integer, nullable=True)  # Общее количество очков
    event_points = Column(Integer, nullable=True)  # Очки в последнем туре
    
    # Relationships
    player = relationship("Player", back_populates="platform_profiles")
    team = relationship("Team", back_populates="player_profiles")
    price_history = relationship("PriceHistory", back_populates="player_profile", cascade="all, delete-orphan")
    stats = relationship("PlayerStats", back_populates="player_profile", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('platform', 'platform_player_id', name='_platform_player_uc'),
        CheckConstraint("platform IN ('FPL', 'FANTEAM', 'SORARE', 'FANTON')", name='valid_platform'),
        CheckConstraint("player_position IN ('GK', 'DEF', 'MID', 'FWD')", name='valid_position'),
    )


# Enums для использования в коде
class Platform:
    FPL = "FPL"
    FANTEAM = "FANTEAM"
    SORARE = "SORARE"
    FANTON = "FANTON"


class Position:
    GK = "GK"
    DEF = "DEF"
    MID = "MID"
    FWD = "FWD"
