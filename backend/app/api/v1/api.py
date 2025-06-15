"""
Main API router configuration for version 1 endpoints.

This module assembles all API route handlers into a single router that
can be mounted by the main FastAPI application. It organizes endpoints
by feature area and applies consistent URL prefixes and tags for
API documentation.
"""

from fastapi import APIRouter

from app.api.v1 import auth, parsers, upload, players, teams

# Create main API router for version 1
api_router = APIRouter()

# Authentication endpoints - user login, registration, token management
api_router.include_router(
    auth.router, 
    prefix="/auth", 
    tags=["auth"]
)

# Parser management endpoints - CRUD operations and execution control
api_router.include_router(
    parsers.router, 
    prefix="/parsers", 
    tags=["parsers"]
)

# File upload endpoints - bulk data import via CSV files
api_router.include_router(
    upload.router, 
    prefix="/upload", 
    tags=["upload"]
)

# Player data endpoints - player information and statistics
api_router.include_router(
    players.router, 
    prefix="/players", 
    tags=["players"]
)

# Team data endpoints - team management and information
api_router.include_router(
    teams.router, 
    prefix="/teams", 
    tags=["teams"]
)
