"""
Celery background tasks for parser execution and system monitoring.

This module defines all Celery tasks including parser execution,
health checks, and schedule management.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

from celery import Task
from sqlalchemy.orm import Session

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.parser import ParserConfig, ParserLog
from app.services.parser_service import ParserService

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """
    Base task class with automatic database session management.
    
    Provides a database session that is automatically closed
    after task completion.
    """
    _db = None

    @property
    def db(self) -> Session:
        """Get or create database session for this task."""
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        """Clean up database session after task completion."""
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(base=DatabaseTask, bind=True, name="run_parser")
def run_parser_task(self, parser_config_id: int) -> Dict[str, Any]:
    """
    Execute a parser by its configuration ID.
    
    This task is automatically scheduled based on cron expressions
    stored in the database. It handles parser execution, logging,
    and error reporting.
    
    Args:
        parser_config_id (int): ID of parser configuration to execute
        
    Returns:
        Dict[str, Any]: Task execution result with status and metadata
    """
    start_time = datetime.now()
    db = self.db
    
    logger.info(f"🚀 Starting parser task for ID: {parser_config_id}")
    
    try:
        # Fetch parser configuration
        parser_config = db.query(ParserConfig).get(parser_config_id)
        if not parser_config:
            logger.error(f"❌ Parser config not found: {parser_config_id}")
            return {
                "success": False, 
                "error": f"Parser config not found: {parser_config_id}"
            }
        
        # Check if parser is still active
        if not parser_config.is_active:
            logger.info(
                f"⏸️ Parser {parser_config.name} is not active, skipping execution"
            )
            return {
                "success": False, 
                "error": f"Parser {parser_config.name} is not active",
                "parser_id": parser_config_id,
                "parser_name": parser_config.name,
                "status": "inactive",
                "message": "Parser was disabled in admin panel"
            }
        
        logger.info(f"▶️ Starting parser: {parser_config.name} (ID: {parser_config_id})")
        
        # Execute parser using asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            success = loop.run_until_complete(
                ParserService.run_parser(parser_config_id, db)
            )
        finally:
            loop.close()
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Log completion status
        if success:
            logger.info(
                f"✅ Parser {parser_config.name} completed successfully "
                f"in {execution_time:.1f}s"
            )
        else:
            logger.error(
                f"❌ Parser {parser_config.name} failed after {execution_time:.1f}s"
            )
        
        return {
            "success": success,
            "parser_id": parser_config_id,
            "parser_name": parser_config.name,
            "execution_time": execution_time,
            "status": "completed" if success else "failed"
        }
        
    except Exception as e:
        logger.error(f"💥 Error running parser {parser_config_id}: {str(e)}")
        
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
        except Exception:
            # Ignore logging errors to prevent infinite recursion
            pass
        
        return {
            "success": False, 
            "error": str(e), 
            "parser_id": parser_config_id,
            "status": "error"
        }


@celery_app.task(name="check_parser_health")
def check_parser_health() -> Dict[str, Any]:
    """
    Monitor parser health and identify stale parsers.
    
    Runs every hour to check for parsers that haven't executed
    in over 24 hours despite having active schedules.
    
    Returns:
        Dict[str, Any]: Health check results with alert information
    """
    logger.info("🏥 Running parser health check...")
    db = SessionLocal()
    
    try:
        # Get all active parsers with schedules
        parsers = db.query(ParserConfig).filter(
            ParserConfig.is_active == True
        ).all()
        
        alerts = []
        
        # Check each parser for staleness
        for parser in parsers:
            if parser.last_run and parser.schedule:
                hours_since_last_run = (
                    datetime.now() - parser.last_run
                ).total_seconds() / 3600
                
                # Alert if parser hasn't run in over 24 hours
                if hours_since_last_run > 24:
                    alerts.append({
                        "parser_id": parser.id,
                        "parser_name": parser.name,
                        "hours_since_last_run": round(hours_since_last_run, 1),
                        "last_status": parser.last_status
                    })
        
        logger.info(f"🏥 Health check completed. Found {len(alerts)} alerts")
        return {
            "success": True, 
            "alerts_count": len(alerts), 
            "alerts": alerts
        }
        
    except Exception as e:
        logger.error(f"💥 Error checking parser health: {str(e)}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()


@celery_app.task(name="force_schedule_update")
def force_schedule_update() -> Dict[str, Any]:
    """
    Force scheduler to update parser schedules from database.
    
    Can be called from admin interface to immediately sync
    schedule changes without waiting for the periodic update.
    
    Returns:
        Dict[str, Any]: Update operation result
    """
    logger.info("🔄 Force updating parser schedules...")
    
    try:
        # Signal scheduler to update by touching a flag file
        import os
        with open('/tmp/force-schedule-update', 'w') as f:
            f.write(str(datetime.now().timestamp()))
        
        logger.info("✅ Schedule update signal sent")
        return {
            "success": True, 
            "message": "Schedule will be updated within 30 seconds",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"💥 Error forcing schedule update: {e}")
        return {"success": False, "error": str(e)}
