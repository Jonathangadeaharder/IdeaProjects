import { renderHook, act } from '@testing-library/react-native';
import { useProcessingWorkflow } from '../../src/hooks/useProcessingWorkflow';
import { PythonBridgeService } from '../../src/services/PythonBridgeService';

// Mock the PythonBridgeService
jest.mock('../../src/services/PythonBridgeService');
const mockPythonBridge = PythonBridgeService as jest.Mocked<typeof PythonBridgeService>;

describe('useProcessingWorkflow - Advanced Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  describe('Error Recovery and Resilience', () => {
    it('should recover from temporary network failures', async () => {
      const { result } = renderHook(() => useProcessingWorkflow());
      
      // Mock network failure followed by success
      mockPythonBridge.startProcessing
        .mockRejectedValueOnce(new Error('Network timeout'))
        .mockResolvedValueOnce({ success: true, processId: 'proc-123' });
      
      // First attempt fails
      await act(async () => {
        await result.current.startProcessing('video.mp4', { steps: ['transcription'] });
      });
      
      expect(result.current.error).toBe('Network timeout');
      expect(result.current.isProcessing).toBe(false);
      
      // Reset error and retry
      act(() => {
        result.current.resetError();
      });
      
      // Second attempt succeeds
      await act(async () => {
        await result.current.startProcessing('video.mp4', { steps: ['transcription'] });
      });
      
      expect(result.current.error).toBeNull();
      expect(result.current.isProcessing).toBe(true);
    });

    it('should handle rapid consecutive start/stop operations', async () => {
      const { result } = renderHook(() => useProcessingWorkflow());
      
      mockPythonBridge.startProcessing.mockResolvedValue({ success: true, processId: 'proc-123' });
      mockPythonBridge.stopProcessing.mockResolvedValue({ success: true });
      
      // Rapid start/stop/start sequence
      await act(async () => {
        await result.current.startProcessing('video.mp4', { steps: ['transcription'] });
      });
      
      act(() => {
        result.current.stopProcessing();
      });
      
      await act(async () => {
        await result.current.startProcessing('video2.mp4', { steps: ['translation'] });
      });
      
      expect(result.current.isProcessing).toBe(true);
      expect(result.current.currentStep).toBe('translation');
    });

    it('should handle processing interruption during step transition', async () => {
      const { result } = renderHook(() => useProcessingWorkflow());
      
      mockPythonBridge.startProcessing.mockResolvedValue({ success: true, processId: 'proc-123' });
      
      await act(async () => {
        await result.current.startProcessing('video.mp4', { steps: ['transcription', 'filtering'] });
      });
      
      // Simulate step completion
      act(() => {
        result.current.updateProgress({
          currentStep: 'transcription',
          stepProgress: 100,
          overallProgress: 50,
          isStepComplete: true
        });
      });
      
      // Interrupt during transition
      act(() => {
        result.current.stopProcessing();
      });
      
      expect(result.current.isProcessing).toBe(false);
      expect(result.current.currentStep).toBe('transcription');
      expect(result.current.stepProgress).toBe(100);
    });
  });

  describe('Memory and Performance', () => {
    it('should handle large progress update batches efficiently', async () => {
      const { result } = renderHook(() => useProcessingWorkflow());
      
      mockPythonBridge.startProcessing.mockResolvedValue({ success: true, processId: 'proc-123' });
      
      await act(async () => {
        await result.current.startProcessing('video.mp4', { steps: ['transcription'] });
      });
      
      // Simulate rapid progress updates
      for (let i = 0; i <= 100; i += 10) {
        act(() => {
          result.current.updateProgress({
            currentStep: 'transcription',
            stepProgress: i,
            overallProgress: i,
            isStepComplete: false
          });
        });
      }
      
      expect(result.current.stepProgress).toBe(100);
      expect(result.current.overallProgress).toBe(100);
    });

    it('should cleanup resources when component unmounts during processing', async () => {
      const { result, unmount } = renderHook(() => useProcessingWorkflow());
      
      mockPythonBridge.startProcessing.mockResolvedValue({ success: true, processId: 'proc-123' });
      mockPythonBridge.stopProcessing.mockResolvedValue({ success: true });
      
      await act(async () => {
        await result.current.startProcessing('video.mp4', { steps: ['transcription'] });
      });
      
      expect(result.current.isProcessing).toBe(true);
      
      // Unmount component during processing
      unmount();
      
      // Should have called stop processing
      expect(mockPythonBridge.stopProcessing).toHaveBeenCalled();
    });

    it('should handle memory pressure during long processing sessions', async () => {
      const { result } = renderHook(() => useProcessingWorkflow());
      
      mockPythonBridge.startProcessing.mockResolvedValue({ success: true, processId: 'proc-123' });
      
      // Start long processing session
      await act(async () => {
        await result.current.startProcessing('large_video.mp4', { 
          steps: ['transcription', 'filtering', 'translation', 'analysis'] 
        });
      });
      
      // Simulate memory pressure error
      act(() => {
        result.current.updateProgress({
          currentStep: 'transcription',
          stepProgress: 50,
          overallProgress: 12.5,
          error: 'Insufficient memory available',
          isStepComplete: false
        });
      });
      
      expect(result.current.error).toBe('Insufficient memory available');
      expect(result.current.isProcessing).toBe(false);
    });
  });

  describe('Edge Cases and Boundary Conditions', () => {
    it('should handle zero-duration video files', async () => {
      const { result } = renderHook(() => useProcessingWorkflow());
      
      mockPythonBridge.startProcessing.mockRejectedValue(
        new Error('Video file has zero duration')
      );
      
      await act(async () => {
        await result.current.startProcessing('empty_video.mp4', { steps: ['transcription'] });
      });
      
      expect(result.current.error).toBe('Video file has zero duration');
      expect(result.current.isProcessing).toBe(false);
    });

    it('should handle extremely large video files', async () => {
      const { result } = renderHook(() => useProcessingWorkflow());
      
      mockPythonBridge.startProcessing.mockResolvedValue({ success: true, processId: 'proc-123' });
      
      await act(async () => {
        await result.current.startProcessing('huge_video.mp4', { 
          steps: ['transcription'],
          estimatedDuration: 7200 // 2 hours
        });
      });
      
      expect(result.current.isProcessing).toBe(true);
      expect(result.current.estimatedTimeRemaining).toBe(7200);
    });

    it('should handle processing steps with zero progress', async () => {
      const { result } = renderHook(() => useProcessingWorkflow());
      
      mockPythonBridge.startProcessing.mockResolvedValue({ success: true, processId: 'proc-123' });
      
      await act(async () => {
        await result.current.startProcessing('video.mp4', { steps: ['transcription'] });
      });
      
      // Update with zero progress multiple times
      for (let i = 0; i < 5; i++) {
        act(() => {
          result.current.updateProgress({
            currentStep: 'transcription',
            stepProgress: 0,
            overallProgress: 0,
            isStepComplete: false
          });
        });
      }
      
      expect(result.current.stepProgress).toBe(0);
      expect(result.current.overallProgress).toBe(0);
    });

    it('should handle progress updates with invalid values', async () => {
      const { result } = renderHook(() => useProcessingWorkflow());
      
      mockPythonBridge.startProcessing.mockResolvedValue({ success: true, processId: 'proc-123' });
      
      await act(async () => {
        await result.current.startProcessing('video.mp4', { steps: ['transcription'] });
      });
      
      // Update with invalid progress values
      act(() => {
        result.current.updateProgress({
          currentStep: 'transcription',
          stepProgress: -10, // Negative progress
          overallProgress: 150, // Over 100%
          isStepComplete: false
        });
      });
      
      // Should clamp values to valid range
      expect(result.current.stepProgress).toBeGreaterThanOrEqual(0);
      expect(result.current.stepProgress).toBeLessThanOrEqual(100);
      expect(result.current.overallProgress).toBeGreaterThanOrEqual(0);
      expect(result.current.overallProgress).toBeLessThanOrEqual(100);
    });

    it('should handle processing with unknown step names', async () => {
      const { result } = renderHook(() => useProcessingWorkflow());
      
      mockPythonBridge.startProcessing.mockResolvedValue({ success: true, processId: 'proc-123' });
      
      await act(async () => {
        await result.current.startProcessing('video.mp4', { steps: ['unknown_step'] });
      });
      
      act(() => {
        result.current.updateProgress({
          currentStep: 'unknown_step',
          stepProgress: 50,
          overallProgress: 50,
          isStepComplete: false
        });
      });
      
      expect(result.current.currentStep).toBe('unknown_step');
      expect(result.current.stepProgress).toBe(50);
    });
  });

  describe('Concurrent Operations', () => {
    it('should handle multiple simultaneous processing requests', async () => {
      const { result } = renderHook(() => useProcessingWorkflow());
      
      mockPythonBridge.startProcessing
        .mockResolvedValueOnce({ success: true, processId: 'proc-1' })
        .mockResolvedValueOnce({ success: true, processId: 'proc-2' });
      
      // Start two processing operations simultaneously
      const promise1 = act(async () => {
        await result.current.startProcessing('video1.mp4', { steps: ['transcription'] });
      });
      
      const promise2 = act(async () => {
        await result.current.startProcessing('video2.mp4', { steps: ['filtering'] });
      });
      
      await Promise.all([promise1, promise2]);
      
      // Should only have one active processing session (latest)
      expect(result.current.isProcessing).toBe(true);
      expect(result.current.currentStep).toBe('filtering');
    });

    it('should handle pause/resume during step transitions', async () => {
      const { result } = renderHook(() => useProcessingWorkflow());
      
      mockPythonBridge.startProcessing.mockResolvedValue({ success: true, processId: 'proc-123' });
      mockPythonBridge.pauseProcessing.mockResolvedValue({ success: true });
      mockPythonBridge.resumeProcessing.mockResolvedValue({ success: true });
      
      await act(async () => {
        await result.current.startProcessing('video.mp4', { steps: ['transcription', 'filtering'] });
      });
      
      // Complete first step
      act(() => {
        result.current.updateProgress({
          currentStep: 'transcription',
          stepProgress: 100,
          overallProgress: 50,
          isStepComplete: true
        });
      });
      
      // Pause during transition
      act(() => {
        result.current.pauseProcessing();
      });
      
      expect(result.current.isPaused).toBe(true);
      
      // Resume and continue to next step
      act(() => {
        result.current.resumeProcessing();
      });
      
      act(() => {
        result.current.updateProgress({
          currentStep: 'filtering',
          stepProgress: 25,
          overallProgress: 62.5,
          isStepComplete: false
        });
      });
      
      expect(result.current.isPaused).toBe(false);
      expect(result.current.currentStep).toBe('filtering');
    });
  });

  describe('Time Estimation Edge Cases', () => {
    it('should handle time estimation with varying step durations', async () => {
      const { result } = renderHook(() => useProcessingWorkflow());
      
      mockPythonBridge.startProcessing.mockResolvedValue({ success: true, processId: 'proc-123' });
      
      await act(async () => {
        await result.current.startProcessing('video.mp4', { 
          steps: ['transcription', 'filtering', 'translation'] 
        });
      });
      
      // Simulate first step taking much longer than expected
      act(() => {
        result.current.updateProgress({
          currentStep: 'transcription',
          stepProgress: 10,
          overallProgress: 3.33,
          isStepComplete: false
        });
      });
      
      // Fast forward time to simulate slow progress
      act(() => {
        jest.advanceTimersByTime(60000); // 1 minute
      });
      
      act(() => {
        result.current.updateProgress({
          currentStep: 'transcription',
          stepProgress: 20,
          overallProgress: 6.66,
          isStepComplete: false
        });
      });
      
      // Time estimation should adjust based on actual progress
      expect(result.current.estimatedTimeRemaining).toBeGreaterThan(0);
    });

    it('should handle time estimation when processing stalls', async () => {
      const { result } = renderHook(() => useProcessingWorkflow());
      
      mockPythonBridge.startProcessing.mockResolvedValue({ success: true, processId: 'proc-123' });
      
      await act(async () => {
        await result.current.startProcessing('video.mp4', { steps: ['transcription'] });
      });
      
      // Initial progress
      act(() => {
        result.current.updateProgress({
          currentStep: 'transcription',
          stepProgress: 50,
          overallProgress: 50,
          isStepComplete: false
        });
      });
      
      // Simulate stalled processing (no progress for extended time)
      act(() => {
        jest.advanceTimersByTime(300000); // 5 minutes
      });
      
      // Same progress after long time
      act(() => {
        result.current.updateProgress({
          currentStep: 'transcription',
          stepProgress: 50,
          overallProgress: 50,
          isStepComplete: false
        });
      });
      
      // Should handle stalled estimation gracefully
      expect(result.current.estimatedTimeRemaining).toBeDefined();
    });
  });

  describe('Configuration Edge Cases', () => {
    it('should handle processing with minimal configuration', async () => {
      const { result } = renderHook(() => useProcessingWorkflow());
      
      mockPythonBridge.startProcessing.mockResolvedValue({ success: true, processId: 'proc-123' });
      
      await act(async () => {
        await result.current.startProcessing('video.mp4', {});
      });
      
      expect(result.current.isProcessing).toBe(true);
    });

    it('should handle processing with maximum configuration', async () => {
      const { result } = renderHook(() => useProcessingWorkflow());
      
      mockPythonBridge.startProcessing.mockResolvedValue({ success: true, processId: 'proc-123' });
      
      const maxConfig = {
        steps: ['transcription', 'filtering', 'translation', 'analysis'],
        language: 'de',
        targetLanguage: 'en',
        quality: 'high',
        enableGPU: true,
        batchSize: 32,
        modelSize: 'large',
        customSettings: {
          transcriptionModel: 'whisper-large',
          translationModel: 'opus-mt',
          filteringThreshold: 0.8
        }
      };
      
      await act(async () => {
        await result.current.startProcessing('video.mp4', maxConfig);
      });
      
      expect(result.current.isProcessing).toBe(true);
      expect(mockPythonBridge.startProcessing).toHaveBeenCalledWith('video.mp4', maxConfig);
    });

    it('should handle processing with invalid configuration values', async () => {
      const { result } = renderHook(() => useProcessingWorkflow());
      
      mockPythonBridge.startProcessing.mockRejectedValue(
        new Error('Invalid configuration: batchSize must be positive')
      );
      
      const invalidConfig = {
        steps: ['transcription'],
        batchSize: -1,
        quality: 'invalid_quality'
      };
      
      await act(async () => {
        await result.current.startProcessing('video.mp4', invalidConfig);
      });
      
      expect(result.current.error).toBe('Invalid configuration: batchSize must be positive');
      expect(result.current.isProcessing).toBe(false);
    });
  });
});