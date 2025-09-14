# iNeat ERP Community Edition - Makefile
# Common commands for development and deployment

.PHONY: help setup start stop restart logs clean deploy-vercel deploy-render deploy-digitalocean

# Default target
help:
	@echo "🚀 iNeat ERP Community Edition - Available Commands"
	@echo "=================================================="
	@echo ""
	@echo "📦 Setup & Installation:"
	@echo "  setup          - Quick setup with Docker"
	@echo "  start          - Start all services"
	@echo "  stop           - Stop all services"
	@echo "  restart        - Restart all services"
	@echo ""
	@echo "🔍 Monitoring:"
	@echo "  logs           - View all logs"
	@echo "  logs-backend   - View backend logs"
	@echo "  logs-db        - View database logs"
	@echo "  status         - Show service status"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  clean          - Clean up containers and volumes"
	@echo "  reset-db       - Reset database (WARNING: deletes all data)"
	@echo ""
	@echo "☁️ Deployment:"
	@echo "  deploy-vercel      - Deploy frontend to Vercel"
	@echo "  deploy-render      - Get Render deployment instructions"
	@echo "  deploy-digitalocean - Get DigitalOcean deployment instructions"
	@echo ""

# Setup and installation
setup:
	@echo "🚀 Setting up iNeat ERP Community Edition..."
	@chmod +x setup.sh
	@./setup.sh

start:
	@echo "🐳 Starting iNeat ERP services..."
	@docker-compose up -d
	@echo "✅ Services started! Access at http://localhost:8000"

stop:
	@echo "🛑 Stopping iNeat ERP services..."
	@docker-compose down
	@echo "✅ Services stopped"

restart: stop start

# Monitoring
logs:
	@docker-compose logs -f

logs-backend:
	@docker-compose logs -f backend

logs-db:
	@docker-compose logs -f db

status:
	@docker-compose ps

# Maintenance
clean:
	@echo "🧹 Cleaning up containers and volumes..."
	@docker-compose down -v
	@docker system prune -f
	@echo "✅ Cleanup complete"

reset-db:
	@echo "⚠️  WARNING: This will delete all data!"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ]
	@docker-compose down -v
	@docker-compose up -d
	@echo "✅ Database reset complete"

# Deployment
deploy-vercel:
	@echo "🚀 Deploying to Vercel..."
	@chmod +x scripts/deploy/vercel-deploy.sh
	@./scripts/deploy/vercel-deploy.sh

deploy-render:
	@echo "🚀 Getting Render deployment instructions..."
	@chmod +x scripts/deploy/render-deploy.sh
	@./scripts/deploy/render-deploy.sh

deploy-digitalocean:
	@echo "🚀 Getting DigitalOcean deployment instructions..."
	@chmod +x scripts/deploy/digitalocean-deploy.sh
	@./scripts/deploy/digitalocean-deploy.sh

# Development helpers
dev:
	@echo "🛠️ Starting development environment..."
	@docker-compose up -d
	@echo "✅ Development environment ready!"
	@echo "🌐 Backend: http://localhost:8000"
	@echo "📚 API Docs: http://localhost:8000/api/docs"
	@echo "⚙️ Admin: http://localhost:8000/admin"

test:
	@echo "🧪 Running tests..."
	@docker-compose exec backend python manage.py test

migrate:
	@echo "🗄️ Running database migrations..."
	@docker-compose exec backend python manage.py migrate

shell:
	@echo "🐚 Opening Django shell..."
	@docker-compose exec backend python manage.py shell

# Quick commands
up: start
down: stop
ps: status