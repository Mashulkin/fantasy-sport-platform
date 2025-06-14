"""
Celery worker entry point
Run with: celery -A app.worker worker --loglevel=info
"""
import logging
from app.core.celery_app import celery_app

# Configure logging
logging.basicConfig(level=logging.INFO)

# Import only production tasks (без test_task)
from app.tasks import (
    run_parser_task,
    check_parser_health
)

# Import all models to ensure they are registered
from app.models import *

# This allows running: celery -A app.worker worker --loglevel=info
worker = celery_app