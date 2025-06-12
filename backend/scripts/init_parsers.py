import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.parser import ParserConfig

def init_parsers():
    db = SessionLocal()
    
    # FPL Players Parser
    fpl_players = db.query(ParserConfig).filter(
        ParserConfig.name == "FPL Players Parser"
    ).first()
    
    if not fpl_players:
        fpl_players = ParserConfig(
            name="FPL Players Parser",
            platform="FPL",
            parser_type="fpl_players",
            schedule="0 */4 * * *",  # Every 4 hours
            is_active=True,
            config={
                "description": "Updates FPL players, teams and prices"
            }
        )
        db.add(fpl_players)
        print("Created FPL Players Parser")
    else:
        # Update schedule if needed
        fpl_players.schedule = "0 */4 * * *"
        print("Updated FPL Players Parser schedule")
    
    # FPL Ownership Parser
    fpl_ownership = db.query(ParserConfig).filter(
        ParserConfig.name == "FPL Ownership Parser"
    ).first()
    
    if not fpl_ownership:
        fpl_ownership = ParserConfig(
            name="FPL Ownership Parser",
            platform="FPL",
            parser_type="fpl_ownership",
            schedule="0 */2 * * *",  # Every 2 hours
            is_active=True,
            config={
                "description": "Updates player ownership percentages"
            }
        )
        db.add(fpl_ownership)
        print("Created FPL Ownership Parser")
    else:
        # Update schedule if needed
        fpl_ownership.schedule = "0 */2 * * *"
        print("Updated FPL Ownership Parser schedule")
    
    db.commit()
    db.close()
    print("Parsers initialization completed")
    
    # Trigger Celery schedule update
    try:
        from app.tasks import update_parser_schedules
        result = update_parser_schedules()
        if result['success']:
            print(f"Celery schedules updated: {result['schedules_count']} active schedules")
    except Exception as e:
        print(f"Note: Could not update Celery schedules (Celery might not be running): {e}")

if __name__ == "__main__":
    init_parsers()
