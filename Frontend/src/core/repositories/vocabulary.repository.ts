/**
 * Vocabulary Repository
 * Manages vocabulary learning data
 */

import { HttpClient } from '../clients/http.client'

export interface VocabularyWord {
  id: string
  word: string
  translation: string
  frequency: number
  difficulty: 'easy' | 'medium' | 'hard'
  is_known: boolean
  times_seen: number
  last_seen?: string
  context_examples?: string[]
}

export interface VocabularyStats {
  total_words: number
  known_words: number
  learning_words: number
  new_words: number
  mastery_percentage: number
  streak_days: number
}

export interface BlockingWords {
  words: VocabularyWord[]
  blocking_percentage: number
  recommended_focus: VocabularyWord[]
}

export class VocabularyRepository {
  private statsCache: VocabularyStats | null = null
  private wordsCache: Map<string, VocabularyWord> = new Map()
  private blockingWordsCache: BlockingWords | null = null
  private cacheExpiry: number = 5 * 60 * 1000 // 5 minutes
  private lastStatsFetch: number = 0
  private lastBlockingFetch: number = 0

  constructor(private http: HttpClient) {}

  async getStats(forceRefresh: boolean = false): Promise<VocabularyStats> {
    const now = Date.now()

    if (!forceRefresh && this.statsCache && (now - this.lastStatsFetch) < this.cacheExpiry) {
      return this.statsCache
    }

    const stats = await this.http.get<VocabularyStats>('/api/vocabulary/stats')
    this.statsCache = stats
    this.lastStatsFetch = now
    return stats
  }

  async getBlockingWords(videoId?: string, forceRefresh: boolean = false): Promise<BlockingWords> {
    const now = Date.now()

    if (!forceRefresh && this.blockingWordsCache && (now - this.lastBlockingFetch) < this.cacheExpiry) {
      return this.blockingWordsCache
    }

    const url = videoId
      ? `/api/vocabulary/blocking-words?video_id=${videoId}`
      : '/api/vocabulary/blocking-words'

    const blockingWords = await this.http.get<BlockingWords>(url)
    this.blockingWordsCache = blockingWords
    this.lastBlockingFetch = now

    // Cache individual words
    blockingWords.words.forEach(word => {
      this.wordsCache.set(word.id, word)
    })

    return blockingWords
  }

  async markWordKnown(wordId: string, isKnown: boolean = true): Promise<VocabularyWord> {
    const word = await this.http.post<VocabularyWord>('/api/vocabulary/mark-known', {
      word_id: wordId,
      is_known: isKnown,
    })

    // Update cache
    this.wordsCache.set(wordId, word)

    // Invalidate stats and blocking words cache
    this.statsCache = null
    this.blockingWordsCache = null

    return word
  }

  async bulkMarkWords(wordIds: string[], isKnown: boolean = true): Promise<void> {
    await this.http.post('/api/vocabulary/bulk-mark', {
      word_ids: wordIds,
      is_known: isKnown,
    })

    // Update cached words
    wordIds.forEach(id => {
      const cached = this.wordsCache.get(id)
      if (cached) {
        cached.is_known = isKnown
      }
    })

    // Invalidate aggregate caches
    this.statsCache = null
    this.blockingWordsCache = null
  }

  async getWordsByLevel(level: 'A1' | 'A2' | 'B1' | 'B2' | 'C1' | 'C2'): Promise<VocabularyWord[]> {
    const words = await this.http.get<VocabularyWord[]>(`/api/vocabulary/library/${level}`)

    // Cache individual words
    words.forEach(word => {
      this.wordsCache.set(word.id, word)
    })

    return words
  }

  async preloadVocabulary(videoId: string): Promise<{ words_loaded: number }> {
    const result = await this.http.post<{ words_loaded: number }>('/api/vocabulary/preload', {
      video_id: videoId,
    })

    // Invalidate caches as vocabulary has been updated
    this.clearCache()

    return result
  }

  async searchWords(query: string): Promise<VocabularyWord[]> {
    const words = await this.http.get<VocabularyWord[]>(`/api/vocabulary/search?q=${encodeURIComponent(query)}`)

    // Cache results
    words.forEach(word => {
      this.wordsCache.set(word.id, word)
    })

    return words
  }

  async getWordDetails(wordId: string): Promise<VocabularyWord | null> {
    // Check cache first
    if (this.wordsCache.has(wordId)) {
      return this.wordsCache.get(wordId)!
    }

    try {
      const word = await this.http.get<VocabularyWord>(`/api/vocabulary/words/${wordId}`)
      this.wordsCache.set(wordId, word)
      return word
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null
      }
      throw error
    }
  }

  // Utility methods
  clearCache(): void {
    this.statsCache = null
    this.blockingWordsCache = null
    this.wordsCache.clear()
    this.lastStatsFetch = 0
    this.lastBlockingFetch = 0
  }

  getCachedStats(): VocabularyStats | null {
    return this.statsCache
  }

  getCachedWord(wordId: string): VocabularyWord | undefined {
    return this.wordsCache.get(wordId)
  }
}