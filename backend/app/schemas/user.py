"""
Pydantic schemas for user authentication and management.

Defines request/response models for user registration, login,
and profile management with JWT token handling.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    """Base schema for user information."""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False


class UserCreate(UserBase):
    """Schema for user registration."""
    email: EmailStr
    username: str
    password: str


class UserUpdate(UserBase):
    """Schema for user profile updates."""
    password: Optional[str] = None


class UserInDBBase(UserBase):
    """Base schema for database user representation."""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(UserInDBBase):
    """Schema for user response (public data only)."""
    pass


class UserInDB(UserInDBBase):
    """Schema for internal user representation with password hash."""
    hashed_password: str


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Schema for JWT token payload validation."""
    sub: Optional[int] = None
