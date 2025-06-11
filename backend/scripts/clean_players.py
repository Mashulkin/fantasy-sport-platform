import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.player import Player, PlayerPlatformProfile
from app.models.stats import PriceHistory
from app.models.team import Team

def clean_players():
    db = SessionLocal()
    
    print("Cleaning player data...")
    
    # Удаляем в правильном порядке из-за foreign keys
    db.query(PriceHistory).delete()
    db.query(PlayerPlatformProfile).delete()
    db.query(Player).delete()
    
    db.commit()
    print("Player data cleaned")
    
    # Показываем количество команд
    teams_count = db.query(Team).count()
    print(f"Teams in database: {teams_count}")
    
    db.close()

if __name__ == "__main__":
    clean_players()
