# Vercel Deployment Guide for TidyGen Frontend

This guide will help you deploy your TidyGen frontend application to Vercel.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **Environment Variables**: Prepare your production environment variables

## Quick Deployment

### Option 1: Deploy via Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy from your project directory**:
   ```bash
   cd /Users/vijayababubollavarapu/dev/tidygen/apps/frontend
   vercel
   ```

4. **For production deployment**:
   ```bash
   vercel --prod
   ```

### Option 2: Deploy via Vercel Dashboard

1. **Connect GitHub Repository**:
   - Go to [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository
   - Select the `apps/frontend` folder as the root directory

2. **Configure Build Settings**:
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

## Environment Variables Setup

### Required Environment Variables

Set these in your Vercel project settings:

```bash
# API Configuration
VITE_API_BASE_URL=https://your-backend-api.vercel.app/api/v1
VITE_APP_NAME=TidyGen
VITE_APP_VERSION=1.0.0

# Payment Integration
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_your_live_stripe_key
VITE_PAYPAL_CLIENT_ID=your_live_paypal_client_id
VITE_PAYPAL_ENVIRONMENT=live

# Feature Flags
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_CRASH_REPORTING=true
VITE_ENABLE_PAYMENTS=true
```

### Setting Environment Variables in Vercel

1. **Via Dashboard**:
   - Go to your project settings
   - Navigate to "Environment Variables"
   - Add each variable with appropriate values

2. **Via CLI**:
   ```bash
   vercel env add VITE_API_BASE_URL
   vercel env add VITE_STRIPE_PUBLISHABLE_KEY
   vercel env add VITE_PAYPAL_CLIENT_ID
   # ... add other variables
   ```

## Build Configuration

### Vercel Configuration (vercel.json)

The project includes a `vercel.json` file with:
- **Build settings**: Static build with Vite
- **Routing**: SPA routing for React Router
- **Headers**: Security headers
- **Redirects**: URL redirects
- **Environment variables**: Production environment setup

### Custom Build Settings

If you need custom build settings:

1. **Build Command**: `npm run build`
2. **Output Directory**: `dist`
3. **Install Command**: `npm install`
4. **Node.js Version**: 18.x (recommended)

## Domain Configuration

### Custom Domain Setup

1. **Add Domain in Vercel**:
   - Go to project settings
   - Navigate to "Domains"
   - Add your custom domain

2. **DNS Configuration**:
   - Add CNAME record pointing to your Vercel deployment
   - Or use Vercel's nameservers

### SSL Certificate

Vercel automatically provides SSL certificates for all deployments.

## Deployment Scripts

The project includes these deployment scripts:

```json
{
  "scripts": {
    "vercel-build": "vite build",
    "deploy": "vercel --prod",
    "deploy:preview": "vercel"
  }
}
```

## Monitoring and Analytics

### Vercel Analytics

1. **Enable Analytics**:
   - Go to project settings
   - Enable Vercel Analytics
   - Add analytics code to your app

2. **Performance Monitoring**:
   - Monitor Core Web Vitals
   - Track deployment performance
   - Set up alerts for issues

## Troubleshooting

### Common Issues

1. **Build Failures**:
   - Check Node.js version (use 18.x)
   - Verify all dependencies are installed
   - Check for TypeScript errors

2. **Environment Variables**:
   - Ensure all required variables are set
   - Check variable names (must start with VITE_)
   - Verify production values

3. **Routing Issues**:
   - Ensure `vercel.json` includes SPA routing
   - Check React Router configuration
   - Verify redirects are working

### Debug Commands

```bash
# Check build locally
npm run build
npm run preview

# Check Vercel deployment
vercel logs
vercel inspect
```

## Production Checklist

Before deploying to production:

- [ ] All environment variables are set
- [ ] Stripe and PayPal keys are production keys
- [ ] API endpoints point to production backend
- [ ] Analytics and monitoring are configured
- [ ] Custom domain is configured (if needed)
- [ ] SSL certificate is active
- [ ] Performance monitoring is enabled

## Support

For deployment issues:
- Check [Vercel Documentation](https://vercel.com/docs)
- Review [Vite Deployment Guide](https://vitejs.dev/guide/static-deploy.html)
- Contact Vercel Support for platform-specific issues

## Next Steps

After successful deployment:

1. **Test the Application**: Verify all features work correctly
2. **Monitor Performance**: Set up monitoring and alerts
3. **Set up CI/CD**: Configure automatic deployments
4. **Backup Strategy**: Implement backup and recovery procedures
5. **Security Review**: Conduct security audit and penetration testing
