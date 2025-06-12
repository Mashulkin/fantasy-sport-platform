import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User

def create_superuser():
    db = SessionLocal()
    
    email = settings.FIRST_SUPERUSER
    password = settings.FIRST_SUPERUSER_PASSWORD
    
    # Check if user exists
    user = db.query(User).filter(User.email == email).first()
    
    if user:
        # Update existing user
        user.is_superuser = True
        user.is_active = True
        user.hashed_password = get_password_hash(password)
        print(f"Updated existing user: {email}")
        print(f"  Superuser: {user.is_superuser}")
        print(f"  Active: {user.is_active}")
    else:
        # Create new user
        user = User(
            email=email,
            username=email.split('@')[0],
            hashed_password=get_password_hash(password),
            is_superuser=True,
            is_active=True,
        )
        db.add(user)
        print(f"Created new superuser: {email}")
    
    db.commit()
    print(f"\nYou can now login with:")
    print(f"  Email: {email}")
    print(f"  Password: {password}")
    
    # Show all users
    print("\nAll users in database:")
    all_users = db.query(User).all()
    for u in all_users:
        print(f"  - {u.email} (superuser: {u.is_superuser}, active: {u.is_active})")
    
    db.close()

if __name__ == "__main__":
    create_superuser()