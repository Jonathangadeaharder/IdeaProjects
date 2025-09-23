/**
 * HTTP Client Abstraction
 * Wraps axios for easier mocking and testing
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { tokenStorage } from '@/utils/token-storage'

export class HttpClient {
  private client: AxiosInstance

  constructor(baseURL: string) {
    this.client = axios.create({
      baseURL,
      timeout: 30000,
    })

    // Add auth token to requests
    this.client.interceptors.request.use((config) => {
      const token = tokenStorage.getToken()
      if (token && !config.headers.Authorization) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })

    // Handle token refresh on 401
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Token expired, try to refresh
          const refreshToken = tokenStorage.getRefreshToken()
          if (refreshToken) {
            try {
              const response = await this.post<{ access_token: string }>('/api/auth/refresh', {
                refresh_token: refreshToken,
              })
              tokenStorage.setToken(response.access_token)

              // Retry original request
              error.config.headers.Authorization = `Bearer ${response.access_token}`
              return this.client.request(error.config)
            } catch (refreshError) {
              tokenStorage.clear()
              window.location.href = '/login'
            }
          }
        }
        return Promise.reject(error)
      }
    )
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<T>(url, config)
    return response.data
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<T>(url, data, config)
    return response.data
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<T>(url, data, config)
    return response.data
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<T>(url, config)
    return response.data
  }

  async patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.patch<T>(url, data, config)
    return response.data
  }
}