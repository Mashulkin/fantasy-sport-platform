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
    """Upload CSV file with players data"""
    
    # Проверяем расширение файла
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed"
        )
    
    # Читаем содержимое файла
    content = await file.read()
    csv_content = content.decode('utf-8')
    
    # Импортируем данные
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
        "errors": result["errors"][:10] if result["errors"] else []  # Показываем первые 10 ошибок
    }
