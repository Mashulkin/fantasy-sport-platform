from fastapi import APIRouter
from app.api.v1 import auth, parsers, upload, players, teams

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(parsers.router, prefix="/parsers", tags=["parsers"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(players.router, prefix="/players", tags=["players"])
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])