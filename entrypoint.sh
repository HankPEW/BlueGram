#!/bin/sh

echo "Waiting for PostgreSQL..."

until nc -z postgres_db 5432; do
  sleep 1
done

echo "Database started"

echo "Running migrations..."
alembic upgrade head

echo "Starting server..."
uvicorn src.main:app --host 0.0.0.0 --port 8000