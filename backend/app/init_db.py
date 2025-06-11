import logging
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db(db: Session) -> None:
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create superuser if doesn't exist
    user = db.query(User).filter(
        User.email == settings.FIRST_SUPERUSER
    ).first()
    
    if not user:
        user = User(
            email=settings.FIRST_SUPERUSER,
            username=settings.FIRST_SUPERUSER.split('@')[0],  # Use email prefix as username
            hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            is_superuser=True,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Created superuser: {user.email}")
    else:
        logger.info(f"Superuser already exists: {user.email}")


if __name__ == "__main__":
    logger.info("Creating initial data")
    db = SessionLocal()
    init_db(db)
    logger.info("Initial data created")
