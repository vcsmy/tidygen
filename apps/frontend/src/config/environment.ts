/**
 * Environment configuration for the application
 * Centralized configuration management for all environment variables
 */

// Environment variables with fallbacks
export const config = {
  // API Configuration
  api: {
    baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
    timeout: parseInt(import.meta.env.VITE_API_TIMEOUT || '10000'),
    debug: import.meta.env.VITE_DEBUG_API_CALLS === 'true',
    mockResponses: import.meta.env.VITE_MOCK_API_RESPONSES === 'true',
  },

  // Authentication
  auth: {
    jwtStorageKey: import.meta.env.VITE_JWT_STORAGE_KEY || 'access_token',
    refreshTokenKey: import.meta.env.VITE_REFRESH_TOKEN_KEY || 'refresh_token',
    tokenExpiryBuffer: 5 * 60 * 1000, // 5 minutes before expiry
  },

  // Application
  app: {
    name: import.meta.env.VITE_APP_NAME || 'TidyGen',
    version: import.meta.env.VITE_APP_VERSION || '1.0.0',
    environment: import.meta.env.VITE_APP_ENVIRONMENT || 'development',
    isDevelopment: import.meta.env.DEV,
    isProduction: import.meta.env.PROD,
  },

  // Feature Flags
  features: {
    analytics: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
    crashReporting: import.meta.env.VITE_ENABLE_CRASH_REPORTING === 'true',
    debugMode: import.meta.env.VITE_ENABLE_DEBUG_MODE === 'true',
  },

  // Payment Gateways
  payments: {
    stripe: {
      publishableKey: import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || '',
      environment: import.meta.env.VITE_PAYPAL_ENVIRONMENT || 'sandbox',
    },
    paypal: {
      clientId: import.meta.env.VITE_PAYPAL_CLIENT_ID || '',
      environment: import.meta.env.VITE_PAYPAL_ENVIRONMENT || 'sandbox',
    },
  },

  // Web3 Integration
  web3: {
    providerUrl: import.meta.env.VITE_WEB3_PROVIDER_URL || '',
    chainId: parseInt(import.meta.env.VITE_WEB3_CHAIN_ID || '1'),
  },

  // External Services
  services: {
    sentry: {
      dsn: import.meta.env.VITE_SENTRY_DSN || '',
    },
    googleAnalytics: {
      id: import.meta.env.VITE_GOOGLE_ANALYTICS_ID || '',
    },
  },

  // Development
  development: {
    enableDebugLogs: import.meta.env.VITE_DEBUG_API_CALLS === 'true',
    mockApiResponses: import.meta.env.VITE_MOCK_API_RESPONSES === 'true',
  },
} as const;

// Type-safe environment variable access
export function getEnvVar(key: string, defaultValue?: string): string {
  const value = import.meta.env[key];
  if (value === undefined && defaultValue === undefined) {
    throw new Error(`Environment variable ${key} is required but not defined`);
  }
  return value || defaultValue || '';
}

export function getBooleanEnvVar(key: string, defaultValue = false): boolean {
  const value = import.meta.env[key];
  if (value === undefined) return defaultValue;
  return value === 'true';
}

export function getNumberEnvVar(key: string, defaultValue = 0): number {
  const value = import.meta.env[key];
  if (value === undefined) return defaultValue;
  const parsed = parseInt(value, 10);
  if (isNaN(parsed)) return defaultValue;
  return parsed;
}

// Validation
export function validateConfig() {
  const errors: string[] = [];

  // Required in production
  if (config.app.isProduction) {
    if (!config.payments.stripe.publishableKey) {
      errors.push('VITE_STRIPE_PUBLISHABLE_KEY is required in production');
    }
    if (!config.payments.paypal.clientId) {
      errors.push('VITE_PAYPAL_CLIENT_ID is required in production');
    }
  }

  // API URL validation
  try {
    new URL(config.api.baseUrl);
  } catch {
    errors.push('VITE_API_BASE_URL must be a valid URL');
  }

  if (errors.length > 0) {
    console.error('Configuration validation failed:', errors);
    if (config.app.isProduction) {
      throw new Error(`Configuration validation failed: ${errors.join(', ')}`);
    }
  }

  return errors.length === 0;
}

// Initialize configuration validation
if (typeof window !== 'undefined') {
  validateConfig();
}

export default config;
