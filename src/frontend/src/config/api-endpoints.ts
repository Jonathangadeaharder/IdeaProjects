/**
 * Centralized API endpoint paths configuration
 *
 * This file contains all API endpoint paths used across the application.
 * Having them in one place makes it easier to maintain and update endpoints.
 *
 * Note: These are relative paths that will be appended to the API base URL
 * configured in api-config.ts
 */

/**
 * Authentication endpoints
 */
export const AUTH_ENDPOINTS = {
  LOGIN: '/api/auth/login',
  REGISTER: '/api/auth/register',
  LOGOUT: '/api/auth/logout',
  REFRESH: '/api/auth/token/refresh',
  ME: '/api/auth/me',
} as const

/**
 * SRT (Subtitle) utility endpoints
 */
export const SRT_ENDPOINTS = {
  BASE: '/api/srt',
  PARSE: '/api/srt/parse',
  PARSE_FILE: '/api/srt/parse-file',
  CONVERT: '/api/srt/convert-to-srt',
  VALIDATE: '/api/srt/validate',
} as const

/**
 * Video endpoints
 */
export const VIDEO_ENDPOINTS = {
  BASE: '/api/videos',
  LIST: '/api/videos',
  UPLOAD: '/api/videos/upload',
  STREAM: '/api/videos/stream',
} as const

/**
 * Processing endpoints
 */
export const PROCESSING_ENDPOINTS = {
  BASE: '/api/process',
  CHUNK: '/api/process/chunk',
  STATUS: '/api/process/status',
} as const

/**
 * Vocabulary endpoints
 */
export const VOCABULARY_ENDPOINTS = {
  BASE: '/api/vocabulary',
  LIST: '/api/vocabulary',
  LEVELS: '/api/vocabulary/levels',
  PROGRESS: '/api/vocabulary/progress',
  KNOWN: '/api/vocabulary/known',
} as const

/**
 * Game endpoints
 */
export const GAME_ENDPOINTS = {
  BASE: '/api/game',
  START: '/api/game/start',
  SUBMIT: '/api/game/submit',
  RESULTS: '/api/game/results',
} as const

/**
 * User profile endpoints
 */
export const USER_ENDPOINTS = {
  BASE: '/api/users',
  PROFILE: '/api/users/me',
  PREFERENCES: '/api/users/preferences',
} as const

/**
 * All endpoint collections
 */
export const API_ENDPOINTS = {
  AUTH: AUTH_ENDPOINTS,
  SRT: SRT_ENDPOINTS,
  VIDEO: VIDEO_ENDPOINTS,
  PROCESSING: PROCESSING_ENDPOINTS,
  VOCABULARY: VOCABULARY_ENDPOINTS,
  GAME: GAME_ENDPOINTS,
  USER: USER_ENDPOINTS,
} as const

/**
 * Helper function to build full URL with base
 */
export function buildApiUrl(endpoint: string, baseUrl?: string): string {
  const base = baseUrl || ''
  return `${base}${endpoint}`
}
