import { describe, it, expect, vi, beforeEach } from 'vitest'
import { VideoRepository, VideoInfo, ProcessingTask } from '../video.repository'
import { HttpClient } from '../../clients/http.client'

describe('VideoRepository', () => {
  let mockHttpClient: jest.Mocked<HttpClient>
  let videoRepository: VideoRepository

  const mockVideos: VideoInfo[] = [
    {
      id: '1',
      series: 'Test Series',
      episode: 'Episode 1',
      title: 'Test Episode 1',
      duration: 1800,
      thumbnail: 'test1.jpg',
      subtitles_available: true,
      processing_status: 'completed',
      vocabulary_count: 150,
      difficulty_level: 'intermediate'
    },
    {
      id: '2',
      series: 'Test Series',
      episode: 'Episode 2',
      title: 'Test Episode 2',
      duration: 2100,
      thumbnail: 'test2.jpg',
      subtitles_available: false,
      processing_status: 'pending',
      vocabulary_count: 0,
      difficulty_level: 'beginner'
    }
  ]

  const mockProcessingTask: ProcessingTask = {
    task_id: 'task-123',
    status: 'processing',
    current_step: 'Extracting audio',
    steps_completed: 2,
    total_steps: 5,
    progress_percentage: 40,
    message: 'Processing video...'
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockHttpClient = {
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn()
    } as jest.Mocked<HttpClient>

    videoRepository = new VideoRepository(mockHttpClient)
  })

  describe('getAll', () => {
    it('fetches videos from API and caches result', async () => {
      mockHttpClient.get.mockResolvedValue(mockVideos)

      const result = await videoRepository.getAll()

      expect(mockHttpClient.get).toHaveBeenCalledWith('/api/videos')
      expect(result).toEqual(mockVideos)
    })

    it('returns cached videos on subsequent calls within cache period', async () => {
      mockHttpClient.get.mockResolvedValue(mockVideos)

      // First call
      const result1 = await videoRepository.getAll()
      // Second call within cache period
      const result2 = await videoRepository.getAll()

      expect(mockHttpClient.get).toHaveBeenCalledTimes(1)
      expect(result1).toEqual(result2)
    })

    it('forces refresh when forceRefresh is true', async () => {
      mockHttpClient.get.mockResolvedValue(mockVideos)

      // First call
      await videoRepository.getAll()
      // Force refresh
      await videoRepository.getAll(true)

      expect(mockHttpClient.get).toHaveBeenCalledTimes(2)
    })

    it('handles API errors gracefully', async () => {
      const error = new Error('Network error')
      mockHttpClient.get.mockRejectedValue(error)

      await expect(videoRepository.getAll()).rejects.toThrow('Network error')
    })
  })

  describe('getById', () => {
    it('fetches video by ID from API', async () => {
      const mockVideo = mockVideos[0]
      mockHttpClient.get.mockResolvedValue(mockVideo)

      const result = await videoRepository.getById('1')

      expect(mockHttpClient.get).toHaveBeenCalledWith('/api/videos/1')
      expect(result).toEqual(mockVideo)
    })

    it('returns cached video if available', async () => {
      // First populate cache with getAll
      mockHttpClient.get.mockResolvedValue(mockVideos)
      await videoRepository.getAll()

      // Clear mock to verify cache is used
      mockHttpClient.get.mockClear()

      const result = await videoRepository.getById('1')

      expect(mockHttpClient.get).not.toHaveBeenCalled()
      expect(result).toEqual(mockVideos[0])
    })

    it('fetches from API if not in cache', async () => {
      const mockVideo = mockVideos[0]
      mockHttpClient.get.mockResolvedValue(mockVideo)

      const result = await videoRepository.getById('1')

      expect(mockHttpClient.get).toHaveBeenCalledWith('/api/videos/1')
      expect(result).toEqual(mockVideo)
    })

    it('handles video not found', async () => {
      const error = new Error('Video not found')
      mockHttpClient.get.mockRejectedValue(error)

      await expect(videoRepository.getById('999')).rejects.toThrow('Video not found')
    })
  })

  describe('startProcessing', () => {
    it('initiates video processing', async () => {
      mockHttpClient.post.mockResolvedValue(mockProcessingTask)

      const result = await videoRepository.startProcessing('1')

      expect(mockHttpClient.post).toHaveBeenCalledWith('/api/videos/1/process', undefined)
      expect(result).toEqual(mockProcessingTask)
    })

    it('handles processing errors', async () => {
      const error = new Error('Processing failed')
      mockHttpClient.post.mockRejectedValue(error)

      await expect(videoRepository.startProcessing('1')).rejects.toThrow('Processing failed')
    })

    it('passes options to processing request', async () => {
      const options = { quality: 'high', includeSubtitles: true }
      mockHttpClient.post.mockResolvedValue(mockProcessingTask)

      const result = await videoRepository.startProcessing('1', options)

      expect(mockHttpClient.post).toHaveBeenCalledWith('/api/videos/1/process', options)
      expect(result).toEqual(mockProcessingTask)
    })
  })

  describe('getProcessingStatus', () => {
    it('fetches processing status for task', async () => {
      mockHttpClient.get.mockResolvedValue(mockProcessingTask)

      const result = await videoRepository.getProcessingStatus('task-123')

      expect(mockHttpClient.get).toHaveBeenCalledWith('/api/process/progress/task-123')
      expect(result).toEqual(mockProcessingTask)
    })

    it('handles status check errors', async () => {
      const error = new Error('Task not found')
      mockHttpClient.get.mockRejectedValue(error)

      await expect(videoRepository.getProcessingStatus('invalid-task')).rejects.toThrow('Task not found')
    })
  })

  describe('clearCache', () => {
    it('clears all cached data', async () => {
      // Populate cache
      mockHttpClient.get.mockResolvedValue(mockVideos)
      await videoRepository.getAll()

      // Clear cache
      videoRepository.clearCache()

      // Next call should fetch from API
      await videoRepository.getAll()

      expect(mockHttpClient.get).toHaveBeenCalledTimes(2)
    })
  })

})