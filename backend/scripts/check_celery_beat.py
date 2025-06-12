import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.parser import ParserConfig
import json

def check_beat_schedule():
    print("=== Checking Celery Beat Schedule ===\n")
    
    try:
        # 1. Check current beat schedule
        print("Current Beat Schedule:")
        print("-" * 50)
        
        schedule = celery_app.conf.beat_schedule
        if not schedule:
            print("No schedules configured!")
        else:
            for name, config in schedule.items():
                print(f"\nSchedule: {name}")
                print(f"  Task: {config['task']}")
                print(f"  Schedule: {config['schedule']}")
                if 'args' in config:
                    print(f"  Args: {config['args']}")
        
        # 2. Check parsers in database
        print("\n\nParsers in Database:")
        print("-" * 50)
        
        db = SessionLocal()
        parsers = db.query(ParserConfig).filter(
            ParserConfig.is_active == True,
            ParserConfig.schedule.isnot(None)
        ).all()
        
        for parser in parsers:
            print(f"\nParser: {parser.name}")
            print(f"  ID: {parser.id}")
            print(f"  Schedule: {parser.schedule}")
            print(f"  Last Run: {parser.last_run}")
            print(f"  Last Status: {parser.last_status}")
        
        db.close()
        
        # 3. Force update schedules
        print("\n\nForcing Schedule Update:")
        print("-" * 50)
        try:
            from app.tasks import update_parser_schedules
            result = update_parser_schedules()
            print(f"Update result: {json.dumps(result, indent=2)}")
        except Exception as e:
            print(f"Note: Could not update schedules (this is normal during initialization): {e}")
            
    except Exception as e:
        print(f"Error during check: {e}")
        print("This might be normal during initial setup")

if __name__ == "__main__":
    check_beat_schedule()