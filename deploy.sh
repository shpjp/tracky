#!/bin/bash

# Deployment script for Placement Tracker

echo "Starting deployment..."

# Activate virtual environment
source .venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
uv pip install -r requirements.txt

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
echo "Creating superuser if needed..."
python manage.py shell -c "
from django.contrib.auth.models import User
import os
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        'admin', 
        os.environ.get('ADMIN_EMAIL', 'admin@example.com'), 
        os.environ.get('ADMIN_PASSWORD', 'admin123')
    )
    print('Superuser created')
else:
    print('Superuser already exists')
"

echo "Deployment completed successfully!"
echo ""
echo "To start the server:"
echo "gunicorn placement_tracker_project.wsgi:application --bind 0.0.0.0:8000"