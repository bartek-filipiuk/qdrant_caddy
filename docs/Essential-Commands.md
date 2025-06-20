# Qdrant Essential Commands

## Setup

```bash
# Clone repository
git clone https://github.com/bartek-filipiuk/qdrant_caddy.git
cd qdrant_caddy

# Configure environment
cp .env.example .env
# Edit .env file with your settings
```

## Basic Operations

```bash
# Start Qdrant
./start.sh                # Starts containers based on ENV setting in .env

# Stop Qdrant
./stop.sh                 # Stops all containers

# Restart Qdrant
./restart.sh              # Restarts containers and applies config changes
```

## Domain Setup (Production Only)

```bash
# Configure domain for production
./scripts/setup-domain.sh # Sets up domain with HTTPS using Let's Encrypt
```

## Backup & Restore

```bash
# Backup a specific collection
python scripts/backup_snapshots.py --collection my_collection

# Backup all collections
python scripts/backup_snapshots.py --all

# Restore a collection
python scripts/restore_snapshots.py --snapshot ./snapshots/my_collection.snapshot --collection my_collection

# Create new collection from backup
python scripts/restore_snapshots.py --snapshot ./snapshots/my_collection.snapshot --new-collection new_collection
```

## Access Information

- **Local Environment**: http://localhost:8081/dashboard
- **Production Environment**: https://your-domain.com/dashboard
- **Default Credentials**: Set in .env file (ADMIN_USER/ADMIN_PASSWORD)
- **API Key**: Set in .env file (QDRANT_API_KEY)
