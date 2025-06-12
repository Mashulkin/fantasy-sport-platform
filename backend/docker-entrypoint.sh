#!/bin/bash
set -e

echo "Waiting for postgres..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

echo "Waiting for redis..."
while ! nc -z redis 6379; do
  sleep 0.1
done
echo "Redis started"

# Fix enum types if needed
echo "Checking database enum types..."
python scripts/fix_enum_types.py || true

# Initialize database
echo "Initializing database..."
python scripts/init_db.py || echo "Database initialization completed with warnings"

# Initialize parsers
echo "Initializing parsers..."
python scripts/init_parsers.py || echo "Parser initialization completed with warnings"

# Start the application
exec "$@"
