import { useState, useEffect, useCallback, useRef } from 'react'
import { getProcessingStatus } from '@/services/api'

type TaskState = 'idle' | 'monitoring' | 'processing' | 'completed' | 'failed' | 'error'

export const useTaskProgress = () => {
  const [taskId, setTaskId] = useState<string | null>(null)
  const [progress, setProgress] = useState<number>(0)
  const [status, setStatus] = useState<TaskState>('idle')
  const [error, setError] = useState<string | null>(null)
  const [isComplete, setIsComplete] = useState<boolean>(false)
  const [result, setResult] = useState<any>(null)
  const intervalRef = useRef<number | null>(null)

  const clearTimer = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }, [])

  const poll = useCallback(async () => {
    if (!taskId) return
    try {
      const res: any = await getProcessingStatus(taskId)
      setProgress(res?.progress ?? 0)

      if (res?.status === 'processing') {
        setStatus('processing')
      } else if (res?.status === 'completed') {
        setStatus('completed')
        setIsComplete(true)
        setResult(res?.result ?? null)
        clearTimer()
      } else if (res?.status === 'failed' || res?.status === 'error') {
        setStatus(res.status === 'failed' ? 'failed' : 'error')
        setError(res?.error || res?.message || 'Processing failed')
        clearTimer()
      } else {
        // Unknown status: keep processing
        setStatus('processing')
      }
    } catch (e: any) {
      setStatus('error')
      setError(e?.message || 'Network error')
      clearTimer()
    }
  }, [taskId, clearTimer])

  const startMonitoring = useCallback((id: string) => {
    setTaskId(id)
    setStatus('monitoring')
    setIsComplete(false)
    setError(null)
    setProgress(0)
    setResult(null)
    clearTimer()
    // Start polling every 2 seconds; first poll after 2s to match tests
    intervalRef.current = setInterval(poll, 2000) as any
  }, [poll, clearTimer])

  const stopMonitoring = useCallback(() => {
    clearTimer()
    setStatus('idle')
  }, [clearTimer])

  const reset = useCallback(() => {
    clearTimer()
    setTaskId(null)
    setProgress(0)
    setStatus('idle')
    setError(null)
    setIsComplete(false)
    setResult(null)
  }, [clearTimer])

  useEffect(() => {
    return () => {
      clearTimer()
    }
  }, [clearTimer])

  return {
    taskId,
    progress,
    status,
    error,
    isComplete,
    result,
    startMonitoring,
    stopMonitoring,
    reset,
  }
}