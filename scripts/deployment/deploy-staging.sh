#!/bin/bash

# TidyGen ERP Staging Deployment Script
# This script deploys the TidyGen ERP platform to the staging environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STAGING_ENV="staging"
DOCKER_COMPOSE_FILE="infra/docker/staging/docker-compose.yml"
BACKUP_DIR="/var/backups/tidygen"
LOG_FILE="/var/log/tidygen/deployment.log"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# Create log directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

# Check if running as root or with sudo
check_permissions() {
    if [ "$EUID" -ne 0 ]; then
        log_error "This script must be run as root or with sudo"
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking deployment prerequisites..."
    
    # Check Docker
    if ! command -v docker >/dev/null 2>&1; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose >/dev/null 2>&1; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if staging environment file exists
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        log_error "Staging Docker Compose file not found: $DOCKER_COMPOSE_FILE"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Backup current deployment
backup_current_deployment() {
    log_info "Creating backup of current deployment..."
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    
    # Backup database
    if docker-compose -f "$DOCKER_COMPOSE_FILE" ps | grep -q "db.*Up"; then
        log_info "Backing up database..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T db pg_dump -U postgres tidygen_erp > "$BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).sql"
        log_success "Database backup completed"
    else
        log_warning "Database container not running, skipping backup"
    fi
    
    # Backup application data
    log_info "Backing up application data..."
    tar -czf "$BACKUP_DIR/app_data_backup_$(date +%Y%m%d_%H%M%S).tar.gz" \
        -C apps/backend media/ \
        -C apps/backend static/ 2>/dev/null || true
    log_success "Application data backup completed"
}

# Pull latest images
pull_latest_images() {
    log_info "Pulling latest Docker images..."
    
    # Pull images
    docker-compose -f "$DOCKER_COMPOSE_FILE" pull
    
    log_success "Latest images pulled successfully"
}

# Build application images
build_images() {
    log_info "Building application images..."
    
    # Build backend image
    log_info "Building backend image..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" build backend
    
    # Build frontend image
    log_info "Building frontend image..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" build frontend
    
    log_success "Application images built successfully"
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    # Wait for database to be ready
    log_info "Waiting for database to be ready..."
    sleep 30
    
    # Run migrations
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec backend python manage.py migrate
    
    log_success "Database migrations completed"
}

# Deploy application
deploy_application() {
    log_info "Deploying application to staging..."
    
    # Stop current services
    log_info "Stopping current services..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" down
    
    # Start services with new images
    log_info "Starting services with new images..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    
    log_success "Application deployed successfully"
}

# Collect static files
collect_static_files() {
    log_info "Collecting static files..."
    
    # Wait for backend to be ready
    sleep 10
    
    # Collect static files
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec backend python manage.py collectstatic --noinput
    
    log_success "Static files collected successfully"
}

# Run health checks
run_health_checks() {
    log_info "Running health checks..."
    
    # Wait for services to be ready
    sleep 30
    
    # Check backend health
    log_info "Checking backend health..."
    if curl -f http://localhost:8000/health/ >/dev/null 2>&1; then
        log_success "Backend health check passed"
    else
        log_error "Backend health check failed"
        return 1
    fi
    
    # Check frontend health
    log_info "Checking frontend health..."
    if curl -f http://localhost:3000/ >/dev/null 2>&1; then
        log_success "Frontend health check passed"
    else
        log_error "Frontend health check failed"
        return 1
    fi
    
    # Check database connection
    log_info "Checking database connection..."
    if docker-compose -f "$DOCKER_COMPOSE_FILE" exec backend python manage.py check --database default >/dev/null 2>&1; then
        log_success "Database connection check passed"
    else
        log_error "Database connection check failed"
        return 1
    fi
    
    log_success "All health checks passed"
}

# Send deployment notification
send_notification() {
    local status=$1
    local message=$2
    
    log_info "Sending deployment notification..."
    
    # Send Slack notification (if webhook is configured)
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"TidyGen ERP Staging Deployment $status: $message\"}" \
            "$SLACK_WEBHOOK_URL" >/dev/null 2>&1 || true
    fi
    
    # Send email notification (if configured)
    if [ -n "$NOTIFICATION_EMAIL" ]; then
        echo "TidyGen ERP Staging Deployment $status: $message" | \
            mail -s "TidyGen ERP Deployment $status" "$NOTIFICATION_EMAIL" 2>/dev/null || true
    fi
    
    log_success "Notification sent"
}

# Rollback deployment
rollback_deployment() {
    log_error "Deployment failed, initiating rollback..."
    
    # Stop current services
    docker-compose -f "$DOCKER_COMPOSE_FILE" down
    
    # Restore from backup
    if [ -f "$BACKUP_DIR/db_backup_latest.sql" ]; then
        log_info "Restoring database from backup..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" up -d db
        sleep 30
        docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T db psql -U postgres -d tidygen_erp < "$BACKUP_DIR/db_backup_latest.sql"
    fi
    
    # Start previous version
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    
    log_warning "Rollback completed"
    send_notification "ROLLBACK" "Deployment failed and was rolled back"
}

# Cleanup old backups
cleanup_backups() {
    log_info "Cleaning up old backups..."
    
    # Keep only last 5 backups
    find "$BACKUP_DIR" -name "*.sql" -type f -mtime +5 -delete 2>/dev/null || true
    find "$BACKUP_DIR" -name "*.tar.gz" -type f -mtime +5 -delete 2>/dev/null || true
    
    log_success "Backup cleanup completed"
}

# Main deployment function
main() {
    log_info "Starting TidyGen ERP staging deployment..."
    
    # Set up error handling
    trap 'rollback_deployment; exit 1' ERR
    
    check_permissions
    check_prerequisites
    backup_current_deployment
    pull_latest_images
    build_images
    deploy_application
    run_migrations
    collect_static_files
    
    if run_health_checks; then
        log_success "Staging deployment completed successfully!"
        send_notification "SUCCESS" "Deployment completed successfully"
        cleanup_backups
    else
        log_error "Health checks failed"
        rollback_deployment
        exit 1
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-backup)
            SKIP_BACKUP=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --force)
            FORCE_DEPLOY=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --skip-backup    Skip backup creation"
            echo "  --skip-tests     Skip running tests"
            echo "  --force          Force deployment even if tests fail"
            echo "  -h, --help       Show this help message"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run main function
main "$@"
