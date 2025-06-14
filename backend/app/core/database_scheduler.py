"""
Custom Celery Beat scheduler that loads schedules from database.

This scheduler automatically synchronizes parser schedules from the database
with Celery Beat, allowing dynamic schedule management through the admin interface.
"""

import logging
import time
from datetime import datetime
from celery.beat import ScheduleEntry, Scheduler
from celery.schedules import crontab
from app.core.database import SessionLocal
from app.models.parser import ParserConfig

logger = logging.getLogger(__name__)


class DatabaseScheduler(Scheduler):
    """
    Custom scheduler that loads parser schedules from PostgreSQL database.
    
    Automatically updates every 90 seconds to sync with database changes.
    Validates and fixes malformed cron expressions during load.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize scheduler with tracking variables."""
        self.last_db_update = 0
        self.last_db_check = 0
        super().__init__(*args, **kwargs)
        
    def setup_schedule(self):
        """Initialize scheduler with base schedules and database parsers."""
        logger.info("🚀 Setting up DatabaseScheduler...")
        
        # Load base system schedules from Celery config
        self.merge_inplace(self.app.conf.beat_schedule)
        self.install_default_entries(self.app.conf.beat_schedule)
        
        # Load parser schedules from database
        self.update_from_database()
        
        # Set short interval for frequent database checks
        self.max_interval = 30  # Check every 30 seconds
        
    def validate_and_fix_cron(self, schedule_str):
        """
        Validate and fix malformed cron expressions.
        
        Args:
            schedule_str (str): Cron expression to validate
            
        Returns:
            tuple: (fixed_schedule, error_message)
                   Returns (None, error) if unfixable
        """
        if not schedule_str:
            return None, "Empty schedule"
        
        try:
            # Clean and split cron expression
            parts = schedule_str.strip().split()
            parts = [part for part in parts if part]  # Remove empty parts
            
            # Ensure we have exactly 5 parts (min, hour, day, month, dow)
            if len(parts) < 5:
                while len(parts) < 5:
                    parts.append('*')
            elif len(parts) > 5:
                parts = parts[:5]
            
            # Clean up malformed wildcards
            clean_parts = []
            for part in parts:
                clean_part = part.replace('**', '*').replace('***', '*')
                clean_parts.append(clean_part)
            
            # Test cron expression by creating crontab object
            test_cron = crontab(
                minute=clean_parts[0],
                hour=clean_parts[1],
                day_of_month=clean_parts[2],
                month_of_year=clean_parts[3],
                day_of_week=clean_parts[4]
            )
            
            fixed_schedule = ' '.join(clean_parts)
            return fixed_schedule, None
            
        except Exception as e:
            return None, f"Invalid cron expression: {e}"
    
    def update_from_database(self):
        """Load and update parser schedules from database."""
        try:
            db = SessionLocal()
            
            # Get all active parsers with schedules
            parsers = db.query(ParserConfig).filter(
                ParserConfig.is_active == True,
                ParserConfig.schedule.isnot(None)
            ).all()
            
            logger.info(f"📋 Found {len(parsers)} active parsers in database")
            
            # Track current parser IDs for cleanup
            current_parser_ids = set(parser.id for parser in parsers)
            
            # Remove schedules for inactive/deleted parsers
            removed_count = self._remove_inactive_schedules(current_parser_ids)
            
            # Add/update schedules for active parsers
            added_count, updated_count, error_count = self._update_parser_schedules(parsers)
            
            db.close()
            
            # Log summary
            total_schedules = len(self.schedule)
            parser_schedules = len([k for k in self.schedule.keys() if k.startswith('parser_')])
            
            if error_count > 0:
                logger.warning(
                    f"⚠️ Database update complete: {added_count} added, "
                    f"{updated_count} updated, {removed_count} removed, "
                    f"{error_count} errors. Total: {parser_schedules} parsers, "
                    f"{total_schedules} schedules"
                )
            else:
                logger.info(
                    f"✅ Database update complete: {added_count} added, "
                    f"{updated_count} updated, {removed_count} removed. "
                    f"Total: {parser_schedules} parsers, {total_schedules} schedules"
                )
            
        except Exception as e:
            logger.error(f"💥 Error updating from database: {e}")
    
    def _remove_inactive_schedules(self, current_parser_ids):
        """Remove schedules for parsers that are no longer active."""
        old_parser_schedules = [
            name for name in self.schedule.keys() 
            if name.startswith('parser_')
        ]
        removed_count = 0
        
        for schedule_name in old_parser_schedules:
            try:
                # Extract parser ID from schedule name (parser_1 -> 1)
                parser_id = int(schedule_name.split('_')[1])
                if parser_id not in current_parser_ids:
                    del self.schedule[schedule_name]
                    removed_count += 1
                    logger.info(f"🗑️ Removed schedule for inactive parser: {schedule_name}")
            except (IndexError, ValueError):
                # Remove malformed schedule names
                del self.schedule[schedule_name]
                removed_count += 1
                logger.warning(f"🗑️ Removed malformed schedule: {schedule_name}")
        
        return removed_count
    
    def _update_parser_schedules(self, parsers):
        """Add or update schedules for active parsers."""
        added_count = 0
        updated_count = 0
        error_count = 0
        
        for parser in parsers:
            if not parser.schedule:
                continue
                
            # Validate and fix cron expression
            fixed_schedule, error = self.validate_and_fix_cron(parser.schedule)
            
            if error:
                logger.error(
                    f"❌ Parser {parser.name} has invalid schedule "
                    f"'{parser.schedule}': {error}"
                )
                error_count += 1
                continue
            
            try:
                parts = fixed_schedule.split()
                schedule_name = f"parser_{parser.id}"
                
                # Check if schedule already exists
                is_update = schedule_name in self.schedule
                
                # Create new schedule entry
                entry = ScheduleEntry(
                    name=schedule_name,
                    task='run_parser',
                    schedule=crontab(
                        minute=parts[0],
                        hour=parts[1],
                        day_of_month=parts[2],
                        month_of_year=parts[3],
                        day_of_week=parts[4]
                    ),
                    args=(parser.id,),
                    kwargs={},
                    options={'expires': 3600},
                    app=self.app
                )
                
                self.schedule[schedule_name] = entry
                
                if is_update:
                    updated_count += 1
                    logger.info(
                        f"🔄 Updated schedule: {parser.name} ({schedule_name}) - {fixed_schedule}"
                    )
                else:
                    added_count += 1
                    logger.info(
                        f"➕ Added schedule: {parser.name} ({schedule_name}) - {fixed_schedule}"
                    )
                
            except Exception as e:
                logger.error(f"❌ Error creating schedule for {parser.name}: {e}")
                error_count += 1
                
        return added_count, updated_count, error_count
    
    def tick(self):
        """
        Override tick to periodically update from database.
        
        Returns:
            float: Time until next tick
        """
        current_time = time.time()
        
        # Update from database every 90 seconds
        if current_time - self.last_db_update > 90:
            logger.info("🔄 Periodic database update...")
            self.update_from_database()
            self.last_db_update = current_time
        
        # Call parent tick method
        return super().tick()
    
    @property
    def schedule(self):
        """Return current schedule dictionary."""
        return self.data
