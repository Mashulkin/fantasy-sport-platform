"""
Custom Celery Beat Scheduler that loads schedules from database
"""
import logging
from celery.beat import ScheduleEntry, Scheduler
from celery.schedules import crontab
from app.core.database import SessionLocal
from app.models.parser import ParserConfig

logger = logging.getLogger(__name__)


class DatabaseScheduler(Scheduler):
    """Scheduler that loads schedules from database"""
    
    def setup_schedule(self):
        """Load schedule from database"""
        self.merge_inplace(self.app.conf.beat_schedule)
        self.install_default_entries(self.app.conf.beat_schedule)
        
        # Load parser schedules from database
        self.update_from_database()
        
        # Update every 60 seconds
        self.max_interval = 60
    
    def update_from_database(self):
        """Update schedule from database"""
        try:
            db = SessionLocal()
            
            # Get all active parsers with schedules
            parsers = db.query(ParserConfig).filter(
                ParserConfig.is_active == True,
                ParserConfig.schedule.isnot(None)
            ).all()
            
            logger.info(f"Loading {len(parsers)} parser schedules from database")
            
            for parser in parsers:
                if parser.schedule:
                    try:
                        # Parse cron expression
                        parts = parser.schedule.split()
                        if len(parts) == 5:
                            schedule_name = f"parser_{parser.id}_{parser.name.replace(' ', '_')}"
                            
                            # Create schedule entry
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
                            
                            self.merge_inplace({schedule_name: entry})
                            logger.info(f"Added schedule for parser: {parser.name} - {parser.schedule}")
                            
                    except Exception as e:
                        logger.error(f"Error parsing schedule for {parser.name}: {e}")
            
            db.close()
            
        except Exception as e:
            logger.error(f"Error updating schedules from database: {e}")
    
    @property
    def schedule(self):
        # Update from database periodically
        self.update_from_database()
        return self.data