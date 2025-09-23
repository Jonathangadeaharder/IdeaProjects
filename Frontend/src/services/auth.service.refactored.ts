/**
 * Refactored Auth Service using Repository Pattern
 * This replaces the old auth.service.ts
 */

import { container } from '@/core/di/container'
import type { LoginData, RegisterData, User } from '@/core/clients/auth.client'

export class AuthServiceRefactored {
  private authRepo = container.auth

  async register(data: RegisterData): Promise<User> {
    // Validation
    if (!this.isValidEmail(data.email)) {
      throw new Error('Invalid email format')
    }
    if ((data.password ?? '').length < 8) {
      throw new Error('Password must be at least 8 characters')
    }

    return this.authRepo.register(data)
  }

  async login(data: LoginData): Promise<User> {
    return this.authRepo.login(data)
  }

  async logout(): Promise<void> {
    return this.authRepo.logout()
  }

  async getCurrentUser(): Promise<User | null> {
    return this.authRepo.getCurrentUser()
  }

  async refreshToken(): Promise<boolean> {
    return this.authRepo.refreshToken()
  }

  isAuthenticated(): boolean {
    return this.authRepo.isAuthenticated()
  }

  private isValidEmail(email: string): boolean {
    return /.+@.+\..+/.test(email)
  }
}

// Export singleton instance for backward compatibility
export const authService = new AuthServiceRefactored()

// Export types for convenience
export type { LoginData, RegisterData, User } from '@/core/clients/auth.client'