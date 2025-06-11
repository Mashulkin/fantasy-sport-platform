from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class TimestampMixin:
    """Mixin для добавления временных меток"""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
