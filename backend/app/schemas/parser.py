from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class ParserConfigBase(BaseModel):
    name: str
    platform: Optional[str] = None
    parser_type: str
    schedule: Optional[str] = None
    is_active: bool = True
    config: Optional[Dict[str, Any]] = {}


class ParserConfigCreate(ParserConfigBase):
    pass


class ParserConfigUpdate(BaseModel):
    name: Optional[str] = None
    platform: Optional[str] = None
    parser_type: Optional[str] = None
    schedule: Optional[str] = None
    is_active: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None


class ParserConfig(ParserConfigBase):
    id: int
    last_run: Optional[datetime] = None
    last_status: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ParserLog(BaseModel):
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
    status: str
    parser_id: int
    parser_name: str
    started_at: datetime
    task_id: Optional[str] = None
