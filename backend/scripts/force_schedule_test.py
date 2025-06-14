# backend/scripts/force_schedule_test.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from app.core.database import SessionLocal
from app.models.parser import ParserConfig
from app.core.celery_app import celery_app
from celery.schedules import crontab

def force_add_schedules():
    """Принудительно добавляем расписания в Celery Beat"""
    
    print("=== ПРИНУДИТЕЛЬНОЕ ДОБАВЛЕНИЕ РАСПИСАНИЙ ===\n")
    
    db = SessionLocal()
    
    try:
        # Получаем парсеры
        parsers = db.query(ParserConfig).filter(
            ParserConfig.is_active == True
        ).all()
        
        print(f"Найдено {len(parsers)} активных парсеров:")
        for parser in parsers:
            print(f"  - {parser.name} (ID: {parser.id}, Schedule: {parser.schedule})")
        
        # Создаем новое расписание
        beat_schedule = {
            # Системные задачи
            'update-parser-schedules': {
                'task': 'update_parser_schedules',
                'schedule': crontab(minute='*/5'),
            },
            'check-parser-health': {
                'task': 'check_parser_health', 
                'schedule': crontab(minute=0),
            },
            'test-task': {
                'task': 'test_task',
                'schedule': crontab(minute='*'),  # Каждую минуту для теста
            }
        }
        
        # Добавляем парсеры
        for parser in parsers:
            if parser.schedule:
                parts = parser.schedule.strip().split()
                
                # Дополняем до 5 частей
                while len(parts) < 5:
                    parts.append('*')
                
                schedule_name = f"parser_{parser.id}"
                
                try:
                    beat_schedule[schedule_name] = {
                        'task': 'run_parser',
                        'schedule': crontab(
                            minute=parts[0],
                            hour=parts[1], 
                            day_of_month=parts[2],
                            month_of_year=parts[3],
                            day_of_week=parts[4]
                        ),
                        'args': (parser.id,)
                    }
                    print(f"✓ Добавлено расписание для {parser.name}: {' '.join(parts)}")
                except Exception as e:
                    print(f"✗ ОШИБКА для {parser.name}: {e}")
        
        # Обновляем конфигурацию Celery
        celery_app.conf.beat_schedule = beat_schedule
        
        print(f"\n=== ИТОГО ===")
        print(f"Всего расписаний: {len(beat_schedule)}")
        print("Расписания парсеров:")
        for name in beat_schedule.keys():
            if name.startswith('parser_'):
                print(f"  - {name}")
        
        # Выводим текущую конфигурацию
        print(f"\n=== ТЕКУЩАЯ КОНФИГУРАЦИЯ CELERY ===")
        for name, config in celery_app.conf.beat_schedule.items():
            print(f"{name}:")
            print(f"  Task: {config['task']}")
            print(f"  Schedule: {config['schedule']}")
            if 'args' in config:
                print(f"  Args: {config['args']}")
            print()
    
    finally:
        db.close()


if __name__ == "__main__":
    force_add_schedules()