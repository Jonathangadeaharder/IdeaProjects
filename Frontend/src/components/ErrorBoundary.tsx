import React from 'react';
import { ErrorBoundary as ReactErrorBoundary } from 'react-error-boundary';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';

const ErrorContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  text-align: center;
`;

const ErrorTitle = styled.h1`
  font-size: 3rem;
  margin-bottom: 1rem;
  font-weight: bold;
`;

const ErrorMessage = styled.p`
  font-size: 1.25rem;
  margin-bottom: 2rem;
  max-width: 600px;
  opacity: 0.9;
`;

const ErrorDetails = styled.details`
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 2rem;
  max-width: 800px;
  width: 100%;
  text-align: left;
`;

const ErrorSummary = styled.summary`
  cursor: pointer;
  font-weight: bold;
  margin-bottom: 0.5rem;
  
  &:hover {
    opacity: 0.8;
  }
`;

const ErrorStack = styled.pre`
  overflow-x: auto;
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
  line-height: 1.5;
  margin-top: 1rem;
  white-space: pre-wrap;
  word-wrap: break-word;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
`;

const Button = styled.button`
  background: white;
  color: #764ba2;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 50px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

interface ErrorFallbackProps {
  error: Error;
  resetErrorBoundary: () => void;
}

function ErrorFallback({ error, resetErrorBoundary }: ErrorFallbackProps) {
  const navigate = useNavigate();
  
  const handleGoHome = () => {
    resetErrorBoundary();
    navigate('/');
  };
  
  const handleReload = () => {
    window.location.reload();
  };
  
  // Log error to console and potentially to a service
  React.useEffect(() => {
    console.error('Error caught by error boundary:', error);
    
    // TODO: Send error to logging service
    // logErrorToService(error);
  }, [error]);
  
  return (
    <ErrorContainer role="alert">
      <ErrorTitle>Oops! Something went wrong</ErrorTitle>
      <ErrorMessage>
        We're sorry, but something unexpected happened. The error has been logged 
        and we'll look into it.
      </ErrorMessage>
      
      {process.env.NODE_ENV === 'development' && (
        <ErrorDetails>
          <ErrorSummary>Error Details (Development Only)</ErrorSummary>
          <div>
            <strong>{error.name}:</strong> {error.message}
          </div>
          {error.stack && (
            <ErrorStack>{error.stack}</ErrorStack>
          )}
        </ErrorDetails>
      )}
      
      <ButtonGroup>
        <Button onClick={resetErrorBoundary}>Try Again</Button>
        <Button onClick={handleGoHome}>Go Home</Button>
        <Button onClick={handleReload}>Reload Page</Button>
      </ButtonGroup>
    </ErrorContainer>
  );
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ComponentType<ErrorFallbackProps>;
  onError?: (error: Error, errorInfo: { componentStack: string }) => void;
  onReset?: () => void;
}

export function ErrorBoundary({ 
  children, 
  fallback = ErrorFallback,
  onError,
  onReset
}: ErrorBoundaryProps) {
  return (
    <ReactErrorBoundary
      FallbackComponent={fallback}
      onError={onError}
      onReset={onReset}
    >
      {children}
    </ReactErrorBoundary>
  );
}

// Specialized error boundary for specific sections
export function SectionErrorBoundary({ 
  children,
  sectionName = 'This section'
}: { 
  children: React.ReactNode;
  sectionName?: string;
}) {
  return (
    <ReactErrorBoundary
      FallbackComponent={({ error, resetErrorBoundary }) => (
        <div style={{ 
          padding: '2rem', 
          background: '#f8f9fa', 
          borderRadius: '8px',
          margin: '1rem 0',
          border: '1px solid #dee2e6'
        }}>
          <h3 style={{ color: '#dc3545', marginBottom: '1rem' }}>
            {sectionName} couldn't load
          </h3>
          <p style={{ color: '#6c757d', marginBottom: '1rem' }}>
            {error.message}
          </p>
          <button
            onClick={resetErrorBoundary}
            style={{
              background: '#007bff',
              color: 'white',
              border: 'none',
              padding: '0.5rem 1rem',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Retry
          </button>
        </div>
      )}
    >
      {children}
    </ReactErrorBoundary>
  );
}

// Hook for imperatively throwing errors to the nearest error boundary
export function useErrorHandler() {
  const [error, setError] = React.useState<Error | null>(null);
  
  React.useEffect(() => {
    if (error) {
      throw error;
    }
  }, [error]);
  
  return setError;
}