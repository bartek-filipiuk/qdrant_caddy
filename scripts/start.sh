#!/bin/bash

# Load environment variables
source "$(dirname "$0")/../.env"

# Check ENV value
if [ "$ENV" == "local" ]; then
    echo "Starting in local environment..."
    cd "$(dirname "$0")/.." && docker compose -f docker-compose.local.yml up -d
elif [ "$ENV" == "prod" ]; then
    echo "Starting in production environment..."
    cd "$(dirname "$0")/.." && docker compose -f docker-compose.prod.yml up -d
else
    echo "Error: Unknown ENV value: $ENV"
    echo "Set ENV=local or ENV=prod in .env file"
    exit 1
fi

echo "Started successfully!"
echo "Qdrant UI available at:"
if [ "$ENV" == "local" ]; then
    echo "http://localhost:$LOCAL_PORT/dashboard"
else
    echo "https://$DOMAIN/dashboard"
fi
echo "Login: $ADMIN_USER"
echo "Password: $ADMIN_PASSWORD"
