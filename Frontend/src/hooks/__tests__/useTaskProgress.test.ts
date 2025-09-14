import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useTaskProgress } from '../useTaskProgress';
import * as api from '@/services/api';

// Mock the API service
vi.mock('@/services/api');
const mockApi = vi.mocked(api);

// Mock timers
vi.useFakeTimers();

describe('useTaskProgress Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.clearAllTimers();
  });

  afterEach(() => {
    vi.runOnlyPendingTimers();
    vi.useRealTimers();
  });

  describe('Initial State', () => {
    it('has correct initial state', () => {
      const { result } = renderHook(() => useTaskProgress());
      
      expect(result.current.progress).toBe(0);
      expect(result.current.status).toBe('idle');
      expect(result.current.error).toBeNull();
      expect(result.current.isComplete).toBe(false);
      expect(result.current.taskId).toBeNull();
    });
  });

  describe('Starting Task Monitoring', () => {
    it('starts monitoring a task successfully', async () => {
      const mockStatus = {
        taskId: 'task-123',
        status: 'processing',
        progress: 25,
        message: 'Processing video...'
      };
      
      mockApi.getProcessingStatus = vi.fn().mockResolvedValue(mockStatus);
      
      const { result } = renderHook(() => useTaskProgress());
      
      act(() => {
        result.current.startMonitoring('task-123');
      });
      
      expect(result.current.taskId).toBe('task-123');
      expect(result.current.status).toBe('monitoring');
      
      // Fast-forward timer to trigger first poll
      await act(async () => {
        vi.advanceTimersByTime(2000);
      });
      
      expect(mockApi.getProcessingStatus).toHaveBeenCalledWith('task-123');
      expect(result.current.progress).toBe(25);
      expect(result.current.status).toBe('processing');
    });

    it('handles task completion', async () => {
      const mockCompletedStatus = {
        taskId: 'task-123',
        status: 'completed',
        progress: 100,
        result: { videoId: 'video-456' }
      };
      
      mockApi.getProcessingStatus = vi.fn().mockResolvedValue(mockCompletedStatus);
      
      const { result } = renderHook(() => useTaskProgress());
      
      act(() => {
        result.current.startMonitoring('task-123');
      });
      
      await act(async () => {
        vi.advanceTimersByTime(2000);
      });
      
      expect(result.current.progress).toBe(100);
      expect(result.current.status).toBe('completed');
      expect(result.current.isComplete).toBe(true);
      expect(result.current.result).toEqual({ videoId: 'video-456' });
    });

    it('handles task failure', async () => {
      const mockFailedStatus = {
        taskId: 'task-123',
        status: 'failed',
        progress: 50,
        error: 'Processing failed: Invalid video format'
      };
      
      mockApi.getProcessingStatus = vi.fn().mockResolvedValue(mockFailedStatus);
      
      const { result } = renderHook(() => useTaskProgress());
      
      act(() => {
        result.current.startMonitoring('task-123');
      });
      
      await act(async () => {
        vi.advanceTimersByTime(2000);
      });
      
      expect(result.current.status).toBe('failed');
      expect(result.current.error).toBe('Processing failed: Invalid video format');
      expect(result.current.isComplete).toBe(false);
    });

    it('handles API errors during monitoring', async () => {
      const apiError = new Error('Network error');
      mockApi.getProcessingStatus = vi.fn().mockRejectedValue(apiError);
      
      const { result } = renderHook(() => useTaskProgress());
      
      act(() => {
        result.current.startMonitoring('task-123');
      });
      
      await act(async () => {
        vi.advanceTimersByTime(2000);
      });
      
      expect(result.current.status).toBe('error');
      expect(result.current.error).toBe('Network error');
    });
  });

  describe('Polling Behavior', () => {
    it('polls at regular intervals', async () => {
      const mockStatus = {
        taskId: 'task-123',
        status: 'processing',
        progress: 25
      };
      
      mockApi.getProcessingStatus = vi.fn().mockResolvedValue(mockStatus);
      
      const { result } = renderHook(() => useTaskProgress());
      
      act(() => {
        result.current.startMonitoring('task-123');
      });
      
      // First poll
      await act(async () => {
        vi.advanceTimersByTime(2000);
      });
      
      expect(mockApi.getProcessingStatus).toHaveBeenCalledTimes(1);
      
      // Second poll
      await act(async () => {
        vi.advanceTimersByTime(2000);
      });
      
      expect(mockApi.getProcessingStatus).toHaveBeenCalledTimes(2);
      
      // Third poll
      await act(async () => {
        vi.advanceTimersByTime(2000);
      });
      
      expect(mockApi.getProcessingStatus).toHaveBeenCalledTimes(3);
    });

    it('stops polling when task completes', async () => {
      let callCount = 0;
      mockApi.getProcessingStatus = vi.fn().mockImplementation(() => {
        callCount++;
        if (callCount === 1) {
          return Promise.resolve({
            taskId: 'task-123',
            status: 'processing',
            progress: 50
          });
        } else {
          return Promise.resolve({
            taskId: 'task-123',
            status: 'completed',
            progress: 100
          });
        }
      });
      
      const { result } = renderHook(() => useTaskProgress());
      
      act(() => {
        result.current.startMonitoring('task-123');
      });
      
      // First poll - processing
      await act(async () => {
        vi.advanceTimersByTime(2000);
      });
      
      expect(result.current.status).toBe('processing');
      
      // Second poll - completed
      await act(async () => {
        vi.advanceTimersByTime(2000);
      });
      
      expect(result.current.status).toBe('completed');
      
      // Third poll should not happen
      await act(async () => {
        vi.advanceTimersByTime(2000);
      });
      
      expect(mockApi.getProcessingStatus).toHaveBeenCalledTimes(2);
    });
  });

  describe('Stop Monitoring', () => {
    it('stops monitoring when requested', async () => {
      const mockStatus = {
        taskId: 'task-123',
        status: 'processing',
        progress: 25
      };
      
      mockApi.getProcessingStatus = vi.fn().mockResolvedValue(mockStatus);
      
      const { result } = renderHook(() => useTaskProgress());
      
      act(() => {
        result.current.startMonitoring('task-123');
      });
      
      // First poll
      await act(async () => {
        vi.advanceTimersByTime(2000);
      });
      
      expect(mockApi.getProcessingStatus).toHaveBeenCalledTimes(1);
      
      // Stop monitoring
      act(() => {
        result.current.stopMonitoring();
      });
      
      // Next poll should not happen
      await act(async () => {
        vi.advanceTimersByTime(2000);
      });
      
      expect(mockApi.getProcessingStatus).toHaveBeenCalledTimes(1);
      expect(result.current.status).toBe('idle');
    });
  });

  describe('Reset', () => {
    it('resets to initial state', () => {
      const { result } = renderHook(() => useTaskProgress());
      
      // Set some state
      act(() => {
        result.current.startMonitoring('task-123');
      });
      
      expect(result.current.taskId).toBe('task-123');
      
      // Reset
      act(() => {
        result.current.reset();
      });
      
      expect(result.current.progress).toBe(0);
      expect(result.current.status).toBe('idle');
      expect(result.current.error).toBeNull();
      expect(result.current.isComplete).toBe(false);
      expect(result.current.taskId).toBeNull();
    });
  });

  describe('Cleanup', () => {
    it('cleans up timers on unmount', () => {
      const { result, unmount } = renderHook(() => useTaskProgress());
      
      act(() => {
        result.current.startMonitoring('task-123');
      });
      
      const clearIntervalSpy = vi.spyOn(global, 'clearInterval');
      
      unmount();
      
      expect(clearIntervalSpy).toHaveBeenCalled();
    });
  });
});