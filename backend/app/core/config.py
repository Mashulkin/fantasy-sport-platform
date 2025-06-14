"""
Application configuration settings.

This module defines the main configuration class using Pydantic settings
for environment variable management and validation.
"""

from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator


class Settings(BaseSettings):
    """Main application settings loaded from environment variables."""
    
    # Project metadata
    PROJECT_NAME: str = "Fantasy Sports Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database connection
    DATABASE_URL: str
    
    # Redis connection for Celery
    REDIS_URL: str = "redis://localhost:6379"
    
    # CORS origins for frontend access
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(
        cls, 
        v: Union[str, List[str]]
    ) -> Union[List[str], str]:
        """Parse CORS origins from string or list format."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Initial superuser for admin access
    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
