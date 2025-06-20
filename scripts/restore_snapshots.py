#!/usr/bin/env python3
"""
Qdrant Collection Snapshot Restore Tool

This script restores Qdrant collections from previously created snapshots.
It can restore a specific collection or create a new collection from a snapshot.

Usage:
    python restore_snapshots.py --snapshot <snapshot_file> --collection <collection_name>
    python restore_snapshots.py --snapshot <snapshot_file> --new-collection <new_collection_name>
    
Options:
    --snapshot       Path to the snapshot file to restore from
    --collection     Name of the existing collection to restore (will be replaced)
    --new-collection Name of a new collection to create from the snapshot
    --host           Qdrant host URL (default: http://localhost:6333)
    --api-key        Qdrant API key (if required)
"""

import argparse
import os
import sys
import time
import requests
from datetime import datetime
from typing import Dict, Optional, Any


class QdrantSnapshotRestore:
    def __init__(
        self,
        host: str = "http://localhost:6333",
        api_key: Optional[str] = None
    ):
        self.host = host.rstrip("/")
        self.api_key = api_key
        self.headers = {}
        
        if api_key:
            self.headers["api-key"] = api_key
            
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to Qdrant API with error handling"""
        url = f"{self.host}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            print(f"Error: Could not connect to Qdrant at {self.host}")
            sys.exit(1)
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
            print(f"Response: {response.text}")
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            sys.exit(1)
        except ValueError:
            print(f"Error: Invalid JSON response from Qdrant")
            sys.exit(1)
            
    def upload_snapshot(self, snapshot_path: str) -> str:
        """Upload a snapshot file to Qdrant server"""
        if not os.path.exists(snapshot_path):
            print(f"Error: Snapshot file not found: {snapshot_path}")
            sys.exit(1)
            
        snapshot_name = os.path.basename(snapshot_path)
        print(f"Uploading snapshot file: {snapshot_name}")
        
        try:
            with open(snapshot_path, 'rb') as f:
                files = {'snapshot': (snapshot_name, f)}
                url = f"{self.host}/snapshots"
                
                response = requests.post(
                    url,
                    headers=self.headers,
                    files=files
                )
                response.raise_for_status()
                
                result = response.json()
                if result.get("status") != "ok":
                    print(f"Error uploading snapshot: {result}")
                    sys.exit(1)
                    
                print(f"Snapshot uploaded successfully")
                return snapshot_name
                
        except IOError as e:
            print(f"Error reading snapshot file: {e}")
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            print(f"Error uploading snapshot: {e}")
            sys.exit(1)
            
    def restore_collection(self, snapshot_name: str, collection_name: str) -> bool:
        """Restore an existing collection from a snapshot"""
        print(f"Restoring collection '{collection_name}' from snapshot '{snapshot_name}'...")
        
        try:
            endpoint = f"/collections/{collection_name}/snapshots/recover"
            params = {"wait": "true"}
            data = {"snapshot_name": snapshot_name}
            
            response = self._make_request(
                "PUT",
                endpoint,
                params=params,
                json=data
            )
            
            if response.get("status") == "ok":
                print(f"Collection '{collection_name}' restored successfully")
                return True
            else:
                print(f"Error restoring collection: {response}")
                return False
                
        except Exception as e:
            print(f"Error restoring collection: {e}")
            return False
            
    def create_collection_from_snapshot(self, snapshot_name: str, new_collection_name: str) -> bool:
        """Create a new collection from a snapshot"""
        print(f"Creating new collection '{new_collection_name}' from snapshot '{snapshot_name}'...")
        
        try:
            endpoint = f"/collections/{new_collection_name}/snapshots/recover"
            params = {"wait": "true"}
            data = {"snapshot_name": snapshot_name}
            
            response = self._make_request(
                "PUT",
                endpoint,
                params=params,
                json=data
            )
            
            if response.get("status") == "ok":
                print(f"Collection '{new_collection_name}' created successfully from snapshot")
                return True
            else:
                print(f"Error creating collection from snapshot: {response}")
                return False
                
        except Exception as e:
            print(f"Error creating collection from snapshot: {e}")
            return False


def print_usage():
    """Print detailed usage instructions"""
    print("""
Qdrant Collection Snapshot Restore Tool
=======================================

This tool restores Qdrant collections from previously created snapshots.

Basic Usage:
-----------
  ./restore_snapshots.py --snapshot <snapshot_file> --collection <collection_name>
  ./restore_snapshots.py --snapshot <snapshot_file> --new-collection <new_collection_name>

Options:
-------
  --snapshot <file>       Path to the snapshot file to restore from
  --collection <name>     Name of the existing collection to restore (will be replaced)
  --new-collection <name> Name of a new collection to create from the snapshot
  --host <url>            Qdrant host URL (default: http://localhost:6333)
  --api-key <key>         Qdrant API key (if required)
  --help                  Show this help message and exit

Examples:
--------
  # Restore an existing collection
  ./restore_snapshots.py --snapshot ./snapshots/my_collection.snapshot --collection my_collection

  # Create a new collection from a snapshot
  ./restore_snapshots.py --snapshot ./snapshots/my_collection.snapshot --new-collection my_new_collection

  # Specify custom host and API key
  ./restore_snapshots.py --snapshot ./snapshots/my_collection.snapshot --collection my_collection --host http://qdrant.example.com:6333 --api-key my_api_key
""")


def main():
    parser = argparse.ArgumentParser(
        description="Qdrant Collection Snapshot Restore Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Restore an existing collection
  %(prog)s --snapshot ./snapshots/my_collection.snapshot --collection my_collection

  # Create a new collection from a snapshot
  %(prog)s --snapshot ./snapshots/my_collection.snapshot --new-collection my_new_collection

  # Specify custom host and API key
  %(prog)s --snapshot ./snapshots/my_collection.snapshot --collection my_collection --host http://qdrant.example.com:6333 --api-key my_api_key
"""
    )
    
    # Check if --help is passed directly
    if "--help" in sys.argv and len(sys.argv) == 2:
        print_usage()
        sys.exit(0)
    
    parser.add_argument("--snapshot", required=True, help="Path to the snapshot file to restore from")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--collection", help="Name of the existing collection to restore (will be replaced)")
    group.add_argument("--new-collection", help="Name of a new collection to create from the snapshot")
    
    parser.add_argument("--host", default="http://localhost:6333", help="Qdrant host URL")
    parser.add_argument("--api-key", help="Qdrant API key (if required)")
    
    args = parser.parse_args()
    
    # Initialize restore tool
    restore_tool = QdrantSnapshotRestore(
        host=args.host,
        api_key=args.api_key
    )
    
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"\nQdrant Snapshot Restore - {timestamp}")
    print(f"Host: {args.host}")
    print(f"Snapshot: {args.snapshot}")
    print("-" * 60)
    
    # Upload snapshot
    snapshot_name = restore_tool.upload_snapshot(args.snapshot)
    
    # Perform restore
    success = False
    if args.collection:
        print(f"Restoring to existing collection: {args.collection}")
        success = restore_tool.restore_collection(snapshot_name, args.collection)
    else:
        print(f"Creating new collection: {args.new_collection}")
        success = restore_tool.create_collection_from_snapshot(snapshot_name, args.new_collection)
    
    # Print summary
    print("\n" + "=" * 60)
    print("Restore Summary:")
    print("-" * 60)
    
    collection_name = args.collection or args.new_collection
    status = "SUCCESS" if success else "FAILED"
    print(f"Collection: {collection_name}")
    print(f"Status: {status}")
    
    elapsed_time = time.time() - start_time
    print(f"\nRestore completed in {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nRestore process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
