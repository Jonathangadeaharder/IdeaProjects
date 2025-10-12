import type {
  ProcessingStatus as ApiProcessingStatus,
  UserRead,
  VideoInfo as ApiVideoInfo,
  VocabularyWord as ApiVocabularyWord,
} from '@/client/types.gen'

export type User = UserRead & {
  name?: string
  is_admin?: boolean
}

export interface AuthResponse {
  token: string
  user: User
  expires_at: string
}

export type VideoInfo = ApiVideoInfo

export type VocabularyWord = ApiVocabularyWord & {
  definition?: string
  known: boolean
}

export interface VocabularyLibraryWord extends VocabularyWord {
  id: string
}

export interface VocabularyLevel {
  level: string
  words: VocabularyLibraryWord[]
  total_count: number
  known_count: number
  target_language?: string
  translation_language?: string | null
}

// TODO: Backend should export VocabularyStats in OpenAPI schema
// Manually defined based on backend api/models/vocabulary.py VocabularyStats
export interface VocabularyStats {
  levels: Record<string, { total_words: number; user_known: number }>
  target_language: string
  translation_language: string | null
  total_words: number
  total_known: number
}

export type ProcessingStatus = ApiProcessingStatus & {
  status: ApiProcessingStatus['status'] | 'monitoring' | 'failed' | 'idle' | 'error'
  current_step?: string | null
  message?: string
  vocabulary?: VocabularyWord[]
  started_at?: number
  translation_path?: string | null
}

export interface VideoSegment {
  start_time: number
  duration: number
  blocking_words: VocabularyWord[]
  subtitles_processed: boolean
}

export interface GameSession {
  video_path: string
  current_segment: number
  segments: VideoSegment[]
  user_progress: Record<string, boolean>
  completed: boolean
}
