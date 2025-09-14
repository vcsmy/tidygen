# Deployment Guide

## 🚀 **Deployment Overview**

This guide covers deploying the TidyGen ERP system to various environments, from development to production. The system supports multiple deployment strategies including Docker, cloud platforms, and traditional server deployments.

## 🐳 **Docker Deployment**

### **Development Environment**
```bash
# Start development environment
make dev

# Or manually
docker-compose up -d
```

### **Production Environment**
```bash
# Start production environment
make prod

# Or manually
docker-compose -f docker-compose.prod.yml up -d
```

### **Environment Variables**
Create environment files for different deployments:

```bash
# Development
cp env.example .env

# Production
cp env.example .env.prod
```

## ☁️ **Cloud Deployment**

### **AWS Deployment**

#### **Using AWS ECS**
```yaml
# aws-ecs-deployment.yml
version: '3.8'
services:
  backend:
    image: your-registry/tidygen-backend:latest
    environment:
      - DJANGO_ENV=production
      - DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/tidygen_erp
      - REDIS_URL=redis://elasticache-endpoint:6379/1
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis

  frontend:
    image: your-registry/tidygen-frontend:latest
    environment:
      - VITE_API_URL=https://api.yourdomain.com
    ports:
      - "3000:3000"
    depends_on:
      - backend

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=tidygen_erp
      - POSTGRES_USER=tidygen_user
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass secure_password
    volumes:
      - redis_data:/data
```

#### **Using AWS EKS (Kubernetes)**
```yaml
# k8s-deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tidygen-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tidygen-backend
  template:
    metadata:
      labels:
        app: tidygen-backend
    spec:
      containers:
      - name: backend
        image: your-registry/tidygen-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DJANGO_ENV
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: tidygen-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: tidygen-secrets
              key: redis-url
---
apiVersion: v1
kind: Service
metadata:
  name: tidygen-backend-service
spec:
  selector:
    app: tidygen-backend
  ports:
  - port: 8000
    targetPort: 8000
  type: LoadBalancer
```

### **Google Cloud Platform**

#### **Using Cloud Run**
```yaml
# cloud-run-deployment.yml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: tidygen-backend
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/execution-environment: gen2
    spec:
      containerConcurrency: 100
      containers:
      - image: gcr.io/your-project/tidygen-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DJANGO_ENV
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: tidygen-secrets
              key: database-url
        resources:
          limits:
            cpu: "2"
            memory: "4Gi"
```

### **Azure Deployment**

#### **Using Azure Container Instances**
```yaml
# azure-container-instances.yml
apiVersion: 2018-10-01
location: eastus
name: tidygen-backend
properties:
  containers:
  - name: backend
    properties:
      image: your-registry.azurecr.io/tidygen-backend:latest
      ports:
      - port: 8000
      environmentVariables:
      - name: DJANGO_ENV
        value: "production"
      - name: DATABASE_URL
        secureValue: "postgresql://user:pass@server:5432/tidygen_erp"
      resources:
        requests:
          cpu: 2
          memoryInGb: 4
  osType: Linux
  restartPolicy: Always
  ipAddress:
    type: Public
    ports:
    - protocol: tcp
      port: 8000
```

## 🏗️ **Traditional Server Deployment**

### **Ubuntu/Debian Server Setup**

#### **1. System Preparation**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.11 python3.11-venv python3.11-dev
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y redis-server nginx
sudo apt install -y git curl

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

#### **2. Database Setup**
```bash
# Create PostgreSQL database
sudo -u postgres psql
CREATE DATABASE tidygen_erp;
CREATE USER tidygen_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE tidygen_erp TO tidygen_user;
\q
```

#### **3. Application Deployment**
```bash
# Clone repository
git clone https://github.com/your-org/tidygen.git
cd tidygen

# Backend setup
cd apps/backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Environment configuration
cp env.example .env
# Edit .env with production values

# Database migrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

# Frontend setup
cd ../frontend
npm install
npm run build
```

#### **4. Process Management with Systemd**
```ini
# /etc/systemd/system/tidygen-backend.service
[Unit]
Description=TidyGen ERP Backend
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/opt/tidygen/apps/backend
Environment=PATH=/opt/tidygen/apps/backend/venv/bin
ExecStart=/opt/tidygen/apps/backend/venv/bin/gunicorn tidygen_erp.wsgi:application --bind 127.0.0.1:8000
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/tidygen-celery.service
[Unit]
Description=TidyGen ERP Celery Worker
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/opt/tidygen/apps/backend
Environment=PATH=/opt/tidygen/apps/backend/venv/bin
ExecStart=/opt/tidygen/apps/backend/venv/bin/celery -A tidygen_erp worker --loglevel=info
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

#### **5. Nginx Configuration**
```nginx
# /etc/nginx/sites-available/tidygen
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Frontend
    location / {
        root /opt/tidygen/apps/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        alias /opt/tidygen/apps/backend/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /opt/tidygen/apps/backend/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
}
```

## 🔒 **SSL/TLS Configuration**

### **Let's Encrypt with Certbot**
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### **Custom SSL Certificate**
```bash
# Place certificate files
sudo cp your-certificate.crt /etc/ssl/certs/
sudo cp your-private-key.key /etc/ssl/private/
sudo chmod 600 /etc/ssl/private/your-private-key.key

# Update Nginx configuration
# Use the certificate paths in ssl_certificate and ssl_certificate_key
```

## 📊 **Monitoring and Logging**

### **Application Monitoring**
```python
# apps/backend/tidygen_erp/settings/production.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Sentry configuration
sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=True
)

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/tidygen/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### **System Monitoring with Prometheus**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'tidygen-backend'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'tidygen-frontend'
    static_configs:
      - targets: ['localhost:3000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:9121']
```

### **Log Management**
```bash
# Logrotate configuration
# /etc/logrotate.d/tidygen
/var/log/tidygen/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload tidygen-backend
    endscript
}
```

## 🔄 **CI/CD Pipeline**

### **GitHub Actions**
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: make test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to server
        uses: appleboy/ssh-action@v0.1.5
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /opt/tidygen
            git pull origin main
            cd apps/backend
            source venv/bin/activate
            pip install -r requirements.txt
            python manage.py migrate
            python manage.py collectstatic --noinput
            systemctl restart tidygen-backend
            systemctl restart tidygen-celery
            cd ../frontend
            npm install
            npm run build
            systemctl reload nginx
```

### **Docker Registry**
```bash
# Build and push images
docker build -t your-registry/tidygen-backend:latest apps/backend/
docker build -t your-registry/tidygen-frontend:latest apps/frontend/

docker push your-registry/tidygen-backend:latest
docker push your-registry/tidygen-frontend:latest
```

## 🗄️ **Database Management**

### **Backup Strategy**
```bash
#!/bin/bash
# backup-database.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"
DB_NAME="tidygen_erp"

# Create backup
pg_dump -h localhost -U tidygen_user $DB_NAME > $BACKUP_DIR/tidygen_erp_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/tidygen_erp_$DATE.sql

# Remove backups older than 30 days
find $BACKUP_DIR -name "tidygen_erp_*.sql.gz" -mtime +30 -delete

# Upload to cloud storage (optional)
aws s3 cp $BACKUP_DIR/tidygen_erp_$DATE.sql.gz s3://your-backup-bucket/
```

### **Database Migration**
```bash
# Production migration
cd apps/backend
source venv/bin/activate

# Backup before migration
pg_dump -h localhost -U tidygen_user tidygen_erp > backup_before_migration.sql

# Run migrations
python manage.py migrate

# Verify migration
python manage.py showmigrations
```

## 🔧 **Performance Optimization**

### **Database Optimization**
```python
# apps/backend/tidygen_erp/settings/production.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tidygen_erp',
        'USER': 'tidygen_user',
        'PASSWORD': 'secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'MAX_CONNS': 20,
            'CONN_MAX_AGE': 600,
        },
    }
}

# Redis caching
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### **Frontend Optimization**
```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu'],
        },
      },
    },
  },
})
```

## 🚨 **Security Hardening**

### **Django Security**
```python
# apps/backend/tidygen_erp/settings/production.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000
SECURE_REDIRECT_EXEMPT = []
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

# Allowed hosts
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]
```

### **Server Security**
```bash
# Firewall configuration
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw deny 8000

# Fail2ban for SSH protection
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## 📋 **Deployment Checklist**

### **Pre-deployment**
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database migrations ready
- [ ] SSL certificates obtained
- [ ] Domain DNS configured
- [ ] Backup strategy in place

### **Deployment**
- [ ] Code deployed to server
- [ ] Dependencies installed
- [ ] Database migrations run
- [ ] Static files collected
- [ ] Services started
- [ ] Nginx configured and reloaded

### **Post-deployment**
- [ ] Application accessible
- [ ] SSL certificate working
- [ ] Database connections working
- [ ] Monitoring configured
- [ ] Logs being generated
- [ ] Backup job scheduled
- [ ] Performance monitoring active

## 🔄 **Rollback Strategy**

### **Quick Rollback**
```bash
# Rollback to previous version
cd /opt/tidygen
git checkout previous-commit-hash
cd apps/backend
source venv/bin/activate
python manage.py migrate previous-commit-hash
systemctl restart tidygen-backend
systemctl restart tidygen-celery
```

### **Database Rollback**
```bash
# Restore from backup
pg_restore -h localhost -U tidygen_user -d tidygen_erp backup_before_migration.sql
```

## 📞 **Troubleshooting**

### **Common Issues**
1. **Database connection errors** - Check credentials and network
2. **Static files not loading** - Verify Nginx configuration
3. **SSL certificate issues** - Check certificate validity
4. **Performance issues** - Monitor database and application logs
5. **Memory issues** - Check system resources and optimize

### **Log Locations**
- Application logs: `/var/log/tidygen/`
- Nginx logs: `/var/log/nginx/`
- System logs: `/var/log/syslog`
- Database logs: `/var/log/postgresql/`
