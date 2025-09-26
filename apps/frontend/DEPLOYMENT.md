# TidyGen Frontend - Deployment Guide

## 🚀 **Vercel Deployment Configuration**

### **Fixed Issues in vercel.json**

#### **1. Removed builds Configuration**
- **Before**: Used `builds` array which overrides Project Settings
- **After**: Using `buildCommand` and `outputDirectory` for cleaner configuration
- **Benefit**: Eliminates the warning about unused build settings

#### **2. Updated Backend API URL**
- **Before**: `https://your-backend-api.vercel.app/api/$1` (placeholder)
- **After**: `https://api.tidygen.com/api/$1` (actual backend)
- **Benefit**: API calls will now work correctly with the proper backend domain

#### **3. Added Environment Variables**
- **Added**: `VITE_API_BASE_URL` and `VITE_APP_ENV`
- **Benefit**: Proper environment configuration for production

### **Current Configuration**

```json
{
  "version": 2,
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://tidygen-backend-api.vercel.app/api/$1"
    },
    {
      "source": "/((?!assets/).*)",
      "destination": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        },
        {
          "key": "Referrer-Policy",
          "value": "strict-origin-when-cross-origin"
        }
      ]
    },
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ],
  "redirects": [
    {
      "source": "/home",
      "destination": "/",
      "permanent": true
    }
  ],
  "env": {
    "VITE_API_BASE_URL": "https://api.tidygen.com/api/v1",
    "VITE_APP_NAME": "TidyGen ERP",
    "VITE_APP_VERSION": "1.0.0",
    "VITE_APP_ENVIRONMENT": "production",
    "VITE_ENABLE_ANALYTICS": "true",
    "VITE_ENABLE_CRASH_REPORTING": "true",
    "VITE_ENABLE_DEBUG_MODE": "false",
    "VITE_DEBUG_API_CALLS": "false",
    "VITE_MOCK_API_RESPONSES": "false",
    "VITE_API_TIMEOUT": "10000",
    "VITE_JWT_STORAGE_KEY": "tidygen_access_token",
    "VITE_REFRESH_TOKEN_KEY": "tidygen_refresh_token",
    "VITE_WEB3_PROVIDER_URL": "https://mainnet.infura.io/v3/YOUR_INFURA_KEY",
    "VITE_WEB3_CHAIN_ID": "1",
    "VITE_STRIPE_PUBLISHABLE_KEY": "pk_live_YOUR_LIVE_STRIPE_KEY",
    "VITE_PAYPAL_CLIENT_ID": "YOUR_PAYPAL_CLIENT_ID",
    "VITE_PAYPAL_ENVIRONMENT": "live",
    "VITE_IPFS_GATEWAY": "https://ipfs.io/ipfs/",
    "VITE_ETHERSCAN_API_KEY": "YOUR_ETHERSCAN_API_KEY",
    "VITE_POLKASCAN_API_KEY": "YOUR_POLKASCAN_API_KEY"
  },
  "functions": {
    "app/api/**/*.ts": {
      "runtime": "nodejs18.x"
    }
  }
}
```

## 🔧 **Environment Variables Setup**

### **Required Environment Variables**

Create these environment variables in your Vercel dashboard:

#### **Production Environment**
```
VITE_API_BASE_URL=https://tidygen-backend-api.vercel.app
VITE_API_VERSION=v1
VITE_APP_NAME=TidyGen ERP
VITE_APP_VERSION=1.0.0
VITE_APP_ENV=production
VITE_ENABLE_WEB3=true
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_DEBUG=false
```

#### **Staging Environment**
```
VITE_API_BASE_URL=https://tidygen-backend-api-staging.vercel.app
VITE_API_VERSION=v1
VITE_APP_NAME=TidyGen ERP (Staging)
VITE_APP_VERSION=1.0.0
VITE_APP_ENV=staging
VITE_ENABLE_WEB3=true
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_DEBUG=true
```

#### **Development Environment**
```
VITE_API_BASE_URL=http://localhost:8000
VITE_API_VERSION=v1
VITE_APP_NAME=TidyGen ERP (Dev)
VITE_APP_VERSION=1.0.0
VITE_APP_ENV=development
VITE_ENABLE_WEB3=true
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_DEBUG=true
```

### **Web3 Configuration**
```
VITE_WEB3_PROVIDER_URL=https://mainnet.infura.io/v3/YOUR_INFURA_KEY
VITE_WEB3_CHAIN_ID=1
VITE_WEB3_NETWORK_NAME=ethereum
VITE_POLKADOT_WS_URL=wss://rpc.polkadot.io
VITE_POLKADOT_CHAIN_ID=polkadot
```

### **External Services**
```
VITE_IPFS_GATEWAY=https://ipfs.io/ipfs/
VITE_ETHERSCAN_API_KEY=YOUR_ETHERSCAN_API_KEY
VITE_POLKASCAN_API_KEY=YOUR_POLKASCAN_API_KEY
```

## 🚀 **Deployment Steps**

### **1. Environment Setup**
1. Go to your Vercel dashboard
2. Select your TidyGen frontend project
3. Go to Settings → Environment Variables
4. Add all required environment variables for each environment

### **2. Backend API Setup**
1. Deploy your backend API to Vercel
2. Update the API URL in `vercel.json` to match your backend URL
3. Ensure CORS is configured on your backend to allow your frontend domain

### **3. Deploy Frontend**
```bash
# Deploy to preview
npm run deploy:preview

# Deploy to production
npm run deploy
```

### **4. Verify Deployment**
1. Check that the deployment URL is accessible
2. Test API connectivity
3. Verify Web3 wallet connections work
4. Test all major functionality

## 🔍 **Troubleshooting**

### **Common Issues**

#### **API Calls Failing**
- **Check**: Backend API URL in `vercel.json`
- **Verify**: Backend is deployed and accessible
- **Ensure**: CORS is configured on backend

#### **Environment Variables Not Working**
- **Check**: Variables are set in Vercel dashboard
- **Verify**: Variable names start with `VITE_`
- **Ensure**: Variables are set for the correct environment

#### **Build Failures**
- **Check**: All dependencies are in `package.json`
- **Verify**: Build command is correct
- **Ensure**: No TypeScript errors

#### **Web3 Connection Issues**
- **Check**: Web3 provider URLs are correct
- **Verify**: Chain IDs match your network
- **Ensure**: Wallet connection is properly configured

### **Performance Optimization**

#### **Build Optimization**
- **Enable**: Vite build optimizations
- **Use**: Code splitting for better loading
- **Implement**: Lazy loading for routes

#### **Caching Strategy**
- **Static Assets**: 1 year cache (already configured)
- **API Responses**: Appropriate cache headers
- **Service Worker**: For offline functionality

## 📊 **Monitoring and Analytics**

### **Performance Monitoring**
- **Vercel Analytics**: Built-in performance monitoring
- **Web Vitals**: Core web vitals tracking
- **Error Tracking**: Error boundary implementation

### **User Analytics**
- **Google Analytics**: User behavior tracking
- **Custom Events**: Web3 interaction tracking
- **Conversion Tracking**: User journey analysis

## 🔒 **Security Considerations**

### **Headers Configuration**
The current configuration includes:
- **X-Content-Type-Options**: Prevents MIME type sniffing
- **X-Frame-Options**: Prevents clickjacking
- **X-XSS-Protection**: XSS protection
- **Referrer-Policy**: Controls referrer information

### **Additional Security**
- **HTTPS**: Enforced by Vercel
- **CSP**: Content Security Policy (consider adding)
- **HSTS**: HTTP Strict Transport Security (consider adding)

## 🎯 **Next Steps**

1. **Set up environment variables** in Vercel dashboard
2. **Deploy backend API** and update the URL
3. **Test the deployment** thoroughly
4. **Monitor performance** and user feedback
5. **Implement additional security** headers as needed

The configuration is now optimized for production deployment with proper environment management and security headers.
