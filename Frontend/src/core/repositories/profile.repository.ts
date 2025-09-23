/**
 * Profile Repository
 * Manages user profile and settings
 */

import { HttpClient } from '../clients/http.client'

export interface UserProfile {
  id: string
  email: string
  username: string
  native_language: string
  target_language: string
  difficulty_level: 'beginner' | 'intermediate' | 'advanced'
  daily_goal: number // minutes per day
  streak_count: number
  total_study_time: number // total minutes
  words_learned: number
  created_at: string
  updated_at: string
}

export interface LanguagePreferences {
  native_language: string
  target_language: string
}

export interface StudySettings {
  daily_goal: number
  difficulty_level: 'beginner' | 'intermediate' | 'advanced'
  subtitle_display: 'native' | 'target' | 'both' | 'none'
  auto_pause: boolean
  playback_speed: number
}

export class ProfileRepository {
  private profileCache: UserProfile | null = null
  private cacheExpiry: number = 10 * 60 * 1000 // 10 minutes
  private lastFetch: number = 0

  constructor(private http: HttpClient) {}

  async getProfile(forceRefresh: boolean = false): Promise<UserProfile | null> {
    const now = Date.now()

    // Return cached profile if valid and not forcing refresh
    if (!forceRefresh && this.profileCache && (now - this.lastFetch) < this.cacheExpiry) {
      return this.profileCache
    }

    try {
      const profile = await this.http.get<UserProfile>('/api/profile')
      this.profileCache = profile
      this.lastFetch = now
      return profile
    } catch (error: any) {
      if (error.response?.status === 401) {
        // User not authenticated
        return null
      }
      throw error
    }
  }

  async updateProfile(updates: Partial<UserProfile>): Promise<UserProfile> {
    const profile = await this.http.patch<UserProfile>('/api/profile', updates)
    this.profileCache = profile
    this.lastFetch = Date.now()
    return profile
  }

  async updateLanguagePreferences(preferences: LanguagePreferences): Promise<UserProfile> {
    const profile = await this.http.put<UserProfile>('/api/profile/languages', preferences)
    this.profileCache = profile
    this.lastFetch = Date.now()
    return profile
  }

  async updateStudySettings(settings: Partial<StudySettings>): Promise<UserProfile> {
    const profile = await this.http.put<UserProfile>('/api/profile/settings', settings)
    this.profileCache = profile
    this.lastFetch = Date.now()
    return profile
  }

  async getSupportedLanguages(): Promise<Array<{ code: string; name: string; native_name: string }>> {
    // This could be cached more aggressively as it rarely changes
    const cached = localStorage.getItem('supported_languages')
    if (cached) {
      try {
        const data = JSON.parse(cached)
        if (data.expiry > Date.now()) {
          return data.languages
        }
      } catch {
        // Invalid cache, fetch fresh
      }
    }

    const response = await this.http.get<{ languages: Array<{ code: string; name: string; native_name: string }> }>(
      '/api/profile/languages'
    )

    // Cache for 24 hours
    localStorage.setItem('supported_languages', JSON.stringify({
      languages: response.languages,
      expiry: Date.now() + 24 * 60 * 60 * 1000
    }))

    return response.languages
  }

  async updateDailyProgress(studyMinutes: number, wordsLearned: number): Promise<UserProfile> {
    const profile = await this.http.post<UserProfile>('/api/profile/progress', {
      study_minutes: studyMinutes,
      words_learned: wordsLearned,
    })
    this.profileCache = profile
    this.lastFetch = Date.now()
    return profile
  }

  // Utility methods
  clearCache(): void {
    this.profileCache = null
    this.lastFetch = 0
  }

  getCachedProfile(): UserProfile | null {
    return this.profileCache
  }

  isCacheValid(): boolean {
    return this.profileCache !== null && (Date.now() - this.lastFetch) < this.cacheExpiry
  }
}