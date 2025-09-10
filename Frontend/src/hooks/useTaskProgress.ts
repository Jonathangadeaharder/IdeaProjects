import { useState, useEffect, useCallback } from 'react'
import { videoService } from '@/services/api'
import type { ProcessingStatus } from '@/types'

export const useTaskProgress = (taskId: string | null, onComplete?: () => void, onError?: (error: string) => void) => {
  const [progress, setProgress] = useState<ProcessingStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const pollProgress = useCallback(async () => {
    if (!taskId) return

    setLoading(true)
    setError(null)

    try {
      const progressData = await videoService.getTaskProgress(taskId)
      setProgress(progressData)

      if (progressData.status === 'completed') {
        onComplete?.()
      } else if (progressData.status === 'error') {
        const errorMessage = progressData.message || 'An error occurred'
        onError?.(errorMessage)
      }
    } catch (err) {
      const errorMessage = 'Failed to fetch progress'
      setError(errorMessage)
      onError?.(errorMessage)
      console.error('Progress polling error:', err)
    } finally {
      setLoading(false)
    }
  }, [taskId, onComplete, onError])

  useEffect(() => {
    if (!taskId) return

    // Poll immediately on task start
    pollProgress()

    // Set up interval for polling
    const interval = setInterval(pollProgress, 1000)

    // Clean up interval on unmount or when task changes
    return () => clearInterval(interval)
  }, [taskId, pollProgress])

  return { progress, loading, error, refetch: pollProgress }
}