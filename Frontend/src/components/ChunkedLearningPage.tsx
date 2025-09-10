import React from 'react'
import { useLocation } from 'react-router-dom'
import { ChunkedLearningFlow } from './ChunkedLearningFlow'
import type { VideoInfo } from '@/types'

export const ChunkedLearningPage: React.FC = () => {
  const location = useLocation()
  const videoInfo = location.state?.videoInfo as VideoInfo

  if (!videoInfo) {
    return (
      <div style={{ 
        color: 'white', 
        padding: '40px', 
        textAlign: 'center',
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#141414'
      }}>
        <h1>Video information not found. Please go back and select an episode.</h1>
      </div>
    )
  }

  return <ChunkedLearningFlow videoInfo={videoInfo} chunkDurationMinutes={5} />
}