import * as clientSdk from './sdk.gen';
import {
  validateUserResponse,
  validateAuthResponse,
  validateRegisterRequest,
  validateLoginRequest,
  SchemaValidationError,
  type UserResponse,
  type AuthResponse,
  type RegisterRequest,
  type LoginRequest,
} from '../utils/schema-validation';

// Custom error types for API validation
export class ApiValidationError extends Error {
  constructor(
    message: string,
    public endpoint?: string,
    public validationErrors?: Array<{ path: string[]; message: string }>,
    public originalError?: Error
  ) {
    super(message);
    this.name = 'ApiValidationError';
  }
}

export class ApiRequestError extends Error {
  constructor(
    message: string,
    public endpoint?: string,
    public statusCode?: number,
    public response?: any,
    public originalError?: Error
  ) {
    super(message);
    this.name = 'ApiRequestError';
  }
}

// Validated API client wrapper
export class ValidatedApiClient {
  /**
   * Register a new user with request/response validation
   */
  static async register(request: RegisterRequest): Promise<{
    data: UserResponse;
    response: { status: number };
  }> {
    try {
      // Validate request data
      const validatedRequest = validateRegisterRequest(request);
      
      // Make API call
      const response = await clientSdk.registerAuthRegisterPost({
        body: validatedRequest,
      });
      
      // Validate response data
      const validatedData = validateUserResponse(response.data);
      
      return {
        data: validatedData,
        response: response.response,
      };
    } catch (error) {
      if (error instanceof SchemaValidationError) {
        throw new ApiValidationError(
          'Registration response validation failed',
          '/auth/register',
          undefined,
          error
        );
      }
      const errorMessage = error instanceof Error ? error.message : 'Registration request failed';
      throw new ApiRequestError(
        errorMessage,
        '/auth/register',
        undefined,
        undefined,
        error as Error
      );
    }
  }

  /**
   * Login user with request/response validation
   */
  static async login(request: LoginRequest): Promise<{
    data: AuthResponse;
    response: { status: number };
  }> {
    try {
      // Validate request data
      const validatedRequest = validateLoginRequest(request);
      
      // Make API call
      const response = await clientSdk.loginAuthLoginPost({
        body: validatedRequest,
      });
      
      // Validate response data
      const validatedData = validateAuthResponse(response.data);
      
      return {
        data: validatedData,
        response: response.response,
      };
    } catch (error) {
      if (error instanceof SchemaValidationError) {
        throw new ApiValidationError(
          'Login response validation failed',
          '/auth/login',
          undefined,
          error
        );
      }
      const errorMessage = error instanceof Error ? error.message : 'Login request failed';
      throw new ApiRequestError(
        errorMessage,
        '/auth/login',
        undefined,
        undefined,
        error as Error
      );
    }
  }

  /**
   * Health check with response validation
   */
  static async healthCheck(): Promise<{
    data: { status: string; timestamp?: string };
    response: { status: number };
  }> {
    try {
      const response = await clientSdk.healthCheckHealthGet();
      
      // Basic validation for health check response
      if (!response.data || typeof response.data !== 'object') {
        throw new ApiValidationError('Invalid health check response format');
      }
      
      // Validate required 'status' field
      if (!('status' in response.data) || typeof response.data.status !== 'string') {
        throw new ApiValidationError('Health check response missing required status field');
      }
      
      return {
        data: response.data as { status: string; timestamp?: string },
        response: response.response,
      };
    } catch (error) {
      if (error instanceof SchemaValidationError || error instanceof ApiValidationError) {
        throw error;
      }
      const errorMessage = error instanceof Error ? error.message : 'Health check request failed';
      throw new ApiRequestError(
        errorMessage,
        '/health',
        undefined,
        undefined,
        error as Error
      );
    }
  }
}

// Structured API client object
export const apiClient = {
  auth: {
    register: ValidatedApiClient.register,
    login: ValidatedApiClient.login,
  },
  health: {
    check: ValidatedApiClient.healthCheck,
  },
};

// Re-export types for convenience
export type {
  UserResponse,
  AuthResponse,
  RegisterRequest,
  LoginRequest,
};