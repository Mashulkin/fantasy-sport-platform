import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tasks import update_parser_schedules

def init_schedules():
    print("Initializing Celery schedules from database...")
    
    # Call the task synchronously
    result = update_parser_schedules()
    
    if result['success']:
        print(f"Successfully initialized {result['schedules_count']} schedules")
        print("Active parsers:")
        for parser in result['parsers']:
            print(f"  - {parser}")
    else:
        print(f"Failed to initialize schedules: {result.get('error')}")

if __name__ == "__main__":
    init_schedules()