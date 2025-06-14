"""
Parser configuration initialization script.

Sets up default FPL parsers with appropriate schedules.
Run this after database initialization to configure automatic data parsing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.parser import ParserConfig


def init_parsers():
    """Initialize default parser configurations."""
    db = SessionLocal()
    
    # FPL Players Parser - comprehensive player data update
    _create_or_update_parser(
        db,
        name="FPL Players Parser",
        platform="FPL",
        parser_type="fpl_players",
        schedule="0 */4 * * *",  # Every 4 hours
        description="Updates FPL players, teams and prices"
    )
    
    # FPL Ownership Parser - frequent ownership updates
    _create_or_update_parser(
        db,
        name="FPL Ownership Parser", 
        platform="FPL",
        parser_type="fpl_ownership",
        schedule="0 */2 * * *",  # Every 2 hours
        description="Updates player ownership percentages"
    )
    
    db.commit()
    db.close()
    print("Parsers initialization completed")
    
    # Trigger Celery schedule update
    _update_celery_schedules()


def _create_or_update_parser(
    db, 
    name: str, 
    platform: str, 
    parser_type: str, 
    schedule: str, 
    description: str
):
    """Create or update a parser configuration."""
    parser = db.query(ParserConfig).filter(
        ParserConfig.name == name
    ).first()
    
    if not parser:
        parser = ParserConfig(
            name=name,
            platform=platform,
            parser_type=parser_type,
            schedule=schedule,
            is_active=True,
            config={"description": description}
        )
        db.add(parser)
        print(f"Created {name}")
    else:
        # Update schedule if needed
        parser.schedule = schedule
        print(f"Updated {name} schedule")


def _update_celery_schedules():
    """Trigger Celery schedule update if available."""
    try:
        from app.tasks import force_schedule_update
        result = force_schedule_update()
        if result['success']:
            print("Celery schedules updated successfully")
    except Exception as e:
        print(f"Note: Could not update Celery schedules (Celery might not be running): {e}")


if __name__ == "__main__":
    init_parsers()
