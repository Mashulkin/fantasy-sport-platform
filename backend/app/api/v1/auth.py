"""
Authentication endpoints for user login and registration.

Provides OAuth2-compatible token authentication and user management
functionality for the fantasy sports platform.
"""

from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.core.config import settings
from app.models.user import User
from app.schemas.user import User as UserSchema, UserCreate, Token

router = APIRouter()


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login endpoint.
    
    Authenticates user with email or username and returns JWT access token
    for subsequent API requests.
    
    Args:
        db: Database session
        form_data: OAuth2 login form with username/email and password
        
    Returns:
        Token: JWT access token and token type
        
    Raises:
        HTTPException: If credentials are invalid or user is inactive
    """
    # Find user by email or username
    user = db.query(User).filter(
        (User.email == form_data.username) | (User.username == form_data.username)
    ).first()
    
    # Validate credentials
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=400, 
            detail="Incorrect email/username or password"
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Generate access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/register", response_model=UserSchema)
def register(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
) -> Any:
    """
    Create new user account.
    
    Registers a new user with email and username validation.
    New users are active by default but not superusers.
    
    Args:
        db: Database session
        user_in: User creation data
        
    Returns:
        User: Created user object
        
    Raises:
        HTTPException: If email or username already exists
    """
    # Check for existing user
    user = db.query(User).filter(
        (User.email == user_in.email) | (User.username == user_in.username)
    ).first()
    
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email or username already exists",
        )
    
    # Create new user
    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=security.get_password_hash(user_in.password),
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserSchema)
def read_users_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current authenticated user information.
    
    Returns the user profile for the currently authenticated user
    based on the provided JWT token.
    
    Args:
        current_user: Current authenticated user from JWT token
        
    Returns:
        User: Current user profile data
    """
    return current_user
