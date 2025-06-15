"""
Pydantic schemas for parser configuration and logging.

Defines request/response models for parser management endpoints
including configuration, execution logs, and task status.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class ParserConfigBase(BaseModel):
    """Base schema for parser configuration."""
    name: str
    platform: Optional[str] = None
    parser_type: str
    schedule: Optional[str] = None
    is_active: bool = True
    config: Optional[Dict[str, Any]] = {}


class ParserConfigCreate(ParserConfigBase):
    """Schema for creating new parser configurations."""
    pass


class ParserConfigUpdate(BaseModel):
    """Schema for updating existing parser configurations."""
    name: Optional[str] = None
    platform: Optional[str] = None
    parser_type: Optional[str] = None
    schedule: Optional[str] = None
    is_active: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None


class ParserConfig(ParserConfigBase):
    """Schema for parser configuration response."""
    id: int
    last_run: Optional[datetime] = None
    last_status: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ParserLog(BaseModel):
    """Schema for parser execution logs."""
    id: int
    parser_config_id: int
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    status: Optional[str]
    records_processed: Optional[int]
    errors_count: Optional[int]
    log_data: Optional[str]
    
    class Config:
        from_attributes = True


class ParserRunResponse(BaseModel):
    """Schema for parser execution response."""
    status: str
    parser_id: int
    parser_name: str
    started_at: datetime
    task_id: Optional[str] = None
