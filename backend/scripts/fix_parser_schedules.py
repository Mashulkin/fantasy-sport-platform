import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.parser import ParserConfig

def fix_schedules():
    """Fix incomplete cron expressions in parser schedules"""
    db = SessionLocal()
    
    parsers = db.query(ParserConfig).filter(
        ParserConfig.schedule.isnot(None)
    ).all()
    
    for parser in parsers:
        old_schedule = parser.schedule
        parts = parser.schedule.split()
        
        # Fix incomplete cron expressions
        if len(parts) < 5:
            # Add missing parts
            while len(parts) < 5:
                parts.append('*')
            
            parser.schedule = ' '.join(parts)
            print(f"Fixed {parser.name}: '{old_schedule}' -> '{parser.schedule}'")
    
    db.commit()
    db.close()
    print("Schedule fix completed")
    
    # Now update Celery schedules
    from app.tasks import update_parser_schedules
    result = update_parser_schedules()
    print(f"Celery update result: {result}")

if __name__ == "__main__":
    fix_schedules()