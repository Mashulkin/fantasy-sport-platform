"""
User model for authentication and authorization.

Defines the User entity with authentication fields and relationships
to tournaments and other user-created content.
"""

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class User(Base, TimestampMixin):
    """
    User account model for platform access.
    
    Handles authentication, authorization, and user-specific data
    like created tournaments and participation records.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Relationships
    created_tournaments = relationship("Tournament", back_populates="creator")
    tournament_participations = relationship("TournamentParticipant", back_populates="user")
