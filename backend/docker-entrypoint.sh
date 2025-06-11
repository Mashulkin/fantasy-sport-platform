#!/bin/bash
set -e

echo "Waiting for postgres..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

# Initialize database
echo "Initializing database..."
python scripts/init_db.py

# Initialize parsers
echo "Initializing parsers..."
python scripts/init_parsers.py

# Start the application
exec "$@"
