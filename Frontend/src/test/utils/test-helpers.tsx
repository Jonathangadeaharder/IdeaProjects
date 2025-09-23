/**
 * Test Utilities and Helpers
 * Provides clean testing utilities for the new architecture
 */

import React from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, MemoryRouter } from 'react-router-dom'
import { vi } from 'vitest'

// Import DI container and types
import { DIContainer, DIProvider } from '@/core/di/container'
import { TestAuthClient } from '@/core/clients/auth.client'
import { AuthRepository } from '@/core/repositories/auth.repository'
import { VideoRepository } from '@/core/repositories/video.repository'
import { ProfileRepository } from '@/core/repositories/profile.repository'
import { VocabularyRepository } from '@/core/repositories/vocabulary.repository'
import { HttpClient } from '@/core/clients/http.client'

/**
 * Create a mock DI container for testing
 */
export const createMockContainer = (): DIContainer => {
  const mockHttpClient = {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    patch: vi.fn(),
  } as unknown as HttpClient

  const testAuthClient = new TestAuthClient()

  return {
    authClient: testAuthClient,
    httpClient: mockHttpClient,
    auth: new AuthRepository(testAuthClient),
    videos: new VideoRepository(mockHttpClient),
    profile: new ProfileRepository(mockHttpClient),
    vocabulary: new VocabularyRepository(mockHttpClient),
  }
}

/**
 * Custom render function with all providers
 */
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  container?: DIContainer
  initialRoute?: string
  queryClient?: QueryClient
}

export const renderWithProviders = (
  ui: React.ReactElement,
  {
    container,
    initialRoute = '/',
    queryClient,
    ...renderOptions
  }: CustomRenderOptions = {}
) => {
  const testContainer = container || createMockContainer()
  const testQueryClient = queryClient || new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })

  const AllProviders: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <QueryClientProvider client={testQueryClient}>
      <DIProvider container={testContainer}>
        <MemoryRouter initialEntries={[initialRoute]}>
          {children}
        </MemoryRouter>
      </DIProvider>
    </QueryClientProvider>
  )

  return {
    ...render(ui, { wrapper: AllProviders, ...renderOptions }),
    container: testContainer,
    queryClient: testQueryClient,
  }
}

/**
 * Factory functions for creating test data
 */
export const createTestUser = (overrides?: Partial<any>) => ({
  id: '123',
  email: 'test@example.com',
  username: 'testuser',
  is_active: true,
  is_verified: false,
  ...overrides,
})

export const createTestVideo = (overrides?: Partial<any>) => ({
  id: 'video-123',
  series: 'TestSeries',
  episode: 'S01E01',
  title: 'Test Episode',
  duration: 1800,
  thumbnail: '/thumbnails/test.jpg',
  subtitles_available: true,
  processing_status: 'completed' as const,
  vocabulary_count: 250,
  difficulty_level: 'intermediate',
  ...overrides,
})

export const createTestTask = (overrides?: Partial<any>) => ({
  task_id: 'task-123',
  status: 'processing' as const,
  current_step: 'transcription',
  steps_completed: 2,
  total_steps: 5,
  progress_percentage: 40,
  message: 'Processing video...',
  ...overrides,
})

export const createTestProfile = (overrides?: Partial<any>) => ({
  id: '123',
  email: 'test@example.com',
  username: 'testuser',
  native_language: 'en',
  target_language: 'de',
  difficulty_level: 'intermediate' as const,
  daily_goal: 30,
  streak_count: 7,
  total_study_time: 420,
  words_learned: 150,
  created_at: '2025-01-01T00:00:00Z',
  updated_at: '2025-01-15T00:00:00Z',
  ...overrides,
})

export const createTestWord = (overrides?: Partial<any>) => ({
  id: 'word-123',
  word: 'Haus',
  translation: 'house',
  frequency: 1000,
  difficulty: 'easy' as const,
  is_known: false,
  times_seen: 5,
  last_seen: '2025-01-15T00:00:00Z',
  context_examples: ['Das ist mein Haus.', 'Ein großes Haus.'],
  ...overrides,
})

/**
 * Mock service builders
 */
export const mockAuthRepository = () => {
  const mock = {
    login: vi.fn().mockResolvedValue(createTestUser()),
    register: vi.fn().mockResolvedValue(createTestUser()),
    logout: vi.fn().mockResolvedValue(undefined),
    getCurrentUser: vi.fn().mockResolvedValue(createTestUser()),
    refreshToken: vi.fn().mockResolvedValue(true),
    isAuthenticated: vi.fn().mockReturnValue(true),
    getCachedUser: vi.fn().mockReturnValue(createTestUser()),
  }
  return mock
}

export const mockVideoRepository = () => {
  const mock = {
    getAll: vi.fn().mockResolvedValue([createTestVideo()]),
    getById: vi.fn().mockResolvedValue(createTestVideo()),
    getBySeries: vi.fn().mockResolvedValue([createTestVideo()]),
    getByEpisode: vi.fn().mockResolvedValue(createTestVideo()),
    startProcessing: vi.fn().mockResolvedValue(createTestTask()),
    getProcessingStatus: vi.fn().mockResolvedValue(createTestTask()),
    uploadVideo: vi.fn().mockResolvedValue(createTestVideo()),
    deleteVideo: vi.fn().mockResolvedValue(undefined),
    clearCache: vi.fn(),
  }
  return mock
}

/**
 * Wait for async operations
 */
export const waitForAsync = () => new Promise(resolve => setTimeout(resolve, 0))

/**
 * Mock fetch for tests
 */
export const mockFetch = (responses: Array<{ url: string | RegExp; response: any; status?: number }>) => {
  const fetch = vi.fn()

  responses.forEach(({ url, response, status = 200 }) => {
    fetch.mockImplementation((requestUrl: string) => {
      const matches = typeof url === 'string' ? requestUrl.includes(url) : url.test(requestUrl)
      if (matches) {
        return Promise.resolve({
          ok: status >= 200 && status < 300,
          status,
          json: () => Promise.resolve(response),
          text: () => Promise.resolve(JSON.stringify(response)),
        })
      }
      return Promise.reject(new Error(`No mock found for ${requestUrl}`))
    })
  })

  global.fetch = fetch as any
  return fetch
}