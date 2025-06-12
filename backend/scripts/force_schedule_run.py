import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from app.core.database import SessionLocal
from app.models.parser import ParserConfig
from app.tasks import run_parser_task

def force_run_scheduled_parsers():
    """Force run all scheduled parsers immediately"""
    db = SessionLocal()
    
    parsers = db.query(ParserConfig).filter(
        ParserConfig.is_active == True,
        ParserConfig.schedule.isnot(None)
    ).all()
    
    print(f"Found {len(parsers)} active parsers with schedules")
    
    for parser in parsers:
        print(f"\nParser: {parser.name}")
        print(f"  Schedule: {parser.schedule}")
        print(f"  Last run: {parser.last_run}")
        
        # Check if parser should run based on schedule
        if parser.last_run:
            hours_since = (datetime.now() - parser.last_run).total_seconds() / 3600
            print(f"  Hours since last run: {hours_since:.1f}")
        
        # Force run
        print("  Forcing run...")
        task = run_parser_task.delay(parser.id)
        print(f"  Task ID: {task.id}")
    
    db.close()
    print("\nAll parsers queued for execution")

if __name__ == "__main__":
    force_run_scheduled_parsers()