/**
 * Translation cache store for offline word translations
 * Implements persistent caching with TTL for translation lookups
 */
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { devtools } from 'zustand/middleware'

interface TranslationCacheEntry {
  translation: string
  timestamp: number
  confidence: number
  partOfSpeech?: string
  level?: string
}

interface TranslationCache {
  [word: string]: TranslationCacheEntry
}

interface TranslationStore {
  cache: TranslationCache
  isLoading: Record<string, boolean>
  errors: Record<string, string>

  // Cache operations
  getWordTranslation: (word: string) => TranslationCacheEntry | null
  cacheTranslation: (
    word: string,
    translation: string,
    metadata?: {
      confidence?: number
      partOfSpeech?: string
      level?: string
    }
  ) => void
  isCacheExpired: (word: string) => boolean
  clearCache: () => void
  pruneExpiredCache: () => void

  // Loading state
  setLoading: (word: string, loading: boolean) => void
  isWordLoading: (word: string) => boolean

  // Error handling
  setError: (word: string, error: string) => void
  clearError: (word: string) => void
  getError: (word: string) => string | null
}

const CACHE_TTL_MS = 7 * 24 * 60 * 60 * 1000 // 7 days

export const useTranslationStore = create<TranslationStore>()(
  devtools(
    persist(
      (set, get) => ({
        cache: {},
        isLoading: {},
        errors: {},

        getWordTranslation: (word: string) => {
          const normalizedWord = word.toLowerCase().trim()
          const cached = get().cache[normalizedWord]

          if (!cached) return null

          // Check if cache is expired
          const isExpired = Date.now() - cached.timestamp > CACHE_TTL_MS
          if (isExpired) {
            // Remove expired entry
            set(state => {
              const newCache = { ...state.cache }
              delete newCache[normalizedWord]
              return { cache: newCache }
            })
            return null
          }

          return cached
        },

        cacheTranslation: (word, translation, metadata = {}) => {
          const normalizedWord = word.toLowerCase().trim()

          set(state => ({
            cache: {
              ...state.cache,
              [normalizedWord]: {
                translation,
                timestamp: Date.now(),
                confidence: metadata.confidence ?? 1.0,
                partOfSpeech: metadata.partOfSpeech,
                level: metadata.level,
              },
            },
          }))
        },

        isCacheExpired: (word: string) => {
          const normalizedWord = word.toLowerCase().trim()
          const cached = get().cache[normalizedWord]

          if (!cached) return true

          return Date.now() - cached.timestamp > CACHE_TTL_MS
        },

        clearCache: () => {
          set({ cache: {} })
        },

        pruneExpiredCache: () => {
          const now = Date.now()
          set(state => {
            const newCache: TranslationCache = {}

            Object.entries(state.cache).forEach(([word, entry]) => {
              if (now - entry.timestamp <= CACHE_TTL_MS) {
                newCache[word] = entry
              }
            })

            return { cache: newCache }
          })
        },

        setLoading: (word, loading) => {
          const normalizedWord = word.toLowerCase().trim()
          set(state => ({
            isLoading: {
              ...state.isLoading,
              [normalizedWord]: loading,
            },
          }))
        },

        isWordLoading: (word: string) => {
          const normalizedWord = word.toLowerCase().trim()
          return get().isLoading[normalizedWord] ?? false
        },

        setError: (word, error) => {
          const normalizedWord = word.toLowerCase().trim()
          set(state => ({
            errors: {
              ...state.errors,
              [normalizedWord]: error,
            },
          }))
        },

        clearError: (word: string) => {
          const normalizedWord = word.toLowerCase().trim()
          set(state => {
            const newErrors = { ...state.errors }
            delete newErrors[normalizedWord]
            return { errors: newErrors }
          })
        },

        getError: (word: string) => {
          const normalizedWord = word.toLowerCase().trim()
          return get().errors[normalizedWord] ?? null
        },
      }),
      {
        name: 'langplug-translation-cache',
        partialize: state => ({ cache: state.cache }),
      }
    ),
    {
      name: 'translation-store',
    }
  )
)

// Prune expired cache entries on app startup
useTranslationStore.getState().pruneExpiredCache()

// Selectors for better performance
export const useTranslationCache = () => useTranslationStore(state => state.cache)
export const useTranslationLoading = (word: string) =>
  useTranslationStore(state => state.isLoading[word.toLowerCase().trim()] ?? false)
export const useTranslationError = (word: string) =>
  useTranslationStore(state => state.errors[word.toLowerCase().trim()] ?? null)
