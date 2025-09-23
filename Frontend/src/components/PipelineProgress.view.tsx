/**
 * PipelineProgress Presentation Component
 * Pure component with no dependencies on routing or services
 * Fully testable with props
 */

import React from 'react'
import styled from 'styled-components'
import { ProcessingTask, VideoInfo } from '@/core/repositories/video.repository'

export interface PipelineProgressViewProps {
  episode: VideoInfo | null
  task: ProcessingTask | null
  loading: boolean
  error: string | null
  onBack: () => void
  onStartProcessing: () => void
  onCancelProcessing: () => void
  onRetry: () => void
}

const Container = styled.div`
  min-height: 100vh;
  background: #141414;
  color: white;
`

const Header = styled.header`
  padding: 20px 40px;
  background: rgba(0, 0, 0, 0.7);
  position: sticky;
  top: 0;
  z-index: 100;
`

const Nav = styled.nav`
  display: flex;
  align-items: center;
  gap: 24px;
`

const BackButton = styled.button`
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;

  &:hover {
    opacity: 0.8;
  }
`

const Title = styled.h1`
  font-size: 24px;
  font-weight: 500;
  margin: 0;
`

const Content = styled.main`
  padding: 40px;
  max-width: 1200px;
  margin: 0 auto;
`

const Card = styled.div`
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 32px;
  margin-bottom: 24px;
`

const ProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  overflow: hidden;
  margin: 20px 0;
`

const ProgressFill = styled.div<{ $percentage: number }>`
  height: 100%;
  background: ${props => props.$percentage === 100 ? '#46d369' : '#e50914'};
  width: ${props => props.$percentage}%;
  transition: width 0.3s ease;
`

const StatusText = styled.div<{ $status: string }>`
  font-size: 18px;
  font-weight: 500;
  color: ${props => {
    switch (props.$status) {
      case 'completed': return '#46d369'
      case 'failed': return '#e50914'
      case 'processing': return '#f4f4f4'
      default: return '#999'
    }
  }};
  margin-bottom: 12px;
`

const StepInfo = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 16px 0;
`

const StepText = styled.span`
  font-size: 14px;
  color: #999;
`

const PercentageText = styled.span`
  font-size: 20px;
  font-weight: bold;
`

const Message = styled.p`
  font-size: 16px;
  line-height: 1.5;
  color: #ccc;
  margin: 16px 0;
`

const ErrorMessage = styled.div`
  background: rgba(229, 9, 20, 0.2);
  border: 1px solid #e50914;
  border-radius: 4px;
  padding: 16px;
  margin: 16px 0;
`

const Button = styled.button`
  background: #e50914;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;

  &:hover:not(:disabled) {
    background: #f40612;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`

const SecondaryButton = styled(Button)`
  background: transparent;
  border: 1px solid #999;
  color: #999;

  &:hover:not(:disabled) {
    background: rgba(255, 255, 255, 0.1);
    border-color: white;
    color: white;
  }
`

const LoadingSpinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
  font-size: 18px;
  color: #999;
`

export const PipelineProgressView: React.FC<PipelineProgressViewProps> = ({
  episode,
  task,
  loading,
  error,
  onBack,
  onStartProcessing,
  onCancelProcessing,
  onRetry,
}) => {
  if (loading) {
    return (
      <Container>
        <LoadingSpinner>Loading episode information...</LoadingSpinner>
      </Container>
    )
  }

  if (error) {
    return (
      <Container>
        <Header>
          <Nav>
            <BackButton onClick={onBack}>
              ← Back
            </BackButton>
            <Title>Error</Title>
          </Nav>
        </Header>
        <Content>
          <ErrorMessage>
            <h3>Failed to load episode</h3>
            <p>{error}</p>
            <Button onClick={onRetry}>Retry</Button>
          </ErrorMessage>
        </Content>
      </Container>
    )
  }

  if (!episode) {
    return (
      <Container>
        <Header>
          <Nav>
            <BackButton onClick={onBack}>
              ← Back
            </BackButton>
            <Title>Episode Not Found</Title>
          </Nav>
        </Header>
        <Content>
          <Message>The requested episode could not be found.</Message>
          <Button onClick={onBack}>Go Back</Button>
        </Content>
      </Container>
    )
  }

  const getStatusDisplay = () => {
    if (!task) return 'Ready to Process'

    switch (task.status) {
      case 'pending': return 'Waiting to Start'
      case 'processing': return 'Processing'
      case 'completed': return 'Completed'
      case 'failed': return 'Failed'
      case 'cancelled': return 'Cancelled'
      default: return 'Unknown'
    }
  }

  return (
    <Container>
      <Header>
        <Nav>
          <BackButton onClick={onBack}>
            ← Back
          </BackButton>
          <Title>{episode.title || `${episode.series} - ${episode.episode}`}</Title>
        </Nav>
      </Header>

      <Content>
        <Card>
          <h2>Processing Pipeline</h2>

          <StatusText $status={task?.status || 'pending'}>
            Status: {getStatusDisplay()}
          </StatusText>

          {task && (
            <>
              <ProgressBar>
                <ProgressFill $percentage={task.progress_percentage} />
              </ProgressBar>

              <StepInfo>
                <StepText>
                  Step {task.steps_completed} of {task.total_steps}: {task.current_step}
                </StepText>
                <PercentageText>{task.progress_percentage}%</PercentageText>
              </StepInfo>

              {task.message && <Message>{task.message}</Message>}

              {task.error && (
                <ErrorMessage>
                  <strong>Error:</strong> {task.error}
                </ErrorMessage>
              )}
            </>
          )}

          <div style={{ marginTop: '24px', display: 'flex', gap: '12px' }}>
            {!task && (
              <Button onClick={onStartProcessing}>
                Start Processing
              </Button>
            )}

            {task?.status === 'processing' && (
              <SecondaryButton onClick={onCancelProcessing}>
                Cancel
              </SecondaryButton>
            )}

            {task?.status === 'failed' && (
              <Button onClick={onRetry}>
                Retry
              </Button>
            )}

            {task?.status === 'completed' && (
              <Button onClick={onBack}>
                Continue to Video
              </Button>
            )}
          </div>
        </Card>

        {episode && (
          <Card>
            <h3>Episode Information</h3>
            <Message>
              <strong>Series:</strong> {episode.series}<br />
              <strong>Episode:</strong> {episode.episode}<br />
              {episode.duration && <><strong>Duration:</strong> {Math.floor(episode.duration / 60)} minutes<br /></>}
              {episode.difficulty_level && <><strong>Difficulty:</strong> {episode.difficulty_level}<br /></>}
              {episode.vocabulary_count && <><strong>Vocabulary Words:</strong> {episode.vocabulary_count}<br /></>}
            </Message>
          </Card>
        )}
      </Content>
    </Container>
  )
}