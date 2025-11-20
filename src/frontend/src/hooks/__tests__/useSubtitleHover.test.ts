import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useSubtitleHover } from '../useSubtitleHover'
import { useTranslationStore } from '../../store/useTranslationStore'

// Mock fetch
global.fetch = vi.fn()

describe('useSubtitleHover', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Clear translation store
    act(() => {
      useTranslationStore.setState({ cache: {} })
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('onWordHover', () => {
    it('should return cached translation immediately', async () => {
      // Pre-cache a translation
      act(() => {
        useTranslationStore.getState().cacheTranslation('Haus', 'house', {
          ipa: 'haʊs',
          partOfSpeech: 'noun'
        })
      })

      const { result } = renderHook(() => useSubtitleHover('de'))

      const mockEvent = {
        currentTarget: { getBoundingClientRect: () => ({ left: 100, top: 50, width: 50, height: 20 }) }
      } as any

      await act(async () => {
        await result.current.onWordHover('Haus', mockEvent)
      })

      expect(result.current.hoveredWord).toBe('haus')
      expect(result.current.translationData?.translation).toBe('house')
      expect(result.current.translationData?.metadata.ipa).toBe('haʊs')
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
        currentTarget: { getBoundingClientRect: () => ({ left: 100, top: 50, width: 50, height: 20 }) }
      } as any

      await act(async () => {
        await result.current.onWordHover('Baum', mockEvent)
      })

      await waitFor(() => {
        expect(result.current.translationData?.translation).toBe('tree')
      })

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/vocabulary/word-info/baum'),
        expect.any(Object)
      )
    })

    it('should handle API errors gracefully', async () => {
      ;(fetch as any).mockRejectedValueOnce(new Error('Network error'))

      const { result } = renderHook(() => useSubtitleHover('de'))

      const mockEvent = {
        currentTarget: { getBoundingClientRect: () => ({ left: 100, top: 50, width: 50, height: 20 }) }
      } as any

      await act(async () => {
        await result.current.onWordHover('test', mockEvent)
      })

      await waitFor(() => {
        expect(result.current.error).toContain('Failed to fetch translation')
      })

      expect(result.current.translationData).toBeNull()
    })

    it('should calculate tooltip position from event', async () => {
      act(() => {
        useTranslationStore.getState().cacheTranslation('test', 'Test', {})
      })

      const { result } = renderHook(() => useSubtitleHover('de'))

      const mockEvent = {
        currentTarget: {
          getBoundingClientRect: () => ({ left: 200, top: 100, width: 60, height: 30 })
        }
      } as any

      await act(async () => {
        await result.current.onWordHover('test', mockEvent)
      })

      expect(result.current.tooltipPosition).toBeTruthy()
      expect(result.current.tooltipPosition?.x).toBeGreaterThan(0)
      expect(result.current.tooltipPosition?.y).toBeGreaterThan(0)
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
        currentTarget: { getBoundingClientRect: () => ({ left: 100, top: 50, width: 50, height: 20 }) }
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

    it('should normalize word to lowercase', async () => {
      act(() => {
        useTranslationStore.getState().cacheTranslation('haus', 'house', {})
      })

      const { result } = renderHook(() => useSubtitleHover('de'))

      const mockEvent = {
        currentTarget: { getBoundingClientRect: () => ({ left: 100, top: 50, width: 50, height: 20 }) }
      } as any

      await act(async () => {
        await result.current.onWordHover('HAUS', mockEvent)
      })

      expect(result.current.hoveredWord).toBe('haus')
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
        currentTarget: { getBoundingClientRect: () => ({ left: 100, top: 50, width: 50, height: 20 }) }
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
      expect(cached?.metadata.ipa).toBe('nɔʏ̯')
    })
  })

  describe('onWordLeave', () => {
    it('should clear hovered word and translation data', async () => {
      act(() => {
        useTranslationStore.getState().cacheTranslation('test', 'Test', {})
      })

      const { result } = renderHook(() => useSubtitleHover('de'))

      const mockEvent = {
        currentTarget: { getBoundingClientRect: () => ({ left: 100, top: 50, width: 50, height: 20 }) }
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
        currentTarget: { getBoundingClientRect: () => ({ left: 100, top: 50, width: 50, height: 20 }) }
      } as any

      await act(async () => {
        await result.current.onWordHover('test', mockEvent)
      })

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(
          expect.stringContaining('?language=de'),
          expect.any(Object)
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
        currentTarget: { getBoundingClientRect: () => ({ left: 100, top: 50, width: 50, height: 20 }) }
      } as any

      await act(async () => {
        await result.current.onWordHover('test', mockEvent)
      })

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(
          expect.stringContaining('?language=es'),
          expect.any(Object)
        )
      })
    })
  })
})
