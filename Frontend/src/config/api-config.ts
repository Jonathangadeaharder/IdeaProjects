/**
 * API Configuration for different environments
 * Handles base URLs, timeouts, and other environment-specific settings
 */

export interface ApiConfig {
  baseUrl: string;
  timeout: number;
  retryAttempts: number;
  retryDelay: number;
  enableLogging: boolean;
  enableValidation: boolean;
}

export type Environment = 'development' | 'staging' | 'production' | 'test';

// Environment-specific configurations
const configs: Record<Environment, ApiConfig> = {
  development: {
    baseUrl: 'http://localhost:8000',
    timeout: 10000,
    retryAttempts: 3,
    retryDelay: 1000,
    enableLogging: true,
    enableValidation: true,
  },
  staging: {
    baseUrl: process.env.VITE_STAGING_API_URL || 'https://staging-api.langplug.com',
    timeout: 15000,
    retryAttempts: 3,
    retryDelay: 2000,
    enableLogging: true,
    enableValidation: true,
  },
  production: {
    baseUrl: process.env.VITE_API_URL || 'https://api.langplug.com',
    timeout: 20000,
    retryAttempts: 2,
    retryDelay: 3000,
    enableLogging: false,
    enableValidation: false,
  },
  test: {
    baseUrl: 'http://localhost:8000',
    timeout: 5000,
    retryAttempts: 1,
    retryDelay: 500,
    enableLogging: false,
    enableValidation: true,
  },
};

/**
 * Get the current environment from various sources
 */
function getCurrentEnvironment(): Environment {
  // Check Vite environment variable first
  if (import.meta.env.VITE_ENVIRONMENT) {
    return import.meta.env.VITE_ENVIRONMENT as Environment;
  }
  
  // Check Node environment
  if (import.meta.env.NODE_ENV === 'production') {
    return 'production';
  }
  
  if (import.meta.env.NODE_ENV === 'test') {
    return 'test';
  }
  
  // Check hostname for staging
  if (typeof window !== 'undefined' && window.location.hostname.includes('staging')) {
    return 'staging';
  }
  
  // Default to development
  return 'development';
}

/**
 * Get API configuration for the current environment
 */
export function getApiConfig(): ApiConfig {
  const environment = getCurrentEnvironment();
  return configs[environment];
}

/**
 * Get API configuration for a specific environment
 */
export function getApiConfigForEnvironment(env: Environment): ApiConfig {
  return configs[env];
}

/**
 * Validate API configuration
 */
export function validateApiConfig(config: ApiConfig): boolean {
  if (!config.baseUrl || !config.baseUrl.startsWith('http')) {
    console.error('Invalid API base URL:', config.baseUrl);
    return false;
  }
  
  if (config.timeout <= 0) {
    console.error('Invalid API timeout:', config.timeout);
    return false;
  }
  
  if (config.retryAttempts < 0) {
    console.error('Invalid retry attempts:', config.retryAttempts);
    return false;
  }
  
  return true;
}

/**
 * Create headers for API requests based on environment
 */
export function createApiHeaders(config: ApiConfig): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };
  
  // Add environment-specific headers
  const environment = getCurrentEnvironment();
  headers['X-Environment'] = environment;
  
  // Add version header for contract versioning
  headers['X-API-Version'] = '1.0';
  
  // Add request ID for tracing in non-production environments
  if (config.enableLogging) {
    headers['X-Request-ID'] = generateRequestId();
  }
  
  return headers;
}

/**
 * Generate a unique request ID for tracing
 */
function generateRequestId(): string {
  return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Log API configuration on startup
 */
export function logApiConfig(): void {
  const config = getApiConfig();
  const environment = getCurrentEnvironment();
  
  if (config.enableLogging) {
    console.log('🔧 API Configuration:', {
      environment,
      baseUrl: config.baseUrl,
      timeout: config.timeout,
      retryAttempts: config.retryAttempts,
      enableValidation: config.enableValidation,
    });
  }
}

// Export current configuration as default
export default getApiConfig();