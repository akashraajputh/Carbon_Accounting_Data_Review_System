#!/usr/bin/env bash
set -e
cd backend
python manage.py migrate --noinput
# Load initial tenant fixture (no-op if already loaded)
python manage.py loaddata initial_tenants.json || true
# Import sample CSVs into the database if there are no records yet
python manage.py shell -c "import os,sys; p=os.path.join(os.getcwd(),'load_sample_data.py');
exec(open(p).read())" || true
exec gunicorn project.wsgi --bind 0.0.0.0:${PORT:-8000}
