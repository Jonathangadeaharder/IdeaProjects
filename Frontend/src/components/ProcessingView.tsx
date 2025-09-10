import React from 'react';
import styled from 'styled-components';
import type { ProcessingStatus } from '@/types';

const ProcessingContainer = styled.div`
  font-size: 12px;
  color: #b3b3b3;
  text-align: center;
  margin-top: 8px;
  width: 100%;
  padding: 0 10px;
`;

const StepTitle = styled.div`
  font-weight: 500;
  color: #e87c03; /* Netflix Orange */
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const ProgressBarContainer = styled.div`
  width: 100%;
  height: 6px;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
  margin: 4px 0;
  overflow: hidden;
`;

const ProgressBarFill = styled.div<{ $progress: number }>`
  width: ${props => props.$progress}%;
  height: 100%;
  background-color: #e87c03;
  border-radius: 3px;
  transition: width 0.3s ease-in-out;
`;

const Message = styled.div`
  font-style: italic;
  height: 2.5em; /* Reserve space for 2 lines to prevent layout shift */
  line-height: 1.25em;
  overflow: hidden;
`;

interface ProcessingViewProps {
  status: ProcessingStatus;
}

export const ProcessingView: React.FC<ProcessingViewProps> = ({ status }) => {
  if (!status || status.status !== 'processing') {
    return null;
  }

  return (
    <ProcessingContainer>
      <StepTitle>{status.current_step} ({Math.round(status.progress)}%)</StepTitle>
      <ProgressBarContainer>
        <ProgressBarFill $progress={status.progress} />
      </ProgressBarContainer>
      <Message>{status.message}</Message>
    </ProcessingContainer>
  );
};