"""
Celery application configuration for background tasks.

This module configures Celery with Redis broker, database scheduler,
and task settings for the fantasy sports platform.
"""

import logging
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Configure logging for Celery operations
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create main Celery application instance
celery_app = Celery(
    "fantasy_sports",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks"]  # Auto-discover tasks module
)

# Configure Celery settings
celery_app.conf.update(
    # Serialization settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # Timezone configuration
    timezone="Europe/Moscow",
    enable_utc=False,
    
    # Task execution settings
    task_track_started=True,
    task_time_limit=30 * 60,        # 30 minutes hard limit
    task_soft_time_limit=25 * 60,   # 25 minutes soft limit
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    
    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={'visibility_timeout': 3600},
    
    # Database scheduler configuration
    beat_scheduler='app.core.database_scheduler:DatabaseScheduler',
    beat_schedule_filename='/tmp/celerybeat-schedule',
    beat_max_loop_interval=60,  # Check database every 60 seconds
    
    # Logging format
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s]'
                           '[%(task_name)s(%(task_id)s)] %(message)s',
)

# Base system schedules (parser schedules loaded from database)
celery_app.conf.beat_schedule = {
    'check-parser-health': {
        'task': 'check_parser_health',
        'schedule': crontab(minute=0),  # Every hour
    },
}

logger.info(
    f"🚀 Celery configured with DatabaseScheduler and "
    f"{len(celery_app.conf.beat_schedule)} base schedules"
)
logger.info("📋 Parser schedules will be loaded automatically from database")
