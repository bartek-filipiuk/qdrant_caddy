# Domain and SSL Configuration Guide

This guide explains how to configure a custom domain name and SSL certificates for your Qdrant deployment using Caddy as a reverse proxy.

## Prerequisites

Before you begin, make sure you have:

- A registered domain name pointing to your server's IP address
- Root access to your server (for binding to ports 80/443)
- Docker and Docker Compose installed
- The Dockabase project properly set up

## Step 1: Configure Environment Variables

Edit the `.env` file in the root directory of your project and set the following variables:

```bash
# Domain configuration
DOMAIN=your-domain.com
ADMIN_EMAIL=your-email@example.com
```

Replace `your-domain.com` with your actual domain name and `your-email@example.com` with a valid email address that will be used for Let's Encrypt notifications.

## Step 2: Run the Domain Setup Script

Navigate to the scripts directory and run the setup-domain.sh script with root privileges:

```bash
cd /path/to/dockabase/scripts
sudo ./setup-domain.sh
```

The script will perform the following checks and actions:

1. Verify that the DOMAIN variable is set in the .env file
2. Check if ADMIN_EMAIL is set (and prompt you to enter it if not)
3. Verify that the script is running with root privileges
4. Check if ports 80 and 443 are available
5. Verify DNS configuration for your domain
6. Generate a password hash for Caddy authentication
7. Update the .env file with the generated password hash
8. Start the production environment with SSL enabled

## Step 3: Verify the Configuration

After the script completes, your Qdrant instance should be accessible at:

```
https://your-domain.com/dashboard
```

It may take a few minutes for Caddy to obtain SSL certificates from Let's Encrypt. You can check the progress by viewing the Caddy logs:

```bash
docker logs qdrant-caddy-1
```

## Step 4: Testing the Connection

To verify that your domain and SSL configuration is working correctly, you can use the following curl command:

```bash
curl -s -X GET -u admin:your_password -H "api-key: your_api_key" https://your-domain.com/collections
```

You should receive a JSON response with a list of collections.

## Troubleshooting

### SSL Certificate Issues

If Caddy cannot obtain an SSL certificate, check the following:

1. Make sure your domain correctly points to your server's IP address:
   ```bash
   host your-domain.com
   ```

2. Verify that ports 80 and 443 are open and not blocked by a firewall:
   ```bash
   sudo ufw status
   ```

3. Check the Caddy logs for specific errors:
   ```bash
   docker logs qdrant-caddy-1
   ```

### Common Issues

- **DNS propagation**: It may take up to 24-48 hours for DNS changes to propagate globally. If you've recently pointed your domain to your server, you might need to wait.

- **Port conflicts**: Make sure no other services (like Apache or Nginx) are running on ports 80 or 443.

- **Rate limiting**: Let's Encrypt has rate limits for certificate issuance. If you've requested too many certificates recently, you might need to wait before trying again.

## Advanced Configuration

### Custom Caddy Configuration

If you need to customize the Caddy configuration beyond what the setup script provides, you can edit the `Caddyfile` in the `caddy` directory:

```bash
nano /path/to/dockabase/caddy/Caddyfile
```

After making changes, restart the containers:

```bash
cd /path/to/dockabase
ENV=prod ./restart.sh
```

### Using a Different SSL Provider

By default, Caddy automatically obtains certificates from Let's Encrypt. If you want to use certificates from a different provider, you'll need to modify the Caddyfile and provide the certificate files manually.

## Security Best Practices

1. Regularly update your SSL certificates
2. Use strong passwords for authentication
3. Consider implementing additional security measures like IP restrictions or a VPN
4. Regularly check the Caddy and Qdrant logs for unauthorized access attempts

## Additional Resources

- [Caddy Documentation](https://caddyserver.com/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
