import { HttpClient } from '../clients/http.client'

export interface ProcessingTask {
  task_id: string
  video_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
  current_step: string
  steps_completed: number
  total_steps: number
  progress_percentage: number
  message: string
  started_at: string
  estimated_completion?: string
  completed_at?: string
  failed_at?: string
  error?: string
  result?: {
    vocabulary_count: number
    subtitle_segments: number
    processing_time: number
  }
}

export interface ProcessingStep {
  step: string
  name: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  duration: number | null
}

export interface ProcessingOptions {
  include_vocabulary?: boolean
  language?: string
  quality?: 'low' | 'medium' | 'high'
}

export interface ProcessingQueue {
  total_tasks: number
  processing_tasks: number
  pending_tasks: number
  average_wait_time: number
  estimated_completion: string
}

export class ProcessingRepository {
  private readonly httpClient: HttpClient
  private readonly taskCache = new Map<string, { task: ProcessingTask; timestamp: number }>()
  private readonly CACHE_DURATION = 5000 // 5 seconds

  constructor(httpClient: HttpClient) {
    this.httpClient = httpClient
  }

  async startProcessing(videoId: string, options: ProcessingOptions = {}): Promise<ProcessingTask> {
    return this.httpClient.post<ProcessingTask>('/api/processing/start', {
      video_id: videoId,
      options
    })
  }

  async getTaskStatus(taskId: string): Promise<ProcessingTask> {
    // Check cache first (but not for completed tasks)
    const cached = this.taskCache.get(taskId)
    if (cached && Date.now() - cached.timestamp < this.CACHE_DURATION) {
      if (cached.task.status !== 'completed' && cached.task.status !== 'failed') {
        return cached.task
      }
    }

    const task = await this.httpClient.get<ProcessingTask>(`/api/processing/${taskId}`)

    // Cache the result (but don't cache completed/failed tasks for long)
    if (task.status !== 'completed' && task.status !== 'failed') {
      this.taskCache.set(taskId, { task, timestamp: Date.now() })
    }

    return task
  }

  async getTaskSteps(taskId: string): Promise<ProcessingStep[]> {
    return this.httpClient.get<ProcessingStep[]>(`/api/processing/${taskId}/steps`)
  }

  async cancelTask(taskId: string): Promise<ProcessingTask> {
    const task = await this.httpClient.post<ProcessingTask>(`/api/processing/${taskId}/cancel`)
    // Remove from cache since status changed
    this.taskCache.delete(taskId)
    return task
  }

  async getUserTasks(
    userId: string,
    status?: ProcessingTask['status'],
    limit?: number
  ): Promise<ProcessingTask[]> {
    const params: Record<string, any> = {}
    if (status) params.status = status
    if (limit) params.limit = limit

    if (Object.keys(params).length > 0) {
      return this.httpClient.get<ProcessingTask[]>(`/api/processing/user/${userId}/tasks`, { params })
    } else {
      return this.httpClient.get<ProcessingTask[]>(`/api/processing/user/${userId}/tasks`)
    }
  }

  async retryTask(taskId: string): Promise<ProcessingTask> {
    const task = await this.httpClient.post<ProcessingTask>(`/api/processing/${taskId}/retry`)
    // Remove from cache since task is being retried
    this.taskCache.delete(taskId)
    return task
  }

  async getProcessingQueue(): Promise<ProcessingQueue> {
    return this.httpClient.get<ProcessingQueue>('/api/processing/queue')
  }

  async deleteTask(taskId: string): Promise<{ success: boolean }> {
    const result = await this.httpClient.delete<{ success: boolean }>(`/api/processing/${taskId}`)
    // Remove from cache
    this.taskCache.delete(taskId)
    return result
  }

  clearCache(): void {
    this.taskCache.clear()
  }

  async pollTaskUntilComplete(taskId: string, intervalMs: number = 2000): Promise<ProcessingTask> {
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const task = await this.getTaskStatus(taskId)

          if (task.status === 'completed' || task.status === 'failed' || task.status === 'cancelled') {
            resolve(task)
            return
          }

          // Continue polling
          setTimeout(poll, intervalMs)
        } catch (error) {
          reject(error)
        }
      }

      poll()
    })
  }
}