#!/bin/bash
set -e

echo "Waiting for MySQL to be ready..."

# Extract connection details from DATABASE_URL or use defaults
DB_HOST="${DATABASE_HOST:-mysql}"
DB_USER="${MYSQL_USER:-pylogic}"
DB_PASS="${MYSQL_PASSWORD:-pylogic}"

# Wait for MySQL to be available (skip SSL for health check)
max_attempts=30
attempt=0
while ! mysql -h"$DB_HOST" -u"$DB_USER" -p"$DB_PASS" --skip-ssl -e "SELECT 1" &>/dev/null; do
    attempt=$((attempt + 1))
    if [ $attempt -ge $max_attempts ]; then
        echo "MySQL is still unavailable after $max_attempts attempts - giving up"
        exit 1
    fi
    echo "MySQL is unavailable - sleeping (attempt $attempt/$max_attempts)"
    sleep 2
done

echo "MySQL is up - starting application"

# Run the application
exec "$@"
