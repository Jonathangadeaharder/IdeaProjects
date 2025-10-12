/**
 * Centralized error message formatting
 * Extracts user-friendly error messages from API errors
 */

export interface ApiError {
  body?: {
    detail?: string
  }
  message?: string
  status?: number
  response?: {
    data?: {
      detail?: string | Array<{ msg?: string }>
    }
    status?: number
  }
}

/**
 * Format API error into user-friendly message
 * @param error - Error object from API call
 * @param fallback - Default message if no specific error found
 * @returns Formatted error message
 */
export function formatApiError(error: unknown, fallback: string): string {
  if (!error) return fallback

  const err = error as ApiError
  // Try different error structures
  if (err?.body?.detail) return err.body.detail
  if (err?.response?.data?.detail) {
    const detail = err.response.data.detail
    // Handle array of validation errors
    if (Array.isArray(detail)) {
      return detail.map(item => item.msg || JSON.stringify(item)).join('; ')
    }
    return detail
  }
  if (err?.message) return err.message

  return fallback
}

/**
 * Check if error is a specific HTTP status code
 */
export function isHttpError(error: unknown, statusCode: number): boolean {
  const err = error as ApiError
  return err?.status === statusCode || err?.response?.status === statusCode
}

/**
 * Check if error is authentication related (401)
 */
export function isAuthError(error: unknown): boolean {
  return isHttpError(error, 401)
}

/**
 * Check if error is rate limiting (429)
 */
export function isRateLimitError(error: unknown): boolean {
  return isHttpError(error, 429)
}

/**
 * Get retry-after header from rate limit error
 */
export function getRetryAfter(error: unknown): number {
  const err = error as ApiError
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const retryAfter = (err?.response as any)?.headers?.['retry-after']
    || (err as any)?.headers?.['retry-after']

  return retryAfter ? parseInt(retryAfter, 10) : 60
}
