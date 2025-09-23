/**
 * PipelineProgress Container Component
 * Handles routing, data fetching, and business logic
 * Renders the presentation component with data
 */

import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useDI } from '@/core/di/container'
import { useTaskProgress } from '@/hooks/useTaskProgress'
import { PipelineProgressView } from './PipelineProgress.view'
import { VideoInfo, ProcessingTask } from '@/core/repositories/video.repository'
import toast from 'react-hot-toast'

export const PipelineProgressContainer: React.FC = () => {
  const { series, episode: episodeParam } = useParams<{ series: string; episode: string }>()
  const navigate = useNavigate()
  const { videos } = useDI()

  const [episode, setEpisode] = useState<VideoInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [taskId, setTaskId] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)

  // Use the existing hook for task progress
  const { progress: task } = useTaskProgress(taskId)

  useEffect(() => {
    loadEpisode()
  }, [series, episodeParam])

  const loadEpisode = async () => {
    if (!series || !episodeParam) {
      setError('Invalid episode parameters')
      setLoading(false)
      return
    }

    try {
      setLoading(true)
      setError(null)

      const foundEpisode = await videos.getByEpisode(series, episodeParam)

      if (foundEpisode) {
        setEpisode(foundEpisode)

        // Check if already processing
        if (foundEpisode.processing_status === 'processing') {
          // TODO: Get task ID from episode metadata
          // For now, we'll need to track this separately
        }
      } else {
        setError('Episode not found')
      }
    } catch (err: any) {
      console.error('Failed to load episode:', err)
      setError(err.message || 'Failed to load episode')
    } finally {
      setLoading(false)
    }
  }

  const handleBack = () => {
    navigate(-1)
  }

  const handleStartProcessing = async () => {
    if (!episode) return

    try {
      setIsProcessing(true)
      setError(null)

      const task = await videos.startProcessing(episode.id, {
        target_language: 'de', // TODO: Get from user profile
        enable_translation: true,
        difficulty_filter: true,
      })

      setTaskId(task.task_id)
      toast.success('Processing started')
    } catch (err: any) {
      console.error('Failed to start processing:', err)
      setError(err.message || 'Failed to start processing')
      toast.error('Failed to start processing')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleCancelProcessing = async () => {
    if (!taskId) return

    try {
      // TODO: Implement cancel endpoint
      toast.success('Processing cancelled')
      setTaskId(null)
    } catch (err: any) {
      console.error('Failed to cancel processing:', err)
      toast.error('Failed to cancel processing')
    }
  }

  const handleRetry = () => {
    if (error && error.includes('episode')) {
      loadEpisode()
    } else {
      handleStartProcessing()
    }
  }

  // Check if processing is complete
  useEffect(() => {
    if (task?.status === 'completed' && episode) {
      toast.success('Processing complete!')

      // Navigate to learning page after a delay
      setTimeout(() => {
        navigate(`/learn/${series}/${episodeParam}`)
      }, 2000)
    } else if (task?.status === 'failed') {
      toast.error('Processing failed')
      setError(task.error || 'Processing failed')
    }
  }, [task?.status])

  return (
    <PipelineProgressView
      episode={episode}
      task={task as ProcessingTask | null}
      loading={loading}
      error={error}
      onBack={handleBack}
      onStartProcessing={handleStartProcessing}
      onCancelProcessing={handleCancelProcessing}
      onRetry={handleRetry}
    />
  )
}