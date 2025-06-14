"""
Parser management endpoints for admin users.

Provides CRUD operations for parser configurations, manual execution,
task monitoring, and log viewing functionality.
"""

from typing import List, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
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
    """
    Get list of all parser configurations.
    
    Returns paginated list of parser configurations with their
    current status and last execution information.
    
    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        db: Database session
        current_user: Current superuser (required for access)
        
    Returns:
        List[ParserConfig]: List of parser configurations
    """
    parsers = db.query(ParserConfig).offset(skip).limit(limit).all()
    return parsers


@router.get("/types")
def get_parser_types(
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get list of available parser types.
    
    Returns all registered parser types that can be configured
    for automatic data collection.
    
    Args:
        current_user: Current superuser (required for access)
        
    Returns:
        List[str]: Available parser type identifiers
    """
    return list(PARSER_REGISTRY.keys())


@router.post("/", response_model=ParserConfigSchema)
def create_parser(
    *,
    db: Session = Depends(deps.get_db),
    parser_in: ParserConfigCreate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new parser configuration.
    
    Creates a new parser with the specified type and schedule.
    The parser type must be registered in the PARSER_REGISTRY.
    
    Args:
        db: Database session
        parser_in: Parser configuration data
        current_user: Current superuser (required for access)
        
    Returns:
        ParserConfig: Created parser configuration
        
    Raises:
        HTTPException: If parser type is not registered
    """
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
    """
    Update existing parser configuration.
    
    Updates parser settings including schedule, active status,
    and configuration parameters.
    
    Args:
        db: Database session
        parser_id: ID of parser to update
        parser_in: Updated parser configuration data
        current_user: Current superuser (required for access)
        
    Returns:
        ParserConfig: Updated parser configuration
        
    Raises:
        HTTPException: If parser not found
    """
    parser = db.query(ParserConfig).get(parser_id)
    if not parser:
        raise HTTPException(status_code=404, detail="Parser not found")
    
    # Update only provided fields
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
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Execute parser manually via Celery task.
    
    Queues the specified parser for immediate execution and returns
    task information for monitoring progress.
    
    Args:
        db: Database session
        parser_id: ID of parser to execute
        current_user: Current superuser (required for access)
        
    Returns:
        ParserRunResponse: Task execution information
        
    Raises:
        HTTPException: If parser not found or inactive
    """
    parser = db.query(ParserConfig).get(parser_id)
    if not parser:
        raise HTTPException(status_code=404, detail="Parser not found")
    
    if not parser.is_active:
        raise HTTPException(status_code=400, detail="Parser is not active")
    
    # Queue parser execution via Celery
    from app.tasks import run_parser_task
    task = run_parser_task.delay(parser_id)
    
    return {
        "status": "started",
        "parser_id": parser_id,
        "parser_name": parser.name,
        "started_at": datetime.now(),
        "task_id": task.id
    }


@router.get("/task/{task_id}/status")
def get_task_status(
    task_id: str,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get Celery task execution status.
    
    Monitors the progress of a parser execution task,
    returning current status and result information.
    
    Args:
        task_id: Celery task ID to monitor
        current_user: Current superuser (required for access)
        
    Returns:
        Dict: Task status information including completion state
    """
    from app.core.celery_app import celery_app
    
    task = celery_app.AsyncResult(task_id)
    
    # Get current task state
    status = task.status
    result = task.result if task.ready() else None
    
    # Determine completion flags
    ready = status in ['SUCCESS', 'FAILURE', 'REVOKED']
    successful = status == 'SUCCESS'
    failed = status == 'FAILURE'
    
    return {
        "task_id": task_id,
        "status": status,
        "result": result,
        "ready": ready,
        "successful": successful,
        "failed": failed
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
    """
    Get parser execution logs.
    
    Returns recent execution logs for the specified parser,
    including performance metrics and error information.
    
    Args:
        db: Database session
        parser_id: ID of parser to get logs for
        skip: Number of logs to skip for pagination
        limit: Maximum number of logs to return
        current_user: Current superuser (required for access)
        
    Returns:
        List[ParserLog]: Recent parser execution logs
    """
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
    """
    Delete parser configuration.
    
    Removes the parser configuration and triggers schedule update
    to remove it from Celery Beat scheduler.
    
    Args:
        db: Database session
        parser_id: ID of parser to delete
        current_user: Current superuser (required for access)
        
    Returns:
        Dict: Deletion confirmation
        
    Raises:
        HTTPException: If parser not found
    """
    parser = db.query(ParserConfig).get(parser_id)
    if not parser:
        raise HTTPException(status_code=404, detail="Parser not found")
    
    db.delete(parser)
    db.commit()
    
    # Trigger Celery schedule update
    from app.tasks import force_schedule_update
    force_schedule_update.delay()
    
    return {"status": "deleted"}
