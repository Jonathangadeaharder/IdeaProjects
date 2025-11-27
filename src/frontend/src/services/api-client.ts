/**
 * Enhanced API client with better error handling
 * Caching is handled by React Query, not here
 */
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios'
import { toast } from 'react-hot-toast'
import { logger } from './logger'

export interface ApiResponse<T = unknown> {
  data: T
  status: number
  message?: string
}

export interface ApiError {
  status: number
  message: string
  code?: string
  details?: Record<string, unknown>
  [key: string]: unknown
}

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // Request interceptor for auth token
    this.client.interceptors.request.use(
      config => {
        const token = localStorage.getItem('authToken')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }

        // Add request ID for tracing
        config.headers['X-Request-ID'] =
          `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

        logger.debug('ApiClient', 'Sending request', {
          method: config.method?.toUpperCase(),
          url: config.url,
          headers: config.headers,
        })

        return config
      },
      error => {
        logger.error('API Request Error', error)
        return Promise.reject(error)
      }
    )

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      response => {
        logger.debug('ApiClient', 'Received response', {
          status: response.status,
          url: response.config.url,
          data: response.data,
        })
        return response
      },
      error => {
        const apiError = this.handleApiError(error)
        logger.error('ApiClient', 'API error occurred', apiError)

        // Show toast for user-facing errors
        if (apiError.status !== 401) {
          toast.error(apiError.message)
        }

        return Promise.reject(apiError)
      }
    )
  }

  private handleApiError(error: unknown): ApiError {
    const axiosError = error as {
      response?: {
        status: number
        data?: {
          detail?: string
          message?: string
          code?: string
          [key: string]: unknown
        }
      }
      request?: unknown
      message?: string
    }

    if (axiosError.response) {
      // Server responded with error status
      const { status, data } = axiosError.response
      const message = data?.detail || data?.message || axiosError.message || 'Server error'

      return {
        status,
        message,
        code: data?.code,
        details: data as Record<string, unknown>,
      }
    } else if (axiosError.request) {
      // Network error
      return {
        status: 0,
        message: 'Network error - please check your connection',
        code: 'NETWORK_ERROR',
      }
    } else {
      // Other error
      return {
        status: 0,
        message: axiosError.message || 'An unexpected error occurred',
        code: 'UNKNOWN_ERROR',
      }
    }
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.client.get<T>(url, config)

    return {
      data: response.data,
      status: response.status,
    }
  }

  async post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.client.post<T>(url, data, config)
    return {
      data: response.data,
      status: response.status,
    }
  }

  async put<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.client.put<T>(url, data, config)
    return {
      data: response.data,
      status: response.status,
    }
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.client.delete<T>(url, config)
    return {
      data: response.data,
      status: response.status,
    }
  }
}

// Global API client instance
export const apiClient = new ApiClient()

// Convenience methods for common patterns
export const api = {
  // Authentication
  auth: {
    login: (credentials: { username: string; password: string }) =>
      apiClient.post('/auth/login', credentials),
    register: (userData: { username: string; email: string; password: string }) =>
      apiClient.post('/auth/register', userData),
    getCurrentUser: () => apiClient.get('/auth/me'),
    logout: () => {
      localStorage.removeItem('authToken')
    },
  },

  // Vocabulary
  vocabulary: {
    search: (query: string, language = 'de', limit = 20) =>
      apiClient.get('/vocabulary/search', {
        params: { query, language, limit },
      }),
    getByLevel: (level: string, language = 'de', skip = 0, limit = 100) =>
      apiClient.get(`/vocabulary/level/${level}`, {
        params: { language, skip, limit },
      }),
    getRandom: (language = 'de', levels?: string[], limit = 10) =>
      apiClient.get('/vocabulary/random', {
        params: { language, levels, limit },
      }),
    markWord: (vocabularyId: number, isKnown: boolean) =>
      apiClient.post('/vocabulary/mark', { vocabulary_id: vocabularyId, is_known: isKnown }),
    bulkMarkWords: (vocabularyIds: number[], isKnown: boolean) =>
      apiClient.post('/vocabulary/mark-bulk', { vocabulary_ids: vocabularyIds, is_known: isKnown }),
    getProgress: (language = 'de') =>
      apiClient.get('/vocabulary/progress', {
        params: { language },
      }),
    getStats: (language = 'de') =>
      apiClient.get('/vocabulary/stats', {
        params: { language },
      }),
  },

  // Videos and processing
  videos: {
    getList: () => apiClient.get('/api/videos'),
    getEpisodes: (series: string) => apiClient.get(`/api/videos/${series}`),
    getStreamUrl: (series: string, episode: string) => {
      const base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const token = localStorage.getItem('authToken')
      const url = `${base}/api/videos/${encodeURIComponent(series)}/${encodeURIComponent(episode)}`
      return token ? `${url}?token=${encodeURIComponent(token)}` : url
    },
  },

  // Processing
  processing: {
    startTranscription: (series: string, episode: string) =>
      apiClient.post('/process/transcribe', { series, episode }),
    getProgress: (taskId: string) => apiClient.get(`/process/progress/${taskId}`),
    prepareEpisode: (series: string, episode: string) =>
      apiClient.post('/process/prepare-episode', { series, episode }),
  },
}
