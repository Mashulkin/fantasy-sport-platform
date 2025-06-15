"""
File upload endpoints for bulk data import.

This module provides REST API endpoints for uploading CSV files containing
player data from various fantasy platforms. It handles file validation,
platform-specific processing, and bulk data import operations with proper
error handling and progress reporting.

Supported platforms:
- FPL (Fantasy Premier League)
- Additional platforms can be added by extending the import service
"""

from typing import Any

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.services.csv_import import CSVImportService

router = APIRouter()


@router.post("/csv/players")
async def upload_players_csv(
    *,
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(...),
    platform: str = Form(...),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Upload and process CSV file with player data for bulk import.
    
    This endpoint accepts CSV files containing player information and imports
    them into the database after validation and processing. The import process
    is platform-specific to handle different data formats and field mappings.
    
    Args:
        db: Database session for data operations
        file: Uploaded CSV file containing player data
        platform: Target fantasy platform identifier (e.g., 'FPL', 'FANTEAM')
        current_user: Authenticated superuser (required for bulk operations)
        
    Returns:
        Dict containing:
            - filename: Original uploaded filename
            - platform: Processed platform name
            - imported: Number of successfully imported records
            - errors: List of first 10 import errors (if any)
        
    Raises:
        HTTPException: 
            - 400: If file is not CSV format or platform unsupported
            - 403: If user lacks superuser privileges
    """
    # Validate file format - only CSV files are accepted
    if not file.filename or not file.filename.lower().endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed"
        )
    
    try:
        # Read and decode file content
        content = await file.read()
        csv_content = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File must be UTF-8 encoded"
        )
    
    # Initialize import service for database operations
    import_service = CSVImportService(db)
    
    # Process import based on platform type
    platform_upper = platform.upper()
    
    if platform_upper == "FPL":
        # Process Fantasy Premier League player data
        result = import_service.import_fpl_players(csv_content)
    else:
        # Platform not yet implemented
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported platform: {platform}. "
                   f"Currently supported: FPL"
        )
    
    # Return import summary with limited error details for response size
    return {
        "filename": file.filename,
        "platform": platform_upper,
        "imported": result["imported"],
        "total_errors": len(result["errors"]) if result["errors"] else 0,
        "errors": result["errors"][:10] if result["errors"] else [],
        "message": f"Successfully imported {result['imported']} records"
    }
