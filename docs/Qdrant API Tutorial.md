# Tutorial: Using Qdrant API with curl

## Introduction

Qdrant is an open-source vector database and vector similarity search engine written in Rust. It is designed for high-performance AI applications at scale, particularly for vector similarity search. Qdrant can be installed locally or on a server, and its API allows storing, searching, and managing vectors with additional data (payload). Since version 1.7, Qdrant also offers a web interface for easier interaction. This tutorial will guide you through the process of configuring Qdrant, API authorization, using key endpoints, and using the web interface.

## Step 1: Configuring Qdrant

Qdrant can be run locally using Docker or as a binary file. In this tutorial, we'll use Docker for simplicity.

1. **Download the Qdrant image**:
   ```bash
   docker pull qdrant/qdrant
   ```

2. **Run the Qdrant container**:
   ```bash
   docker run -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage:z qdrant/qdrant
   ```
   - This command runs Qdrant on port 6333.
   - The `-v` flag mounts a local directory (`qdrant_storage`) for data storage.

3. **Access the web interface**:
   - After running Qdrant, the web interface is available at:
     ```
     http://localhost:6333/dashboard
     ```
   - The web interface allows you to manage collections, browse points, and perform searches interactively.

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
        "size": 128,
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
          "vector": [0.1, 0.2, 0.3, 0.4],
          "payload": {"city": "Warsaw"}
        },
        {
          "id": 2,
          "vector": [0.4, 0.5, 0.6, 0.7],
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
      "vector": [0.2, 0.3, 0.4, 0.5],
      "limit": 10
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
