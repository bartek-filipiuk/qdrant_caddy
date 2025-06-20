# Tutorial: Using Qdrant API with curl

## Introduction

Qdrant is an open-source vector database and vector similarity search engine written in Rust. It is designed for high-performance AI applications at scale, particularly for vector similarity search. Qdrant can be installed locally or on a server, and its API allows storing, searching, and managing vectors with additional data (payload). Since version 1.7, Qdrant also offers a web interface for easier interaction. This tutorial will guide you through the process of configuring Qdrant, API authorization, using key endpoints, and using the web interface.

## Step 1: Configuring and Running Qdrant in the Project

In this project, Qdrant is managed using Docker Compose along with a Caddy server, which acts as a reverse proxy and provides HTTPS in a production environment. Configuration is done via the `.env` file.

1.  **Prepare the configuration file**:
    *   Copy the `.env.example` file to a new file named `.env` in the project's root directory:
        ```bash
        cp .env.example .env
        ```
    *   Open the `.env` file and adjust the environment variables to your needs. Key variables are:
        *   `ENV`: Set to `local` for a local environment or `prod` for production. Defaults to `local`.
        *   `DOMAIN`: Your domain (used in `prod` mode), e.g., `qdrant.yourdomain.com`. Remember to configure the appropriate DNS records for this domain to point to the IP address of the server where you are running the project.
        *   `ADMIN_USER`: Username for the Caddy admin panel.
        *   `ADMIN_PASSWORD`: Password for `ADMIN_USER`. The `scripts/setup-domain.sh` script can help generate a password hash (`ADMIN_PASSWORD_HASH`) for Caddy if required.
        *   `QDRANT_API_KEY`: API key to secure access to Qdrant. Ensure it is a strong, unique key.
        *   `LOCAL_PORT`: Port on which Qdrant will be available locally via Caddy (used in `local` mode), e.g., `8081`.
        *   `ADMIN_EMAIL`: Email address used by Caddy to obtain SSL/TLS certificates from Let's Encrypt (in `prod` mode).

2.  **Start the services**:
    *   Ensure you have Docker and Docker Compose installed.
    *   In the project's root directory, run the `start.sh` script:
        ```bash
        ./start.sh
        ```
    *   This script will automatically read the configuration from the `.env` file and start the appropriate containers (`qdrant` and `caddy`) using `docker-compose`. In `prod` mode, Caddy will automatically try to obtain an SSL certificate for your domain.

3.  **Accessing the Qdrant web interface**:
    *   After successful startup, the Qdrant web interface will be available at:
        *   **For local environment (`ENV=local`)**: `http://localhost:LOCAL_PORT/dashboard` (where `LOCAL_PORT` is the value from the `.env` file, e.g., `http://localhost:8081/dashboard`). Qdrant API access will be at `http://localhost:LOCAL_PORT/`.
        *   **For production environment (`ENV=prod`)**: `https://DOMAIN/dashboard` (where `DOMAIN` is the value from the `.env` file, e.g., `https://qdrant.yourdomain.com/dashboard`). Qdrant API access will be at `https://DOMAIN/`.
    *   The web interface allows managing collections, browsing points, and performing searches interactively. Accessing the Qdrant API (e.g., via `curl` or programming clients) will require using the `QDRANT_API_KEY` defined in the `.env` file as an `api-key` header.

## Step 2: Authorization

Qdrant supports API key-based authorization to secure the instance. By default, authorization is disabled, but in a production environment, it is recommended to enable it.

- **Enabling API key authorization**:
  - The API key can be set using a configuration file or environment variables.
  - Example using an environment variable:
    ```bash
    docker run -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage:z -e QDRANT__SERVICE__API_KEY=your_secret_api_key qdrant/qdrant
    ```
    - Replace `your_secret_api_key` with a secure key.

- **Adding the API key to requests**:
  - Include the key in the header of each API request:
    ```bash
    -H 'api-key: your_secret_api_key'
    ```
  - Example:
    ```bash
    curl -X GET 'http://localhost:6333' -H 'api-key: your_secret_api_key'
    ```

- **Note**: If authorization is disabled (default in local installations), you can omit the API key header. In a production environment, always enable authorization and use HTTPS.

## Step 3: Key API Endpoints

Qdrant offers a REST API for interacting with the database. Below are the key endpoints, their functionality, and curl command examples.

### 1. Creating a Collection
- **Endpoint**: `PUT /collections/{collection_name}`
- **Description**: Creates a new collection for storing vectors.
- **Example**:
  ```bash
  curl -X PUT 'https://quadro.run/collections/my_collection' \
    -u admin:password123 \
    -H 'Content-Type: application/json' \
    -H 'api-key: secret_key_123' \
    -d '{
      "vectors": {
        "size": 1536,
        "distance": "Cosine"
      },
      "optimizers_config": {
        "default_segment_number": 2
      },
      "on_disk_payload": true
    }'
  ```
- **Explanation**:
  - `name`: Collection name.
  - `vectors.size`: Vector dimensions (e.g., 128).
  - `vectors.distance`: Distance metric (e.g., "Cosine" for cosine similarity).

### 2. Adding/Updating Points
- **Endpoint**: `PUT /collections/{collection_name}/points`
- **Description**: Adds or updates points (vectors with optional payload) in the collection.
- **Example**:
  ```bash
  curl -X PUT 'https://quadro.run/collections/my_collection/points' \
    -u admin:password123 \
    -H 'Content-Type: application/json' \
    -H 'api-key: secret_key_123' \
    -d '{
      "points": [
        {
          "id": 1,
          "vector": [0.1, 0.2, 0.3, 0.4, /* ... more values to complete 1536 dimensions ... */],
          "payload": {"city": "Warsaw"}
        },
        {
          "id": 2,
          "vector": [0.4, 0.5, 0.6, 0.7, /* ... more values to complete 1536 dimensions ... */],
          "payload": {"city": "Krakow"}
        }
      ]
    }'
  ```
- **Explanation**:
  - `id`: Unique point identifier.
  - `vector`: Vector data (must match the collection size).
  - `payload`: Optional metadata (e.g., {"city": "Warsaw"}).

### 3. Searching for Points
- **Endpoint**: `POST /collections/{collection_name}/points/search`
- **Description**: Searches for points similar to the given vector.
- **Example**:
  ```bash
  curl -X POST 'https://quadro.run/collections/my_collection/points/search' \
    -u admin:password123 \
    -H 'Content-Type: application/json' \
    -H 'api-key: secret_key_123' \
    -d '{
      "vector": [0.2, 0.3, 0.4, 0.5, /* ... more values ... */],
      "limit": 10
      /* Note: This collection requires 1536-dimensional vectors */
    }'
  ```
- **Explanation**:
  - `vector`: Query vector for searching similar points.
  - `limit`: Number of results to return (e.g., 10).

### 4. Getting Collection Information
- **Endpoint**: `GET /collections/{collection_name}`
- **Description**: Returns information about the collection.
- **Example**:
  ```bash
  curl -X GET 'https://quadro.run/collections/my_collection' \
    -u admin:password123 \
    -H 'Content-Type: application/json' \
    -H 'api-key: secret_key_123'
  ```

### 5. Deleting a Collection
- **Endpoint**: `DELETE /collections/{collection_name}`
- **Description**: Deletes the collection and all its points.
- **Example**:
  ```bash
  curl -X DELETE 'https://quadro.run/collections/my_collection' \
    -u admin:password123 \
    -H 'Content-Type: application/json' \
    -H 'api-key: secret_key_123'
  ```

### 6. Listing Snapshots
- **Endpoint**: `GET /snapshots`
- **Description**: Displays all available snapshots for collections.
- **Example**:
  ```bash
  curl -X GET 'https://quadro.run/snapshots' \
    -u admin:password123 \
    -H 'Content-Type: application/json' \
    -H 'api-key: secret_key_123'
  ```

### 7. Creating a Shard Key (for distributed mode)
- **Endpoint**: `POST /distributed/shard-key`
- **Description**: Creates a shard key for distributed deployments.
- **Example**:
  ```bash
  curl -X POST 'https://quadro.run/distributed/shard-key' \
    -H 'Content-Type: application/json' \
    -H 'api-key: your_secret_api_key' \
    -d '{
      "shard_key": "your_shard_key"
    }'
  ```

## Step 4: Using the Web Interface

- After running Qdrant, the web interface is available at:
  ```
  http://localhost:6333/dashboard
  ```
- For cloud deployments, add `:6333/dashboard` to your cluster URL (e.g., `https://xyz-example.cloud.qdrant.io:6333/dashboard`).
- The web interface offers intuitive features such as:
  - Collection management.
  - Browsing and searching points.
  - Monitoring cluster status.

## Step 5: Additional Notes

- **Authorization**:
  - If authorization is enabled, add the API key to each request:
    ```bash
    -H 'api-key: your_secret_api_key'
    ```
- **Notes for Production Environment**:
  - Always enable API key authorization.
  - Use HTTPS (TLS) to secure communication.
  - For distributed deployments, refer to the documentation on managing shard keys.
- **API Documentation**:
  - A complete list of endpoints and detailed documentation are available in the [Qdrant API Reference](https://api.qdrant.tech/v-1-13-x/api-reference).
  - You can also review the OpenAPI specification in [OpenAPI JSON](https://github.com/qdrant/qdrant/blob/master/docs/redoc/master/openapi.json).
