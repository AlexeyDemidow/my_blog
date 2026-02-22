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

if [ "$CREATE_SUPERUSER" = "1" ]; then
  echo "Checking for superuser..."

  python manage.py shell << END
from django.contrib.auth import get_user_model
import os

User = get_user_model()

username = os.environ.get("ADMIN_USERNAME")
email = os.environ.get("ADMIN_EMAIL")
password = os.environ.get("ADMIN_PASSWORD")

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        email=email,
        password=password,
        username=username
    )
    print("Superuser created.")
else:
    print("Superuser already exists.")
END
fi


exec "$@"
