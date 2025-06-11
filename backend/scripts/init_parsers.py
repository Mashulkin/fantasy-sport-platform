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
    
    db.commit()
    db.close()
    print("Parsers initialization completed")

if __name__ == "__main__":
    init_parsers()
