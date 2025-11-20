import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useSubtitleHover } from '../useSubtitleHover'
import { useTranslationStore } from '../../store/useTranslationStore'

// Mock fetch
global.fetch = vi.fn()

describe('useSubtitleHover', () => {
  const originalConsoleError = console.error

  beforeEach(() => {
    vi.clearAllMocks()
    // Suppress expected console.error calls
    console.error = vi.fn()
    // Clear translation store
    act(() => {
      useTranslationStore.setState({ cache: {}, loading: {}, errors: {} })
    })
  })

  afterEach(() => {
    console.error = originalConsoleError
    vi.restoreAllMocks()
  })

  describe('onWordHover', () => {
    it('should return cached translation immediately', async () => {
      // Pre-cache a translation (cache key is lowercase)
      act(() => {
        useTranslationStore.getState().cacheTranslation('haus', 'house', {
          partOfSpeech: 'noun'
        })
      })

      const { result } = renderHook(() => useSubtitleHover('de'))

      const mockEvent = {
        clientX: 100,
        clientY: 50
      } as any

      await act(async () => {
        await result.current.onWordHover('Haus', mockEvent)
      })

      expect(result.current.hoveredWord).toBe('Haus') // Original word, not normalized
      expect(result.current.translationData?.translation).toBe('house')
      expect(result.current.translationData?.partOfSpeech).toBe('noun')
      expect(fetch).not.toHaveBeenCalled()
    })

    it('should fetch translation from API when not cached', async () => {
      const mockResponse = {
        word: 'Baum',
        translation: 'tree',
        ipa: 'baʊm',
        part_of_speech: 'noun',
        example_sentence: 'Der Baum ist groß'
      }

      ;(fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      })

      const { result } = renderHook(() => useSubtitleHover('de'))

      const mockEvent = {
        clientX: 100,
        clientY: 50
      } as any

      await act(async () => {
        await result.current.onWordHover('Baum', mockEvent)
      })

      await waitFor(() => {
        expect(result.current.translationData?.translation).toBe('tree')
      })

      // API uses original word, not normalized
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/vocabulary/word-info/Baum?language=de')
      )
    })

    it('should handle API errors gracefully', async () => {
      ;(fetch as any).mockRejectedValueOnce(new Error('Network error'))

      const { result } = renderHook(() => useSubtitleHover('de'))

      const mockEvent = {
        clientX: 100,
        clientY: 50
      } as any

      await act(async () => {
        await result.current.onWordHover('test', mockEvent)
      })

      await waitFor(() => {
        expect(result.current.translationData?.translation).toBe('Translation unavailable')
      })

      expect(result.current.error).toContain('Network error')
      expect(console.error).toHaveBeenCalledWith(
        expect.stringContaining('[ERROR] Translation fetch failed'),
        expect.any(Error)
      )
    })

    it('should calculate tooltip position from event', async () => {
      act(() => {
        useTranslationStore.getState().cacheTranslation('test', 'Test', {})
      })

      const { result } = renderHook(() => useSubtitleHover('de'))

      const mockEvent = {
        clientX: 200,
        clientY: 100
      } as any

      await act(async () => {
        await result.current.onWordHover('test', mockEvent)
      })

      expect(result.current.tooltipPosition).toBeTruthy()
      expect(result.current.tooltipPosition?.x).toBe(200)
      expect(result.current.tooltipPosition?.y).toBe(100)
    })

    it('should prevent race conditions with rapid hovers', async () => {
      ;(fetch as any).mockImplementation(() =>
        new Promise(resolve =>
          setTimeout(
            () =>
              resolve({
                ok: true,
                json: async () => ({ word: 'test', translation: 'Test' })
              }),
            100
          )
        )
      )

      const { result } = renderHook(() => useSubtitleHover('de'))

      const mockEvent = {
        clientX: 100,
        clientY: 50
      } as any

      // Hover over first word
      act(() => {
        result.current.onWordHover('first', mockEvent)
      })

      // Immediately hover over second word (should cancel first)
      await act(async () => {
        await result.current.onWordHover('second', mockEvent)
      })

      // Wait for resolution
      await waitFor(() => {
        expect(result.current.hoveredWord).toBe('second')
      })

      // Should only have made one successful fetch for 'second'
      expect(result.current.hoveredWord).toBe('second')
    })

    it('should normalize word to lowercase for cache lookup', async () => {
      act(() => {
        useTranslationStore.getState().cacheTranslation('haus', 'house', {})
      })

      const { result } = renderHook(() => useSubtitleHover('de'))

      const mockEvent = {
        clientX: 100,
        clientY: 50
      } as any

      await act(async () => {
        await result.current.onWordHover('HAUS', mockEvent)
      })

      // hoveredWord stores original word, but it successfully finds cached lowercase version
      expect(result.current.hoveredWord).toBe('HAUS')
      expect(result.current.translationData?.translation).toBe('house')
    })

    it('should cache fetched translations', async () => {
      const mockResponse = {
        word: 'neu',
        translation: 'new',
        ipa: 'nɔʏ̯',
        part_of_speech: 'adjective'
      }

      ;(fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      })

      const { result } = renderHook(() => useSubtitleHover('de'))

      const mockEvent = {
        clientX: 100,
        clientY: 50
      } as any

      await act(async () => {
        await result.current.onWordHover('neu', mockEvent)
      })

      await waitFor(() => {
        expect(result.current.translationData?.translation).toBe('new')
      })

      // Check that it's now cached
      const cached = useTranslationStore.getState().getWordTranslation('neu')
      expect(cached?.translation).toBe('new')
      expect(cached?.partOfSpeech).toBe('adjective')
    })
  })

  describe('onWordLeave', () => {
    it('should clear hovered word and translation data', async () => {
      act(() => {
        useTranslationStore.getState().cacheTranslation('test', 'Test', {})
      })

      const { result } = renderHook(() => useSubtitleHover('de'))

      const mockEvent = {
        clientX: 100,
        clientY: 50
      } as any

      // First hover
      await act(async () => {
        await result.current.onWordHover('test', mockEvent)
      })

      expect(result.current.hoveredWord).toBe('test')

      // Then leave
      act(() => {
        result.current.onWordLeave()
      })

      expect(result.current.hoveredWord).toBeNull()
      expect(result.current.translationData).toBeNull()
      expect(result.current.tooltipPosition).toBeNull()
    })
  })

  describe('language parameter', () => {
    it('should use default language (de) when not specified', async () => {
      ;(fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ word: 'test', translation: 'Test' })
      })

      const { result } = renderHook(() => useSubtitleHover())

      const mockEvent = {
        clientX: 100,
        clientY: 50
      } as any

      await act(async () => {
        await result.current.onWordHover('test', mockEvent)
      })

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(
          expect.stringContaining('?language=de')
        )
      })
    })

    it('should use specified language', async () => {
      ;(fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ word: 'test', translation: 'Test' })
      })

      const { result } = renderHook(() => useSubtitleHover('es'))

      const mockEvent = {
        clientX: 100,
        clientY: 50
      } as any

      await act(async () => {
        await result.current.onWordHover('test', mockEvent)
      })

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(
          expect.stringContaining('?language=es')
        )
      })
    })
  })
})
