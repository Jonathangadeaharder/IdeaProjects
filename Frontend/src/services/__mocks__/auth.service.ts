import { vi } from 'vitest'

export class AuthService {
  register = vi.fn()
  login = vi.fn()
  logout = vi.fn()
  getCurrentUser = vi.fn()
  refreshToken = vi.fn()
  clearCache = vi.fn()
}

export const authService = new AuthService()