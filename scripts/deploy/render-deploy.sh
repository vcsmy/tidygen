#!/bin/bash

# TidyGen ERP Community Edition - Render Deployment Script
# This script provides instructions and configuration for Render deployment

set -e

echo "🚀 TidyGen ERP Community Edition - Render Deployment"
echo "=================================================="

echo "📋 Render Deployment Instructions:"
echo ""
echo "1. 🌐 Go to https://render.com and sign up/login"
echo "2. 📦 Create a new Web Service"
echo "3. 🔗 Connect your GitHub repository"
echo "4. ⚙️ Configure the following settings:"
echo ""
echo "   📝 Build Command:"
echo "   cd apps/backend && pip install -r requirements.txt"
echo ""
echo "   🚀 Start Command:"
echo "   cd apps/backend && python manage.py migrate && python manage.py collectstatic --noinput && python manage.py setup_single_organization --create-admin && gunicorn backend.wsgi:application"
echo ""
echo "   🌍 Environment Variables:"
echo "   - DJANGO_ENV=production"
echo "   - DEBUG=False"
echo "   - SECRET_KEY=your-secret-key-here"
echo "   - DATABASE_URL=postgresql://user:pass@host:port/db (use Render PostgreSQL)"
echo "   - ALLOWED_HOSTS=your-app.onrender.com"
echo "   - CORS_ALLOWED_ORIGINS=https://your-frontend-url.com"
echo ""
echo "5. 🗄️ Add PostgreSQL Database:"
echo "   - Go to Dashboard > New > PostgreSQL"
echo "   - Copy the connection string to DATABASE_URL"
echo ""
echo "6. 🔄 Deploy and test your application"
echo ""
echo "📚 For detailed instructions, see:"
echo "https://render.com/docs/deploy-django"
echo ""
echo "🔗 Useful Links:"
echo "- Render Dashboard: https://dashboard.render.com"
echo "- Render Documentation: https://render.com/docs"
echo ""
