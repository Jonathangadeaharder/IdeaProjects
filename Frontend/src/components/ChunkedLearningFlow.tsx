import React, { useState, useEffect, useCallback } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import { ProcessingScreen } from './ProcessingScreen'
import { VocabularyGame } from './VocabularyGame'
import { ChunkedLearningPlayer } from './ChunkedLearningPlayer'
import { videoService, handleApiError } from '@/services/api'
import type { VideoInfo, ProcessingStatus, VocabularyWord } from '@/types'

interface ChunkData {
  chunkNumber: number
  startTime: number // in seconds
  endTime: number // in seconds
  vocabulary: VocabularyWord[]
  subtitlePath?: string
  isProcessed: boolean
}

interface ChunkedLearningFlowProps {
  videoInfo: VideoInfo
  chunkDurationMinutes?: number // Default 5 minutes
}

export const ChunkedLearningFlow: React.FC<ChunkedLearningFlowProps> = ({ 
  videoInfo, 
  chunkDurationMinutes = 5 
}) => {
  const navigate = useNavigate()
  const { series, episode } = useParams<{ series: string; episode: string }>()
  
  // State management
  const [currentPhase, setCurrentPhase] = useState<'processing' | 'game' | 'video'>('processing')
  const [currentChunk, setCurrentChunk] = useState(0)
  const [chunks, setChunks] = useState<ChunkData[]>([])
  const [processingStatus, setProcessingStatus] = useState<ProcessingStatus>({
    status: 'processing',
    progress: 0,
    current_step: 'Initializing',
    message: 'Starting processing...'
  })
  const [taskId, setTaskId] = useState<string | null>(null)
  const [gameWords, setGameWords] = useState<VocabularyWord[]>([])
  const [learnedWords, setLearnedWords] = useState<Set<string>>(new Set())

  // Calculate total chunks based on video duration
  useEffect(() => {
    console.log(`[ChunkedLearningFlow] 🎬 Initializing chunks for video: ${videoInfo.path}`)
    const videoDurationMinutes = videoInfo.duration || 25 // Assume 25 minutes if not provided
    const totalChunks = Math.ceil(videoDurationMinutes / chunkDurationMinutes)
    
    console.log(`[ChunkedLearningFlow] Video duration: ${videoDurationMinutes} min, Chunk size: ${chunkDurationMinutes} min, Total chunks: ${totalChunks}`)
    
    const newChunks: ChunkData[] = []
    for (let i = 0; i < totalChunks; i++) {
      newChunks.push({
        chunkNumber: i + 1,
        startTime: i * chunkDurationMinutes * 60,
        endTime: Math.min((i + 1) * chunkDurationMinutes * 60, videoDurationMinutes * 60),
        vocabulary: [],
        isProcessed: false
      })
    }
    console.log(`[ChunkedLearningFlow] Created ${newChunks.length} chunks`)
    setChunks(newChunks)
  }, [videoInfo.duration, chunkDurationMinutes])

  // Format time for display
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  // Process current chunk
  const processChunk = async (chunkIndex: number) => {
    console.log(`[ChunkedLearningFlow] 🎬 processChunk called with index: ${chunkIndex}/${chunks.length}`)
    
    if (chunkIndex >= chunks.length) {
      console.log(`[ChunkedLearningFlow] 🎉 All chunks processed! Episode completed!`)
      // All chunks processed
      toast.success('Episode completed!')
      navigate(`/series/${series}`)
      return
    }

    const chunk = chunks[chunkIndex]
    console.log(`[ChunkedLearningFlow] Processing chunk details:`, {
      chunkNumber: chunk.chunkNumber,
      startTime: chunk.startTime,
      endTime: chunk.endTime,
      videoPath: videoInfo.path
    })
    
    console.log(`[ChunkedLearningFlow] Setting phase to PROCESSING`)
    setCurrentPhase('processing')
    setProcessingStatus({
      status: 'processing',
      progress: 0,
      current_step: 'Processing chunk',
      message: `Processing segment ${formatTime(chunk.startTime)} - ${formatTime(chunk.endTime)}`
    })

    try {
      console.log(`[ChunkedLearningFlow] 📡 Calling backend to process chunk...`)
      // Call backend to process this specific chunk
      const response = await videoService.processChunk(
        videoInfo.path,
        chunk.startTime,
        chunk.endTime
      )
      
      console.log(`[ChunkedLearningFlow] Backend response:`, response)
      console.log(`[ChunkedLearningFlow] Task ID received: ${response.task_id}`)
      setTaskId(response.task_id)
      
      // Start polling for progress
      console.log(`[ChunkedLearningFlow] Starting progress polling...`)
      pollProgress(response.task_id, chunkIndex)
    } catch (error) {
      console.error('[ChunkedLearningFlow] ❌ Failed to start chunk processing:', error)
      handleApiError(error)
      toast.error('Failed to process chunk')
    }
  }

  // Poll for processing progress
  const pollProgress = async (taskId: string, chunkIndex: number) => {
    console.log(`[ChunkedLearningFlow] 🔄 Starting progress polling for task: ${taskId}, chunk: ${chunkIndex}`)
    const maxAttempts = 180 // 15 minutes max
    let attempts = 0

    const poll = async () => {
      try {
        console.log(`[ChunkedLearningFlow] Polling attempt ${attempts + 1}/${maxAttempts} for task: ${taskId}`)
        const progress = await videoService.getTaskProgress(taskId)
        console.log('[ChunkedLearningFlow] Progress received:', JSON.stringify(progress, null, 2))
        setProcessingStatus(progress)

        if (progress.status === 'completed') {
          console.log(`[ChunkedLearningFlow] ✅ Processing COMPLETED for chunk ${chunkIndex}!`)
          console.log(`[ChunkedLearningFlow] Vocabulary items received: ${progress.vocabulary?.length || 0}`)
          console.log(`[ChunkedLearningFlow] Subtitle path: ${progress.subtitle_path}`)
          
          // Update chunk data with results
          const updatedChunks = [...chunks]
          updatedChunks[chunkIndex] = {
            ...updatedChunks[chunkIndex],
            vocabulary: progress.vocabulary || [],
            subtitlePath: progress.subtitle_path,
            isProcessed: true
          }
          setChunks(updatedChunks)
          setGameWords(progress.vocabulary || [])
          
          console.log(`[ChunkedLearningFlow] 🎮 Transitioning to GAME phase from PROCESSING phase`)
          // Move to game phase
          setCurrentPhase('game')
          return
        }

        if (progress.status === 'error') {
          console.error(`[ChunkedLearningFlow] ❌ Processing FAILED: ${progress.message}`)
          toast.error(`Processing failed: ${progress.message}`)
          return
        }

        attempts++
        if (attempts < maxAttempts) {
          console.log(`[ChunkedLearningFlow] Status: ${progress.status}, Progress: ${progress.progress}%, will poll again in 3s`)
          setTimeout(poll, 3000) // Poll every 3 seconds
        } else {
          console.error(`[ChunkedLearningFlow] ⏱️ Processing TIMEOUT after ${maxAttempts} attempts`)
          toast.error('Processing timeout')
        }
      } catch (error) {
        console.error('[ChunkedLearningFlow] ❌ Error polling progress:', error)
        attempts++
        if (attempts < maxAttempts) {
          console.log(`[ChunkedLearningFlow] Retrying poll in 3 seconds...`)
          setTimeout(poll, 3000)
        } else {
          console.error(`[ChunkedLearningFlow] Failed after ${maxAttempts} attempts`)
        }
      }
    }

    poll()
  }

  // Handle game completion
  const handleGameComplete = (knownWords: string[], unknownWords: string[]) => {
    console.log(`[ChunkedLearningFlow] 🎮 Game completed!`)
    console.log(`[ChunkedLearningFlow] Known words: ${knownWords.length}, Unknown words: ${unknownWords.length}`)
    
    // Add known words to learned set
    knownWords.forEach(word => learnedWords.add(word))
    setLearnedWords(new Set(learnedWords))
    
    console.log(`[ChunkedLearningFlow] 📺 Transitioning to VIDEO phase from GAME phase`)
    // Move to video phase
    setCurrentPhase('video')
  }

  // Handle video completion
  const handleVideoComplete = () => {
    console.log(`[ChunkedLearningFlow] 📺 Video phase completed for chunk ${currentChunk}`)
    
    // Move to next chunk
    const nextChunk = currentChunk + 1
    console.log(`[ChunkedLearningFlow] Moving to chunk ${nextChunk}/${chunks.length}`)
    setCurrentChunk(nextChunk)
    
    if (nextChunk < chunks.length) {
      console.log(`[ChunkedLearningFlow] 🔄 Processing next chunk: ${nextChunk}`)
      // Process next chunk
      processChunk(nextChunk)
    } else {
      console.log(`[ChunkedLearningFlow] 🎉 All chunks completed! Episode finished!`)
      // All chunks completed
      toast.success('🎉 Episode completed! Great job!')
      navigate(`/series/${series}`)
    }
  }

  // Start processing first chunk on mount
  useEffect(() => {
    console.log(`[ChunkedLearningFlow] useEffect triggered - chunks.length: ${chunks.length}, currentChunk: ${currentChunk}, currentPhase: ${currentPhase}`)
    if (chunks.length > 0 && currentChunk === 0 && currentPhase === 'processing') {
      console.log(`[ChunkedLearningFlow] 🚀 Starting processing of first chunk`)
      processChunk(0)
    }
  }, [chunks])

  // Render based on current phase
  const renderPhase = () => {
    const chunk = chunks[currentChunk]
    if (!chunk) return null

    switch (currentPhase) {
      case 'processing':
        return (
          <ProcessingScreen 
            status={processingStatus}
            chunkNumber={currentChunk + 1}
            totalChunks={chunks.length}
            chunkDuration={`${formatTime(chunk.startTime)} - ${formatTime(chunk.endTime)}`}
          />
        )
      
      case 'game':
        return (
          <VocabularyGame 
            words={gameWords}
            onComplete={handleGameComplete}
            episodeTitle={videoInfo.title}
            chunkInfo={{
              current: currentChunk + 1,
              total: chunks.length,
              duration: `${formatTime(chunk.startTime)} - ${formatTime(chunk.endTime)}`
            }}
          />
        )
      
      case 'video':
        return (
          <ChunkedLearningPlayer
            videoPath={videoInfo.path}
            series={videoInfo.series}
            episode={videoInfo.episode}
            subtitlePath={chunk.subtitlePath}
            startTime={chunk.startTime}
            endTime={chunk.endTime}
            onComplete={handleVideoComplete}
            learnedWords={Array.from(learnedWords)}
            chunkInfo={{
              current: currentChunk + 1,
              total: chunks.length,
              duration: `${formatTime(chunk.startTime)} - ${formatTime(chunk.endTime)}`
            }}
          />
        )
      
      default:
        return null
    }
  }

  return (
    <>
      {renderPhase()}
    </>
  )
}