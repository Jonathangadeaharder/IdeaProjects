import { renderHook, act } from '@testing-library/react-native';
import { useProcessingWorkflow } from '../../src/hooks/useProcessingWorkflow';

// Mock timers for testing
jest.useFakeTimers();

// Mock fetch for API calls
global.fetch = jest.fn();

describe('useProcessingWorkflow Hook', () => {
  const mockVideoFile = '/path/to/video.mp4';
  const mockConfig = {
    language: 'de',
    srcLang: 'de',
    tgtLang: 'en',
    enableFiltering: true,
    enableTranslation: true,
  };

  const mockOnStageChange = jest.fn();
  const mockOnComplete = jest.fn();
  const mockOnError = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    jest.clearAllTimers();
    (fetch as jest.MockedFunction<typeof fetch>).mockClear();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
  });

  describe('Initial State', () => {
    it('should initialize with correct default values', () => {
      const { result } = renderHook(() =>
        useProcessingWorkflow({
          videoFile: mockVideoFile,
          config: mockConfig,
          onStageChange: mockOnStageChange,
          onComplete: mockOnComplete,
          onError: mockOnError,
        })
      );

      expect(result.current.currentStage).toBe('idle');
      expect(result.current.isProcessing).toBe(false);
      expect(result.current.overallProgress).toBe(0);
      expect(result.current.currentStep).toBeNull();
      expect(result.current.steps).toHaveLength(0);
      expect(result.current.result).toBeNull();
      expect(result.current.error).toBeNull();
      expect(result.current.estimatedTimeRemaining).toBe(0);
    });

    it('should handle missing optional callbacks', () => {
      const { result } = renderHook(() =>
        useProcessingWorkflow({
          videoFile: mockVideoFile,
          config: mockConfig,
          // No callbacks provided
        })
      );

      expect(result.current.currentStage).toBe('idle');
      expect(result.current.isProcessing).toBe(false);
    });
  });

  describe('Processing Workflow', () => {
    it('should start processing workflow correctly', async () => {
      const mockResponse = {
        ok: true,
        json: async () => ({
          success: true,
          steps: [
            {
              id: 'transcription',
              name: 'Transcription',
              stage: 'transcription',
              progress: 0,
              status: 'pending',
            },
            {
              id: 'filtering',
              name: 'Filtering',
              stage: 'filtering',
              progress: 0,
              status: 'pending',
            },
          ],
        }),
      };

      (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValueOnce(
        mockResponse as Response
      );

      const { result } = renderHook(() =>
        useProcessingWorkflow({
          videoFile: mockVideoFile,
          config: mockConfig,
          onStageChange: mockOnStageChange,
        })
      );

      await act(async () => {
        await result.current.startProcessing();
      });

      expect(result.current.isProcessing).toBe(true);
      expect(result.current.currentStage).toBe('transcription');
      expect(result.current.steps).toHaveLength(2);
      expect(mockOnStageChange).toHaveBeenCalledWith('transcription');
    });

    it('should handle API error during start', async () => {
      const mockResponse = {
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
      };

      (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValueOnce(
        mockResponse as Response
      );

      const { result } = renderHook(() =>
        useProcessingWorkflow({
          videoFile: mockVideoFile,
          config: mockConfig,
          onError: mockOnError,
        })
      );

      await act(async () => {
        await result.current.startProcessing();
      });

      expect(result.current.isProcessing).toBe(false);
      expect(result.current.currentStage).toBe('error');
      expect(result.current.error).toContain('Failed to start processing');
      expect(mockOnError).toHaveBeenCalled();
    });

    it('should handle network error during start', async () => {
      (fetch as jest.MockedFunction<typeof fetch>).mockRejectedValueOnce(
        new Error('Network error')
      );

      const { result } = renderHook(() =>
        useProcessingWorkflow({
          videoFile: mockVideoFile,
          config: mockConfig,
          onError: mockOnError,
        })
      );

      await act(async () => {
        await result.current.startProcessing();
      });

      expect(result.current.isProcessing).toBe(false);
      expect(result.current.currentStage).toBe('error');
      expect(result.current.error).toContain('Network error');
      expect(mockOnError).toHaveBeenCalled();
    });
  });

  describe('Progress Updates', () => {
    it('should update step progress correctly', () => {
      const { result } = renderHook(() =>
        useProcessingWorkflow({
          videoFile: mockVideoFile,
          config: mockConfig,
        })
      );

      // Initialize with some steps
      act(() => {
        result.current.updateStepProgress('transcription', 50, 'Processing audio...');
      });

      const step = result.current.steps.find(s => s.id === 'transcription');
      expect(step?.progress).toBe(50);
      expect(step?.message).toBe('Processing audio...');
      expect(step?.status).toBe('active');
    });

    it('should calculate overall progress correctly', () => {
      const { result } = renderHook(() =>
        useProcessingWorkflow({
          videoFile: mockVideoFile,
          config: mockConfig,
        })
      );

      // Initialize steps
      act(() => {
        result.current.updateStepProgress('transcription', 100);
        result.current.updateStepProgress('filtering', 50);
        result.current.updateStepProgress('translation', 0);
      });

      // Overall progress should be (100 + 50 + 0) / 3 = 50
      expect(result.current.overallProgress).toBe(50);
    });

    it('should mark step as completed when progress reaches 100', () => {
      const { result } = renderHook(() =>
        useProcessingWorkflow({
          videoFile: mockVideoFile,
          config: mockConfig,
          onStageChange: mockOnStageChange,
        })
      );

      act(() => {
        result.current.updateStepProgress('transcription', 100, 'Completed');
      });

      const step = result.current.steps.find(s => s.id === 'transcription');
      expect(step?.status).toBe('completed');
      expect(step?.progress).toBe(100);
    });

    it('should advance to next stage when current step completes', () => {
      const { result } = renderHook(() =>
        useProcessingWorkflow({
          videoFile: mockVideoFile,
          config: mockConfig,
          onStageChange: mockOnStageChange,
        })
      );

      // Initialize with multiple steps
      act(() => {
        result.current.updateStepProgress('transcription', 0);
        result.current.updateStepProgress('filtering', 0);
      });

      // Complete transcription
      act(() => {
        result.current.updateStepProgress('transcription', 100);
      });

      expect(result.current.currentStage).toBe('filtering');
      expect(mockOnStageChange).toHaveBeenCalledWith('filtering');
    });
  });

  describe('Error Handling', () => {
    it('should handle step error correctly', () => {
      const { result } = renderHook(() =>
        useProcessingWorkflow({
          videoFile: mockVideoFile,
          config: mockConfig,
          onError: mockOnError,
        })
      );

      act(() => {
        result.current.setStepError('transcription', 'Transcription failed');
      });

      const step = result.current.steps.find(s => s.id === 'transcription');
      expect(step?.status).toBe('error');
      expect(step?.error).toBe('Transcription failed');
      expect(result.current.currentStage).toBe('error');
      expect(result.current.error).toBe('Transcription failed');
      expect(mockOnError).toHaveBeenCalledWith('Transcription failed');
    });

    it('should stop processing on error', () => {
      const { result } = renderHook(() =>
        useProcessingWorkflow({
          videoFile: mockVideoFile,
          config: mockConfig,
        })
      );

      // Start processing
      act(() => {
        result.current.updateStepProgress('transcription', 50);
      });

      expect(result.current.isProcessing).toBe(true);

      // Trigger error
      act(() => {
        result.current.setStepError('transcription', 'Error occurred');
      });

      expect(result.current.isProcessing).toBe(false);
      expect(result.current.currentStage).toBe('error');
    });
  });

  describe('Processing Completion', () => {
    it('should complete processing when all steps are done', async () => {
      const mockResult = {
        transcription: 'Test transcription',
        filteredWords: ['word1', 'word2'],
        translations: { word1: 'translation1' },
      };

      const mockResponse = {
        ok: true,
        json: async () => mockResult,
      };

      (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValueOnce(
        mockResponse as Response
      );

      const { result } = renderHook(() =>
        useProcessingWorkflow({
          videoFile: mockVideoFile,
          config: mockConfig,
          onComplete: mockOnComplete,
        })
      );

      // Initialize steps
      act(() => {
        result.current.updateStepProgress('transcription', 0);
        result.current.updateStepProgress('filtering', 0);
      });

      // Complete all steps
      await act(async () => {
        result.current.updateStepProgress('transcription', 100);
        result.current.updateStepProgress('filtering', 100);
      });

      expect(result.current.currentStage).toBe('complete');
      expect(result.current.isProcessing).toBe(false);
      expect(result.current.overallProgress).toBe(100);
      expect(result.current.result).toEqual(mockResult);
      expect(mockOnComplete).toHaveBeenCalledWith(mockResult);
    });

    it('should handle completion API error', async () => {
      const mockResponse = {
        ok: false,
        status: 500,
      };

      (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValueOnce(
        mockResponse as Response
      );

      const { result } = renderHook(() =>
        useProcessingWorkflow({
          videoFile: mockVideoFile,
          config: mockConfig,
          onError: mockOnError,
        })
      );

      // Initialize and complete steps
      act(() => {
        result.current.updateStepProgress('transcription', 0);
      });

      await act(async () => {
        result.current.updateStepProgress('transcription', 100);
      });

      expect(result.current.currentStage).toBe('error');
      expect(mockOnError).toHaveBeenCalled();
    });
  });

  describe('Processing Control', () => {
    it('should pause processing correctly', () => {
      const { result } = renderHook(() =>
        useProcessingWorkflow({
          videoFile: mockVideoFile,
          config: mockConfig,
        })
      );

      // Start processing
      act(() => {
        result.current.updateStepProgress('transcription', 50);
      });

      expect(result.current.isProcessing).toBe(true);

      // Pause processing
      act(() => {
        result.current.pauseProcessing();
      });

      expect(result.current.isProcessing).toBe(false);
      expect(result.current.currentStage).toBe('transcription'); // Stage should remain the same
    });

    it('should resume processing correctly', () => {
      const { result } = renderHook(() =>
        useProcessingWorkflow({
          videoFile: mockVideoFile,
          config: mockConfig,
        })
      );

      // Start and pause processing
      act(() => {
        result.current.updateStepProgress('transcription', 50);
        result.current.pauseProcessing();
      });

      expect(result.current.isProcessing).toBe(false);

      // Resume processing
      act(() => {
        result.current.resumeProcessing();
      });

      expect(result.current.isProcessing).toBe(true);
    });

    it('should cancel processing correctly', () => {
      const { result } = renderHook(() =>
        useProcessingWorkflow({
          videoFile: mockVideoFile,
          config: mockConfig,
        })
      );

      // Start processing
      act(() => {
        result.current.updateStepProgress('transcription', 50);
      });

      expect(result.current.isProcessing).toBe(true);

      // Cancel processing
      act(() => {
        result.current.cancelProcessing();
      });

      expect(result.current.isProcessing).toBe(false);
      expect(result.current.currentStage).toBe('idle');
      expect(result.current.steps).toHaveLength(0);
      expect(result.current.overallProgress).toBe(0);
    });
  });

  describe('Time Estimation', () => {
    it('should calculate estimated time remaining', () => {
      const { result } = renderHook(() =>
        useProcessingWorkflow({
          videoFile: mockVideoFile,
          config: mockConfig,
        })
      );

      // Initialize steps
      act(() => {
        result.current.updateStepProgress('transcription', 0);
        result.current.updateStepProgress('filtering', 0);
        result.current.updateStepProgress('translation', 0);
      });

      // Simulate progress over time
      act(() => {
        jest.advanceTimersByTime(10000); // 10 seconds
        result.current.updateStepProgress('transcription', 50);
      });

      // Should estimate remaining time based on current progress rate
      expect(result.current.estimatedTimeRemaining).toBeGreaterThan(0);
    });

    it('should update estimated time as progress changes', () => {
      const { result } = renderHook(() =>
        useProcessingWorkflow({
          videoFile: mockVideoFile,
          config: mockConfig,
        })
      );

      // Initialize steps
      act(() => {
        result.current.updateStepProgress('transcription', 0);
      });

      // First progress update
      act(() => {
        jest.advanceTimersByTime(5000);
        result.current.updateStepProgress('transcription', 25);
      });

      const firstEstimate = result.current.estimatedTimeRemaining;

      // Second progress update (faster progress)
      act(() => {
        jest.advanceTimersByTime(2000);
        result.current.updateStepProgress('transcription', 75);
      });

      const secondEstimate = result.current.estimatedTimeRemaining;

      // Second estimate should be lower due to faster progress
      expect(secondEstimate).toBeLessThan(firstEstimate);
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty video file', async () => {
      const { result } = renderHook(() =>
        useProcessingWorkflow({
          videoFile: '',
          config: mockConfig,
          onError: mockOnError,
        })
      );

      await act(async () => {
        await result.current.startProcessing();
      });

      expect(result.current.currentStage).toBe('error');
      expect(result.current.error).toContain('Video file is required');
      expect(mockOnError).toHaveBeenCalled();
    });

    it('should handle invalid config', async () => {
      const { result } = renderHook(() =>
        useProcessingWorkflow({
          videoFile: mockVideoFile,
          config: {} as any, // Invalid config
          onError: mockOnError,
        })
      );

      await act(async () => {
        await result.current.startProcessing();
      });

      expect(result.current.currentStage).toBe('error');
      expect(mockOnError).toHaveBeenCalled();
    });

    it('should handle progress updates for non-existent steps', () => {
      const { result } = renderHook(() =>
        useProcessingWorkflow({
          videoFile: mockVideoFile,
          config: mockConfig,
        })
      );

      // Should not throw error when updating non-existent step
      expect(() => {
        act(() => {
          result.current.updateStepProgress('non-existent', 50);
        });
      }).not.toThrow();
    });

    it('should handle multiple rapid progress updates', () => {
      const { result } = renderHook(() =>
        useProcessingWorkflow({
          videoFile: mockVideoFile,
          config: mockConfig,
        })
      );

      // Rapid progress updates should not cause issues
      act(() => {
        for (let i = 0; i <= 100; i += 10) {
          result.current.updateStepProgress('transcription', i);
        }
      });

      const step = result.current.steps.find(s => s.id === 'transcription');
      expect(step?.progress).toBe(100);
      expect(step?.status).toBe('completed');
    });
  });

  describe('Memory Management', () => {
    it('should clean up resources on unmount', () => {
      const { unmount } = renderHook(() =>
        useProcessingWorkflow({
          videoFile: mockVideoFile,
          config: mockConfig,
        })
      );

      // Should not throw errors on unmount
      expect(() => {
        unmount();
      }).not.toThrow();
    });

    it('should handle component re-renders without issues', () => {
      const { result, rerender } = renderHook(
        (props) => useProcessingWorkflow(props),
        {
          initialProps: {
            videoFile: mockVideoFile,
            config: mockConfig,
          },
        }
      );

      // Start processing
      act(() => {
        result.current.updateStepProgress('transcription', 50);
      });

      // Re-render with new props
      rerender({
        videoFile: '/new/video.mp4',
        config: { ...mockConfig, language: 'en' },
      });

      // Should maintain state consistency
      expect(result.current.currentStage).toBe('transcription');
    });
  });
});