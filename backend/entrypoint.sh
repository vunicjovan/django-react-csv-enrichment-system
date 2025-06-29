#!/bin/bash

# Wait for database to be properly started and ready to accept connection requests
echo "Waiting for database..."
while ! python -c "import socket; socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('$DATABASE_HOST', 5432))" 2>/dev/null; do
  sleep 1
done

echo "Making migrations..."
python manage.py makemigrations transformer

echo "Applying migrations..."
python manage.py migrate

echo "Starting server..."
python manage.py runserver 0:8000
