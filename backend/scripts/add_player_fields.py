import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine
from sqlalchemy import text

def add_fields():
    with engine.connect() as conn:
        try:
            # Добавляем новые поля
            conn.execute(text("""
                ALTER TABLE player_platform_profiles 
                ADD COLUMN IF NOT EXISTS status VARCHAR(20),
                ADD COLUMN IF NOT EXISTS form FLOAT,
                ADD COLUMN IF NOT EXISTS total_points INTEGER,
                ADD COLUMN IF NOT EXISTS event_points INTEGER;
            """))
            conn.commit()
            print("Fields added successfully")
        except Exception as e:
            print(f"Error adding fields: {e}")

if __name__ == "__main__":
    add_fields()
