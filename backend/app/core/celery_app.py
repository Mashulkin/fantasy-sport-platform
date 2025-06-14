from celery import Celery
from celery.schedules import crontab
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Celery instance
celery_app = Celery(
    "fantasy_sports",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=False,
    
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
    
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    
    result_expires=3600,
    result_backend_transport_options={'visibility_timeout': 3600},
    
    # Используем наш кастомный планировщик
    beat_scheduler='app.core.database_scheduler:DatabaseScheduler',
    beat_schedule_filename='/tmp/celerybeat-schedule',
    beat_max_loop_interval=60,
    
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s',
)

# Только необходимые системные задачи (БЕЗ тестовой задачи)
celery_app.conf.beat_schedule = {
    'check-parser-health': {
        'task': 'check_parser_health',
        'schedule': crontab(minute=0),  # Каждый час
    },
    # Убрали test-task!
}

logger.info(f"🚀 Celery configured with DatabaseScheduler and {len(celery_app.conf.beat_schedule)} base schedules")
logger.info("📋 Parser schedules will be loaded automatically from database")
