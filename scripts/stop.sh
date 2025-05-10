#!/bin/bash

# Load environment variables
source "$(dirname "$0")/../.env"

# Check ENV value
if [ "$ENV" == "local" ]; then
    echo "Stopping local environment..."
    cd "$(dirname "$0")/.." && docker compose -f docker-compose.local.yml down
elif [ "$ENV" == "prod" ]; then
    echo "Stopping production environment..."
    cd "$(dirname "$0")/.." && docker compose -f docker-compose.prod.yml down
else
    echo "Error: Unknown ENV value: $ENV"
    echo "Set ENV=local or ENV=prod in .env file"
    exit 1
fi

echo "Stopped successfully!"
