/**
 * Auth Repository
 * Manages authentication state and operations
 */

import { AuthClient, LoginData, RegisterData, User, AuthResponse } from '../clients/auth.client'
import { tokenStorage } from '@/utils/token-storage'

export class AuthRepository {
  private userCache: User | null = null

  constructor(private authClient: AuthClient) {}

  async login(credentials: LoginData): Promise<User> {
    // Clear any existing session
    this.clearSession()

    // Perform login
    const authResponse = await this.authClient.login(credentials)

    // Store token
    tokenStorage.setToken(authResponse.access_token)
    if (authResponse.expires_in) {
      // Store expiry for reference
      const expiryTime = Date.now() + authResponse.expires_in * 1000
      localStorage.setItem('token_expiry', expiryTime.toString())
    }

    // Fetch and cache user data
    const user = await this.authClient.getCurrentUser(authResponse.access_token)
    this.userCache = user

    return user
  }

  async register(data: RegisterData): Promise<User> {
    const user = await this.authClient.register(data)
    return user
  }

  async logout(): Promise<void> {
    const token = tokenStorage.getToken()

    try {
      if (token) {
        await this.authClient.logout(token)
      }
    } finally {
      this.clearSession()
    }
  }

  async getCurrentUser(forceRefresh: boolean = false): Promise<User | null> {
    // Return cached user if available and not forcing refresh
    if (this.userCache && !forceRefresh) {
      return this.userCache
    }

    const token = tokenStorage.getToken()
    if (!token) {
      return null
    }

    try {
      const user = await this.authClient.getCurrentUser(token)
      this.userCache = user
      return user
    } catch (error) {
      // Token might be invalid
      this.clearSession()
      return null
    }
  }

  async refreshToken(): Promise<boolean> {
    const refreshToken = tokenStorage.getRefreshToken()
    if (!refreshToken) {
      // Clear session when no refresh token is available
      this.clearSession()
      return false
    }

    try {
      const authResponse = await this.authClient.refreshToken(refreshToken)
      tokenStorage.setToken(authResponse.access_token)

      if (authResponse.expires_in) {
        const expiryTime = Date.now() + authResponse.expires_in * 1000
        localStorage.setItem('token_expiry', expiryTime.toString())
      }

      return true
    } catch (error) {
      this.clearSession()
      return false
    }
  }

  isAuthenticated(): boolean {
    const token = tokenStorage.getToken()
    if (!token) return false

    // Check if token is expired
    const expiryStr = localStorage.getItem('token_expiry')
    if (expiryStr) {
      const expiry = parseInt(expiryStr, 10)
      if (Date.now() > expiry) {
        this.clearSession()
        return false
      }
    }

    return true
  }

  private clearSession(): void {
    tokenStorage.clear()
    localStorage.removeItem('token_expiry')
    this.userCache = null
  }

  // Utility method for tests
  getCachedUser(): User | null {
    return this.userCache
  }
}