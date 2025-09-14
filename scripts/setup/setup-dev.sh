#!/bin/bash

# TidyGen ERP Development Environment Setup Script
# This script sets up the development environment for the TidyGen ERP platform

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Node.js
    if ! command_exists node; then
        log_error "Node.js is not installed. Please install Node.js 18+ from https://nodejs.org/"
        exit 1
    fi
    
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 18 ]; then
        log_error "Node.js version 18+ is required. Current version: $(node --version)"
        exit 1
    fi
    
    # Check Python
    if ! command_exists python3; then
        log_error "Python 3 is not installed. Please install Python 3.11+ from https://python.org/"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [ "$(echo "$PYTHON_VERSION < 3.11" | bc -l)" -eq 1 ]; then
        log_error "Python 3.11+ is required. Current version: $(python3 --version)"
        exit 1
    fi
    
    # Check Docker
    if ! command_exists docker; then
        log_error "Docker is not installed. Please install Docker from https://docker.com/"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command_exists docker-compose; then
        log_error "Docker Compose is not installed. Please install Docker Compose from https://docker.com/"
        exit 1
    fi
    
    log_success "All prerequisites are satisfied"
}

# Install dependencies
install_dependencies() {
    log_info "Installing dependencies..."
    
    # Install Node.js dependencies
    if command_exists pnpm; then
        log_info "Installing Node.js dependencies with pnpm..."
        pnpm install
    else
        log_info "Installing Node.js dependencies with npm..."
        npm install
    fi
    
    # Install Python dependencies
    log_info "Installing Python dependencies..."
    cd apps/backend
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements-dev.txt
    cd ../..
    
    log_success "Dependencies installed successfully"
}

# Setup environment variables
setup_environment() {
    log_info "Setting up environment variables..."
    
    # Create .env files if they don't exist
    if [ ! -f .env.local ]; then
        log_info "Creating .env.local file..."
        cat > .env.local << EOF
# Development Environment Variables
NODE_ENV=development
DEBUG=true

# Database Configuration
POSTGRES_DB=tidygen_erp_dev
POSTGRES_USER=tidygen_user
POSTGRES_PASSWORD=tidygen_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Django Configuration
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Frontend Configuration
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000

# Web3 Configuration
WEB3_PROVIDER_URL=https://goerli.infura.io/v3/YOUR_INFURA_KEY
WEB3_PRIVATE_KEY=your_private_key_for_development
EOF
        log_success ".env.local file created"
    else
        log_warning ".env.local file already exists"
    fi
    
    # Create backend .env file
    if [ ! -f apps/backend/.env ]; then
        log_info "Creating backend .env file..."
        cp .env.local apps/backend/.env
        log_success "Backend .env file created"
    fi
    
    # Create frontend .env file
    if [ ! -f apps/frontend/.env ]; then
        log_info "Creating frontend .env file..."
        cp .env.local apps/frontend/.env
        log_success "Frontend .env file created"
    fi
}

# Setup database
setup_database() {
    log_info "Setting up database..."
    
    # Start database services
    log_info "Starting database services with Docker..."
    docker-compose -f infra/docker/development/docker-compose.yml up -d db redis
    
    # Wait for database to be ready
    log_info "Waiting for database to be ready..."
    sleep 10
    
    # Run migrations
    log_info "Running database migrations..."
    cd apps/backend
    source venv/bin/activate
    python manage.py migrate
    cd ../..
    
    log_success "Database setup completed"
}

# Setup development tools
setup_dev_tools() {
    log_info "Setting up development tools..."
    
    # Install pre-commit hooks
    if command_exists pre-commit; then
        log_info "Installing pre-commit hooks..."
        pre-commit install
        log_success "Pre-commit hooks installed"
    else
        log_warning "pre-commit not found. Install with: pip install pre-commit"
    fi
    
    # Setup Git hooks
    if [ -d .git ]; then
        log_info "Setting up Git hooks..."
        chmod +x .git/hooks/*
        log_success "Git hooks configured"
    fi
}

# Run initial tests
run_tests() {
    log_info "Running initial tests..."
    
    # Run backend tests
    log_info "Running backend tests..."
    cd apps/backend
    source venv/bin/activate
    python manage.py test --verbosity=2
    cd ../..
    
    # Run frontend tests
    log_info "Running frontend tests..."
    cd apps/frontend
    npm test -- --watchAll=false
    cd ../..
    
    log_success "All tests passed"
}

# Main setup function
main() {
    log_info "Starting TidyGen ERP development environment setup..."
    
    check_prerequisites
    install_dependencies
    setup_environment
    setup_database
    setup_dev_tools
    run_tests
    
    log_success "Development environment setup completed successfully!"
    log_info "Next steps:"
    echo "  1. Start the development environment: npm run dev"
    echo "  2. Access the application: http://localhost:3000"
    echo "  3. Access the API: http://localhost:8000"
    echo "  4. Access the admin panel: http://localhost:8000/admin"
    echo "  5. Create a superuser: npm run superuser"
}

# Run main function
main "$@"
