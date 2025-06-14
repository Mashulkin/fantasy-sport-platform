"""
Team management endpoints.

Provides basic CRUD operations for sports teams across
different leagues and competitions.
"""

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models.team import Team
from app.schemas.team import Team as TeamSchema

router = APIRouter()


@router.get("/", response_model=List[TeamSchema])
def get_teams(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get list of all teams.
    
    Returns paginated list of teams with basic information
    including name, abbreviation, and league.
    
    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List[Team]: List of team objects
    """
    teams = db.query(Team).offset(skip).limit(limit).all()
    return teams


@router.get("/{team_id}", response_model=TeamSchema)
def get_team(
    team_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get single team by ID.
    
    Returns complete team information including all
    associated metadata.
    
    Args:
        team_id: Team database ID
        db: Database session
        
    Returns:
        Team: Team object with complete information
        
    Raises:
        HTTPException: If team not found
    """
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team
