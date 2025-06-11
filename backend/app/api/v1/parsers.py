from typing import List, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api import deps
from app.models.parser import ParserConfig, ParserLog
from app.models.user import User
from app.schemas.parser import (
    ParserConfigCreate, 
    ParserConfigUpdate, 
    ParserConfig as ParserConfigSchema,
    ParserLog as ParserLogSchema,
    ParserRunResponse
)
from app.services.parser_service import ParserService, PARSER_REGISTRY

router = APIRouter()


@router.get("/", response_model=List[ParserConfigSchema])
def get_parsers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Get list of all parser configurations"""
    parsers = db.query(ParserConfig).offset(skip).limit(limit).all()
    return parsers


@router.get("/types")
def get_parser_types(
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Get list of available parser types"""
    return list(PARSER_REGISTRY.keys())


@router.post("/", response_model=ParserConfigSchema)
def create_parser(
    *,
    db: Session = Depends(deps.get_db),
    parser_in: ParserConfigCreate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Create new parser configuration"""
    if parser_in.parser_type not in PARSER_REGISTRY:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown parser type: {parser_in.parser_type}"
        )
    
    parser = ParserConfig(**parser_in.dict())
    db.add(parser)
    db.commit()
    db.refresh(parser)
    return parser


@router.put("/{parser_id}", response_model=ParserConfigSchema)
def update_parser(
    *,
    db: Session = Depends(deps.get_db),
    parser_id: int,
    parser_in: ParserConfigUpdate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Update parser configuration"""
    parser = db.query(ParserConfig).get(parser_id)
    if not parser:
        raise HTTPException(status_code=404, detail="Parser not found")
    
    update_data = parser_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(parser, field, value)
    
    db.commit()
    db.refresh(parser)
    return parser


@router.post("/{parser_id}/run", response_model=ParserRunResponse)
async def run_parser(
    *,
    db: Session = Depends(deps.get_db),
    parser_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Run parser manually"""
    parser = db.query(ParserConfig).get(parser_id)
    if not parser:
        raise HTTPException(status_code=404, detail="Parser not found")
    
    if not parser.is_active:
        raise HTTPException(status_code=400, detail="Parser is not active")
    
    # Запускаем парсер в фоне
    background_tasks.add_task(
        ParserService.run_parser,
        parser_id,
        db
    )
    
    return {
        "status": "started",
        "parser_id": parser_id,
        "parser_name": parser.name,
        "started_at": datetime.now()
    }


@router.get("/{parser_id}/logs", response_model=List[ParserLogSchema])
def get_parser_logs(
    *,
    db: Session = Depends(deps.get_db),
    parser_id: int,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Get parser execution logs"""
    logs = db.query(ParserLog).filter(
        ParserLog.parser_config_id == parser_id
    ).order_by(desc(ParserLog.started_at)).offset(skip).limit(limit).all()
    
    return logs


@router.delete("/{parser_id}")
def delete_parser(
    *,
    db: Session = Depends(deps.get_db),
    parser_id: int,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Delete parser configuration"""
    parser = db.query(ParserConfig).get(parser_id)
    if not parser:
        raise HTTPException(status_code=404, detail="Parser not found")
    
    db.delete(parser)
    db.commit()
    
    return {"status": "deleted"}
