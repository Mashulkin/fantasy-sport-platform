"""
File upload endpoints for bulk data import.

Provides endpoints for uploading CSV files containing player data
from various fantasy platforms for bulk import operations.
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
    Upload CSV file with player data for bulk import.
    
    Processes CSV files containing player information and imports
    them into the database with appropriate validation and error handling.
    
    Args:
        db: Database session
        file: Uploaded CSV file
        platform: Target platform for the data (FPL, FANTEAM, etc.)
        current_user: Current superuser (required for access)
        
    Returns:
        Dict: Import results including success count and errors
        
    Raises:
        HTTPException: If file format invalid or platform unsupported
    """
    # Validate file extension
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed"
        )
    
    # Read file content
    content = await file.read()
    csv_content = content.decode('utf-8')
    
    # Process import based on platform
    import_service = CSVImportService(db)
    
    if platform.upper() == "FPL":
        result = import_service.import_fpl_players(csv_content)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported platform: {platform}"
        )
    
    return {
        "filename": file.filename,
        "platform": platform,
        "imported": result["imported"],
        "errors": result["errors"][:10] if result["errors"] else []  # Show first 10 errors
    }
