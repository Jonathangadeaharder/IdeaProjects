/**
 * Auth Client Abstraction
 * Separates HTTP implementation details from business logic
 */

export interface LoginData {
  email: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  expires_in?: number
}

export interface User {
  id: string
  email: string
  username: string
  is_active?: boolean
  is_verified?: boolean
}

export interface AuthClient {
  login(data: LoginData): Promise<AuthResponse>
  register(data: RegisterData): Promise<User>
  logout(token?: string): Promise<void>
  getCurrentUser(token: string): Promise<User>
  refreshToken(refreshToken: string): Promise<AuthResponse>
}

import { HttpClient } from './http.client'

/**
 * Production implementation using real HTTP calls
 */
export class ProductionAuthClient implements AuthClient {
  constructor(private http: HttpClient) {}

  async login(data: LoginData): Promise<AuthResponse> {
    // Production: Use URLSearchParams for form-data
    const formData = new URLSearchParams()
    formData.set('username', data.email) // FastAPI expects username field
    formData.set('password', data.password)

    const response = await this.http.post<AuthResponse>('/api/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })

    return response
  }

  async register(data: RegisterData): Promise<User> {
    const response = await this.http.post<User>('/api/auth/register', data)
    return response
  }

  async logout(token?: string): Promise<void> {
    if (token) {
      await this.http.post('/api/auth/logout', {}, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
    }
  }

  async getCurrentUser(token: string): Promise<User> {
    const response = await this.http.get<User>('/api/auth/me', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
    return response
  }

  async refreshToken(refreshToken: string): Promise<AuthResponse> {
    const response = await this.http.post<AuthResponse>('/api/auth/refresh', {
      refresh_token: refreshToken,
    })
    return response
  }
}

/**
 * Test implementation for unit tests
 * No HTTP calls, no URLSearchParams issues
 */
export class TestAuthClient implements AuthClient {
  private mockUsers: Map<string, User> = new Map()
  private mockTokens: Map<string, User> = new Map()

  constructor() {
    // Set up default test user
    const testUser: User = {
      id: '123',
      email: 'test@example.com',
      username: 'testuser',
      is_active: true,
      is_verified: false,
    }
    this.mockUsers.set('test@example.com', testUser)
    this.mockTokens.set('mock-jwt-token', testUser)
  }

  async login(data: LoginData): Promise<AuthResponse> {
    const user = this.mockUsers.get(data.email)
    if (!user || data.password !== 'TestPassword123!') {
      throw new Error('Invalid credentials')
    }

    return {
      access_token: 'mock-jwt-token',
      token_type: 'bearer',
      expires_in: 3600,
    }
  }

  async register(data: RegisterData): Promise<User> {
    if (this.mockUsers.has(data.email)) {
      throw new Error('Email already registered')
    }

    const newUser: User = {
      id: Math.random().toString(36).substr(2, 9),
      email: data.email,
      username: data.username,
      is_active: true,
      is_verified: false,
    }

    this.mockUsers.set(data.email, newUser)
    return newUser
  }

  async logout(): Promise<void> {
    // Test implementation: just resolve
    return Promise.resolve()
  }

  async getCurrentUser(token: string): Promise<User> {
    const user = this.mockTokens.get(token)
    if (!user) {
      throw new Error('Invalid token')
    }
    return user
  }

  async refreshToken(): Promise<AuthResponse> {
    return {
      access_token: 'refreshed-mock-token',
      token_type: 'bearer',
      expires_in: 3600,
    }
  }

  // Test helper methods
  addMockUser(user: User, password: string = 'TestPassword123!'): void {
    this.mockUsers.set(user.email, user)
  }

  addMockToken(token: string, user: User): void {
    this.mockTokens.set(token, user)
  }

  reset(): void {
    this.mockUsers.clear()
    this.mockTokens.clear()

    // Re-add default test user
    const testUser: User = {
      id: '123',
      email: 'test@example.com',
      username: 'testuser',
      is_active: true,
      is_verified: false,
    }
    this.mockUsers.set('test@example.com', testUser)
    this.mockTokens.set('mock-jwt-token', testUser)
  }
}