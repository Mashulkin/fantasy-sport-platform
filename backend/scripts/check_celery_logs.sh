#!/bin/bash

echo "=== CELERY WORKER LOGS ==="
echo "=========================="
docker-compose logs --tail=50 celery_worker

echo -e "\n\n=== CELERY BEAT LOGS ==="
echo "========================"
docker-compose logs --tail=50 celery_beat

echo -e "\n\n=== CHECKING CELERY BEAT SCHEDULE ==="
echo "====================================="
docker-compose exec backend python scripts/check_celery_beat.py

echo -e "\n\n=== RECENT PARSER LOGS FROM DB ==="
echo "==================================="
docker-compose exec backend python -c "
from app.core.database import SessionLocal
from app.models.parser import ParserLog
from sqlalchemy import desc

db = SessionLocal()
logs = db.query(ParserLog).order_by(desc(ParserLog.started_at)).limit(5).all()

for log in logs:
    print(f'\\nParser Config ID: {log.parser_config_id}')
    print(f'Started: {log.started_at}')
    print(f'Finished: {log.finished_at}')
    print(f'Status: {log.status}')
    print(f'Records: {log.records_processed}')
    print(f'Errors: {log.errors_count}')
    print('-' * 50)

db.close()
"