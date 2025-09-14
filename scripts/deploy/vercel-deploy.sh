#!/bin/bash

# TidyGen ERP Community Edition - Vercel Deployment Script
# This script deploys the frontend to Vercel and provides instructions for backend deployment

set -e

echo "🚀 TidyGen ERP Community Edition - Vercel Deployment"
echo "=================================================="

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI is not installed. Installing..."
    npm install -g vercel
fi

# Check if user is logged in to Vercel
if ! vercel whoami &> /dev/null; then
    echo "🔐 Please log in to Vercel:"
    vercel login
fi

echo "📦 Deploying frontend to Vercel..."

# Navigate to frontend directory
cd apps/frontend

# Install dependencies
echo "📥 Installing dependencies..."
npm install

# Build the project
echo "🔨 Building project..."
npm run build

# Deploy to Vercel
echo "🚀 Deploying to Vercel..."
vercel --prod

echo ""
echo "✅ Frontend deployed successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Note the deployment URL from Vercel"
echo "2. Deploy the backend to a service like Railway, Render, or DigitalOcean"
echo "3. Update the CORS_ALLOWED_ORIGINS in your backend environment"
echo "4. Update the API_BASE_URL in your frontend environment"
echo ""
echo "🔗 Useful Links:"
echo "- Vercel Dashboard: https://vercel.com/dashboard"
echo "- Backend Deployment Guide: See DEPLOYMENT.md"
echo ""
