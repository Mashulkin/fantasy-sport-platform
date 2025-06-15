"""
Pydantic schema models for API serialization and validation.

This module provides a centralized import point for all Pydantic schemas
used throughout the application for request/response validation and
serialization in FastAPI endpoints.

The schemas define the structure and validation rules for data exchanged
between the API and clients, ensuring type safety and data integrity.
"""

# Import all schema modules to make them available at package level
from app.schemas.user import *
from app.schemas.parser import *
