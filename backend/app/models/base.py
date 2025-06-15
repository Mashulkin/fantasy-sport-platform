"""
Base model classes and mixins for SQLAlchemy models.

This module provides common functionality and mixins that can be used
across different model classes to ensure consistency and reduce code
duplication. Currently includes timestamp functionality for tracking
record creation and modification times.
"""

from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class TimestampMixin:
    """
    Mixin class that adds automatic timestamp columns to models.
    
    Provides created_at and updated_at columns that are automatically
    managed by the database. The created_at field is set once when the
    record is created, while updated_at is updated on every modification.
    
    Attributes:
        created_at (DateTime): Timestamp when record was created
        updated_at (DateTime): Timestamp when record was last modified
    """
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False,
        comment="Timestamp when the record was created"
    )
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False,
        comment="Timestamp when the record was last updated"
    )
