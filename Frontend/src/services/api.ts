import axios, { AxiosRequestConfig } from 'axios'
import { toast } from 'react-hot-toast'
import { logger } from './logger'
import type { 
  LoginRequest, 
  RegisterRequest, 
  AuthResponse, 
  User, 
  VideoInfo, 
  VocabularyWord,
  ProcessingStatus,
  VocabularyLevel,
  VocabularyStats
} from '@/types'

// Extend AxiosRequestConfig to include metadata
interface ExtendedAxiosRequestConfig extends AxiosRequestConfig {
  metadata?: {
    startTime: number
  }
}

// Get API base URL from environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Token management
let authToken: string | null = localStorage.getItem('authToken')

api.interceptors.request.use((config) => {
  const startTime = Date.now()
  const extendedConfig = config as ExtendedAxiosRequestConfig
  extendedConfig.metadata = { startTime }
  
  if (authToken) {
    config.headers.Authorization = `Bearer ${authToken}`
  }
  
  // Log API request
  logger.apiRequest(config.method?.toUpperCase() || 'UNKNOWN', config.url || 'unknown', config.data)
  
  return config
})

api.interceptors.response.use(
  (response) => {
    // Log successful response
    const extendedConfig = response.config as ExtendedAxiosRequestConfig
    const duration = extendedConfig.metadata ? Date.now() - extendedConfig.metadata.startTime : undefined
    logger.apiResponse(
      response.config.method?.toUpperCase() || 'UNKNOWN',
      response.config.url || 'unknown',
      response.status,
      response.data,
      duration
    )
    return response
  },
  (error) => {
    // Log error response
    const extendedConfig = error.config as ExtendedAxiosRequestConfig
    const duration = extendedConfig?.metadata ? Date.now() - extendedConfig.metadata.startTime : undefined
    logger.apiResponse(
      error.config?.method?.toUpperCase() || 'UNKNOWN',
      error.config?.url || 'unknown',
      error.response?.status || 0,
      error.response?.data,
      duration
    )
    
    if (error.response?.status === 401) {
      logger.warn('Auth', 'Unauthorized - redirecting to login', { error: error.response?.data })
      localStorage.removeItem('authToken')
      authToken = null
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authService = {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const { data } = await api.post<AuthResponse>('/auth/login', credentials)
    authToken = data.token
    localStorage.setItem('authToken', data.token)
    return data
  },

  async register(userData: RegisterRequest): Promise<User> {
    const { data } = await api.post<User>('/auth/register', userData)
    return data
  },

  async logout(): Promise<void> {
    try {
      await api.post('/auth/logout')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      authToken = null
      localStorage.removeItem('authToken')
    }
  },

  async getCurrentUser(): Promise<User> {
    const { data } = await api.get<User>('/auth/me')
    return data
  },

  isAuthenticated(): boolean {
    return !!authToken
  }
}

export const videoService = {
  async getVideos(): Promise<VideoInfo[]> {
    const { data } = await api.get<VideoInfo[]>('/videos')
    return data
  },

  getVideoStreamUrl(series: string, episode: string): string {
    const token = localStorage.getItem('authToken')
    const baseUrl = `${API_BASE_URL}/videos/${encodeURIComponent(series)}/${encodeURIComponent(episode)}`
    return token ? `${baseUrl}?token=${encodeURIComponent(token)}` : baseUrl
  },

  async uploadVideo(series: string, videoFile: File): Promise<VideoInfo> {
    const formData = new FormData()
    formData.append('video_file', videoFile)
    
    const { data } = await api.post<VideoInfo>(`/videos/upload/${encodeURIComponent(series)}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return data
  },

  // MODIFIED: This function will now start the full pipeline
  async prepareEpisode(videoPath: string): Promise<{ task_id: string; status: string }> {
    const { data } = await api.post('/process/prepare-episode', { video_path: videoPath })
    return data
  },

  // The old transcribeVideo can be removed or kept for other purposes
  // async transcribeVideo(videoPath: string): Promise<{ task_id: string; status: string }> { ... }

  async filterSubtitles(videoPath: string): Promise<{ task_id: string; status: string }> {
    const { data } = await api.post('/process/filter-subtitles', { video_path: videoPath })
    return data
  },

  async translateSubtitles(videoPath: string, sourceLang: string, targetLang: string): Promise<{ task_id: string; status: string }> {
    const { data } = await api.post('/process/translate-subtitles', { video_path: videoPath, source_lang: sourceLang, target_lang: targetLang })
    return data
  },

  async getTaskProgress(taskId: string): Promise<ProcessingStatus> {
    const { data } = await api.get(`/process/progress/${taskId}`)
    return data
  },

  async processChunk(videoPath: string, startTime: number, endTime: number): Promise<{ task_id: string; status: string }> {
    const { data } = await api.post('/process/chunk', { 
      video_path: videoPath,
      start_time: startTime,
      end_time: endTime
    })
    return data
  }
}

export const vocabularyService = {
  async getBlockingWords(
    videoPath: string, 
    segmentStart: number = 0, 
    segmentDuration: number = 300
  ): Promise<VocabularyWord[]> {
    const { data } = await api.get('/vocabulary/blocking-words', {
      params: {
        video_path: videoPath,
        segment_start: segmentStart,
        segment_duration: segmentDuration
      }
    })
    return data.blocking_words
  },

  async markWordAsKnown(word: string, known: boolean): Promise<void> {
    await api.post('/vocabulary/mark-known', { word, known })
  },

  // Vocabulary Library APIs
  async preloadVocabulary(): Promise<{ success: boolean; message: string; levels: Record<string, number> }> {
    const { data } = await api.post('/vocabulary/preload')
    return data
  },

  async getVocabularyLevel(level: string): Promise<VocabularyLevel> {
    const { data } = await api.get<VocabularyLevel>(`/vocabulary/library/${level}`)
    return data
  },

  async bulkMarkLevel(level: string, known: boolean): Promise<{ success: boolean; message: string; word_count: number }> {
    const { data } = await api.post('/vocabulary/library/bulk-mark', { level, known })
    return data
  },

  async getVocabularyStats(): Promise<VocabularyStats> {
    const { data } = await api.get<VocabularyStats>('/vocabulary/library/stats')
    return data
  }
}

// Export the api instance for direct use when needed
export { api }

export const handleApiError = (error: any) => {
  let message = 'An error occurred'
  
  if (error.response?.data) {
    const data = error.response.data
    
    // Handle Pydantic validation errors
    if (Array.isArray(data) && data[0]?.type && data[0]?.msg) {
      message = `Validation error: ${data[0].msg}`
    }
    // Handle standard FastAPI errors
    else if (data.detail) {
      message = typeof data.detail === 'string' ? data.detail : 'Request validation failed'
    }
  }
  // Handle network errors
  else if (error.message) {
    message = error.message
  }
  
  toast.error(message)
  console.error('API Error:', error)
}

// Legacy API wrapper functions for test compatibility
export const getProcessingStatus = (taskId: string) => 
  api.get(`/processing/${taskId}/status`).then(res => res.data)