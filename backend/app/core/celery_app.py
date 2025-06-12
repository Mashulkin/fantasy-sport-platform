from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "fantasy_sports",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks"]  # Include tasks module
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",  # Измените на ваш часовой пояс
    enable_utc=False,  # Использовать локальное время
    # Task execution settings
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={
        'visibility_timeout': 3600,
    },
)

# Initial beat schedule - will be updated from database
celery_app.conf.beat_schedule = {
    'update-parser-schedules': {
        'task': 'update_parser_schedules',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'check-parser-health': {
        'task': 'check_parser_health',
        'schedule': crontab(minute=0),  # Every hour
    },
}