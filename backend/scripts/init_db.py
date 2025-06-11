import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base
from app.core.config import settings
from app.core.security import get_password_hash
from sqlalchemy.orm import Session

# Import all models to register them
from app.models import *

def init_db():
    print("Creating database tables...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
    
    # Create superuser
    from app.models.user import User
    db = Session(bind=engine)
    
    try:
        user = db.query(User).filter(User.email == settings.FIRST_SUPERUSER).first()
        if not user:
            user = User(
                email=settings.FIRST_SUPERUSER,
                username=settings.FIRST_SUPERUSER.split('@')[0],
                hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                is_superuser=True,
                is_active=True,
            )
            db.add(user)
            db.commit()
            print(f"Superuser {settings.FIRST_SUPERUSER} created!")
        else:
            print(f"Superuser {settings.FIRST_SUPERUSER} already exists!")
    except Exception as e:
        print(f"Error creating superuser: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
