# TidyGen Community Edition Setup Guide

## Overview

The TidyGen Community Edition is a free, open-source, self-hosted ERP solution optimized for Web3 Foundation grant requirements. This guide will help you set up and deploy your own instance.

## Features

### Core ERP Modules
- **Inventory Management**: Product catalog, stock tracking, suppliers
- **Finance Management**: Invoicing, payments, expense tracking
- **Human Resources**: Employee management, payroll, attendance
- **Analytics Dashboard**: Business intelligence and reporting

### Web3 Integration
- **Decentralized Identity (DID)**: Login with Web3 wallets
- **On-Chain Audit Logs**: Immutable audit trail on Substrate
- **IPFS File Storage**: Decentralized document storage
- **Blockchain Analytics**: Web3 transaction monitoring

## Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for development)
- Git
- 4GB RAM minimum
- 20GB disk space

## Quick Start with Docker

### 1. Clone the Repository

```bash
git clone https://github.com/vcsmy/tidygen.git
cd tidygen
```

### 2. Environment Configuration

Create a `.env` file in the root directory:

```env
# Database
POSTGRES_DB=tidygen
POSTGRES_USER=tidygen_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Web3 Configuration
SUBSTRATE_ENDPOINT=wss://rpc.polkadot.io
IPFS_GATEWAY=https://ipfs.io/ipfs/
ENABLE_WEB3_FEATURES=True

# Email (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 3. Start the Application

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 4. Initial Setup

```bash
# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Run migrations
docker-compose exec backend python manage.py migrate

# Collect static files
docker-compose exec backend python manage.py collectstatic --noinput

# Load sample data (optional)
docker-compose exec backend python manage.py loaddata fixtures/sample_data.json
```

## Manual Installation

### Backend Setup

```bash
# Navigate to backend
cd apps/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Database setup
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend Setup

```bash
# Navigate to frontend
cd apps/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Web3 Configuration

### 1. Substrate Node Connection

The application connects to a Substrate node for on-chain audit logs. Configure the endpoint in your environment:

```env
SUBSTRATE_ENDPOINT=wss://rpc.polkadot.io
# Or use a local node: ws://localhost:9944
```

### 2. IPFS Configuration

For decentralized file storage, configure IPFS:

```env
IPFS_GATEWAY=https://ipfs.io/ipfs/
# Or use a local IPFS node: http://localhost:8080/ipfs/
```

### 3. Web3 Wallet Integration

Supported wallets:
- **Polkadot.js**: Primary Web3 wallet
- **MetaMask**: Ethereum compatibility
- **Substrate Connect**: Light client connection

## Database Schema

### Core Tables

```sql
-- Tenants (Multi-tenant support)
CREATE TABLE tenants (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    plan VARCHAR(20) DEFAULT 'free',
    settings JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    tenant_id UUID REFERENCES tenants(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Audit Logs (On-chain)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(100) NOT NULL,
    metadata JSONB,
    block_hash VARCHAR(66),
    transaction_hash VARCHAR(66),
    on_chain BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## API Documentation

### Authentication Endpoints

```bash
# Login with traditional credentials
POST /api/v1/auth/login/
{
    "email": "user@example.com",
    "password": "password"
}

# Login with Web3 wallet
POST /api/v1/auth/web3-login/
{
    "did": "did:substrate:5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY",
    "signature": "0x...",
    "provider": "polkadot-js"
}
```

### Audit Log Endpoints

```bash
# Submit audit log to blockchain
POST /api/v1/audit/submit/
{
    "action": "user_login",
    "resource": "authentication",
    "metadata": {
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0..."
    }
}

# Get audit logs
GET /api/v1/audit/logs/?tenant_id=uuid&limit=100
```

## Security Considerations

### 1. Environment Variables

- Never commit `.env` files to version control
- Use strong, unique passwords
- Rotate secret keys regularly

### 2. Database Security

```bash
# Create dedicated database user
CREATE USER tidygen_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE tidygen TO tidygen_user;
```

### 3. Web3 Security

- Validate all Web3 signatures
- Implement rate limiting for API endpoints
- Use HTTPS in production
- Validate DID documents

## Production Deployment

### 1. Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. SSL Certificate

```bash
# Using Let's Encrypt
sudo certbot --nginx -d your-domain.com
```

### 3. Database Backup

```bash
# Create backup script
#!/bin/bash
pg_dump -h localhost -U tidygen_user tidygen > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
psql -h localhost -U tidygen_user tidygen < backup_file.sql
```

## Monitoring and Maintenance

### 1. Health Checks

```bash
# Check application health
curl http://localhost:8000/api/v1/health/

# Check database connection
docker-compose exec backend python manage.py check --database default
```

### 2. Log Monitoring

```bash
# View application logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Log rotation
sudo logrotate /etc/logrotate.d/tidygen
```

### 3. Performance Monitoring

- Monitor database performance
- Track API response times
- Monitor Web3 transaction success rates
- Set up alerts for system failures

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check if database is running
   docker-compose ps
   
   # Restart database
   docker-compose restart db
   ```

2. **Web3 Connection Issues**
   ```bash
   # Check Substrate endpoint
   curl -H "Content-Type: application/json" \
        -d '{"id":1, "jsonrpc":"2.0", "method": "system_health"}' \
        https://rpc.polkadot.io
   ```

3. **IPFS Upload Failures**
   ```bash
   # Test IPFS gateway
   curl https://ipfs.io/ipfs/QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG/readme
   ```

### Support

- **Documentation**: [GitHub Wiki](https://github.com/vcsmy/tidygen/wiki)
- **Issues**: [GitHub Issues](https://github.com/vcsmy/tidygen/issues)
- **Community**: [Discord Server](https://discord.gg/tidygen-community)
- **Email**: support@tidygen.io

## Contributing

We welcome contributions to the Community Edition:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt
npm install --dev

# Run tests
python manage.py test
npm test

# Code formatting
black .
prettier --write .
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Web3 Foundation for grant support
- Polkadot ecosystem for blockchain infrastructure
- IPFS for decentralized storage
- Open source community contributors

---

**Need Help?** Join our community Discord or open an issue on GitHub!
