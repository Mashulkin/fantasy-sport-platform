import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

from celery import Task
from celery.schedules import crontab
from sqlalchemy.orm import Session

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.parser import ParserConfig, ParserLog
from app.services.parser_service import ParserService

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task with database session management"""
    _db = None

    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(base=DatabaseTask, bind=True, name="run_parser")
def run_parser_task(self, parser_config_id: int) -> Dict[str, Any]:
    """
    Celery task to run a parser
    
    Args:
        parser_config_id: ID of the parser configuration
        
    Returns:
        Dict with execution results
    """
    start_time = datetime.now()
    db = self.db
    
    try:
        # Get parser configuration
        parser_config = db.query(ParserConfig).get(parser_config_id)
        if not parser_config:
            logger.error(f"Parser config not found: {parser_config_id}")
            return {
                "success": False,
                "error": f"Parser config not found: {parser_config_id}"
            }
        
        if not parser_config.is_active:
            logger.info(f"Parser {parser_config.name} is not active, skipping")
            return {
                "success": False,
                "error": f"Parser {parser_config.name} is not active"
            }
        
        logger.info(f"Starting parser: {parser_config.name} (ID: {parser_config_id})")
        
        # Run parser using asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            success = loop.run_until_complete(
                ParserService.run_parser(parser_config_id, db)
            )
        finally:
            loop.close()
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "success": success,
            "parser_id": parser_config_id,
            "parser_name": parser_config.name,
            "execution_time": execution_time
        }
        
    except Exception as e:
        logger.error(f"Error running parser {parser_config_id}: {str(e)}")
        
        # Log error to database
        try:
            parser_log = ParserLog(
                parser_config_id=parser_config_id,
                started_at=start_time,
                finished_at=datetime.now(),
                status="failed",
                errors_count=1,
                log_data=f"Celery task error: {str(e)}"
            )
            db.add(parser_log)
            db.commit()
        except:
            pass
        
        return {
            "success": False,
            "error": str(e),
            "parser_id": parser_config_id
        }


@celery_app.task(name="update_parser_schedules")
def update_parser_schedules() -> Dict[str, Any]:
    """
    Update Celery Beat schedule from database parser configurations
    """
    db = SessionLocal()
    
    try:
        # Get all active parsers with schedules
        parsers = db.query(ParserConfig).filter(
            ParserConfig.is_active == True,
            ParserConfig.schedule.isnot(None)
        ).all()
        
        # Get current beat schedule
        current_schedule = dict(celery_app.conf.beat_schedule)
        
        # Keep system tasks
        new_schedule = {
            k: v for k, v in current_schedule.items() 
            if not k.startswith('parser_')
        }
        
        # Add parser schedules
        for parser in parsers:
            if parser.schedule:
                try:
                    # Parse cron expression
                    parts = parser.schedule.split()
                    if len(parts) >= 5:  # Allow for incomplete cron expressions
                        schedule_name = f"parser_{parser.id}_{parser.name.replace(' ', '_')}"
                        
                        # Fill missing parts with wildcards
                        while len(parts) < 5:
                            parts.append('*')
                        
                        new_schedule[schedule_name] = {
                            'task': 'run_parser',
                            'schedule': crontab(
                                minute=parts[0],
                                hour=parts[1],
                                day_of_month=parts[2],
                                month_of_year=parts[3],
                                day_of_week=parts[4]
                            ),
                            'args': (parser.id,),
                            'options': {
                                'expires': 3600  # Expire after 1 hour if not executed
                            }
                        }
                        logger.info(f"Added schedule for parser: {parser.name} - {parser.schedule}")
                except Exception as e:
                    logger.error(f"Invalid cron expression for parser {parser.name}: {parser.schedule} - {e}")
                    continue
        
        # Update Celery beat schedule
        celery_app.conf.beat_schedule = new_schedule
        
        # Force beat to reload schedule
        from celery.bin import beat
        beat_instance = celery_app.Beat()
        if hasattr(beat_instance, 'scheduler'):
            beat_instance.scheduler.sync()
        
        logger.info(f"Updated parser schedules. Active schedules: {len([k for k in new_schedule.keys() if k.startswith('parser_')])}")
        
        return {
            "success": True,
            "schedules_count": len([k for k in new_schedule.keys() if k.startswith('parser_')]),
            "parsers": [k for k in new_schedule.keys() if k.startswith('parser_')]
        }
        
    except Exception as e:
        logger.error(f"Error updating parser schedules: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(name="check_parser_health")
def check_parser_health() -> Dict[str, Any]:
    """
    Health check task that runs every hour to check parser status
    """
    db = SessionLocal()
    
    try:
        # Check for parsers that haven't run in a while
        parsers = db.query(ParserConfig).filter(
            ParserConfig.is_active == True
        ).all()
        
        alerts = []
        
        for parser in parsers:
            if parser.last_run and parser.schedule:
                # Simple check: if parser hasn't run in 24 hours, alert
                hours_since_last_run = (datetime.now() - parser.last_run).total_seconds() / 3600
                
                if hours_since_last_run > 24:
                    alerts.append({
                        "parser_id": parser.id,
                        "parser_name": parser.name,
                        "hours_since_last_run": round(hours_since_last_run, 1),
                        "last_status": parser.last_status
                    })
        
        return {
            "success": True,
            "alerts_count": len(alerts),
            "alerts": alerts
        }
        
    except Exception as e:
        logger.error(f"Error checking parser health: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


# Schedule periodic tasks
celery_app.conf.beat_schedule.update({
    'update-parser-schedules': {
        'task': 'update_parser_schedules',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'check-parser-health': {
        'task': 'check_parser_health',
        'schedule': crontab(minute=0),  # Every hour
    },
})