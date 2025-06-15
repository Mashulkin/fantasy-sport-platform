"""
FastAPI dependency functions for authentication and database access.

This module provides reusable dependency functions that can be injected
into FastAPI route handlers. It includes database session management,
user authentication, and authorization checks based on JWT tokens.
"""

from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.user import User
from app.schemas.user import TokenPayload

# OAuth2 scheme for token authentication
# Points to the login endpoint where clients can obtain tokens
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


def get_db() -> Generator:
    """
    Database session dependency.
    
    Provides a SQLAlchemy database session that is automatically closed
    after the request is completed. This ensures proper resource cleanup
    and prevents connection leaks.
    
    Yields:
        Session: SQLAlchemy database session
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> User:
    """
    Extract and validate current user from JWT token.
    
    Decodes the JWT token, validates its structure and signature,
    then retrieves the corresponding user from the database.
    
    Args:
        db: Database session dependency
        token: JWT token from Authorization header
        
    Returns:
        User: The authenticated user object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        # Decode and validate JWT token
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    # Retrieve user from database
    user = db.query(User).filter(User.id == token_data.sub).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Ensure the current user is active.
    
    Adds an additional check on top of authentication to ensure
    the user account is still active and not disabled.
    
    Args:
        current_user: The authenticated user from get_current_user
        
    Returns:
        User: The active user object
        
    Raises:
        HTTPException: If user account is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user


def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Ensure the current user has superuser privileges.
    
    Provides authorization check for admin-only endpoints by verifying
    the user has superuser status. This is used to protect sensitive
    operations like user management and system configuration.
    
    Args:
        current_user: The authenticated user from get_current_user
        
    Returns:
        User: The superuser object
        
    Raises:
        HTTPException: If user lacks superuser privileges
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="The user doesn't have enough privileges"
        )
    return current_user
