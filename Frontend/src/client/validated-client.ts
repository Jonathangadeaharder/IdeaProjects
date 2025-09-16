import * as sdkGen from './sdk.gen';
import { 
  SchemaValidationError,
  validateRegisterRequest,
  validateLoginRequest,
  validateUserResponse,
  validateAuthResponse,
  HealthCheckResponseSchema,
  validateApiResponse
} from '../utils/schema-validation';

export class ApiValidationError extends Error {
  constructor(
    message: string,
    public endpoint: string,
    public validationErrors: Array<{ path: string[]; message: string }>
  ) {
    super(message);
    this.name = 'ApiValidationError';
  }
}

export class ApiRequestError extends Error {
  constructor(
    message: string,
    public endpoint: string,
    public statusCode: number,
    public response: any
  ) {
    super(message);
    this.name = 'ApiRequestError';
  }
}

export class ValidatedApiClient {
  static async register(request: { username: string; password: string }) {
    try {
      // Validate request
      validateRegisterRequest(request);

      // Make API call
      const response = await sdkGen.registerApiAuthRegisterPost({
        body: request
      });

      // Validate response
      validateUserResponse(response.data);

      return response;
    } catch (error) {
      if (error instanceof SchemaValidationError) {
        throw new ApiValidationError(
          'Registration validation failed',
          '/auth/register',
          error.issues.map(issue => ({
            path: issue.path.map(String),
            message: issue.message
          }))
        );
      }
      const err = error as any;
      throw new ApiRequestError(
        err.message || 'Request failed',
        '/auth/register',
        err.response?.status || 0,
        err.response?.data
      );
    }
  }

  static async login(request: { username: string; password: string }) {
    try {
      // Validate request
      validateLoginRequest(request);

      // Make API call
      const response = await sdkGen.loginApiAuthLoginPost({
        body: request
      });

      // Validate response
      validateAuthResponse(response.data);

      return response;
    } catch (error) {
      if (error instanceof SchemaValidationError) {
        throw new ApiValidationError(
          'Login validation failed',
          '/auth/login',
          error.issues.map(issue => ({
            path: issue.path.map(String),
            message: issue.message
          }))
        );
      }
      const err = error as any;
      throw new ApiRequestError(
        err.message || 'Request failed',
        '/auth/login',
        err.response?.status || 0,
        err.response?.data
      );
    }
  }

  static async healthCheck() {
    try {
      // Make API call - need to check what the actual function name is
      const response = await sdkGen.healthCheckHealthGet();

      // Validate response
      const validatedData = validateApiResponse(response.data, HealthCheckResponseSchema);

      return response;
    } catch (error) {
      if (error instanceof SchemaValidationError) {
        throw new ApiValidationError(
          'Health check validation failed',
          '/health',
          error.issues.map(issue => ({
            path: issue.path.map(String),
            message: issue.message
          }))
        );
      }
      const err = error as any;
      throw new ApiRequestError(
        err.message || 'Request failed',
        '/health',
        err.response?.status || 0,
        err.response?.data
      );
    }
  }
}

// Structured API client object
export const apiClient = {
  auth: {
    register: ValidatedApiClient.register,
    login: ValidatedApiClient.login
  },
  health: {
    check: ValidatedApiClient.healthCheck
  }
};
