# Qdrant Backup and Restore Guide

This guide explains how to create backups of your Qdrant collections and restore them when needed using the provided Python scripts.

## Prerequisites

Before you begin, make sure you have:

- Python 3.6 or higher installed
- The `requests` Python package installed (`pip install requests`)
- Access to a running Qdrant instance
- Proper permissions to create and restore snapshots

## Backup Process

### Understanding Snapshots

Qdrant uses snapshots for backup and recovery. A snapshot is a point-in-time copy of a collection that includes:

- Vector data
- Payload data
- Collection configuration
- Index structures

Snapshots are created per collection and can be used to restore data to the same or a different collection.

### Using the Backup Script

The `backup_snapshots.py` script allows you to create and download snapshots of your Qdrant collections.

#### Script Location

The backup script is located in the `scripts` directory:

```
/path/to/dockabase/scripts/backup_snapshots.py
```

#### Basic Usage

To backup a specific collection:

```bash
python backup_snapshots.py --collection my_collection
```

To backup all collections:

```bash
python backup_snapshots.py --all
```

#### Advanced Options

The script supports several additional options:

```bash
python backup_snapshots.py [--collection COLLECTION | --all] 
                          [--host HOST] 
                          [--api-key API_KEY] 
                          [--output-dir OUTPUT_DIR]
```

- `--host`: Specify the Qdrant host URL (default: http://localhost:6333)
- `--api-key`: Provide an API key if your Qdrant instance requires authentication
- `--output-dir`: Specify a custom directory to save snapshots (default: ./snapshots)

#### Example

```bash
python backup_snapshots.py --collection product_vectors --host http://qdrant.example.com:6333 --api-key your_api_key --output-dir /backups/qdrant
```

This command will:
1. Connect to the Qdrant instance at http://qdrant.example.com:6333
2. Authenticate using the provided API key
3. Create a snapshot of the "product_vectors" collection
4. Download the snapshot to the "/backups/qdrant" directory

### Backup Process Details

When you run the backup script, it performs the following steps:

1. Connects to the Qdrant server using the provided host and API key
2. Lists available collections (if using the `--all` option)
3. For each collection to backup:
   - Creates a snapshot on the Qdrant server
   - Downloads the snapshot file to the specified output directory
4. Provides a summary of successful and failed backups

## Restore Process

### Using the Restore Script

The `restore_snapshots.py` script allows you to restore collections from previously created snapshots.

#### Script Location

The restore script is located in the `scripts` directory:

```
/path/to/dockabase/scripts/restore_snapshots.py
```

#### Basic Usage

To restore an existing collection (this will replace the current data):

```bash
python restore_snapshots.py --snapshot ./snapshots/my_collection.snapshot --collection my_collection
```

To create a new collection from a snapshot:

```bash
python restore_snapshots.py --snapshot ./snapshots/my_collection.snapshot --new-collection my_new_collection
```

#### Advanced Options

The script supports several additional options:

```bash
python restore_snapshots.py --snapshot SNAPSHOT_FILE 
                           [--collection COLLECTION | --new-collection NEW_COLLECTION] 
                           [--host HOST] 
                           [--api-key API_KEY]
```

- `--host`: Specify the Qdrant host URL (default: http://localhost:6333)
- `--api-key`: Provide an API key if your Qdrant instance requires authentication

#### Example

```bash
python restore_snapshots.py --snapshot /backups/qdrant/product_vectors.snapshot --new-collection product_vectors_restored --host http://qdrant.example.com:6333 --api-key your_api_key
```

This command will:
1. Connect to the Qdrant instance at http://qdrant.example.com:6333
2. Authenticate using the provided API key
3. Upload the snapshot file to the Qdrant server
4. Create a new collection named "product_vectors_restored" using the data from the snapshot

### Restore Process Details

When you run the restore script, it performs the following steps:

1. Connects to the Qdrant server using the provided host and API key
2. Uploads the snapshot file to the Qdrant server
3. Depending on the options:
   - Restores an existing collection (replacing current data)
   - Creates a new collection from the snapshot
4. Provides a summary of the restore operation

## Backup Scheduling

For production environments, it's recommended to schedule regular backups using cron or another scheduling system.

### Example Cron Setup

To create daily backups at 2 AM:

```bash
# Edit crontab
crontab -e

# Add the following line
0 2 * * * /usr/bin/python3 /path/to/dockabase/scripts/backup_snapshots.py --all --output-dir /backups/qdrant/$(date +\%Y-\%m-\%d) --host http://localhost:6333 --api-key your_api_key >> /var/log/qdrant-backup.log 2>&1
```

## Backup Retention Policy

Consider implementing a backup retention policy to manage disk space:

```bash
# Keep only the last 7 daily backups
find /backups/qdrant/ -type d -name "202*" -mtime +7 -exec rm -rf {} \;
```

## Troubleshooting

### Common Backup Issues

- **Connection errors**: Ensure the Qdrant server is running and accessible
- **Authentication errors**: Verify the API key is correct
- **Permission errors**: Make sure the script has write permissions to the output directory
- **Disk space issues**: Ensure there's enough space for the snapshots

### Common Restore Issues

- **Snapshot not found**: Verify the path to the snapshot file
- **Collection already exists**: Use `--collection` to replace an existing collection
- **Collection doesn't exist**: Use `--new-collection` to create a new collection
- **Invalid snapshot**: Ensure the snapshot file is not corrupted

## Best Practices

1. **Regular backups**: Schedule automatic backups for critical collections
2. **Test restores**: Periodically test the restore process to ensure backups are valid
3. **Offsite storage**: Store backups in a different location for disaster recovery
4. **Documentation**: Keep track of what each snapshot contains
5. **Monitoring**: Set up alerts for backup failures

## Additional Resources

- [Qdrant Documentation on Snapshots](https://qdrant.tech/documentation/concepts/snapshots/)
- [Python Requests Library](https://docs.python-requests.org/)
