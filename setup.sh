#!/bin/bash

# iNeat ERP Community Edition - Quick Setup Script
# This script sets up the development environment quickly

set -e

echo "🚀 iNeat ERP Community Edition - Quick Setup"
echo "============================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. You can edit it if needed."
else
    echo "✅ .env file already exists"
fi

# Start the services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
docker-compose ps

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Your iNeat ERP Community Edition is now running:"
echo "   🌐 Backend API: http://localhost:8000"
echo "   ⚙️ Admin Interface: http://localhost:8000/admin"
echo "   📚 API Documentation: http://localhost:8000/api/docs"
echo ""
echo "🔑 Default login credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "⚠️  Important: Change the default password after first login!"
echo ""
echo "📖 For more information, see README.md"
echo ""
echo "🛠️ Useful commands:"
echo "   docker-compose logs -f backend    # View backend logs"
echo "   docker-compose down              # Stop all services"
echo "   docker-compose up -d             # Start all services"
echo ""
