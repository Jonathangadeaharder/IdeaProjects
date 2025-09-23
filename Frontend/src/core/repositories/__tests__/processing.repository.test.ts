import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ProcessingRepository, ProcessingTask, ProcessingStep } from '../processing.repository'
import { HttpClient } from '../../clients/http.client'

describe('ProcessingRepository', () => {
  let mockHttpClient: jest.Mocked<HttpClient>
  let processingRepository: ProcessingRepository

  const mockTask: ProcessingTask = {
    task_id: 'task-123',
    video_id: 'video-456',
    status: 'processing',
    current_step: 'extracting_audio',
    steps_completed: 2,
    total_steps: 5,
    progress_percentage: 40,
    message: 'Extracting audio from video...',
    started_at: '2025-09-23T10:00:00Z',
    estimated_completion: '2025-09-23T10:15:00Z'
  }

  const mockCompletedTask: ProcessingTask = {
    ...mockTask,
    task_id: 'task-completed',
    status: 'completed',
    current_step: 'completed',
    steps_completed: 5,
    progress_percentage: 100,
    message: 'Processing completed successfully',
    completed_at: '2025-09-23T10:12:00Z',
    result: {
      vocabulary_count: 250,
      subtitle_segments: 45,
      processing_time: 720
    }
  }

  const mockFailedTask: ProcessingTask = {
    ...mockTask,
    task_id: 'task-failed',
    status: 'failed',
    current_step: 'extracting_audio',
    progress_percentage: 20,
    message: 'Processing failed',
    error: 'Unsupported video format',
    failed_at: '2025-09-23T10:05:00Z'
  }

  const mockSteps: ProcessingStep[] = [
    { step: 'upload_validation', name: 'Validating upload', status: 'completed', duration: 2 },
    { step: 'extracting_audio', name: 'Extracting audio', status: 'processing', duration: null },
    { step: 'speech_recognition', name: 'Speech recognition', status: 'pending', duration: null },
    { step: 'vocabulary_extraction', name: 'Extracting vocabulary', status: 'pending', duration: null },
    { step: 'subtitle_generation', name: 'Generating subtitles', status: 'pending', duration: null }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    mockHttpClient = {
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn()
    } as jest.Mocked<HttpClient>

    processingRepository = new ProcessingRepository(mockHttpClient)
  })

  describe('startProcessing', () => {
    it('initiates video processing', async () => {
      mockHttpClient.post.mockResolvedValue(mockTask)

      const result = await processingRepository.startProcessing('video-456', {
        include_vocabulary: true,
        language: 'en',
        quality: 'high'
      })

      expect(mockHttpClient.post).toHaveBeenCalledWith('/api/processing/start', {
        video_id: 'video-456',
        options: {
          include_vocabulary: true,
          language: 'en',
          quality: 'high'
        }
      })
      expect(result).toEqual(mockTask)
    })

    it('uses default options when none provided', async () => {
      mockHttpClient.post.mockResolvedValue(mockTask)

      const result = await processingRepository.startProcessing('video-456')

      expect(mockHttpClient.post).toHaveBeenCalledWith('/api/processing/start', {
        video_id: 'video-456',
        options: {}
      })
      expect(result).toEqual(mockTask)
    })

    it('handles processing start errors', async () => {
      const error = new Error('Video not found')
      mockHttpClient.post.mockRejectedValue(error)

      await expect(processingRepository.startProcessing('invalid-video')).rejects.toThrow('Video not found')
    })
  })

  describe('getTaskStatus', () => {
    it('fetches task status by ID', async () => {
      mockHttpClient.get.mockResolvedValue(mockTask)

      const result = await processingRepository.getTaskStatus('task-123')

      expect(mockHttpClient.get).toHaveBeenCalledWith('/api/processing/task-123')
      expect(result).toEqual(mockTask)
    })

    it('caches task status for short period', async () => {
      mockHttpClient.get.mockResolvedValue(mockTask)

      // First call
      const result1 = await processingRepository.getTaskStatus('task-123')
      // Second call within cache period (5 seconds)
      const result2 = await processingRepository.getTaskStatus('task-123')

      expect(mockHttpClient.get).toHaveBeenCalledTimes(1)
      expect(result1).toEqual(result2)
    })

    it('bypasses cache for completed tasks', async () => {
      mockHttpClient.get.mockResolvedValue(mockCompletedTask)

      // Multiple calls for completed task should always fetch fresh data
      await processingRepository.getTaskStatus('task-completed')
      await processingRepository.getTaskStatus('task-completed')

      expect(mockHttpClient.get).toHaveBeenCalledTimes(2)
    })

    it('handles task not found', async () => {
      const error = new Error('Task not found')
      mockHttpClient.get.mockRejectedValue(error)

      await expect(processingRepository.getTaskStatus('invalid-task')).rejects.toThrow('Task not found')
    })
  })

  describe('getTaskSteps', () => {
    it('fetches processing steps for task', async () => {
      mockHttpClient.get.mockResolvedValue(mockSteps)

      const result = await processingRepository.getTaskSteps('task-123')

      expect(mockHttpClient.get).toHaveBeenCalledWith('/api/processing/task-123/steps')
      expect(result).toEqual(mockSteps)
    })

    it('handles steps fetch error', async () => {
      const error = new Error('Steps not available')
      mockHttpClient.get.mockRejectedValue(error)

      await expect(processingRepository.getTaskSteps('task-123')).rejects.toThrow('Steps not available')
    })
  })

  describe('cancelTask', () => {
    it('cancels processing task', async () => {
      const cancelledTask = { ...mockTask, status: 'cancelled' as const }
      mockHttpClient.post.mockResolvedValue(cancelledTask)

      const result = await processingRepository.cancelTask('task-123')

      expect(mockHttpClient.post).toHaveBeenCalledWith('/api/processing/task-123/cancel')
      expect(result).toEqual(cancelledTask)
    })

    it('handles cancellation errors', async () => {
      const error = new Error('Cannot cancel completed task')
      mockHttpClient.post.mockRejectedValue(error)

      await expect(processingRepository.cancelTask('task-completed')).rejects.toThrow('Cannot cancel completed task')
    })
  })

  describe('getUserTasks', () => {
    it('fetches tasks for user', async () => {
      const userTasks = [mockTask, mockCompletedTask]
      mockHttpClient.get.mockResolvedValue(userTasks)

      const result = await processingRepository.getUserTasks('user-123')

      expect(mockHttpClient.get).toHaveBeenCalledWith('/api/processing/user/user-123/tasks')
      expect(result).toEqual(userTasks)
    })

    it('filters tasks by status', async () => {
      const activeTasks = [mockTask]
      mockHttpClient.get.mockResolvedValue(activeTasks)

      const result = await processingRepository.getUserTasks('user-123', 'processing')

      expect(mockHttpClient.get).toHaveBeenCalledWith('/api/processing/user/user-123/tasks', {
        params: { status: 'processing' }
      })
      expect(result).toEqual(activeTasks)
    })

    it('limits results when specified', async () => {
      const limitedTasks = [mockTask]
      mockHttpClient.get.mockResolvedValue(limitedTasks)

      const result = await processingRepository.getUserTasks('user-123', undefined, 1)

      expect(mockHttpClient.get).toHaveBeenCalledWith('/api/processing/user/user-123/tasks', {
        params: { limit: 1 }
      })
      expect(result).toEqual(limitedTasks)
    })
  })

  describe('retryTask', () => {
    it('retries failed task', async () => {
      const retriedTask = { ...mockFailedTask, status: 'pending' as const, error: undefined }
      mockHttpClient.post.mockResolvedValue(retriedTask)

      const result = await processingRepository.retryTask('task-failed')

      expect(mockHttpClient.post).toHaveBeenCalledWith('/api/processing/task-failed/retry')
      expect(result).toEqual(retriedTask)
    })

    it('handles retry errors', async () => {
      const error = new Error('Cannot retry successful task')
      mockHttpClient.post.mockRejectedValue(error)

      await expect(processingRepository.retryTask('task-completed')).rejects.toThrow('Cannot retry successful task')
    })
  })

  describe('getProcessingQueue', () => {
    it('fetches current processing queue', async () => {
      const queueInfo = {
        total_tasks: 5,
        processing_tasks: 2,
        pending_tasks: 3,
        average_wait_time: 180,
        estimated_completion: '2025-09-23T11:00:00Z'
      }
      mockHttpClient.get.mockResolvedValue(queueInfo)

      const result = await processingRepository.getProcessingQueue()

      expect(mockHttpClient.get).toHaveBeenCalledWith('/api/processing/queue')
      expect(result).toEqual(queueInfo)
    })
  })

  describe('deleteTask', () => {
    it('deletes completed task', async () => {
      mockHttpClient.delete.mockResolvedValue({ success: true })

      const result = await processingRepository.deleteTask('task-completed')

      expect(mockHttpClient.delete).toHaveBeenCalledWith('/api/processing/task-completed')
      expect(result).toEqual({ success: true })
    })

    it('handles delete errors', async () => {
      const error = new Error('Cannot delete active task')
      mockHttpClient.delete.mockRejectedValue(error)

      await expect(processingRepository.deleteTask('task-123')).rejects.toThrow('Cannot delete active task')
    })
  })

  describe('clearCache', () => {
    it('clears all cached task data', async () => {
      // Populate cache
      mockHttpClient.get.mockResolvedValue(mockTask)
      await processingRepository.getTaskStatus('task-123')

      // Clear cache
      processingRepository.clearCache()

      // Next call should fetch from API
      await processingRepository.getTaskStatus('task-123')

      expect(mockHttpClient.get).toHaveBeenCalledTimes(2)
    })
  })

  describe('pollTaskUntilComplete', () => {
    it('polls task status until completion', async () => {
      mockHttpClient.get
        .mockResolvedValueOnce(mockTask)
        .mockResolvedValueOnce({ ...mockTask, progress_percentage: 60 })
        .mockResolvedValueOnce(mockCompletedTask)

      const result = await processingRepository.pollTaskUntilComplete('task-123', 100)

      expect(mockHttpClient.get).toHaveBeenCalledTimes(3)
      expect(result).toEqual(mockCompletedTask)
    })

    it('stops polling if task fails', async () => {
      mockHttpClient.get
        .mockResolvedValueOnce(mockTask)
        .mockResolvedValueOnce(mockFailedTask)

      const result = await processingRepository.pollTaskUntilComplete('task-failed', 100)

      expect(mockHttpClient.get).toHaveBeenCalledTimes(2)
      expect(result).toEqual(mockFailedTask)
    })

    it('handles polling errors gracefully', async () => {
      const error = new Error('Network error')
      mockHttpClient.get.mockRejectedValue(error)

      await expect(processingRepository.pollTaskUntilComplete('task-123', 100)).rejects.toThrow('Network error')
    })
  })
})