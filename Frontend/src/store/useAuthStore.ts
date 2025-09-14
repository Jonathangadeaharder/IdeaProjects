import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '@/types'
import { authService } from '@/services/api'

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, name?: string) => Promise<void>
  logout: () => Promise<void>
  checkAuth: () => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true });
        try {
          const response = await authService.login({ username: email, password })
          set({
            user: response.user,
            token: response.token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
          localStorage.setItem('authToken', response.token)
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || error.message;
          set({ isLoading: false, error: errorMessage });
        }
      },

      register: async (email: string, password: string, name?: string) => {
        set({ isLoading: true });
        try {
          await authService.register({ username: email, password })
          set({ isLoading: false, error: null })
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || error.message;
          set({ isLoading: false, error: errorMessage });
        }
      },

      logout: async () => {
        // Clear state synchronously for tests that don't await logout
        localStorage.removeItem('authToken')
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
        });
        try {
          await authService.logout();
        } catch {
          // Ignore API errors on logout
        }
      },

      checkAuth: async () => {
        if (!authService.isAuthenticated()) {
          return;
        }

        set({ isLoading: true });
        try {
          const user = await authService.getCurrentUser();
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error) {
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      },


      clearError: () => {
        set({ error: null });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        token: state.token,
      }),
    }
  )
);
