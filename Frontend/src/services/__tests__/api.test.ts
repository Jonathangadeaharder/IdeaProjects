import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import axios from 'axios';
import { 
  getVideos, 
  getVideoDetails, 
  uploadVideo, 
  processVideo, 
  getProcessingStatus,
  login,
  register,
  getProfile
} from '../api';

// Mock axios
vi.mock('axios');
const mockAxios = vi.mocked(axios);

// Mock axios.create to return the mocked axios instance
mockAxios.create = vi.fn(() => mockAxios);

describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Setup default axios mock responses
    mockAxios.get = vi.fn();
    mockAxios.post = vi.fn();
    mockAxios.put = vi.fn();
    mockAxios.delete = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Video API', () => {
    it('fetches videos successfully', async () => {
      const mockVideos = [
        { id: '1', title: 'Test Video 1', description: 'Description 1' },
        { id: '2', title: 'Test Video 2', description: 'Description 2' }
      ];
      
      mockAxios.get.mockResolvedValue({ data: mockVideos });
      
      const result = await getVideos();
      
      expect(mockAxios.get).toHaveBeenCalledWith('/videos');
      expect(result).toEqual(mockVideos);
    });

    it('fetches video details successfully', async () => {
      const mockVideoDetails = {
        id: '1',
        title: 'Test Video',
        description: 'Test Description',
        episodes: [
          { id: '1', title: 'Episode 1', duration: 1800 }
        ]
      };
      
      mockAxios.get.mockResolvedValue({ data: mockVideoDetails });
      
      const result = await getVideoDetails('1');
      
      expect(mockAxios.get).toHaveBeenCalledWith('/videos/1');
      expect(result).toEqual(mockVideoDetails);
    });

    it('handles video upload', async () => {
      const mockFile = new File(['test'], 'test.mp4', { type: 'video/mp4' });
      const mockResponse = { taskId: 'task-123', status: 'processing' };
      
      mockAxios.post.mockResolvedValue({ data: mockResponse });
      
      const result = await uploadVideo(mockFile, 'Test Video');
      
      expect(mockAxios.post).toHaveBeenCalledWith(
        '/videos/upload',
        expect.any(FormData),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'multipart/form-data'
          })
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('processes video successfully', async () => {
      const mockResponse = { taskId: 'task-456', status: 'started' };
      
      mockAxios.post.mockResolvedValue({ data: mockResponse });
      
      const result = await processVideo('video-123');
      
      expect(mockAxios.post).toHaveBeenCalledWith('/videos/video-123/process');
      expect(result).toEqual(mockResponse);
    });

    it('gets processing status', async () => {
      const mockStatus = {
        taskId: 'task-123',
        status: 'completed',
        progress: 100,
        result: { videoId: 'video-123' }
      };
      
      mockAxios.get.mockResolvedValue({ data: mockStatus });
      
      const result = await getProcessingStatus('task-123');
      
      expect(mockAxios.get).toHaveBeenCalledWith('/processing/task-123/status');
      expect(result).toEqual(mockStatus);
    });
  });

  describe('Authentication API', () => {
    it('logs in user successfully', async () => {
      const mockLoginResponse = {
        token: 'jwt-token-123',
        user: { id: '1', email: 'test@example.com', name: 'Test User' }
      };
      
      mockAxios.post.mockResolvedValue({ data: mockLoginResponse });
      
      const result = await login('test@example.com', 'password123');
      
      expect(mockAxios.post).toHaveBeenCalledWith('/auth/login', {
        email: 'test@example.com',
        password: 'password123'
      });
      expect(result).toEqual(mockLoginResponse);
    });

    it('registers user successfully', async () => {
      const mockRegisterResponse = {
        token: 'jwt-token-456',
        user: { id: '2', email: 'new@example.com', name: 'New User' }
      };
      
      mockAxios.post.mockResolvedValue({ data: mockRegisterResponse });
      
      const result = await register('new@example.com', 'password123', 'New User');
      
      expect(mockAxios.post).toHaveBeenCalledWith('/auth/register', {
        email: 'new@example.com',
        password: 'password123',
        name: 'New User'
      });
      expect(result).toEqual(mockRegisterResponse);
    });

    it('gets user profile', async () => {
      const mockProfile = {
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
        learningStats: { wordsLearned: 150, streak: 7 }
      };
      
      mockAxios.get.mockResolvedValue({ data: mockProfile });
      
      const result = await getProfile();
      
      expect(mockAxios.get).toHaveBeenCalledWith('/auth/profile');
      expect(result).toEqual(mockProfile);
    });
  });

  describe('Error Handling', () => {
    it('handles network errors', async () => {
      const networkError = new Error('Network Error');
      mockAxios.get.mockRejectedValue(networkError);
      
      await expect(getVideos()).rejects.toThrow('Network Error');
    });

    it('handles API errors with status codes', async () => {
      const apiError = {
        response: {
          status: 404,
          data: { message: 'Video not found' }
        }
      };
      mockAxios.get.mockRejectedValue(apiError);
      
      await expect(getVideoDetails('nonexistent')).rejects.toEqual(apiError);
    });
  });
});