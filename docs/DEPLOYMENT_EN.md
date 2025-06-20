# Qdrant - Production Deployment Guide

This document contains detailed instructions for deploying Qdrant in a production environment using Caddy as a reverse proxy with HTTPS support.

## Prerequisites

- Linux server
- Docker and Docker Compose installed
- Domain name pointing to the server's IP address
- Open ports 80 and 443 on the server (for HTTP and HTTPS)

## 1. Environment Preparation

### 1.1. Configuring the .env File

Edit the `.env` file and set the following variables:

```bash
ENV=prod
DOMAIN=your-domain.com
ADMIN_USER=admin
ADMIN_PASSWORD=strong_password
QDRANT_API_KEY=your_secret_api_key
```

Remember to:
- Replace `your-domain.com` with your actual domain
- Set a strong password for the administrator user
- Generate a secure API key for Qdrant

### 1.2. Checking DNS Configuration

Make sure your domain points to the server's IP address. You can check this using the command:

```bash
host your-domain.com
```

The result should include your server's IP address.

## 2. Deployment

### 2.1. Running the Domain Configuration Script

Navigate to the scripts directory and run the domain configuration script:

```bash
cd /path/to/qdrant/scripts
sudo ./setup-domain.sh
```

The script will perform the following actions:
- Check if the DOMAIN variable is set
- Check if the script is running with root privileges
- Check if ports 80 and 443 are available
- Check DNS configuration
- Generate a password hash for Caddy
- Update the .env file with the generated hash
- Launch the production environment

### 2.2. Verifying the Deployment

After the script completes, Qdrant should be accessible at:

```
https://your-domain.com/dashboard
```

Caddy will automatically obtain an SSL certificate from Let's Encrypt, which may take a few minutes.

## 3. Testing the API

To check if the Qdrant API is working correctly, execute the following query:

```bash
curl -s -X GET -u admin:strong_password -H "api-key: your_secret_api_key" https://your-domain.com/collections
```

You should receive a JSON response with a list of collections.

## 4. Troubleshooting

### 4.1. Checking Logs

If you encounter problems, check the container logs:

```bash
# Caddy logs
docker logs qdrant-caddy-1

# Qdrant logs
docker logs qdrant-qdrant-1
```

### 4.2. SSL Certificate Issues

If Caddy cannot obtain an SSL certificate, make sure that:
- The domain correctly points to the server's IP address
- Ports 80 and 443 are open and available
- There are no other services using these ports

### 4.3. Authentication Problems

If you have login problems:
- Check if you're using the correct password and API key
- Make sure the ADMIN_PASSWORD and QDRANT_API_KEY variables in the .env file are correct
- Check if the password hash was generated correctly

## 5. Backups

### 5.1. Creating a Backup

To create a backup of Qdrant data, use the script:

```bash
cd /path/to/qdrant/scripts
./backup.sh
```

The backup will be saved in the `backups` directory.

### 5.2. Restoring from a Backup

To restore data from a backup, use the script:

```bash
cd /path/to/qdrant/scripts
./restore.sh backup_filename
```

## 6. Updating

To update Qdrant to the latest version:

1. Stop the containers:
   ```bash
   cd /path/to/qdrant
   ./stop.sh
   ```

2. Edit the `docker-compose.prod.yml` file and change the Qdrant image version (optional)

3. Restart the environment:
   ```bash
   ENV=prod ./restart.sh
   ```

## 7. Security

- Regularly change the administrator password and API key
- Monitor logs for unauthorized access attempts
- Consider additional network-level security measures (firewall, VPN)
- Perform regular data backups

## 8. Additional Resources

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Caddy Documentation](https://caddyserver.com/docs/)
- [Let's Encrypt](https://letsencrypt.org/docs/)
