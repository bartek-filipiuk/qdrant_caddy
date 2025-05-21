## Recommendations for Adding Resource Limits to `docker-compose.prod.yml`

Setting resource limits (CPU and memory) for your Docker containers in a production environment is a crucial practice for several reasons:

**1. Preventing Resource Starvation:**
   - If one container consumes an excessive amount of CPU or memory, other containers on the same host might be starved of resources. This can lead to performance degradation or even crashes for those other services.
   - Resource limits ensure that each container gets its fair share and prevents a single misbehaving or unexpectedly high-load container from impacting the entire system.

**2. Ensuring Stability and Predictability:**
   - By defining limits, you create a more predictable environment. You have a clearer understanding of how much resource each service is expected to use.
   - This helps in capacity planning and prevents situations where a sudden spike in resource usage by one container brings down the entire host or critical services.
   - It also helps in preventing Out Of Memory (OOM) errors for containers, which can lead to abrupt termination.

**3. Enhancing Security (Indirectly):**
   - While not a direct security feature, resource limits can mitigate the impact of certain types of attacks, like denial-of-service (DoS) attacks that might try to exhaust resources.

**Example of How to Add Resource Limits:**

You can add resource limits to your services within the `docker-compose.prod.yml` file using the `deploy` key. This key is typically used for Docker Swarm deployments, but Docker Compose can also interpret it for setting resource constraints when deploying with `docker-compose up` (though it might be more strictly enforced in a Swarm environment).

Here's an example for the `qdrant` service:

```yaml
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:v1.14.0
    expose:
      - "6333"
    environment:
      - QDRANT__SERVICE__API_KEY=${QDRANT_API_KEY}
      - QDRANT__SERVICE__HTTP_ALLOW_ORIGIN="*"
    volumes:
      - prod_qdrant_storage:/qdrant/storage
    networks:
      - qdrant_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    deploy: # <--- Add this section
      resources:
        limits:
          cpus: '0.75'  # Limits the container to use at most 75% of one CPU core
          memory: '2G'   # Limits the container to use at most 2 Gigabytes of RAM
        reservations:
          cpus: '0.50'  # Guarantees the container at least 50% of one CPU core
          memory: '1G'   # Guarantees the container at least 1 Gigabyte of RAM

  caddy:
    image: caddy:2.10.0-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/Caddyfile.prod:/etc/caddy/Caddyfile
      - caddy_data:/data
      - caddy_config:/config
    depends_on:
      - qdrant
    networks:
      - qdrant_network
    environment:
      - ADMIN_USER=${ADMIN_USER}
      - ADMIN_PASSWORD_HASH=${ADMIN_PASSWORD_HASH}
      - QDRANT_API_KEY=${QDRANT_API_KEY}
      - DOMAIN=${DOMAIN}
      - ADMIN_EMAIL=${ADMIN_EMAIL}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    deploy: # <--- Add this section for Caddy as well
      resources:
        limits:
          cpus: '0.50' # Example: Caddy might need less CPU
          memory: '512M' # Example: Caddy might need less RAM
        reservations:
          cpus: '0.25'
          memory: '256M'

networks:
  qdrant_network:
    driver: bridge

volumes:
  prod_qdrant_storage:
  caddy_data:
  caddy_config:
```

**Explanation of `limits` and `reservations`:**

-   **`limits`**: This is the hard cap on the resources a container can use.
    -   `cpus`: Specifies how much of the available CPU resources a container can use. `'0.50'` means 50% of one CPU core. `'1.0'` means 1 full CPU core.
    -   `memory`: The maximum amount of RAM the container can use.
-   **`reservations`**: This is the amount of resources guaranteed to be available to the container.
    -   This is a soft guarantee. If the system has spare resources, containers can use more than their reservation (up to their limit).
    -   It helps the Docker scheduler make better decisions about placing containers on nodes (in a Swarm context) or managing resources.

**Important Considerations:**

*   **These Values are Examples:** The CPU and memory values shown above (`cpus: '0.75'`, `memory: '2G'` for Qdrant, and `cpus: '0.50'`, `memory: '512M'` for Caddy) are **placeholders and examples only**.
*   **Monitor Your Application:** The ideal values depend heavily on:
    *   The specific workload of your Qdrant instance (number of collections, size of vectors, query rate).
    *   The traffic handled by Caddy.
    *   The total resources available on your production host machine.
*   **Adjust Based on Needs:** You **must** monitor your application's performance and resource consumption in your production environment and adjust these limits and reservations accordingly. Start with conservative estimates, monitor, and then fine-tune.
*   **Test Thoroughly:** After applying resource limits, thoroughly test your application under load to ensure it performs as expected and that the limits are not too restrictive, causing performance bottlenecks or crashes.

By implementing resource limits, you contribute significantly to the stability and reliability of your production deployment. Remember to tailor these settings to your specific operational context.
