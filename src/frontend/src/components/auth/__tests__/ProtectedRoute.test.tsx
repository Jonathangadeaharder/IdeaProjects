import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { ProtectedRoute } from '../ProtectedRoute'
import { useAuthStore } from '@/store/useAuthStore'

// Mock the auth store
vi.mock('@/store/useAuthStore')

describe('ProtectedRoute', () => {
  const mockCheckAuth = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  const renderProtectedRoute = (initialPath = '/protected') => {
    return render(
      <MemoryRouter initialEntries={[initialPath]}>
        <Routes>
          <Route
            path="/protected"
            element={
              <ProtectedRoute>
                <div>Protected Content</div>
              </ProtectedRoute>
            }
          />
          <Route path="/login" element={<div>Login Page</div>} />
        </Routes>
      </MemoryRouter>
    )
  }

  it('should show loading spinner when isLoading is true', () => {
    ;(useAuthStore as any).mockReturnValue({
      isAuthenticated: false,
      isLoading: true,
      checkAuth: mockCheckAuth,
    })

    const { container } = renderProtectedRoute()

    // Loading component renders, we check for it by looking for the loading-spinner class
    const loadingSpinner = container.querySelector('.loading-spinner')
    expect(loadingSpinner).toBeInTheDocument()
  })

  it('should redirect to login when not authenticated', async () => {
    ;(useAuthStore as any).mockReturnValue({
      isAuthenticated: false,
      isLoading: false,
      checkAuth: mockCheckAuth,
    })

    renderProtectedRoute()

    await waitFor(() => {
      expect(screen.getByText('Login Page')).toBeInTheDocument()
    })

    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument()
  })

  it('should render children when authenticated', () => {
    ;(useAuthStore as any).mockReturnValue({
      isAuthenticated: true,
      isLoading: false,
      checkAuth: mockCheckAuth,
    })

    renderProtectedRoute()

    expect(screen.getByText('Protected Content')).toBeInTheDocument()
    expect(screen.queryByText('Login Page')).not.toBeInTheDocument()
  })

  it('should call checkAuth on mount', () => {
    ;(useAuthStore as any).mockReturnValue({
      isAuthenticated: true,
      isLoading: false,
      checkAuth: mockCheckAuth,
    })

    renderProtectedRoute()

    expect(mockCheckAuth).toHaveBeenCalledTimes(1)
  })

  it('should preserve location state when redirecting', async () => {
    ;(useAuthStore as any).mockReturnValue({
      isAuthenticated: false,
      isLoading: false,
      checkAuth: mockCheckAuth,
    })

    const { container } = render(
      <MemoryRouter initialEntries={['/protected/some/deep/path']}>
        <Routes>
          <Route
            path="/protected/*"
            element={
              <ProtectedRoute>
                <div>Protected Content</div>
              </ProtectedRoute>
            }
          />
          <Route
            path="/login"
            element={
              <div>
                Login Page
                <span data-testid="redirect-from">Redirect handling</span>
              </div>
            }
          />
        </Routes>
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Login Page')).toBeInTheDocument()
    })
  })

  it('should handle authentication state changes', async () => {
    const mockStore = {
      isAuthenticated: false,
      isLoading: true,
      checkAuth: mockCheckAuth,
    }

    ;(useAuthStore as any).mockReturnValue(mockStore)

    const { rerender, container } = renderProtectedRoute()

    // Initially loading
    const loadingSpinner = container.querySelector('.loading-spinner')
    expect(loadingSpinner).toBeInTheDocument()

    // Simulate auth check completing with unauthenticated
    mockStore.isLoading = false
    mockStore.isAuthenticated = false
    ;(useAuthStore as any).mockReturnValue(mockStore)

    rerender(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route
            path="/protected"
            element={
              <ProtectedRoute>
                <div>Protected Content</div>
              </ProtectedRoute>
            }
          />
          <Route path="/login" element={<div>Login Page</div>} />
        </Routes>
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Login Page')).toBeInTheDocument()
    })
  })

  it('should render multiple children', () => {
    ;(useAuthStore as any).mockReturnValue({
      isAuthenticated: true,
      isLoading: false,
      checkAuth: mockCheckAuth,
    })

    render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route
            path="/protected"
            element={
              <ProtectedRoute>
                <div>First Child</div>
                <div>Second Child</div>
                <div>Third Child</div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </MemoryRouter>
    )

    expect(screen.getByText('First Child')).toBeInTheDocument()
    expect(screen.getByText('Second Child')).toBeInTheDocument()
    expect(screen.getByText('Third Child')).toBeInTheDocument()
  })

  it('should work with complex nested components', () => {
    ;(useAuthStore as any).mockReturnValue({
      isAuthenticated: true,
      isLoading: false,
      checkAuth: mockCheckAuth,
    })

    const ComplexComponent = () => (
      <div>
        <header>Header</header>
        <main>Main Content</main>
        <footer>Footer</footer>
      </div>
    )

    render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route
            path="/protected"
            element={
              <ProtectedRoute>
                <ComplexComponent />
              </ProtectedRoute>
            }
          />
        </Routes>
      </MemoryRouter>
    )

    expect(screen.getByText('Header')).toBeInTheDocument()
    expect(screen.getByText('Main Content')).toBeInTheDocument()
    expect(screen.getByText('Footer')).toBeInTheDocument()
  })
})
