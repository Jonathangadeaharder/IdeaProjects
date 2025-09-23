import { describe, it, expect, vi, beforeEach } from 'vitest'
import { VocabularyRepository, VocabularyWord, VocabularyStats, BlockingWords } from '../vocabulary.repository'
import { HttpClient } from '../../clients/http.client'

describe('VocabularyRepository', () => {
  let mockHttpClient: jest.Mocked<HttpClient>
  let vocabularyRepository: VocabularyRepository

  const mockWords: VocabularyWord[] = [
    {
      id: '1',
      word: 'hello',
      translation: 'hola',
      frequency: 150,
      difficulty: 'easy',
      is_known: false,
      times_seen: 5,
      last_seen: '2025-09-23T10:00:00Z',
      context_examples: ['Hello, how are you?']
    },
    {
      id: '2',
      word: 'sophisticated',
      translation: 'sofisticado',
      frequency: 25,
      difficulty: 'hard',
      is_known: true,
      times_seen: 3,
      last_seen: '2025-09-22T15:30:00Z',
      context_examples: ['A sophisticated approach']
    }
  ]

  const mockStats: VocabularyStats = {
    total_words: 1250,
    known_words: 380,
    learning_words: 120,
    new_words: 750,
    mastery_percentage: 30.4,
    streak_days: 7
  }

  const mockBlockingWords: BlockingWords = {
    words: mockWords,
    blocking_percentage: 15.6,
    recommended_focus: [mockWords[0]]
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockHttpClient = {
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn()
    } as jest.Mocked<HttpClient>

    vocabularyRepository = new VocabularyRepository(mockHttpClient)
  })

  describe('getStats', () => {
    it('fetches vocabulary statistics', async () => {
      mockHttpClient.get.mockResolvedValue(mockStats)

      const result = await vocabularyRepository.getStats()

      expect(mockHttpClient.get).toHaveBeenCalledWith('/api/vocabulary/stats')
      expect(result).toEqual(mockStats)
    })

    it('caches statistics results', async () => {
      mockHttpClient.get.mockResolvedValue(mockStats)

      // First call
      const result1 = await vocabularyRepository.getStats()
      // Second call should use cache
      const result2 = await vocabularyRepository.getStats()

      expect(mockHttpClient.get).toHaveBeenCalledTimes(1)
      expect(result1).toEqual(result2)
    })

    it('forces refresh when specified', async () => {
      mockHttpClient.get.mockResolvedValue(mockStats)

      // First call
      await vocabularyRepository.getStats()
      // Force refresh
      await vocabularyRepository.getStats(true)

      expect(mockHttpClient.get).toHaveBeenCalledTimes(2)
    })

    it('handles API errors', async () => {
      const error = new Error('Stats not available')
      mockHttpClient.get.mockRejectedValue(error)

      await expect(vocabularyRepository.getStats()).rejects.toThrow('Stats not available')
    })
  })

  describe('getBlockingWords', () => {
    it('fetches blocking words without video filter', async () => {
      mockHttpClient.get.mockResolvedValue(mockBlockingWords)

      const result = await vocabularyRepository.getBlockingWords()

      expect(mockHttpClient.get).toHaveBeenCalledWith('/api/vocabulary/blocking-words')
      expect(result).toEqual(mockBlockingWords)
    })

    it('fetches blocking words for specific video', async () => {
      mockHttpClient.get.mockResolvedValue(mockBlockingWords)

      const result = await vocabularyRepository.getBlockingWords('video-123')

      expect(mockHttpClient.get).toHaveBeenCalledWith('/api/vocabulary/blocking-words?video_id=video-123')
      expect(result).toEqual(mockBlockingWords)
    })

    it('caches blocking words results', async () => {
      mockHttpClient.get.mockResolvedValue(mockBlockingWords)

      // First call
      const result1 = await vocabularyRepository.getBlockingWords()
      // Second call should use cache
      const result2 = await vocabularyRepository.getBlockingWords()

      expect(mockHttpClient.get).toHaveBeenCalledTimes(1)
      expect(result1).toEqual(result2)
    })

    it('forces refresh when specified', async () => {
      mockHttpClient.get.mockResolvedValue(mockBlockingWords)

      // First call
      await vocabularyRepository.getBlockingWords()
      // Force refresh
      await vocabularyRepository.getBlockingWords(undefined, true)

      expect(mockHttpClient.get).toHaveBeenCalledTimes(2)
    })

    it('caches individual words from blocking words response', async () => {
      mockHttpClient.get.mockResolvedValue(mockBlockingWords)

      await vocabularyRepository.getBlockingWords()

      // Individual words should be cached
      expect(vocabularyRepository['wordsCache'].has('1')).toBe(true)
      expect(vocabularyRepository['wordsCache'].has('2')).toBe(true)
    })

    it('handles API errors', async () => {
      const error = new Error('Blocking words not available')
      mockHttpClient.get.mockRejectedValue(error)

      await expect(vocabularyRepository.getBlockingWords()).rejects.toThrow('Blocking words not available')
    })
  })

  describe('markWordKnown', () => {
    it('marks word as known', async () => {
      const updatedWord = { ...mockWords[0], is_known: true }
      mockHttpClient.post.mockResolvedValue(updatedWord)

      const result = await vocabularyRepository.markWordKnown('word-1', true)

      expect(mockHttpClient.post).toHaveBeenCalledWith('/api/vocabulary/mark-known', {
        word_id: 'word-1',
        is_known: true
      })
      expect(result).toEqual(updatedWord)
    })

    it('marks word as unknown', async () => {
      const updatedWord = { ...mockWords[1], is_known: false }
      mockHttpClient.post.mockResolvedValue(updatedWord)

      const result = await vocabularyRepository.markWordKnown('word-2', false)

      expect(mockHttpClient.post).toHaveBeenCalledWith('/api/vocabulary/mark-known', {
        word_id: 'word-2',
        is_known: false
      })
      expect(result).toEqual(updatedWord)
    })

    it('defaults to marking as known when isKnown not specified', async () => {
      const updatedWord = { ...mockWords[0], is_known: true }
      mockHttpClient.post.mockResolvedValue(updatedWord)

      const result = await vocabularyRepository.markWordKnown('word-1')

      expect(mockHttpClient.post).toHaveBeenCalledWith('/api/vocabulary/mark-known', {
        word_id: 'word-1',
        is_known: true
      })
      expect(result).toEqual(updatedWord)
    })

    it('updates word cache', async () => {
      const updatedWord = { ...mockWords[0], is_known: true }
      mockHttpClient.post.mockResolvedValue(updatedWord)

      await vocabularyRepository.markWordKnown('word-1', true)

      // Word should be cached
      expect(vocabularyRepository['wordsCache'].get('word-1')).toEqual(updatedWord)
    })

    it('invalidates stats and blocking words cache', async () => {
      const updatedWord = { ...mockWords[0], is_known: true }
      mockHttpClient.post.mockResolvedValue(updatedWord)

      // First populate caches
      mockHttpClient.get.mockResolvedValueOnce(mockStats)
      mockHttpClient.get.mockResolvedValueOnce(mockBlockingWords)
      await vocabularyRepository.getStats()
      await vocabularyRepository.getBlockingWords()

      // Mark word as known
      await vocabularyRepository.markWordKnown('word-1', true)

      // Caches should be invalidated
      expect(vocabularyRepository['statsCache']).toBeNull()
      expect(vocabularyRepository['blockingWordsCache']).toBeNull()
    })

    it('handles marking errors', async () => {
      const error = new Error('Mark failed')
      mockHttpClient.post.mockRejectedValue(error)

      await expect(vocabularyRepository.markWordKnown('word-1', true)).rejects.toThrow('Mark failed')
    })
  })

  describe('bulkMarkWords', () => {
    it('marks multiple words as known', async () => {
      mockHttpClient.post.mockResolvedValue(undefined)

      await vocabularyRepository.bulkMarkWords(['word-1', 'word-2'], true)

      expect(mockHttpClient.post).toHaveBeenCalledWith('/api/vocabulary/bulk-mark', {
        word_ids: ['word-1', 'word-2'],
        is_known: true
      })
    })

    it('marks multiple words as unknown', async () => {
      mockHttpClient.post.mockResolvedValue(undefined)

      await vocabularyRepository.bulkMarkWords(['word-1', 'word-2'], false)

      expect(mockHttpClient.post).toHaveBeenCalledWith('/api/vocabulary/bulk-mark', {
        word_ids: ['word-1', 'word-2'],
        is_known: false
      })
    })

    it('defaults to marking as known when isKnown not specified', async () => {
      mockHttpClient.post.mockResolvedValue(undefined)

      await vocabularyRepository.bulkMarkWords(['word-1', 'word-2'])

      expect(mockHttpClient.post).toHaveBeenCalledWith('/api/vocabulary/bulk-mark', {
        word_ids: ['word-1', 'word-2'],
        is_known: true
      })
    })

    it('invalidates caches after bulk operation', async () => {
      mockHttpClient.post.mockResolvedValue(undefined)

      // First populate caches
      mockHttpClient.get.mockResolvedValueOnce(mockStats)
      mockHttpClient.get.mockResolvedValueOnce(mockBlockingWords)
      await vocabularyRepository.getStats()
      await vocabularyRepository.getBlockingWords()

      // Bulk mark words
      await vocabularyRepository.bulkMarkWords(['word-1', 'word-2'], true)

      // Caches should be invalidated
      expect(vocabularyRepository['statsCache']).toBeNull()
      expect(vocabularyRepository['blockingWordsCache']).toBeNull()
    })

    it('handles bulk marking errors', async () => {
      const error = new Error('Bulk mark failed')
      mockHttpClient.post.mockRejectedValue(error)

      await expect(vocabularyRepository.bulkMarkWords(['word-1', 'word-2'], true)).rejects.toThrow('Bulk mark failed')
    })
  })

  describe('clearCache', () => {
    it('clears all cached data', async () => {
      // Populate caches
      mockHttpClient.get.mockResolvedValueOnce(mockStats)
      mockHttpClient.get.mockResolvedValueOnce(mockBlockingWords)
      await vocabularyRepository.getStats()
      await vocabularyRepository.getBlockingWords()

      // Clear cache
      vocabularyRepository.clearCache()

      // Mock additional responses for after cache clear
      mockHttpClient.get.mockResolvedValueOnce(mockStats)
      mockHttpClient.get.mockResolvedValueOnce(mockBlockingWords)

      // Next calls should fetch from API
      await vocabularyRepository.getStats()
      await vocabularyRepository.getBlockingWords()

      expect(mockHttpClient.get).toHaveBeenCalledTimes(4) // 2 initial + 2 after clear
    })

    it('clears individual words cache', async () => {
      // Populate words cache
      mockHttpClient.get.mockResolvedValue(mockBlockingWords)
      await vocabularyRepository.getBlockingWords()

      expect(vocabularyRepository['wordsCache'].size).toBeGreaterThan(0)

      // Clear cache
      vocabularyRepository.clearCache()

      expect(vocabularyRepository['wordsCache'].size).toBe(0)
    })
  })

  describe('Cache Management', () => {
    it('respects cache expiry time', async () => {
      mockHttpClient.get.mockResolvedValue(mockStats)

      // Mock Date.now to simulate time passing
      const originalNow = Date.now
      let currentTime = 1000000

      vi.spyOn(Date, 'now').mockImplementation(() => currentTime)

      try {
        // First call
        await vocabularyRepository.getStats()

        // Second call within cache period (should use cache)
        currentTime += 1000 // 1 second later
        await vocabularyRepository.getStats()

        expect(mockHttpClient.get).toHaveBeenCalledTimes(1)

        // Third call after cache expiry (should fetch again)
        currentTime += 6 * 60 * 1000 // 6 minutes later (past 5-minute expiry)
        await vocabularyRepository.getStats()

        expect(mockHttpClient.get).toHaveBeenCalledTimes(2)
      } finally {
        Date.now = originalNow
      }
    })
  })
})