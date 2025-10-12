/**
 * Custom hooks for API interactions with error handling and caching
 */
import { useState, useEffect, useCallback, useRef } from 'react'
import { api, ApiResponse } from '@/services/api-client'
import type { ApiError } from '@/services/api-client'
import { useAppStore } from '@/store/useAppStore'

export interface UseApiState<T> {
  data: T | null
  loading: boolean
  error: string | null
  refetch: () => Promise<void>
  reset: () => void
}

export interface UseApiOptions {
  immediate?: boolean
  cache?: boolean
  cacheTtl?: number
  retries?: number
  retryDelay?: number
}

/**
 * Generic hook for API calls with error handling and loading states
 */
export function useApi<T>(
  apiCall: () => Promise<ApiResponse<T>>,
  deps: React.DependencyList = [],
  options: UseApiOptions = {}
): UseApiState<T> {
  const {
    immediate = true,
    cache = false,
    cacheTtl = 5 * 60 * 1000,
    retries = 3,
    retryDelay = 1000,
  } = options

  const [state, setState] = useState<{
    data: T | null
    loading: boolean
    error: string | null
  }>({
    data: null,
    loading: false,
    error: null,
  })

  const setError = useAppStore(state => state.setError)
  const retryCount = useRef(0)
  const cacheRef = useRef<{ data: T; timestamp: number } | null>(null)

  const fetchData = useCallback(async () => {
    // Check cache first
    if (cache && cacheRef.current) {
      const { data, timestamp } = cacheRef.current
      if (Date.now() - timestamp < cacheTtl) {
        setState({ data, loading: false, error: null })
        return
      }
    }

    setState(prev => ({ ...prev, loading: true, error: null }))

    try {
      const response = await apiCall()
      const data = response.data

      // Cache the data
      if (cache) {
        cacheRef.current = { data, timestamp: Date.now() }
      }

      setState({ data, loading: false, error: null })
      retryCount.current = 0
    } catch (error) {
      const apiError = error as ApiError
      const errorMessage = apiError.message || 'An unexpected error occurred'

      setState(prev => ({ ...prev, loading: false, error: errorMessage }))
      setError(errorMessage)

      // Retry logic
      if (retryCount.current < retries && apiError.status !== 401 && apiError.status !== 403) {
        retryCount.current++
        setTimeout(() => {
          fetchData()
        }, retryDelay * retryCount.current)
      }
    }
  }, [apiCall, cache, cacheTtl, retries, retryDelay, setError])

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null })
    retryCount.current = 0
    cacheRef.current = null
  }, [])

  useEffect(() => {
    if (immediate) {
      fetchData()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fetchData, immediate, ...deps]) // Spread deps is intentional - controlled by caller

  return {
    ...state,
    refetch: fetchData,
    reset,
  }
}

/**
 * Hook for authentication-related API calls
 */
export function useAuth() {
  const setError = useAppStore(state => state.setError)

  const login = useCallback(
    async (credentials: { username: string; password: string }) => {
      try {
        const response = await api.auth.login(credentials)
        const { access_token } = response.data as { access_token: string }
        localStorage.setItem('authToken', access_token)
        return response.data
      } catch (error) {
        const apiError = error as ApiError
        setError(apiError.message)
        throw error
      }
    },
    [setError]
  )

  const register = useCallback(
    async (userData: { username: string; email: string; password: string }) => {
      try {
        const response = await api.auth.register(userData)
        return response.data
      } catch (error) {
        const apiError = error as ApiError
        setError(apiError.message)
        throw error
      }
    },
    [setError]
  )

  const logout = useCallback(() => {
    api.auth.logout()
    localStorage.removeItem('authToken')
  }, [])

  const getCurrentUser = useApi(() => api.auth.getCurrentUser(), [], {
    cache: true,
    cacheTtl: 60000,
  })

  return {
    login,
    register,
    logout,
    currentUser: getCurrentUser,
  }
}

/**
 * Hook for searching vocabulary words
 */
export function useVocabularySearch(query: string, language = 'de', limit = 20) {
  return useApi(() => api.vocabulary.search(query, language, limit), [query, language, limit], {
    cache: true,
    cacheTtl: 10 * 60 * 1000,
    immediate: !!query,
  })
}

/**
 * Hook for getting words by level
 */
export function useWordsByLevel(level: string, language = 'de') {
  return useApi(() => api.vocabulary.getByLevel(level, language), [level, language], {
    cache: true,
    cacheTtl: 30 * 60 * 1000,
  })
}

/**
 * Hook for getting random words
 */
export function useRandomWords(language = 'de', levels?: string[], limit = 10) {
  return useApi(
    () => api.vocabulary.getRandom(language, levels, limit),
    [language, JSON.stringify(levels), limit],
    { cache: true, cacheTtl: 5 * 60 * 1000 }
  )
}

/**
 * Hook for getting user progress
 */
export function useUserProgress(language = 'de') {
  return useApi(() => api.vocabulary.getProgress(language), [language], {
    cache: true,
    cacheTtl: 30 * 1000,
  })
}

/**
 * Hook for getting vocabulary stats
 */
export function useVocabularyStats(language = 'de') {
  return useApi(() => api.vocabulary.getStats(language), [language], {
    cache: true,
    cacheTtl: 60 * 1000,
  })
}

/**
 * Hook for vocabulary mutations (mark/bulk mark)
 */
export function useVocabularyMutations() {
  const markWord = useCallback(async (vocabularyId: number, isKnown: boolean) => {
    try {
      const response = await api.vocabulary.markWord(vocabularyId, isKnown)
      return response.data
    } catch (error) {
      const apiError = error as ApiError
      throw new Error(apiError.message)
    }
  }, [])

  const bulkMarkWords = useCallback(async (vocabularyIds: number[], isKnown: boolean) => {
    try {
      const response = await api.vocabulary.bulkMarkWords(vocabularyIds, isKnown)
      return response.data
    } catch (error) {
      const apiError = error as ApiError
      throw new Error(apiError.message)
    }
  }, [])

  return {
    markWord,
    bulkMarkWords,
  }
}

/**
 * Hook for getting processing progress
 */
export function useProcessingProgress(taskId: string) {
  return useApi(() => api.processing.getProgress(taskId), [taskId], { immediate: !!taskId })
}

/**
 * Hook for processing mutations (start transcription, prepare episode)
 */
export function useProcessingMutations() {
  const startTranscription = useCallback(async (series: string, episode: string) => {
    try {
      const response = await api.processing.startTranscription(series, episode)
      return response.data
    } catch (error) {
      const apiError = error as ApiError
      throw new Error(apiError.message)
    }
  }, [])

  const prepareEpisode = useCallback(async (series: string, episode: string) => {
    try {
      const response = await api.processing.prepareEpisode(series, episode)
      return response.data
    } catch (error) {
      const apiError = error as ApiError
      throw new Error(apiError.message)
    }
  }, [])

  return {
    startTranscription,
    prepareEpisode,
  }
}

/**
 * Hook for getting video list
 */
export function useVideoList() {
  return useApi(() => api.videos.getList(), [], { cache: true, cacheTtl: 10 * 60 * 1000 })
}

/**
 * Hook for getting episodes for a series
 */
export function useEpisodes(series: string) {
  return useApi(() => api.videos.getEpisodes(series), [series], {
    cache: true,
    cacheTtl: 10 * 60 * 1000,
    immediate: !!series,
  })
}

/**
 * Hook for video utilities (get stream URL)
 */
export function useVideoUtils() {
  const getStreamUrl = useCallback(
    (series: string, episode: string) => api.videos.getStreamUrl(series, episode),
    []
  )

  return {
    getStreamUrl,
  }
}

/**
 * Hook for handling async operations with loading and error states
 */
export function useAsyncOperation<T extends (...args: never[]) => Promise<unknown>>(
  operation: T
): [T, { loading: boolean; error: string | null }] {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const wrappedOperation = useCallback(
    async (...args: Parameters<T>) => {
      setLoading(true)
      setError(null)

      try {
        const result = await operation(...args)
        return result
      } catch (error) {
        const apiError = error as ApiError
        const errorMessage = apiError.message || 'An unexpected error occurred'
        setError(errorMessage)
        throw error
      } finally {
        setLoading(false)
      }
    },
    [operation]
  ) as T

  return [wrappedOperation, { loading, error }]
}
