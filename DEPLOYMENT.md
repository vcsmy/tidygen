# iNEAT ERP Community Edition - Deployment Guide

This guide covers deploying the iNEAT ERP Community Edition, a single-tenant ERP system designed for small to medium businesses.

## Architecture Overview

The community edition uses a simple, single-tenant architecture:

- **One PostgreSQL Database** - Stores all application data
- **One Redis Instance** (Optional) - For caching and background tasks
- **One Backend Service** - Django REST API
- **One Frontend Build** - React/Next.js application
- **One Nginx Instance** (Optional) - Reverse proxy and static file serving

## Prerequisites

- Docker and Docker Compose
- Git
- Basic knowledge of Linux/Unix commands

## Quick Start (Development)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/ineat-erp-community.git
   cd ineat-erp-community
   ```

2. **Set up environment variables:**
   ```bash
   cp apps/backend/env.example apps/backend/.env
   # Edit the .env file with your configuration
   ```

3. **Start the services:**
   ```bash
   docker-compose up -d
   ```

4. **Access the application:**
   - Backend API: http://localhost:8000
   - Admin Interface: http://localhost:8000/admin
   - API Documentation: http://localhost:8000/api/docs

5. **Default admin credentials:**
   - Username: `admin`
   - Password: `admin123`

## Production Deployment

### 1. Environment Setup

Create a production environment file:

```bash
cp apps/backend/env.example apps/backend/.env.prod
```

Update the production environment variables:

```env
# Django Configuration
DJANGO_ENV=production
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database Configuration
DATABASE_URL=postgresql://ineat_user:your-secure-password@db:5432/ineat_erp
POSTGRES_DB=ineat_erp
POSTGRES_USER=ineat_user
POSTGRES_PASSWORD=your-secure-password

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# CORS Configuration
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.your-provider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@yourdomain.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Security Settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
```

### 2. SSL Certificate Setup

For production, you'll need SSL certificates. Create the ssl directory and add your certificates:

```bash
mkdir ssl
# Copy your SSL certificates to:
# ssl/cert.pem (your SSL certificate)
# ssl/key.pem (your private key)
```

### 3. Deploy with Docker Compose

```bash
# Use the production docker-compose file
docker-compose -f docker-compose.prod.yml --env-file apps/backend/.env.prod up -d
```

### 4. Verify Deployment

Check that all services are running:

```bash
docker-compose -f docker-compose.prod.yml ps
```

Access your application:
- Backend API: https://yourdomain.com
- Admin Interface: https://yourdomain.com/admin

## Configuration Options

### Database Configuration

The system uses PostgreSQL as the primary database. Key configuration options:

- `DATABASE_URL`: Full database connection string
- `POSTGRES_DB`: Database name
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password

### Redis Configuration (Optional)

Redis is used for caching and background tasks. If you don't need these features, you can disable Redis by:

1. Removing the Redis service from docker-compose.yml
2. Updating the backend environment to use database sessions instead of Redis

### Web3 Configuration (Optional)

The system includes optional Web3 features for blockchain integration:

- `WEB3_ENABLED`: Set to `True` to enable Web3 features
- `WEB3_PROVIDER_URL`: Blockchain RPC endpoint
- `WEB3_NETWORK_ID`: Network ID (1 for Ethereum mainnet, 5 for Goerli testnet)

## Scaling Considerations

### Horizontal Scaling

For higher traffic, you can scale the backend service:

```bash
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

### Database Scaling

For high-traffic scenarios, consider:

1. **Read Replicas**: Set up PostgreSQL read replicas for read-heavy workloads
2. **Connection Pooling**: Use PgBouncer for connection pooling
3. **Database Optimization**: Tune PostgreSQL settings for your workload

### Caching Strategy

1. **Redis Caching**: Enable Redis for session storage and application caching
2. **CDN**: Use a CDN for static file delivery
3. **Application Caching**: Configure Django caching backends

## Monitoring and Maintenance

### Health Checks

The application includes health check endpoints:

- `/health/`: Basic health check
- `/api/v1/health/`: Detailed health information

### Logging

Logs are available in the following locations:

- Application logs: `docker logs ineat_erp_backend_prod`
- Nginx logs: `docker logs ineat_erp_nginx_prod`
- Database logs: `docker logs ineat_erp_db_prod`

### Backup Strategy

1. **Database Backups**: Set up regular PostgreSQL backups
2. **Media Files**: Backup the media volume
3. **Configuration**: Keep environment files secure and backed up

### Updates

To update the application:

1. Pull the latest changes: `git pull`
2. Rebuild the containers: `docker-compose -f docker-compose.prod.yml build`
3. Restart the services: `docker-compose -f docker-compose.prod.yml up -d`

## Security Considerations

### Production Security Checklist

- [ ] Change default admin password
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS with valid SSL certificates
- [ ] Configure proper CORS settings
- [ ] Set up firewall rules
- [ ] Regular security updates
- [ ] Database access restrictions
- [ ] Backup encryption

### Network Security

- Use Docker networks to isolate services
- Configure firewall rules
- Use reverse proxy (Nginx) for SSL termination
- Implement rate limiting

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Check database credentials
   - Verify database service is running
   - Check network connectivity

2. **Permission Issues**
   - Ensure proper file permissions
   - Check Docker volume mounts

3. **SSL Certificate Issues**
   - Verify certificate files exist
   - Check certificate validity
   - Ensure proper file permissions

### Debug Mode

For debugging, you can run in development mode:

```bash
docker-compose up -d
```

This will enable debug mode and console logging.

## Support

For community support:

- GitHub Issues: [Create an issue](https://github.com/your-org/ineat-erp-community/issues)
- Documentation: [Read the docs](https://docs.ineat-erp.com)
- Community Forum: [Join the discussion](https://community.ineat-erp.com)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
