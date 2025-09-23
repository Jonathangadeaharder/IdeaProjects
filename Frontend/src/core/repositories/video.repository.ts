/**
 * Video Repository
 * Manages video data and caching
 */

import { HttpClient } from '../clients/http.client'

export interface VideoInfo {
  id: string
  series: string
  episode: string
  title: string
  duration?: number
  thumbnail?: string
  subtitles_available?: boolean
  processing_status?: 'pending' | 'processing' | 'completed' | 'failed'
  vocabulary_count?: number
  difficulty_level?: string
}

export interface ProcessingTask {
  task_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
  current_step: string
  steps_completed: number
  total_steps: number
  progress_percentage: number
  message: string
  error?: string
  result?: any
}

export class VideoRepository {
  private cache: Map<string, VideoInfo> = new Map()
  private listCache: VideoInfo[] | null = null
  private cacheExpiry: number = 5 * 60 * 1000 // 5 minutes
  private lastFetch: number = 0

  constructor(private http: HttpClient) {}

  async getAll(forceRefresh: boolean = false): Promise<VideoInfo[]> {
    const now = Date.now()

    // Return cached list if valid and not forcing refresh
    if (!forceRefresh && this.listCache && (now - this.lastFetch) < this.cacheExpiry) {
      return this.listCache
    }

    try {
      const videos = await this.http.get<VideoInfo[]>('/api/videos')

      // Update caches
      this.listCache = videos
      this.lastFetch = now

      // Update individual cache entries
      videos.forEach(video => {
        this.cache.set(video.id, video)
      })

      return videos
    } catch (error) {
      // If we have cached data, return it even if stale
      if (this.listCache) {
        return this.listCache
      }
      throw error
    }
  }

  async getById(id: string, forceRefresh: boolean = false): Promise<VideoInfo | null> {
    // Check cache first unless forcing refresh
    if (!forceRefresh && this.cache.has(id)) {
      return this.cache.get(id)!
    }

    try {
      const video = await this.http.get<VideoInfo>(`/api/videos/${id}`)
      this.cache.set(id, video)
      return video
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null
      }
      throw error
    }
  }

  async getBySeries(series: string): Promise<VideoInfo[]> {
    const allVideos = await this.getAll()
    return allVideos.filter(video => video.series === series)
  }

  async getByEpisode(series: string, episode: string): Promise<VideoInfo | null> {
    const seriesVideos = await this.getBySeries(series)
    return seriesVideos.find(video => video.episode === episode) || null
  }

  async startProcessing(videoId: string, options?: any): Promise<ProcessingTask> {
    const response = await this.http.post<ProcessingTask>(
      `/api/videos/${videoId}/process`,
      options
    )
    return response
  }

  async getProcessingStatus(taskId: string): Promise<ProcessingTask> {
    const response = await this.http.get<ProcessingTask>(
      `/api/process/progress/${taskId}`
    )
    return response
  }

  async uploadVideo(file: File, metadata: Partial<VideoInfo>): Promise<VideoInfo> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('metadata', JSON.stringify(metadata))

    const response = await this.http.post<VideoInfo>('/api/videos/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    // Add to cache
    this.cache.set(response.id, response)

    // Invalidate list cache to force refresh
    this.listCache = null

    return response
  }

  async deleteVideo(id: string): Promise<void> {
    await this.http.delete(`/api/videos/${id}`)

    // Remove from caches
    this.cache.delete(id)
    if (this.listCache) {
      this.listCache = this.listCache.filter(v => v.id !== id)
    }
  }

  // Utility methods for testing
  clearCache(): void {
    this.cache.clear()
    this.listCache = null
    this.lastFetch = 0
  }

  getCacheSize(): number {
    return this.cache.size
  }

  isVideoCached(id: string): boolean {
    return this.cache.has(id)
  }
}