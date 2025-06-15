"""
Security utilities for authentication and password management.

This module provides core security functionality including JWT token
generation, password hashing and verification. It uses industry-standard
libraries (passlib for password hashing, python-jose for JWT) to ensure
secure authentication mechanisms.
"""

from datetime import datetime, timedelta
from typing import Any, Union, Optional

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing context using bcrypt algorithm
# bcrypt is recommended for password hashing due to its adaptive nature
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token for authentication.
    
    Generates a signed JWT token containing the subject (typically user ID)
    and expiration time. The token is signed with the application secret key
    and can be used for API authentication.
    
    Args:
        subject: The subject to encode in the token (usually user ID)
        expires_delta: Optional custom expiration time, defaults to app setting
        
    Returns:
        str: Encoded JWT token string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Create payload with expiration and subject
    to_encode = {"exp": expire, "sub": str(subject)}
    
    # Sign and encode the JWT token
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hashed version.
    
    Uses bcrypt's built-in verification which handles salt extraction
    and timing-safe comparison automatically.
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The stored hashed password
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generate a secure hash of a plain text password.
    
    Uses bcrypt hashing with automatic salt generation. The resulting
    hash includes the salt and can be safely stored in the database.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        str: Securely hashed password with salt
    """
    return pwd_context.hash(password)
