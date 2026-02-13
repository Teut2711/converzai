#!/bin/bash
set -e

echo "Starting ecommerce-api..."

# Function to wait for service
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    
    echo "Waiting for $service_name..."
    while ! nc -z "$host" "$port"; do
        sleep 0.1
    done
    echo "$service_name is up!"
}

# Wait for database
wait_for_service "mysql" "3306" "MySQL"

# Wait for Elasticsearch
wait_for_service "elasticsearch" "9200" "Elasticsearch"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Health check for the application
echo "Performing application health check..."
python -c "
import sys
try:
    from app.core.database import engine
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
    sys.exit(1)
"

echo "Application startup complete!"
exec "$@"
