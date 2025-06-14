"""
Parser configuration and logging models.

Manages automated data parsing schedules, configurations,
and execution logs for monitoring parser performance.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class ParserConfig(Base, TimestampMixin):
    """
    Configuration for automated data parsers.
    
    Stores parser settings, schedules, and execution metadata
    for background data collection tasks.
    """
    __tablename__ = "parser_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    platform = Column(String(20))              # Target platform (FPL, etc.)
    parser_type = Column(String(50))            # Parser implementation type
    schedule = Column(String(100))              # Cron expression for scheduling
    is_active = Column(Boolean, default=True)
    last_run = Column(DateTime)                 # Last execution timestamp
    last_status = Column(String(50))            # Last execution result
    config = Column(JSON)                       # Parser-specific configuration
    
    # Relationships
    logs = relationship(
        "ParserLog", 
        back_populates="parser_config", 
        cascade="all, delete-orphan"
    )


class ParserLog(Base):
    """
    Execution log for parser runs.
    
    Tracks parser performance, errors, and processing statistics
    for debugging and monitoring purposes.
    """
    __tablename__ = "parser_logs"

    id = Column(Integer, primary_key=True, index=True)
    parser_config_id = Column(Integer, ForeignKey("parser_configs.id"))
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    status = Column(String(50))                 # running, success, failed
    records_processed = Column(Integer)
    errors_count = Column(Integer)
    log_data = Column(Text)                     # Detailed log output
    created_at = Column(DateTime)
    
    # Relationships
    parser_config = relationship("ParserConfig", back_populates="logs")
