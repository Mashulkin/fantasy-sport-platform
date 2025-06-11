from typing import List, Any, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api import deps
from app.models.player import Player, PlayerPlatformProfile, Platform
from app.models.team import Team
from app.schemas.player import Player as PlayerSchema, PlayerWithProfiles, PlayerPlatformProfile as ProfileSchema

router = APIRouter()


@router.get("/", response_model=List[PlayerWithProfiles])
def get_players(
    skip: int = 0,
    limit: int = 100,
    platform: Optional[str] = None,
    team_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(deps.get_db),
) -> Any:
    """Get list of players with filters"""
    query = db.query(Player).join(PlayerPlatformProfile)
    
    # Search by name
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Player.first_name.ilike(search_term)) |
            (Player.last_name.ilike(search_term)) |
            (Player.web_name.ilike(search_term))
        )
    
    # Filter by platform
    if platform:
        query = query.filter(PlayerPlatformProfile.platform == platform)
    
    # Filter by team
    if team_id:
        query = query.filter(PlayerPlatformProfile.team_id == team_id)
    
    # Добавляем distinct чтобы не было дубликатов
    players = query.distinct().offset(skip).limit(limit).all()
    return players


@router.get("/count")
def get_players_count(
    platform: Optional[str] = None,
    db: Session = Depends(deps.get_db),
) -> Any:
    """Get total count of players"""
    query = db.query(func.count(Player.id))
    
    if platform:
        query = query.join(PlayerPlatformProfile).filter(
            PlayerPlatformProfile.platform == platform
        )
    
    count = query.scalar()
    return {"total": count, "platform": platform}


@router.get("/{player_id}", response_model=PlayerWithProfiles)
def get_player(
    player_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """Get player by ID with all platform profiles"""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    return player


@router.get("/platform/{platform}/{platform_player_id}")
def get_player_by_platform_id(
    platform: str,
    platform_player_id: str,
    db: Session = Depends(deps.get_db),
) -> Any:
    """Get player by platform-specific ID"""
    profile = db.query(PlayerPlatformProfile).filter(
        PlayerPlatformProfile.platform == platform,
        PlayerPlatformProfile.platform_player_id == platform_player_id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Player not found on this platform")
    
    return profile.player
