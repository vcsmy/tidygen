#!/bin/bash

# TidyGen Community Edition Installer
# Self-hosted setup script for Community Edition deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="tidygen"
DOMAIN=""
EMAIL=""
ADMIN_USER=""
ADMIN_EMAIL=""
ADMIN_PASSWORD=""
DATABASE_PASSWORD=""
SECRET_KEY=""
ENABLE_WEB3="true"
SUBSTRATE_ENDPOINT="wss://rpc.polkadot.io"
IPFS_GATEWAY="https://ipfs.io/ipfs/"

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    TidyGen Installer                       ║"
    echo "║              Community Edition - Self-Hosted                ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check system requirements
check_requirements() {
    print_step "Checking system requirements..."
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        print_warning "Running as root. Consider using a non-root user for security."
    fi
    
    # Check OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_info "Linux detected"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        print_info "macOS detected"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    
    # Check available memory
    if command_exists free; then
        MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
        if [ "$MEMORY_GB" -lt 2 ]; then
            print_warning "Less than 2GB RAM detected. TidyGen requires at least 2GB."
        fi
    fi
    
    # Check available disk space
    DISK_SPACE=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$DISK_SPACE" -lt 10 ]; then
        print_warning "Less than 10GB disk space available. TidyGen requires at least 10GB."
    fi
}

# Install Docker and Docker Compose
install_docker() {
    print_step "Installing Docker and Docker Compose..."
    
    if command_exists docker && command_exists docker-compose; then
        print_info "Docker and Docker Compose already installed"
        return
    fi
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Update package index
        sudo apt-get update
        
        # Install prerequisites
        sudo apt-get install -y \
            apt-transport-https \
            ca-certificates \
            curl \
            gnupg \
            lsb-release
        
        # Add Docker's official GPG key
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        
        # Set up stable repository
        echo \
            "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
            $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # Install Docker Engine
        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io
        
        # Install Docker Compose
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        
        # Add current user to docker group
        sudo usermod -aG docker $USER
        
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        print_info "Please install Docker Desktop for macOS from https://www.docker.com/products/docker-desktop"
        print_info "After installation, run this script again."
        exit 1
    fi
    
    print_success "Docker and Docker Compose installed successfully"
}

# Get user input
get_user_input() {
    print_step "Gathering configuration information..."
    
    # Domain
    read -p "Enter your domain (e.g., erp.yourcompany.com) or press Enter for localhost: " DOMAIN
    if [ -z "$DOMAIN" ]; then
        DOMAIN="localhost"
    fi
    
    # Email for SSL certificates
    read -p "Enter your email address (for SSL certificates): " EMAIL
    
    # Admin user details
    read -p "Enter admin username (default: admin): " ADMIN_USER
    if [ -z "$ADMIN_USER" ]; then
        ADMIN_USER="admin"
    fi
    
    read -p "Enter admin email: " ADMIN_EMAIL
    
    # Generate secure passwords
    ADMIN_PASSWORD=$(openssl rand -base64 32)
    DATABASE_PASSWORD=$(openssl rand -base64 32)
    SECRET_KEY=$(openssl rand -base64 50)
    
    print_info "Generated secure passwords for admin and database"
    
    # Web3 features
    read -p "Enable Web3 features? (y/n, default: y): " ENABLE_WEB3_INPUT
    if [[ "$ENABLE_WEB3_INPUT" =~ ^[Nn]$ ]]; then
        ENABLE_WEB3="false"
    fi
    
    if [ "$ENABLE_WEB3" = "true" ]; then
        read -p "Enter Substrate endpoint (default: wss://rpc.polkadot.io): " SUBSTRATE_INPUT
        if [ -n "$SUBSTRATE_INPUT" ]; then
            SUBSTRATE_ENDPOINT="$SUBSTRATE_INPUT"
        fi
        
        read -p "Enter IPFS gateway (default: https://ipfs.io/ipfs/): " IPFS_INPUT
        if [ -n "$IPFS_INPUT" ]; then
            IPFS_GATEWAY="$IPFS_INPUT"
        fi
    fi
}

# Create project directory
create_project() {
    print_step "Creating project directory..."
    
    if [ -d "$PROJECT_NAME" ]; then
        print_warning "Directory $PROJECT_NAME already exists"
        read -p "Do you want to remove it and continue? (y/n): " REMOVE_EXISTING
        if [[ "$REMOVE_EXISTING" =~ ^[Yy]$ ]]; then
            rm -rf "$PROJECT_NAME"
        else
            print_error "Installation cancelled"
            exit 1
        fi
    fi
    
    mkdir -p "$PROJECT_NAME"
    cd "$PROJECT_NAME"
    
    print_success "Project directory created: $(pwd)"
}

# Download and setup application
setup_application() {
    print_step "Setting up TidyGen application..."
    
    # Clone repository
    print_info "Downloading TidyGen..."
    git clone https://github.com/vcsmy/tidygen.git .
    
    # Create environment file
    print_info "Creating environment configuration..."
    cat > .env << EOF
# Database Configuration
POSTGRES_DB=tidygen
POSTGRES_USER=tidygen_user
POSTGRES_PASSWORD=$DATABASE_PASSWORD
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Django Configuration
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=$DOMAIN,localhost,127.0.0.1

# Admin Configuration
ADMIN_USERNAME=$ADMIN_USER
ADMIN_EMAIL=$ADMIN_EMAIL
ADMIN_PASSWORD=$ADMIN_PASSWORD

# Web3 Configuration
ENABLE_WEB3_FEATURES=$ENABLE_WEB3
SUBSTRATE_ENDPOINT=$SUBSTRATE_ENDPOINT
IPFS_GATEWAY=$IPFS_GATEWAY

# Email Configuration (Optional)
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# SSL Configuration
DOMAIN=$DOMAIN
SSL_EMAIL=$EMAIL
EOF

    print_success "Environment configuration created"
}

# Setup SSL with Let's Encrypt
setup_ssl() {
    if [ "$DOMAIN" != "localhost" ]; then
        print_step "Setting up SSL certificate with Let's Encrypt..."
        
        # Create nginx configuration
        cat > nginx.conf << EOF
server {
    listen 80;
    server_name $DOMAIN;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name $DOMAIN;
    
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

        # Add SSL setup to docker-compose
        cat >> docker-compose.override.yml << EOF
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - certbot-www:/var/www/certbot
      - certbot-conf:/etc/letsencrypt
    depends_on:
      - frontend
      - backend

  certbot:
    image: certbot/certbot
    volumes:
      - certbot-www:/var/www/certbot
      - certbot-conf:/etc/letsencrypt
    command: certonly --webroot --webroot-path=/var/www/certbot --email $EMAIL --agree-tos --no-eff-email -d $DOMAIN

volumes:
  certbot-www:
  certbot-conf:
EOF

        print_info "SSL configuration added. Certificate will be obtained after first startup."
    fi
}

# Start services
start_services() {
    print_step "Starting TidyGen services..."
    
    # Start services
    docker-compose up -d
    
    # Wait for services to be ready
    print_info "Waiting for services to start..."
    sleep 30
    
    # Run database migrations
    print_info "Running database migrations..."
    docker-compose exec -T backend python manage.py migrate
    
    # Create superuser
    print_info "Creating admin user..."
    docker-compose exec -T backend python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$ADMIN_USER').exists():
    User.objects.create_superuser('$ADMIN_USER', '$ADMIN_EMAIL', '$ADMIN_PASSWORD')
    print('Admin user created successfully')
else:
    print('Admin user already exists')
EOF
    
    # Collect static files
    print_info "Collecting static files..."
    docker-compose exec -T backend python manage.py collectstatic --noinput
    
    # Load sample data (optional)
    read -p "Load sample data for testing? (y/n): " LOAD_SAMPLE
    if [[ "$LOAD_SAMPLE" =~ ^[Yy]$ ]]; then
        print_info "Loading sample data..."
        docker-compose exec -T backend python manage.py loaddata fixtures/sample_data.json
    fi
    
    print_success "Services started successfully"
}

# Setup monitoring and maintenance
setup_monitoring() {
    print_step "Setting up monitoring and maintenance..."
    
    # Create backup script
    cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec -T db pg_dump -U tidygen_user tidygen > $BACKUP_DIR/database_$DATE.sql

# Backup uploaded files
tar -czf $BACKUP_DIR/files_$DATE.tar.gz -C apps/backend media/

echo "Backup completed: $BACKUP_DIR/database_$DATE.sql and $BACKUP_DIR/files_$DATE.tar.gz"
EOF

    chmod +x backup.sh
    
    # Create update script
    cat > update.sh << 'EOF'
#!/bin/bash
echo "Updating TidyGen..."

# Pull latest changes
git pull origin main

# Rebuild and restart services
docker-compose down
docker-compose build
docker-compose up -d

# Run migrations
docker-compose exec -T backend python manage.py migrate

# Collect static files
docker-compose exec -T backend python manage.py collectstatic --noinput

echo "Update completed successfully"
EOF

    chmod +x update.sh
    
    print_success "Monitoring and maintenance scripts created"
}

# Display final information
show_completion_info() {
    print_step "Installation completed successfully!"
    
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    Installation Complete                     ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo -e "${BLUE}Access Information:${NC}"
    if [ "$DOMAIN" = "localhost" ]; then
        echo "  URL: http://localhost"
    else
        echo "  URL: https://$DOMAIN"
    fi
    echo "  Admin Username: $ADMIN_USER"
    echo "  Admin Email: $ADMIN_EMAIL"
    echo "  Admin Password: $ADMIN_PASSWORD"
    echo ""
    
    echo -e "${BLUE}Important Files:${NC}"
    echo "  Environment: .env"
    echo "  Docker Compose: docker-compose.yml"
    echo "  Backup Script: backup.sh"
    echo "  Update Script: update.sh"
    echo ""
    
    echo -e "${BLUE}Useful Commands:${NC}"
    echo "  View logs: docker-compose logs -f"
    echo "  Stop services: docker-compose down"
    echo "  Start services: docker-compose up -d"
    echo "  Create backup: ./backup.sh"
    echo "  Update system: ./update.sh"
    echo ""
    
    if [ "$ENABLE_WEB3" = "true" ]; then
        echo -e "${BLUE}Web3 Features Enabled:${NC}"
        echo "  Substrate Endpoint: $SUBSTRATE_ENDPOINT"
        echo "  IPFS Gateway: $IPFS_GATEWAY"
        echo "  On-chain audit logs: Enabled"
        echo "  Decentralized file storage: Enabled"
        echo ""
    fi
    
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Save the admin credentials securely"
    echo "2. Access the application and complete initial setup"
    echo "3. Configure your business settings"
    echo "4. Set up regular backups"
    echo "5. Join our community for support: https://discord.gg/tidygen-community"
    echo ""
    
    echo -e "${GREEN}Thank you for choosing TidyGen!${NC}"
}

# Main installation process
main() {
    print_header
    
    # Check if running interactively
    if [ ! -t 0 ]; then
        print_error "This script must be run interactively"
        exit 1
    fi
    
    # Check requirements
    check_requirements
    
    # Install Docker if needed
    install_docker
    
    # Get user input
    get_user_input
    
    # Create project
    create_project
    
    # Setup application
    setup_application
    
    # Setup SSL if domain provided
    setup_ssl
    
    # Start services
    start_services
    
    # Setup monitoring
    setup_monitoring
    
    # Show completion info
    show_completion_info
}

# Run main function
main "$@"
