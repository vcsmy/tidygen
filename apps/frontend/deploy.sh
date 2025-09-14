#!/bin/bash

# TidyGen Frontend Deployment Script for Vercel
# This script helps deploy the frontend application to Vercel

set -e

echo "🚀 Starting TidyGen Frontend Deployment to Vercel..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    print_error "Vercel CLI is not installed. Please install it first:"
    echo "npm i -g vercel"
    exit 1
fi

# Check if user is logged in to Vercel
if ! vercel whoami &> /dev/null; then
    print_warning "You are not logged in to Vercel. Please login first:"
    echo "vercel login"
    exit 1
fi

# Check if we're in the correct directory
if [ ! -f "package.json" ]; then
    print_error "package.json not found. Please run this script from the frontend directory."
    exit 1
fi

# Check if vercel.json exists
if [ ! -f "vercel.json" ]; then
    print_error "vercel.json not found. Please ensure the Vercel configuration file exists."
    exit 1
fi

print_status "Installing dependencies..."
npm install

print_status "Running linting..."
npm run lint

print_status "Building the application..."
npm run build

print_status "Deploying to Vercel..."

# Check if this is a production deployment
if [ "$1" = "--prod" ]; then
    print_status "Deploying to production..."
    vercel --prod
    print_success "Production deployment completed!"
else
    print_status "Deploying to preview..."
    vercel
    print_success "Preview deployment completed!"
fi

print_success "🎉 Deployment completed successfully!"
print_status "Your application is now live on Vercel!"

# Display helpful information
echo ""
echo "📋 Next Steps:"
echo "1. Check your deployment URL in the Vercel dashboard"
echo "2. Set up environment variables in Vercel project settings"
echo "3. Configure your custom domain (if needed)"
echo "4. Test all features to ensure everything works correctly"
echo ""
echo "🔧 Useful Commands:"
echo "- View deployment logs: vercel logs"
echo "- Inspect deployment: vercel inspect"
echo "- Set environment variables: vercel env add"
echo ""
echo "📚 Documentation:"
echo "- Vercel Docs: https://vercel.com/docs"
echo "- Deployment Guide: ./VERCEL_DEPLOYMENT.md"
