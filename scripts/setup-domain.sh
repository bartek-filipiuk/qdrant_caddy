#!/bin/bash

# Setup domain script for Qdrant with Caddy
# This script helps configure a domain for production environment

# Load environment variables
source ../.env

# Check if DOMAIN is set
if [ -z "$DOMAIN" ]; then
    echo "Error: DOMAIN is not set in .env file"
    echo "Please set DOMAIN=your.domain.com in .env file"
    exit 1
fi

# Check if ADMIN_EMAIL is set (needed for Let's Encrypt)
if [ -z "$ADMIN_EMAIL" ]; then
    echo "ADMIN_EMAIL is not set in .env file. This is needed for Let's Encrypt certificates."
    echo "Please enter an email address for Let's Encrypt notifications:"
    read -r ADMIN_EMAIL
    
    # Add ADMIN_EMAIL to .env file
    if grep -q "ADMIN_EMAIL=" ../.env; then
        sed -i "s|ADMIN_EMAIL=.*|ADMIN_EMAIL=$ADMIN_EMAIL|" ../.env
    else
        echo "ADMIN_EMAIL=$ADMIN_EMAIL" >> ../.env
    fi
fi

echo "=== Setting up domain for Qdrant with Caddy ==="
echo "Domain: $DOMAIN"

# Check if running as root (required for port 80/443)
if [ "$EUID" -ne 0 ]; then
    echo "Warning: This script should be run as root to bind to ports 80/443"
    echo "Continue anyway? (y/n)"
    read -r answer
    if [ "$answer" != "y" ]; then
        echo "Aborted"
        exit 1
    fi
fi

# Check if ports 80 and 443 are available
echo "Checking if ports 80 and 443 are available..."
if lsof -i:80 -i:443 > /dev/null; then
    echo "Warning: Ports 80 and/or 443 are already in use"
    echo "Please stop any services using these ports (e.g. Apache, Nginx) before continuing"
    echo "Continue anyway? (y/n)"
    read -r answer
    if [ "$answer" != "y" ]; then
        echo "Aborted"
        exit 1
    fi
fi

# Check DNS configuration
echo "Checking DNS configuration for $DOMAIN..."
if ! host "$DOMAIN" > /dev/null; then
    echo "Warning: Could not resolve $DOMAIN"
    echo "Please make sure your DNS is configured correctly to point to this server's IP address"
    echo "Continue anyway? (y/n)"
    read -r answer
    if [ "$answer" != "y" ]; then
        echo "Aborted"
        exit 1
    fi
fi

# Generate password hash for Caddy
echo "Generating password hash for Caddy..."
PASSWORD_HASH=$(docker run --rm caddy:2 caddy hash-password --plaintext "$ADMIN_PASSWORD")
echo "Generated hash: $PASSWORD_HASH"

# Update .env file with password hash
echo "Updating .env file with password hash..."
if grep -q "ADMIN_PASSWORD_HASH=" ../.env; then
    # Update existing hash - use double quotes to preserve the hash format with special characters
    sed -i "s|ADMIN_PASSWORD_HASH=.*|ADMIN_PASSWORD_HASH=\"$PASSWORD_HASH\"|" ../.env
else
    # Add hash if it doesn't exist - use double quotes to preserve the hash format with special characters
    echo "ADMIN_PASSWORD_HASH=\"$PASSWORD_HASH\"" >> ../.env
fi

# Start production environment
echo "Starting production environment..."
cd .. && ENV=prod ./restart.sh

echo "=== Domain setup completed successfully! ==="
echo "Qdrant UI should be available at: https://$DOMAIN/dashboard"
echo "It may take a few minutes for Caddy to obtain SSL certificates"
echo "You can check the logs with: docker logs qdrant-caddy-1"
