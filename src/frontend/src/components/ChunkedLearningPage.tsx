import React, { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { ChunkedLearningFlow } from './ChunkedLearningFlow'
import type { VideoInfo } from '@/types'
import { profileGetApiProfileGet } from '@/client/services.gen'

export const ChunkedLearningPage: React.FC = () => {
  const location = useLocation()
  let videoInfo = location.state?.videoInfo as VideoInfo
  const [chunkDuration, setChunkDuration] = useState<number>(20)

  useEffect(() => {
    const loadUserPreferences = async () => {
      try {
        const profile = (await profileGetApiProfileGet()) as unknown as { chunk_duration_minutes?: number }
        if (profile?.chunk_duration_minutes) {
          setChunkDuration(profile.chunk_duration_minutes)
        }
      } catch (error) {
        console.error('Failed to load user preferences:', error)
        // Use default value of 20 if loading fails
      }
    }
    loadUserPreferences()
  }, [])

  // Fallback for E2E tests: check sessionStorage
  // This allows tests to inject videoInfo without fighting React Router's state management
  if (!videoInfo && typeof window !== 'undefined' && sessionStorage) {
    try {
      const testVideoInfo = sessionStorage.getItem('testVideoInfo')
      if (testVideoInfo) {
        videoInfo = JSON.parse(testVideoInfo) as VideoInfo
      }
    } catch (error) {
      console.warn('Failed to parse test videoInfo from sessionStorage', error)
    }
  }

  if (!videoInfo) {
    return (
      <div
        style={{
          color: 'white',
          padding: '40px',
          textAlign: 'center',
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: '#141414',
        }}
      >
        <h1>Video information not found. Please go back and select an episode.</h1>
      </div>
    )
  }

  return <ChunkedLearningFlow videoInfo={videoInfo} chunkDurationMinutes={chunkDuration} />
}
