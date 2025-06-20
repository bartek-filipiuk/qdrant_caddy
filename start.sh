#!/bin/bash

# Helper script to start Qdrant
# This script calls the actual implementation in scripts/start.sh

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Call the implementation script
"$DIR/scripts/start.sh"
