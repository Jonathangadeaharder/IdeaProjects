import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useGameStore } from '../useGameStore'
import { vocabularyService } from '@/services/api'
import type { VocabularyWord, VideoSegment } from '@/types'

// Mock the vocabulary service
vi.mock('@/services/api', () => ({
  vocabularyService: {
    getBlockingWords: vi.fn(),
    markWordAsKnown: vi.fn()
  }
}))

describe('useGameStore', () => {
  const mockWords: VocabularyWord[] = [
    {
      id: '1',
      word: 'hello',
      translation: 'hola',
      difficulty_level: 'beginner',
      known: false,
      context: 'Hello, how are you?',
      timestamp: 10.5
    },
    {
      id: '2',
      word: 'goodbye',
      translation: 'adiós',
      difficulty_level: 'beginner',
      known: false,
      context: 'Goodbye, see you later!',
      timestamp: 25.8
    },
    {
      id: '3',
      word: 'sophisticated',
      translation: 'sofisticado',
      difficulty_level: 'advanced',
      known: true,
      context: 'A sophisticated approach',
      timestamp: 45.2
    }
  ]

  const mockSegments: VideoSegment[] = [
    {
      start: 0,
      end: 300,
      text: 'First segment with basic vocabulary',
      words: mockWords.slice(0, 2)
    },
    {
      start: 300,
      end: 600,
      text: 'Second segment with advanced vocabulary',
      words: mockWords.slice(2)
    }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    // Reset store state
    useGameStore.getState().resetGame()
  })

  describe('Initial State', () => {
    it('has correct initial state', () => {
      const { result } = renderHook(() => useGameStore())

      expect(result.current.gameSession).toBeNull()
      expect(result.current.currentWords).toEqual([])
      expect(result.current.currentWordIndex).toBe(0)
      expect(result.current.showSubtitles).toBe(false)
      expect(result.current.isProcessing).toBe(false)
    })
  })

  describe('startGame', () => {
    it('initializes game session with video path', () => {
      const { result } = renderHook(() => useGameStore())

      act(() => {
        result.current.startGame('test-video.mp4')
      })

      expect(result.current.gameSession).toEqual({
        video_path: 'test-video.mp4',
        current_segment: 0,
        segments: [],
        user_progress: {},
        completed: false
      })
      expect(result.current.currentWords).toEqual([])
      expect(result.current.currentWordIndex).toBe(0)
      expect(result.current.showSubtitles).toBe(false)
      expect(result.current.isProcessing).toBe(false)
    })

    it('resets previous game state', () => {
      const { result } = renderHook(() => useGameStore())

      // Set some previous state
      act(() => {
        result.current.startGame('previous-video.mp4')
      })

      // Start new game
      act(() => {
        result.current.startGame('new-video.mp4')
      })

      expect(result.current.gameSession?.video_path).toBe('new-video.mp4')
      expect(result.current.currentWords).toEqual([])
      expect(result.current.currentWordIndex).toBe(0)
    })
  })

  describe('loadSegmentWords', () => {
    it('loads words for segment and updates state', async () => {
      const { result } = renderHook(() => useGameStore())

      // Mock API response
      vi.mocked(vocabularyService.getBlockingWords).mockResolvedValue(mockWords.slice(0, 2))

      // Start game first
      act(() => {
        result.current.startGame('test-video.mp4')
      })

      // Load segment words
      await act(async () => {
        await result.current.loadSegmentWords(0)
      })

      expect(vocabularyService.getBlockingWords).toHaveBeenCalledWith('test-video.mp4', 0, 300)
      expect(result.current.currentWords).toEqual(mockWords.slice(0, 2))
      expect(result.current.currentWordIndex).toBe(0)
      expect(result.current.isProcessing).toBe(false)
    })

    it('sets processing state during API call', async () => {
      const { result } = renderHook(() => useGameStore())

      // Mock slow API response
      let resolvePromise: (value: VocabularyWord[]) => void
      const apiPromise = new Promise<VocabularyWord[]>((resolve) => {
        resolvePromise = resolve
      })
      vi.mocked(vocabularyService.getBlockingWords).mockReturnValue(apiPromise)

      act(() => {
        result.current.startGame('test-video.mp4')
      })

      // Start loading and check processing state
      let loadPromise: Promise<void>
      act(() => {
        loadPromise = result.current.loadSegmentWords(0)
      })

      // Check processing state is true
      expect(result.current.isProcessing).toBe(true)

      // Resolve API call
      resolvePromise!(mockWords.slice(0, 2))
      await act(async () => {
        await loadPromise!
      })

      // Check processing state is false
      expect(result.current.isProcessing).toBe(false)
    })

    it('handles API errors gracefully', async () => {
      const { result } = renderHook(() => useGameStore())

      // Mock API error
      vi.mocked(vocabularyService.getBlockingWords).mockRejectedValue(new Error('API Error'))

      act(() => {
        result.current.startGame('test-video.mp4')
      })

      await act(async () => {
        await result.current.loadSegmentWords(0)
      })

      expect(result.current.isProcessing).toBe(false)
      expect(result.current.currentWords).toEqual([])
    })

    it('does nothing if no game session exists', async () => {
      const { result } = renderHook(() => useGameStore())

      await act(async () => {
        await result.current.loadSegmentWords(0)
      })

      expect(vocabularyService.getBlockingWords).not.toHaveBeenCalled()
      expect(result.current.isProcessing).toBe(false)
    })
  })

  describe('markWordKnown', () => {
    it('marks word as known and updates API', async () => {
      const { result } = renderHook(() => useGameStore())

      vi.mocked(vocabularyService.markWordAsKnown).mockResolvedValue(undefined)

      act(() => {
        result.current.startGame('test-video.mp4')
      })

      await act(async () => {
        await result.current.markWordKnown('hello', true)
      })

      expect(vocabularyService.markWordAsKnown).toHaveBeenCalledWith('hello', true)
    })

    it('marks word as unknown', async () => {
      const { result } = renderHook(() => useGameStore())

      vi.mocked(vocabularyService.markWordAsKnown).mockResolvedValue(undefined)

      act(() => {
        result.current.startGame('test-video.mp4')
      })

      await act(async () => {
        await result.current.markWordKnown('sophisticated', false)
      })

      expect(vocabularyService.markWordAsKnown).toHaveBeenCalledWith('sophisticated', false)
    })

    it('handles marking errors gracefully', async () => {
      const { result } = renderHook(() => useGameStore())

      vi.mocked(vocabularyService.markWordAsKnown).mockRejectedValue(new Error('Mark failed'))

      act(() => {
        result.current.startGame('test-video.mp4')
      })

      // Should not throw
      await act(async () => {
        await result.current.markWordKnown('hello', true)
      })

      expect(vocabularyService.markWordAsKnown).toHaveBeenCalledWith('hello', true)
    })
  })

  describe('nextWord', () => {
    it('advances to next word in list', async () => {
      const { result } = renderHook(() => useGameStore())

      vi.mocked(vocabularyService.getBlockingWords).mockResolvedValue(mockWords)

      act(() => {
        result.current.startGame('test-video.mp4')
      })

      await act(async () => {
        await result.current.loadSegmentWords(0)
      })

      expect(result.current.currentWordIndex).toBe(0)

      act(() => {
        result.current.nextWord()
      })

      expect(result.current.currentWordIndex).toBe(1)

      act(() => {
        result.current.nextWord()
      })

      expect(result.current.currentWordIndex).toBe(2)
    })

    it('does not advance beyond last word', async () => {
      const { result } = renderHook(() => useGameStore())

      vi.mocked(vocabularyService.getBlockingWords).mockResolvedValue(mockWords)

      act(() => {
        result.current.startGame('test-video.mp4')
      })

      await act(async () => {
        await result.current.loadSegmentWords(0)
      })

      // Advance to last word
      act(() => {
        result.current.nextWord()
        result.current.nextWord()
      })

      expect(result.current.currentWordIndex).toBe(2)

      // Try to advance beyond
      act(() => {
        result.current.nextWord()
      })

      expect(result.current.currentWordIndex).toBe(2)
    })
  })

  describe('toggleSubtitles', () => {
    it('toggles subtitle visibility', () => {
      const { result } = renderHook(() => useGameStore())

      expect(result.current.showSubtitles).toBe(false)

      act(() => {
        result.current.toggleSubtitles()
      })

      expect(result.current.showSubtitles).toBe(true)

      act(() => {
        result.current.toggleSubtitles()
      })

      expect(result.current.showSubtitles).toBe(false)
    })
  })

  describe('nextSegment', () => {
    it('advances to next segment and loads words', async () => {
      const { result } = renderHook(() => useGameStore())

      // Mock different words for each segment
      vi.mocked(vocabularyService.getBlockingWords)
        .mockResolvedValueOnce(mockWords.slice(0, 2))  // First segment
        .mockResolvedValueOnce(mockWords.slice(2))     // Second segment

      act(() => {
        result.current.startGame('test-video.mp4')
      })

      // Load first segment
      await act(async () => {
        await result.current.loadSegmentWords(0)
      })

      expect(result.current.currentWords).toEqual(mockWords.slice(0, 2))

      // Move to next segment
      await act(async () => {
        await result.current.nextSegment()
      })

      expect(result.current.gameSession?.current_segment).toBe(1)
      expect(result.current.currentWords).toEqual(mockWords.slice(2))
      expect(result.current.currentWordIndex).toBe(0)
    })

    it('handles segment loading errors', async () => {
      const { result } = renderHook(() => useGameStore())

      vi.mocked(vocabularyService.getBlockingWords)
        .mockResolvedValueOnce(mockWords)
        .mockRejectedValueOnce(new Error('Segment load failed'))

      act(() => {
        result.current.startGame('test-video.mp4')
      })

      await act(async () => {
        await result.current.loadSegmentWords(0)
      })

      // Should not throw
      await act(async () => {
        await result.current.nextSegment()
      })

      expect(result.current.gameSession?.current_segment).toBe(1)
    })

    it('does nothing if no game session exists', async () => {
      const { result } = renderHook(() => useGameStore())

      await act(async () => {
        await result.current.nextSegment()
      })

      expect(vocabularyService.getBlockingWords).not.toHaveBeenCalled()
    })
  })

  describe('resetGame', () => {
    it('resets all game state to initial values', async () => {
      const { result } = renderHook(() => useGameStore())

      vi.mocked(vocabularyService.getBlockingWords).mockResolvedValue(mockWords)

      // Set up game state
      act(() => {
        result.current.startGame('test-video.mp4')
      })

      await act(async () => {
        await result.current.loadSegmentWords(0)
      })

      act(() => {
        result.current.nextWord()
        result.current.toggleSubtitles()
      })

      // Verify state is set
      expect(result.current.gameSession).not.toBeNull()
      expect(result.current.currentWords.length).toBeGreaterThan(0)
      expect(result.current.currentWordIndex).toBe(1)
      expect(result.current.showSubtitles).toBe(true)

      // Reset game
      act(() => {
        result.current.resetGame()
      })

      // Verify state is reset
      expect(result.current.gameSession).toBeNull()
      expect(result.current.currentWords).toEqual([])
      expect(result.current.currentWordIndex).toBe(0)
      expect(result.current.showSubtitles).toBe(false)
      expect(result.current.isProcessing).toBe(false)
    })
  })

  describe('State Integration', () => {
    it('maintains consistent state through game flow', async () => {
      const { result } = renderHook(() => useGameStore())

      vi.mocked(vocabularyService.getBlockingWords).mockResolvedValue(mockWords)
      vi.mocked(vocabularyService.markWordAsKnown).mockResolvedValue(undefined)

      // Start game
      act(() => {
        result.current.startGame('integration-test.mp4')
      })

      expect(result.current.gameSession?.video_path).toBe('integration-test.mp4')

      // Load words
      await act(async () => {
        await result.current.loadSegmentWords(0)
      })

      expect(result.current.currentWords).toEqual(mockWords)
      expect(result.current.currentWordIndex).toBe(0)

      // Mark current word as known
      await act(async () => {
        await result.current.markWordKnown(mockWords[0].word, true)
      })

      // Advance to next word
      act(() => {
        result.current.nextWord()
      })

      expect(result.current.currentWordIndex).toBe(1)

      // Toggle subtitles
      act(() => {
        result.current.toggleSubtitles()
      })

      expect(result.current.showSubtitles).toBe(true)

      // State should remain consistent
      expect(result.current.gameSession?.video_path).toBe('integration-test.mp4')

      // Expect updated words with first word marked as known
      const expectedWords = [
        { ...mockWords[0], known: true },
        ...mockWords.slice(1)
      ]
      expect(result.current.currentWords).toEqual(expectedWords)
      expect(result.current.isProcessing).toBe(false)
    })
  })
})