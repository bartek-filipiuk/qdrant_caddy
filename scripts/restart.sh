#!/bin/bash

# Restart script for Qdrant with Caddy
# This script updates configuration files with values from .env and restarts containers

# Load environment variables
source "$(dirname "$0")/../.env"

# Check ENV value
if [ "$ENV" == "local" ]; then
    CONFIG_FILE="$(dirname "$0")/../config/Caddyfile.local"
    COMPOSE_FILE="$(dirname "$0")/../docker-compose.local.yml"
elif [ "$ENV" == "prod" ]; then
    CONFIG_FILE="$(dirname "$0")/../config/Caddyfile.prod"
    COMPOSE_FILE="$(dirname "$0")/../docker-compose.prod.yml"
else
    echo "Error: Unknown ENV value: $ENV"
    echo "Set ENV=local or ENV=prod in .env file"
    exit 1
fi

echo "=== Restarting Qdrant with Caddy ==="
echo "Environment: $ENV"
echo "Using config file: $CONFIG_FILE"
echo "Using compose file: $COMPOSE_FILE"

# Stop containers
echo "Stopping containers..."
docker compose -f $COMPOSE_FILE down

# Update Caddy configuration with current values from .env
echo "Updating Caddy configuration..."

# No Caddy configuration needed anymore
echo "Using direct access to Qdrant without Caddy"

# Start containers
echo "Starting containers..."
cd "$(dirname "$0")/.." && docker compose -f $COMPOSE_FILE up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 3

echo "=== Restart completed successfully! ==="
echo "Qdrant UI available at:"
if [ "$ENV" == "local" ]; then
    echo "http://localhost:8081/dashboard"
else
    echo "https://$DOMAIN/dashboard"
fi
echo "API Key: $QDRANT_API_KEY"
