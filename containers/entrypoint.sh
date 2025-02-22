#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Wait for postgres to be ready
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  echo "Waiting for postgres..."
  sleep 0.1
done
echo "PostgreSQL started"

export DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"


exec "$@"