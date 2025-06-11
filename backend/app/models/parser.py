from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class ParserConfig(Base, TimestampMixin):
    __tablename__ = "parser_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    platform = Column(String(20))
    parser_type = Column(String(50))  # 'players', 'stats', 'odds'
    schedule = Column(String(100))  # Cron expression
    is_active = Column(Boolean, default=True)
    last_run = Column(DateTime)
    last_status = Column(String(50))
    config = Column(JSON)
    """
    Example config:
    {
        "api_url": "https://fantasy.premierleague.com/api/bootstrap-static/",
        "headers": {"User-Agent": "Mozilla/5.0"},
        "timeout": 30,
        "retry_count": 3,
        "season": "2024-25"
    }
    """
    
    # Relationships
    logs = relationship("ParserLog", back_populates="parser_config", cascade="all, delete-orphan")


class ParserLog(Base):
    __tablename__ = "parser_logs"

    id = Column(Integer, primary_key=True, index=True)
    parser_config_id = Column(Integer, ForeignKey("parser_configs.id"))
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    status = Column(String(50))  # 'running', 'success', 'failed'
    records_processed = Column(Integer)
    errors_count = Column(Integer)
    log_data = Column(Text)
    created_at = Column(DateTime)
    
    # Relationships
    parser_config = relationship("ParserConfig", back_populates="logs")
