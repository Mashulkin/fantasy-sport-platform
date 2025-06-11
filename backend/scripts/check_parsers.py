import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.parser import ParserConfig

def check_parsers():
    db = SessionLocal()
    
    parsers = db.query(ParserConfig).all()
    
    print(f"Found {len(parsers)} parsers in database:")
    for parser in parsers:
        print(f"- {parser.name} (ID: {parser.id}, Type: {parser.parser_type}, Active: {parser.is_active})")
    
    db.close()

if __name__ == "__main__":
    check_parsers()
