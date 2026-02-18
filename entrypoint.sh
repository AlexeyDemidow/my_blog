#!/bin/bash
set -e

echo "Waiting for postgres..."

while ! nc -z db 5432; do
  sleep 0.5
done

echo "PostgreSQL started"

if [ "$RUN_MIGRATIONS" = "1" ]; then
  echo "Running migrations..."
  python manage.py migrate --noinput
  echo "Collecting static files..."
  python manage.py collectstatic --noinput
fi
if [ "$INIT_DB" = "1" ]; then
  python db_fill_script.py
fi

exec "$@"
