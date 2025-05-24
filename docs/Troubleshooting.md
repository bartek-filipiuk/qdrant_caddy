# Troubleshooting Guide: Qdrant with Caddy

This document describes common issues encountered when setting up Qdrant with Caddy as a reverse proxy, and their solutions.

## Authentication Issues

### Basic Auth Problems

**Issue**: 401 Unauthorized errors with message: `crypto/bcrypt: hashedSecret too short to be a bcrypted password`

**Solution**:
1. Generate a proper bcrypt hash using Caddy's built-in tool:
   ```bash
   docker run --rm caddy:alpine caddy hash-password --plaintext haslo123
   ```
2. Use the generated hash directly in the Caddyfile:
   ```
   basicauth {
     admin $2a$14$4ZcVRpfLes68NCOf.RaDBOpKHAtJbmvwtAagvcMzpjxMPmf158Chy
   }
   ```
3. Avoid using environment variables for password hashes in Caddyfile as they may not be properly interpolated.

### API Key Forwarding

**Issue**: 401 Unauthorized errors with message: `Must provide an API key or an Authorization bearer token` when accessing Qdrant API endpoints.

**Solution**:
1. Qdrant expects the API key in the `api-key` header (lowercase with hyphen). Make sure you're using the correct header format in your requests.
2. Ensure your API key is correctly set in the `.env` file and that Caddy is forwarding it properly:
   ```
   reverse_proxy qdrant:6333 {
     # Forward API key in the correct format
     header_up api-key {$QDRANT_API_KEY}
   }
   ```
3. When making API requests, use the `api-key` header format as shown in the example below:
   ```bash
   curl -X GET 'https://your-domain.com/collections' \
     -u admin:your_password \
     -H 'Content-Type: application/json' \
     -H 'api-key: your_api_key'
   ```

## Configuration Issues

### Environment Variables

**Issue**: Environment variables in docker-compose files may not be properly interpolated in container configurations.

**Solution**:
1. Use hardcoded values directly in configuration files for critical settings:
   ```yaml
   environment:
     - QDRANT__SERVICE__API_KEY=tajny_klucz_123
   ```
2. For production environments, consider using Docker secrets or a more robust environment variable management solution.

### Caddy Reverse Proxy Configuration

**Issue**: Timeouts or incomplete responses when making requests to Qdrant through Caddy.

**Solution**:
1. Configure longer timeouts in the Caddy reverse proxy settings:
   ```
   reverse_proxy qdrant:6333 {
     transport http {
       response_header_timeout 5m
       read_timeout 5m
       write_timeout 5m
     }
   }
   ```
2. This ensures that long-running operations in Qdrant (like vector searches on large collections) have enough time to complete.

## Testing API Connectivity

To verify that your setup is working correctly:

1. Use the `test-api.sh` script in the `scripts` directory to run a comprehensive test of all API endpoints.
2. Check that both Basic Auth and API Key validation are working correctly.
3. Verify that you can create collections, add vectors, search, and delete collections through the Caddy proxy.

## Common curl Commands

When testing manually, remember to include both Basic Auth and the API Key:

```bash
curl -u admin:haslo123 -H "api-key: tajny_klucz_123" http://localhost:8080/collections
```

For operations that modify data, include the Content-Type header:

```bash
curl -X PUT -u admin:haslo123 -H "api-key: tajny_klucz_123" -H "Content-Type: application/json" -d '{...}' http://localhost:8080/collections/my_collection
```
