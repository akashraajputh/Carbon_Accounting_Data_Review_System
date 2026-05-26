#!/usr/bin/env bash
set -e
cd backend
python manage.py migrate --noinput
exec gunicorn project.wsgi --bind 0.0.0.0:${PORT:-8000}
