import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

def fix_enum_types():
    """Drop and recreate enum types to fix conflicts"""
    
    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()
        
        try:
            # Check if enum exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_type WHERE typname = 'tournament_type_enum'
                );
            """))
            enum_exists = result.scalar()
            
            if enum_exists:
                print("Enum 'tournament_type_enum' exists, checking usage...")
                
                # Check if enum is used in any column
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM information_schema.columns 
                    WHERE udt_name = 'tournament_type_enum';
                """))
                usage_count = result.scalar()
                
                if usage_count == 0:
                    # Safe to drop
                    print("Enum not in use, dropping...")
                    conn.execute(text("DROP TYPE IF EXISTS tournament_type_enum CASCADE;"))
                    print("Enum dropped successfully")
                else:
                    print(f"Enum is used in {usage_count} columns, skipping drop")
            
            trans.commit()
            print("Enum fix completed")
            
        except Exception as e:
            trans.rollback()
            print(f"Error fixing enum: {e}")
            raise

if __name__ == "__main__":
    fix_enum_types()