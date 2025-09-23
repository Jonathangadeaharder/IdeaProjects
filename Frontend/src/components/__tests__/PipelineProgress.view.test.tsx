/**
 * Tests for PipelineProgress Presentation Component
 * Tests pure component logic without any dependencies
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { PipelineProgressView } from '../PipelineProgress.view'
import { createTestVideo, createTestTask } from '@/test/utils/test-helpers'

describe('PipelineProgressView Component', () => {
  const mockHandlers = {
    onBack: vi.fn(),
    onStartProcessing: vi.fn(),
    onCancelProcessing: vi.fn(),
    onRetry: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders loading state', () => {
    render(
      <PipelineProgressView
        episode={null}
        task={null}
        loading={true}
        error={null}
        {...mockHandlers}
      />
    )

    expect(screen.getByText('Loading episode information...')).toBeInTheDocument()
  })

  it('renders error state', () => {
    render(
      <PipelineProgressView
        episode={null}
        task={null}
        loading={false}
        error="Network error occurred"
        {...mockHandlers}
      />
    )

    expect(screen.getByText('Failed to load episode')).toBeInTheDocument()
    expect(screen.getByText('Network error occurred')).toBeInTheDocument()

    const retryButton = screen.getByText('Retry')
    fireEvent.click(retryButton)
    expect(mockHandlers.onRetry).toHaveBeenCalled()
  })

  it('renders episode not found state', () => {
    render(
      <PipelineProgressView
        episode={null}
        task={null}
        loading={false}
        error={null}
        {...mockHandlers}
      />
    )

    expect(screen.getByText('Episode Not Found')).toBeInTheDocument()
    expect(screen.getByText('The requested episode could not be found.')).toBeInTheDocument()

    const backButton = screen.getByText('Go Back')
    fireEvent.click(backButton)
    expect(mockHandlers.onBack).toHaveBeenCalled()
  })

  it('renders episode ready to process', () => {
    const episode = createTestVideo()

    render(
      <PipelineProgressView
        episode={episode}
        task={null}
        loading={false}
        error={null}
        {...mockHandlers}
      />
    )

    expect(screen.getByText(episode.title)).toBeInTheDocument()
    expect(screen.getByText('Status: Ready to Process')).toBeInTheDocument()
    expect(screen.getByText('Start Processing')).toBeInTheDocument()

    const startButton = screen.getByText('Start Processing')
    fireEvent.click(startButton)
    expect(mockHandlers.onStartProcessing).toHaveBeenCalled()
  })

  it('renders processing state with progress', () => {
    const episode = createTestVideo()
    const task = createTestTask({
      status: 'processing',
      progress_percentage: 60,
      current_step: 'filtering',
      steps_completed: 3,
      total_steps: 5,
      message: 'Filtering subtitles...',
    })

    render(
      <PipelineProgressView
        episode={episode}
        task={task}
        loading={false}
        error={null}
        {...mockHandlers}
      />
    )

    expect(screen.getByText('Status: Processing')).toBeInTheDocument()
    expect(screen.getByText('60%')).toBeInTheDocument()
    expect(screen.getByText('Step 3 of 5: filtering')).toBeInTheDocument()
    expect(screen.getByText('Filtering subtitles...')).toBeInTheDocument()

    const cancelButton = screen.getByText('Cancel')
    fireEvent.click(cancelButton)
    expect(mockHandlers.onCancelProcessing).toHaveBeenCalled()
  })

  it('renders completed state', () => {
    const episode = createTestVideo()
    const task = createTestTask({
      status: 'completed',
      progress_percentage: 100,
      current_step: 'complete',
      steps_completed: 5,
      total_steps: 5,
      message: 'Processing complete!',
    })

    render(
      <PipelineProgressView
        episode={episode}
        task={task}
        loading={false}
        error={null}
        {...mockHandlers}
      />
    )

    expect(screen.getByText('Status: Completed')).toBeInTheDocument()
    expect(screen.getByText('100%')).toBeInTheDocument()
    expect(screen.getByText('Processing complete!')).toBeInTheDocument()

    const continueButton = screen.getByText('Continue to Video')
    fireEvent.click(continueButton)
    expect(mockHandlers.onBack).toHaveBeenCalled()
  })

  it('renders failed state with error', () => {
    const episode = createTestVideo()
    const task = createTestTask({
      status: 'failed',
      progress_percentage: 40,
      error: 'Transcription service unavailable',
    })

    render(
      <PipelineProgressView
        episode={episode}
        task={task}
        loading={false}
        error={null}
        {...mockHandlers}
      />
    )

    expect(screen.getByText('Status: Failed')).toBeInTheDocument()
    expect(screen.getByText('Error:', { exact: false })).toBeInTheDocument()
    expect(screen.getByText('Transcription service unavailable')).toBeInTheDocument()

    const retryButton = screen.getByText('Retry')
    fireEvent.click(retryButton)
    expect(mockHandlers.onRetry).toHaveBeenCalled()
  })

  it('displays episode information correctly', () => {
    const episode = createTestVideo({
      series: 'Dark',
      episode: 'S01E03',
      duration: 3600,
      difficulty_level: 'advanced',
      vocabulary_count: 350,
    })

    render(
      <PipelineProgressView
        episode={episode}
        task={null}
        loading={false}
        error={null}
        {...mockHandlers}
      />
    )

    expect(screen.getByText('Episode Information')).toBeInTheDocument()
    expect(screen.getByText('Dark', { exact: false })).toBeInTheDocument()
    expect(screen.getByText('S01E03', { exact: false })).toBeInTheDocument()
    expect(screen.getByText('60 minutes', { exact: false })).toBeInTheDocument()
    expect(screen.getByText('advanced', { exact: false })).toBeInTheDocument()
    expect(screen.getByText('350', { exact: false })).toBeInTheDocument()
  })

  it('handles back navigation correctly', () => {
    const episode = createTestVideo()

    render(
      <PipelineProgressView
        episode={episode}
        task={null}
        loading={false}
        error={null}
        {...mockHandlers}
      />
    )

    const backButton = screen.getByText('← Back')
    fireEvent.click(backButton)
    expect(mockHandlers.onBack).toHaveBeenCalled()
  })
})