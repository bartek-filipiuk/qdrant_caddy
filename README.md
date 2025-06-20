# Qdrant Vector Database

Qdrant configuration with API key and HTTPS support for local and production environments.

## Description

This repository contains a ready-to-use configuration for Qdrant - an efficient vector database, with the following features:

- Local environment with direct access to Qdrant
- Production environment with Caddy as a reverse proxy (HTTPS, Basic Auth)
- API key authentication
- Management scripts (start, stop, restart)
- Automatic SSL certificate acquisition in production environment

## Requirements

- Docker and Docker Compose
- Bash

## Quick Start

1. Copy `.env.example` to `.env` and adjust variables:
   ```bash
   cp .env.example .env
   ```

2. Start Qdrant locally:
   ```bash
   ./start.sh
   ```

3. Access the dashboard:
   ```
   http://localhost:8081/dashboard
   ```
   
4. Use the API key from the `.env` file to authenticate requests.

## Project Structure

- `config/` - Configuration files (Caddyfile)
- `scripts/` - Management and configuration scripts
- `docs/` - Documentation
- `docker-compose.local.yml` - Configuration for local environment
- `docker-compose.prod.yml` - Configuration for production environment

## Production Deployment

To deploy to production:

1. Set the `DOMAIN` variable in the `.env` file
2. Run the domain setup script:
   ```bash
   sudo ./scripts/setup-domain.sh
   ```

Detailed instructions can be found in `docs/DEPLOYMENT.md`.

## Documentation

- `docs/FAQ.md` - Frequently Asked Questions (password management, authentication, etc.)
- `docs/Troubleshooting.md` - Troubleshooting guide
- `docs/Tutorial korzystania z API Qdrant.md` - API usage examples (Polish)
- `docs/Qdrant API Tutorial.md` - API usage examples (English)
