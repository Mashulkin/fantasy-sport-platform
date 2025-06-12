import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from app.core.database import SessionLocal
from app.models.parser import ParserConfig
from app.core.celery_app import celery_app
from celery.schedules import crontab

def setup_schedules():
    """Setup Celery Beat schedules manually"""
    
    db = SessionLocal()
    
    # Get parsers
    parsers = db.query(ParserConfig).filter(
        ParserConfig.is_active == True
    ).all()
    
    print("Setting up schedules for parsers:")
    
    # Build schedule
    beat_schedule = {
        # System tasks
        'update-parser-schedules': {
            'task': 'update_parser_schedules',
            'schedule': crontab(minute='*/5'),
        },
        'check-parser-health': {
            'task': 'check_parser_health', 
            'schedule': crontab(minute=0),
        }
    }
    
    for parser in parsers:
        if parser.schedule:
            parts = parser.schedule.strip().split()
            
            # Ensure we have 5 parts
            while len(parts) < 5:
                parts.append('*')
            
            schedule_name = f"parser_{parser.id}"
            
            try:
                beat_schedule[schedule_name] = {
                    'task': 'run_parser',
                    'schedule': crontab(
                        minute=parts[0],
                        hour=parts[1], 
                        day_of_month=parts[2],
                        month_of_year=parts[3],
                        day_of_week=parts[4]
                    ),
                    'args': (parser.id,)
                }
                print(f"  - {parser.name}: {' '.join(parts)}")
            except Exception as e:
                print(f"  - ERROR {parser.name}: {e}")
    
    # Save schedule
    celery_app.conf.beat_schedule = beat_schedule
    
    print(f"\nTotal schedules: {len(beat_schedule)}")
    print("Parser schedules: ", [k for k in beat_schedule.keys() if k.startswith('parser_')])
    
    db.close()

if __name__ == "__main__":
    setup_schedules()