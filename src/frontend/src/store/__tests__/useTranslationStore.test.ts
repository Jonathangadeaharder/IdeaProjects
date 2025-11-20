import { describe, it, expect, beforeEach, vi } from 'vitest'
import { act } from '@testing-library/react'
import { useTranslationStore } from '../useTranslationStore'

describe('useTranslationStore', () => {
  beforeEach(() => {
    // Clear the store before each test
    act(() => {
      useTranslationStore.setState({ cache: {} })
    })
    // Clear localStorage
    localStorage.clear()
  })

  describe('cacheTranslation', () => {
    it('should cache a word translation', () => {
      const store = useTranslationStore.getState()

      act(() => {
        store.cacheTranslation('Haus', 'house', { partOfSpeech: 'noun' })
      })

      const cached = store.getWordTranslation('Haus')
      expect(cached).toBeTruthy()
      expect(cached?.translation).toBe('house')
      expect(cached?.partOfSpeech).toBe('noun')
    })

    it('should cache with lowercase key', () => {
      const store = useTranslationStore.getState()

      act(() => {
        store.cacheTranslation('HAUS', 'house', {})
      })

      const cached = store.getWordTranslation('haus')
      expect(cached).toBeTruthy()
      expect(cached?.translation).toBe('house')
    })

    it('should update timestamp when caching', () => {
      const store = useTranslationStore.getState()
      const now = Date.now()
      vi.setSystemTime(now)

      act(() => {
        store.cacheTranslation('test', 'test translation', {})
      })

      const cached = store.getWordTranslation('test')
      expect(cached?.timestamp).toBe(now)
    })
  })

  describe('getWordTranslation', () => {
    it('should return null for uncached word', () => {
      const store = useTranslationStore.getState()
      const cached = store.getWordTranslation('nonexistent')
      expect(cached).toBeNull()
    })

    it('should return cached translation', () => {
      const store = useTranslationStore.getState()

      act(() => {
        store.cacheTranslation('hello', 'hallo', { partOfSpeech: 'interjection' })
      })

      const cached = store.getWordTranslation('hello')
      expect(cached?.translation).toBe('hallo')
      expect(cached?.partOfSpeech).toBe('interjection')
    })

    it('should remove expired translations', () => {
      const oldTime = Date.now() - (8 * 24 * 60 * 60 * 1000) // 8 days ago (past 7-day TTL)

      // Directly set an expired entry in the cache
      act(() => {
        useTranslationStore.setState({
          cache: {
            old: {
              translation: 'alt',
              timestamp: oldTime,
              confidence: 1.0,
            },
          },
        })
      })

      const store = useTranslationStore.getState()
      const cached = store.getWordTranslation('old')
      expect(cached).toBeNull()
    })

    it('should keep non-expired translations', () => {
      const recentTime = Date.now() - (3 * 24 * 60 * 60 * 1000) // 3 days ago (within 7-day TTL)

      // Directly set a non-expired entry in the cache
      act(() => {
        useTranslationStore.setState({
          cache: {
            recent: {
              translation: 'kürzlich',
              timestamp: recentTime,
              confidence: 1.0,
            },
          },
        })
      })

      const store = useTranslationStore.getState()
      const cached = store.getWordTranslation('recent')
      expect(cached).toBeTruthy()
      expect(cached?.translation).toBe('kürzlich')
    })
  })

  describe('loading state', () => {
    it('should set loading state for a word', () => {
      const store = useTranslationStore.getState()

      act(() => {
        store.setLoading('test', true)
      })

      expect(store.isWordLoading('test')).toBe(true)
    })

    it('should clear loading state', () => {
      const store = useTranslationStore.getState()

      act(() => {
        store.setLoading('test', true)
        store.setLoading('test', false)
      })

      expect(store.isWordLoading('test')).toBe(false)
    })

    it('should return false for non-loading word', () => {
      const store = useTranslationStore.getState()
      expect(store.isWordLoading('nonexistent')).toBe(false)
    })
  })

  describe('error state', () => {
    it('should set error for a word', () => {
      const store = useTranslationStore.getState()

      act(() => {
        store.setError('test', 'Translation failed')
      })

      expect(store.getError('test')).toBe('Translation failed')
    })

    it('should clear error by calling clearError', () => {
      const store = useTranslationStore.getState()

      act(() => {
        store.setError('test', 'Error')
        store.clearError('test')
      })

      expect(store.getError('test')).toBeNull()
    })

    it('should return null for word with no error', () => {
      const store = useTranslationStore.getState()
      expect(store.getError('nonexistent')).toBeNull()
    })
  })

  describe('cache management', () => {
    it('should prune expired entries from cache', () => {
      const oldTime = Date.now() - (8 * 24 * 60 * 60 * 1000) // 8 days ago
      const recentTime = Date.now() - (1 * 24 * 60 * 60 * 1000) // 1 day ago

      act(() => {
        useTranslationStore.setState({
          cache: {
            old: { translation: 'alt', timestamp: oldTime, confidence: 1.0 },
            recent: { translation: 'neu', timestamp: recentTime, confidence: 1.0 },
          },
        })
      })

      const store = useTranslationStore.getState()

      act(() => {
        store.pruneExpiredCache()
      })

      const { cache } = store
      expect(cache.old).toBeUndefined()
      expect(cache.recent).toBeTruthy()
    })

    it('should clear all cache', () => {
      act(() => {
        useTranslationStore.getState().cacheTranslation('test1', 'translation1', {})
        useTranslationStore.getState().cacheTranslation('test2', 'translation2', {})
      })

      const store = useTranslationStore.getState()

      act(() => {
        store.clearCache()
      })

      expect(store.cache).toEqual({})
    })
  })
})
