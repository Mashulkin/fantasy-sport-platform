import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tasks import run_parser_task, update_parser_schedules, check_parser_health
from app.core.database import SessionLocal
from app.models.parser import ParserConfig

def test_celery():
    print("Testing Celery tasks...")
    
    # Test 1: Update schedules
    print("\n1. Testing update_parser_schedules...")
    result = update_parser_schedules.delay()
    print(f"Task ID: {result.id}")
    print(f"Result: {result.get(timeout=10)}")
    
    # Test 2: Check health
    print("\n2. Testing check_parser_health...")
    result = check_parser_health.delay()
    print(f"Task ID: {result.id}")
    print(f"Result: {result.get(timeout=10)}")
    
    # Test 3: Run a parser (if exists)
    print("\n3. Testing run_parser_task...")
    db = SessionLocal()
    parser = db.query(ParserConfig).first()
    if parser:
        print(f"Running parser: {parser.name}")
        result = run_parser_task.delay(parser.id)
        print(f"Task ID: {result.id}")
        print("Waiting for result (this may take a while)...")
        try:
            task_result = result.get(timeout=60)
            print(f"Result: {task_result}")
        except Exception as e:
            print(f"Error or timeout: {e}")
    else:
        print("No parsers found in database")
    
    db.close()
    print("\nCelery tests completed!")

if __name__ == "__main__":
    test_celery()