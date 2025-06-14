# backend/scripts/check_cron_expressions.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from celery.schedules import crontab
from app.core.database import SessionLocal
from app.models.parser import ParserConfig

def test_cron_expression(cron_str, test_time=None):
    """Тестирует cron выражение"""
    if test_time is None:
        test_time = datetime.now()
    
    try:
        parts = cron_str.strip().split()
        if len(parts) < 5:
            while len(parts) < 5:
                parts.append('*')
        
        schedule = crontab(
            minute=parts[0],
            hour=parts[1],
            day_of_month=parts[2],
            month_of_year=parts[3],
            day_of_week=parts[4]
        )
        
        # Проверяем следующие 10 дней
        next_runs = []
        check_time = test_time
        for _ in range(20):  # Проверяем 20 периодов
            if schedule.is_due(check_time):
                next_runs.append(check_time.strftime('%Y-%m-%d %H:%M:%S %A'))
                if len(next_runs) >= 5:  # Показываем первые 5
                    break
            check_time += timedelta(minutes=1)
        
        return {
            'valid': True,
            'parsed_parts': parts,
            'next_runs': next_runs
        }
    except Exception as e:
        return {
            'valid': False,
            'error': str(e),
            'original': cron_str
        }

def check_all_parser_crons():
    """Проверяет все cron выражения парсеров"""
    print("=== ПРОВЕРКА CRON ВЫРАЖЕНИЙ ПАРСЕРОВ ===\n")
    
    db = SessionLocal()
    
    try:
        parsers = db.query(ParserConfig).filter(
            ParserConfig.is_active == True,
            ParserConfig.schedule.isnot(None)
        ).all()
        
        print(f"Найдено {len(parsers)} активных парсеров с расписанием:\n")
        
        for parser in parsers:
            print(f"Парсер: {parser.name} (ID: {parser.id})")
            print(f"Расписание: '{parser.schedule}'")
            
            result = test_cron_expression(parser.schedule)
            
            if result['valid']:
                print(f"✓ Валидное выражение")
                print(f"  Разобрано как: {' '.join(result['parsed_parts'])}")
                print(f"  Следующие запуски:")
                for run_time in result['next_runs']:
                    print(f"    - {run_time}")
            else:
                print(f"✗ ОШИБКА: {result['error']}")
            
            print("-" * 60)
        
        # Тестируем стандартные выражения
        print("\n=== ТЕСТ СТАНДАРТНЫХ ВЫРАЖЕНИЙ ===\n")
        
        test_expressions = [
            ("0 */4 * * *", "Каждые 4 часа"),
            ("0 */2 * * *", "Каждые 2 часа"),
            ("*/15 * * * *", "Каждые 15 минут"),
            ("0 0 * * *", "Каждый день в полночь"),
            ("0 9,21 * * *", "В 9:00 и 21:00"),
            ("*", "Каждую минуту (неполное)"),
            ("0 6", "Неполное выражение")
        ]
        
        for expr, description in test_expressions:
            print(f"Тест: '{expr}' ({description})")
            result = test_cron_expression(expr)
            
            if result['valid']:
                print(f"✓ Валидно: {' '.join(result['parsed_parts'])}")
                if result['next_runs']:
                    print(f"  Первый запуск: {result['next_runs'][0]}")
            else:
                print(f"✗ Ошибка: {result['error']}")
            print()
    
    finally:
        db.close()

def suggest_fixes():
    """Предлагает исправления для проблемных расписаний"""
    print("\n=== ПРЕДЛАГАЕМЫЕ ИСПРАВЛЕНИЯ ===\n")
    
    db = SessionLocal()
    
    try:
        parsers = db.query(ParserConfig).filter(
            ParserConfig.is_active == True,
            ParserConfig.schedule.isnot(None)
        ).all()
        
        for parser in parsers:
            result = test_cron_expression(parser.schedule)
            
            if not result['valid']:
                print(f"Парсер: {parser.name}")
                print(f"Проблемное расписание: '{parser.schedule}'")
                
                # Пытаемся предложить исправление
                parts = parser.schedule.strip().split()
                if len(parts) < 5:
                    fixed_parts = parts + ['*'] * (5 - len(parts))
                    fixed_schedule = ' '.join(fixed_parts)
                    
                    print(f"Предлагаемое исправление: '{fixed_schedule}'")
                    
                    # Тестируем исправление
                    fix_result = test_cron_expression(fixed_schedule)
                    if fix_result['valid']:
                        print(f"✓ Исправленное выражение валидно")
                        if fix_result['next_runs']:
                            print(f"  Первый запуск: {fix_result['next_runs'][0]}")
                    else:
                        print(f"✗ Исправление не помогло: {fix_result['error']}")
                
                print()
    
    finally:
        db.close()

if __name__ == "__main__":
    check_all_parser_crons()
    suggest_fixes()