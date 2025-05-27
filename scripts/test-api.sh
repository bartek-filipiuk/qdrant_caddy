#!/bin/bash

# Test API script for Qdrant with Caddy
# This script tests various API endpoints of Qdrant through Caddy proxy
# and generates a report of the test results

# Set variables
HOST="localhost:8443"
USERNAME="admin"
PASSWORD="zupa"
API_KEY="pomidorowa"
INSECURE="-k" # Skip SSL verification for self-signed certificates
TEST_COLLECTION="test_collection_$(date +%s)" # Unique collection name with timestamp

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Report variables
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

echo -e "${BOLD}${BLUE}=== Qdrant API Test Report ===${NC}"
echo -e "${YELLOW}Testing Qdrant API through Caddy proxy${NC}"
echo "Host: $HOST"
echo "Username: $USERNAME"
echo "API Key: $API_KEY"
echo "Test Collection: $TEST_COLLECTION"
echo "Date: $(date)"
echo "-----------------------------------"
echo

# Function to make API calls and check results
call_api() {
    local endpoint=$1
    local method=${2:-GET}
    local data=$3
    local test_name=$4
    local expected_status=${5:-200}
    
    TOTAL_TESTS=$((TOTAL_TESTS+1))
    
    echo -e "\n${YELLOW}Test $TOTAL_TESTS: $test_name${NC}"
    echo -e "Endpoint: $endpoint (Method: $method)"
    
    # Build the curl command
    cmd="curl -s -w '\n%{http_code}' -X $method"
    cmd="$cmd -u $USERNAME:$PASSWORD"
    cmd="$cmd -H \"X-API-KEY: $API_KEY\""
    
    if [ ! -z "$data" ]; then
        cmd="$cmd -H \"Content-Type: application/json\" -d '$data'"
    fi
    
    cmd="$cmd http://$HOST$endpoint"
    
    # Execute the command
    echo "Command: $cmd"
    result=$(eval $cmd)
    exit_code=$?
    
    # Extract status code from the last line
    status_code=$(echo "$result" | tail -n1)
    # Extract response body (all but the last line)
    response_body=$(echo "$result" | sed \$d)
    
    # Check exit code and status code
    if [ $exit_code -ne 0 ]; then
        echo -e "${RED}✗ FAILED: curl command failed with exit code $exit_code${NC}"
        FAILED_TESTS=$((FAILED_TESTS+1))
        return 1
    elif [ "$status_code" != "$expected_status" ]; then
        echo -e "${RED}✗ FAILED: Expected status $expected_status but got $status_code${NC}"
        echo "Response: $response_body"
        FAILED_TESTS=$((FAILED_TESTS+1))
        return 1
    else
        echo -e "${GREEN}✓ PASSED${NC}"
        echo "Status: $status_code"
        echo "Response: $response_body"
        PASSED_TESTS=$((PASSED_TESTS+1))
        return 0
    fi
}

# Run the tests

# Test 1: Check API root endpoint
call_api "/" "GET" "" "Check API root endpoint"

# Test 2: List collections (should be empty or contain previous collections)
call_api "/collections" "GET" "" "List collections"

# Test 3: Create a test collection
collection_data="{
  \"vectors\": {
    \"size\": 4,
    \"distance\": \"Cosine\"
  }
}"
call_api "/collections/$TEST_COLLECTION" "PUT" "$collection_data" "Create test collection"

# Test 4: Verify collection was created
call_api "/collections/$TEST_COLLECTION" "GET" "" "Verify collection exists"

# Test 5: Add points to collection
points_data="{
  \"points\": [
    {
      \"id\": 1,
      \"vector\": [0.1, 0.2, 0.3, 0.4],
      \"payload\": {\"city\": \"Warsaw\"}
    },
    {
      \"id\": 2,
      \"vector\": [0.4, 0.5, 0.6, 0.7],
      \"payload\": {\"city\": \"Krakow\"}
    }
  ]
}"
call_api "/collections/$TEST_COLLECTION/points" "PUT" "$points_data" "Add points to collection"

# Test 6: Search points in collection
search_data="{
  \"vector\": [0.2, 0.3, 0.4, 0.5],
  \"limit\": 2
}"
call_api "/collections/$TEST_COLLECTION/points/search" "POST" "$search_data" "Search for similar vectors"

# Test 7: Delete collection
call_api "/collections/$TEST_COLLECTION" "DELETE" "" "Delete test collection"

# Test 8: Verify collection was deleted
call_api "/collections/$TEST_COLLECTION" "GET" "" "Verify collection was deleted" 404

# Generate summary report
echo -e "\n${BOLD}${BLUE}=== Test Summary ===${NC}"
echo -e "Total tests: ${BOLD}$TOTAL_TESTS${NC}"
echo -e "${GREEN}Passed: ${BOLD}$PASSED_TESTS${NC}"
echo -e "${RED}Failed: ${BOLD}$FAILED_TESTS${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "\n${GREEN}${BOLD}All tests passed! The Qdrant API with Caddy proxy is working correctly.${NC}"
else
    echo -e "\n${RED}${BOLD}Some tests failed. Please check the logs above for details.${NC}"
fi
