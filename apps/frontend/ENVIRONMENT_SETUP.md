# TidyGen Frontend - Environment Variables Setup Guide

## 🚀 **Updated Vercel Configuration**

### **Backend API URL Updated**
- **Before**: `https://tidygen-backend-api.vercel.app/api/$1`
- **After**: `https://api.tidygen.com/api/$1`
- **Reason**: Matches the backend production configuration in `apps/backend/backend/settings/production.py`

### **Comprehensive Environment Variables Added**

The `vercel.json` now includes all necessary environment variables for production deployment:

```json
{
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
  }
}
```

## 🔧 **Environment Variables by Category**

### **1. API Configuration**
```bash
VITE_API_BASE_URL=https://api.tidygen.com/api/v1
VITE_API_TIMEOUT=10000
VITE_DEBUG_API_CALLS=false
VITE_MOCK_API_RESPONSES=false
```

### **2. Application Configuration**
```bash
VITE_APP_NAME=TidyGen ERP
VITE_APP_VERSION=1.0.0
VITE_APP_ENVIRONMENT=production
```

### **3. Authentication**
```bash
VITE_JWT_STORAGE_KEY=tidygen_access_token
VITE_REFRESH_TOKEN_KEY=tidygen_refresh_token
```

### **4. Feature Flags**
```bash
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_CRASH_REPORTING=true
VITE_ENABLE_DEBUG_MODE=false
```

### **5. Payment Gateways**
```bash
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_LIVE_STRIPE_KEY
VITE_PAYPAL_CLIENT_ID=YOUR_PAYPAL_CLIENT_ID
VITE_PAYPAL_ENVIRONMENT=live
```

### **6. Web3 Configuration**
```bash
VITE_WEB3_PROVIDER_URL=https://mainnet.infura.io/v3/YOUR_INFURA_KEY
VITE_WEB3_CHAIN_ID=1
```

### **7. Polkadot Configuration**
```bash
VITE_POLKADOT_WS_URL=wss://rpc.polkadot.io
VITE_POLKADOT_CHAIN_ID=polkadot
```

### **8. External Services**
```bash
VITE_IPFS_GATEWAY=https://ipfs.io/ipfs/
VITE_ETHERSCAN_API_KEY=YOUR_ETHERSCAN_API_KEY
VITE_POLKASCAN_API_KEY=YOUR_POLKASCAN_API_KEY
```

## 🌍 **Environment-Specific Configurations**

### **Production Environment**
```bash
# API Configuration
VITE_API_BASE_URL=https://api.tidygen.com/api/v1
VITE_APP_ENVIRONMENT=production
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_DEBUG_MODE=false

# Payment Gateways (Live)
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_LIVE_STRIPE_KEY
VITE_PAYPAL_ENVIRONMENT=live

# Web3 (Mainnet)
VITE_WEB3_PROVIDER_URL=https://mainnet.infura.io/v3/YOUR_INFURA_KEY
VITE_WEB3_CHAIN_ID=1
```

### **Staging Environment**
```bash
# API Configuration
VITE_API_BASE_URL=https://api-staging.tidygen.com/api/v1
VITE_APP_ENVIRONMENT=staging
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_DEBUG_MODE=true

# Payment Gateways (Sandbox)
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_TEST_STRIPE_KEY
VITE_PAYPAL_ENVIRONMENT=sandbox

# Web3 (Testnet)
VITE_WEB3_PROVIDER_URL=https://sepolia.infura.io/v3/YOUR_INFURA_KEY
VITE_WEB3_CHAIN_ID=11155111
```

### **Development Environment**
```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_ENVIRONMENT=development
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_DEBUG_MODE=true

# Payment Gateways (Test)
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_TEST_STRIPE_KEY
VITE_PAYPAL_ENVIRONMENT=sandbox

# Web3 (Local/Testnet)
VITE_WEB3_PROVIDER_URL=http://localhost:8545
VITE_WEB3_CHAIN_ID=1337
```

## 🔐 **Required API Keys and Secrets**

### **Infura (Web3 Provider)**
1. Go to [Infura.io](https://infura.io)
2. Create a new project
3. Copy your Project ID
4. Replace `YOUR_INFURA_KEY` with your Project ID

### **Stripe (Payment Processing)**
1. Go to [Stripe Dashboard](https://dashboard.stripe.com)
2. Get your publishable key from API Keys section
3. Replace `YOUR_LIVE_STRIPE_KEY` with your live publishable key

### **PayPal (Payment Processing)**
1. Go to [PayPal Developer](https://developer.paypal.com)
2. Create a new application
3. Copy your Client ID
4. Replace `YOUR_PAYPAL_CLIENT_ID` with your Client ID

### **Etherscan (Blockchain Explorer)**
1. Go to [Etherscan.io](https://etherscan.io)
2. Create an account and get API key
3. Replace `YOUR_ETHERSCAN_API_KEY` with your API key

### **Polkascan (Polkadot Explorer)**
1. Go to [Polkascan.io](https://polkascan.io)
2. Create an account and get API key
3. Replace `YOUR_POLKASCAN_API_KEY` with your API key

## 🚀 **Vercel Deployment Setup**

### **1. Set Environment Variables in Vercel Dashboard**

1. Go to your Vercel dashboard
2. Select your TidyGen frontend project
3. Go to **Settings** → **Environment Variables**
4. Add each environment variable for the appropriate environments:

#### **Production Environment Variables**
```
VITE_API_BASE_URL=https://api.tidygen.com/api/v1
VITE_APP_NAME=TidyGen ERP
VITE_APP_VERSION=1.0.0
VITE_APP_ENVIRONMENT=production
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_CRASH_REPORTING=true
VITE_ENABLE_DEBUG_MODE=false
VITE_DEBUG_API_CALLS=false
VITE_MOCK_API_RESPONSES=false
VITE_API_TIMEOUT=10000
VITE_JWT_STORAGE_KEY=tidygen_access_token
VITE_REFRESH_TOKEN_KEY=tidygen_refresh_token
VITE_WEB3_PROVIDER_URL=https://mainnet.infura.io/v3/YOUR_INFURA_KEY
VITE_WEB3_CHAIN_ID=1
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_LIVE_STRIPE_KEY
VITE_PAYPAL_CLIENT_ID=YOUR_PAYPAL_CLIENT_ID
VITE_PAYPAL_ENVIRONMENT=live
VITE_IPFS_GATEWAY=https://ipfs.io/ipfs/
VITE_ETHERSCAN_API_KEY=YOUR_ETHERSCAN_API_KEY
VITE_POLKASCAN_API_KEY=YOUR_POLKASCAN_API_KEY
```

#### **Preview Environment Variables**
```
VITE_API_BASE_URL=https://api-staging.tidygen.com/api/v1
VITE_APP_NAME=TidyGen ERP (Staging)
VITE_APP_VERSION=1.0.0
VITE_APP_ENVIRONMENT=staging
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_CRASH_REPORTING=true
VITE_ENABLE_DEBUG_MODE=true
VITE_DEBUG_API_CALLS=true
VITE_MOCK_API_RESPONSES=false
VITE_API_TIMEOUT=10000
VITE_JWT_STORAGE_KEY=tidygen_access_token
VITE_REFRESH_TOKEN_KEY=tidygen_refresh_token
VITE_WEB3_PROVIDER_URL=https://sepolia.infura.io/v3/YOUR_INFURA_KEY
VITE_WEB3_CHAIN_ID=11155111
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_TEST_STRIPE_KEY
VITE_PAYPAL_CLIENT_ID=YOUR_PAYPAL_CLIENT_ID
VITE_PAYPAL_ENVIRONMENT=sandbox
VITE_IPFS_GATEWAY=https://ipfs.io/ipfs/
VITE_ETHERSCAN_API_KEY=YOUR_ETHERSCAN_API_KEY
VITE_POLKASCAN_API_KEY=YOUR_POLKASCAN_API_KEY
```

### **2. Deploy the Application**

```bash
# Deploy to preview
npm run deploy:preview

# Deploy to production
npm run deploy
```

### **3. Verify Deployment**

1. **Check API Connectivity**: Test that API calls work
2. **Verify Web3 Integration**: Test wallet connections
3. **Test Payment Gateways**: Verify Stripe/PayPal integration
4. **Check Analytics**: Ensure analytics are working
5. **Test All Features**: Comprehensive functionality testing

## 🔍 **Troubleshooting**

### **Common Issues**

#### **API Calls Failing**
- **Check**: Backend API URL is correct (`https://api.tidygen.com`)
- **Verify**: Backend is deployed and accessible
- **Ensure**: CORS is configured on backend for your frontend domain

#### **Environment Variables Not Working**
- **Check**: Variables are set in Vercel dashboard
- **Verify**: Variable names start with `VITE_`
- **Ensure**: Variables are set for the correct environment (Production/Preview)

#### **Web3 Connection Issues**
- **Check**: Web3 provider URL is correct
- **Verify**: Chain ID matches your network
- **Ensure**: Infura API key is valid

#### **Payment Gateway Issues**
- **Check**: Stripe/PayPal keys are correct
- **Verify**: Environment matches (live/sandbox)
- **Ensure**: Keys are for the correct environment

### **Debug Mode**

To enable debug mode for troubleshooting:

```bash
# Set in Vercel environment variables
VITE_ENABLE_DEBUG_MODE=true
VITE_DEBUG_API_CALLS=true
```

This will provide additional logging and debugging information in the browser console.

## 📊 **Monitoring and Analytics**

### **Performance Monitoring**
- **Vercel Analytics**: Built-in performance monitoring
- **Web Vitals**: Core web vitals tracking
- **Error Tracking**: Error boundary implementation

### **User Analytics**
- **Google Analytics**: User behavior tracking (if enabled)
- **Custom Events**: Web3 interaction tracking
- **Conversion Tracking**: User journey analysis

## 🔒 **Security Considerations**

### **Environment Variables Security**
- **Never commit**: API keys or secrets to version control
- **Use Vercel**: Environment variables for sensitive data
- **Rotate keys**: Regularly rotate API keys and secrets
- **Monitor usage**: Track API key usage and limits

### **Production Security**
- **HTTPS**: Enforced by Vercel
- **CORS**: Properly configured on backend
- **Headers**: Security headers configured in vercel.json
- **Rate Limiting**: Implemented on backend

## 🎯 **Next Steps**

1. **Set up API keys**: Get all required API keys and secrets
2. **Configure Vercel**: Set environment variables in Vercel dashboard
3. **Deploy backend**: Ensure backend is deployed to `api.tidygen.com`
4. **Test deployment**: Verify all functionality works
5. **Monitor performance**: Set up monitoring and analytics
6. **Update documentation**: Keep environment setup guide updated

The configuration is now optimized for production deployment with proper environment management, security headers, and comprehensive API integration.
