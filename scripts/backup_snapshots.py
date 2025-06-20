#!/usr/bin/env python3
"""
Qdrant Collection Snapshot Backup Tool

This script creates and downloads snapshots of Qdrant collections.
It can backup a specific collection or all collections.

Usage:
    python backup_snapshots.py --collection <collection_name>
    python backup_snapshots.py --all
    
Options:
    --collection  Name of the collection to backup
    --all         Backup all collections
    --host        Qdrant host URL (default: http://localhost:6333)
    --api-key     Qdrant API key (if required)
    --output-dir  Directory to save snapshots (default: ./snapshots)
"""

import argparse
import os
import sys
import time
import requests
from datetime import datetime
from typing import List, Dict, Optional, Any


class QdrantSnapshotBackup:
    def __init__(
        self,
        host: str = "http://localhost:6333",
        api_key: Optional[str] = None,
        output_dir: str = "./snapshots"
    ):
        self.host = host.rstrip("/")
        self.api_key = api_key
        self.output_dir = output_dir
        self.headers = {}
        
        if api_key:
            self.headers["api-key"] = api_key
            
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
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
            
    def list_collections(self) -> List[str]:
        """Get list of all collections from Qdrant"""
        print("Fetching list of collections...")
        
        try:
            response = self._make_request("GET", "/collections")
            collections = [col["name"] for col in response["result"]["collections"]]
            return collections
        except (KeyError, TypeError) as e:
            print(f"Error parsing collections response: {e}")
            sys.exit(1)
            
    def create_snapshot(self, collection_name: str) -> Dict[str, Any]:
        """Create a snapshot for the specified collection"""
        print(f"Creating snapshot for collection '{collection_name}'...")
        
        try:
            response = self._make_request(
                "POST", 
                f"/collections/{collection_name}/snapshots",
                params={"wait": "true"}
            )
            return response["result"]
        except (KeyError, TypeError) as e:
            print(f"Error creating snapshot for collection '{collection_name}': {e}")
            return None
            
    def download_snapshot(self, collection_name: str, snapshot_name: str) -> str:
        """Download a snapshot file"""
        snapshot_url = f"/collections/{collection_name}/snapshots/{snapshot_name}"
        local_path = os.path.join(self.output_dir, snapshot_name)
        
        print(f"Downloading snapshot '{snapshot_name}'...")
        
        try:
            url = f"{self.host}{snapshot_url}"
            response = requests.get(url, headers=self.headers, stream=True)
            response.raise_for_status()
            
            with open(local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            print(f"Snapshot saved to: {local_path}")
            return local_path
        except requests.exceptions.RequestException as e:
            print(f"Error downloading snapshot '{snapshot_name}': {e}")
            return None
        except IOError as e:
            print(f"Error writing snapshot file '{local_path}': {e}")
            return None
            
    def backup_collection(self, collection_name: str) -> bool:
        """Create and download a snapshot for a collection"""
        try:
            # Create snapshot
            snapshot_info = self.create_snapshot(collection_name)
            if not snapshot_info:
                print(f"Failed to create snapshot for collection '{collection_name}'")
                return False
                
            # Download snapshot
            snapshot_name = snapshot_info["name"]
            local_path = self.download_snapshot(collection_name, snapshot_name)
            
            if local_path:
                print(f"Successfully backed up collection '{collection_name}'")
                return True
            else:
                print(f"Failed to download snapshot for collection '{collection_name}'")
                return False
                
        except Exception as e:
            print(f"Unexpected error backing up collection '{collection_name}': {e}")
            return False
            
    def backup_all_collections(self) -> Dict[str, bool]:
        """Backup all collections"""
        collections = self.list_collections()
        
        if not collections:
            print("No collections found in Qdrant")
            return {}
            
        print(f"Found {len(collections)} collections: {', '.join(collections)}")
        
        results = {}
        for collection in collections:
            print(f"\n{'=' * 50}")
            print(f"Backing up collection: {collection}")
            print(f"{'=' * 50}")
            
            success = self.backup_collection(collection)
            results[collection] = success
            
        return results


def print_usage():
    """Print detailed usage instructions"""
    print("""
Qdrant Collection Snapshot Backup Tool
======================================

This tool creates and downloads snapshots of Qdrant collections for backup purposes.

Basic Usage:
-----------
  ./backup_snapshots.py --collection <collection_name>  # Backup a specific collection
  ./backup_snapshots.py --all                          # Backup all collections

Options:
-------
  --collection <name>   Name of the collection to backup
  --all                 Backup all collections
  --host <url>          Qdrant host URL (default: http://localhost:6333)
  --api-key <key>       Qdrant API key (if required)
  --output-dir <path>   Directory to save snapshots (default: ./snapshots)
  --help                Show this help message and exit

Examples:
--------
  # Backup a specific collection
  ./backup_snapshots.py --collection my_collection

  # Backup all collections
  ./backup_snapshots.py --all

  # Specify custom host and API key
  ./backup_snapshots.py --collection my_collection --host http://qdrant.example.com:6333 --api-key my_api_key

  # Specify custom output directory
  ./backup_snapshots.py --all --output-dir /path/to/backups
""")


def main():
    parser = argparse.ArgumentParser(
        description="Qdrant Collection Snapshot Backup Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Backup a specific collection
  %(prog)s --collection my_collection

  # Backup all collections
  %(prog)s --all

  # Specify custom host and API key
  %(prog)s --collection my_collection --host http://qdrant.example.com:6333 --api-key my_api_key

  # Specify custom output directory
  %(prog)s --all --output-dir /path/to/backups
"""
    )
    
    # Check if --help is passed directly
    if "--help" in sys.argv and len(sys.argv) == 2:
        print_usage()
        sys.exit(0)
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--collection", help="Name of the collection to backup")
    group.add_argument("--all", action="store_true", help="Backup all collections")
    
    parser.add_argument("--host", default="http://localhost:6333", help="Qdrant host URL")
    parser.add_argument("--api-key", help="Qdrant API key (if required)")
    parser.add_argument("--output-dir", default="./snapshots", help="Directory to save snapshots")
    
    args = parser.parse_args()
    
    # Initialize backup tool
    backup_tool = QdrantSnapshotBackup(
        host=args.host,
        api_key=args.api_key,
        output_dir=args.output_dir
    )
    
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"\nQdrant Snapshot Backup - {timestamp}")
    print(f"Host: {args.host}")
    print(f"Output directory: {args.output_dir}")
    print("-" * 60)
    
    # Perform backup
    if args.all:
        print("Backing up all collections...")
        results = backup_tool.backup_all_collections()
        
        # Print summary
        print("\n" + "=" * 60)
        print("Backup Summary:")
        print("-" * 60)
        
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        for collection, success in results.items():
            status = "SUCCESS" if success else "FAILED"
            print(f"{collection}: {status}")
            
        print("-" * 60)
        print(f"Total: {success_count}/{total_count} collections backed up successfully")
        
    else:
        print(f"Backing up collection: {args.collection}")
        success = backup_tool.backup_collection(args.collection)
        
        print("\n" + "=" * 60)
        print("Backup Summary:")
        print("-" * 60)
        print(f"{args.collection}: {'SUCCESS' if success else 'FAILED'}")
        
    elapsed_time = time.time() - start_time
    print(f"\nBackup completed in {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBackup process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
