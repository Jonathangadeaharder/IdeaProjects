import { PythonBridgeService } from './PythonBridgeService';
import type { 
  ProcessingResult, 
  A1DeciderResult, 
  TranslationResult, 
  VocabularyAnalysisResult,
  HealthStatus,
  PipelineConfiguration
} from './PythonBridgeService';

// Mock fetch for testing
global.fetch = jest.fn();

describe('PythonBridgeService Data Mapping Layer', () => {
  let service: PythonBridgeService;
  const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

  beforeEach(() => {
    service = new PythonBridgeService();
    mockFetch.mockClear();
  });

  describe('Domain Model Mapping', () => {
    it('should map subtitle creation response to ProcessingResult domain model', async () => {
      // Mock successful API response
      const mockApiResponse = {
        success: true,
        message: 'Processing completed',
        results: {
          output_path: '/path/to/output.srt',
          duration: 120,
          total_segments: 50
        }
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockApiResponse,
      } as Response);

      const result = await service.requestSubtitleCreation('test-video.mp4', 'en');

      // Verify it returns a domain model, not raw API response
      expect(result).toEqual({
        success: true,
        message: 'Processing completed',
        outputFile: '/path/to/output.srt',
        duration: undefined, // Current mapping doesn't extract duration
        totalSegments: undefined // Current mapping doesn't extract segments
      });

      // Verify it's a ProcessingResult type
      expect(typeof result.success).toBe('boolean');
      expect(typeof result.message).toBe('string');
    });

    it('should map A1 processing response to A1DeciderResult domain model', async () => {
      const mockApiResponse = {
        success: true,
        message: 'A1 processing completed',
        results: {
          filtered_subtitle_file: '/path/to/filtered.srt',
          vocabulary: [
            {
              word: 'Hallo',
              translation: 'Hello',
              frequency: 5,
              is_relevant: true,
              affected_subtitles: 3
            }
          ],
          total_unknown_words: 25,
          total_subtitles: 100,
          skipped_subtitles: 10
        }
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockApiResponse,
      } as Response);

      const result = await service.requestA1Processing('test-subtitle.srt', false);

      // Verify it returns a domain model with proper structure
      expect(result).toEqual({
        success: true,
        message: 'A1 processing completed',
        filteredSubtitleFile: '/path/to/filtered.srt',
        vocabularyWords: [
          {
            id: 'word_0',
            german: 'Hallo',
            english: 'Hello',
            difficulty: 'A1',
            frequency: 5,
            context: 'Found in 3 subtitles'
          }
        ],
        statistics: {
          totalWords: 25,
          knownCount: 90, // total_subtitles - skipped_subtitles
          unknownCount: 25,
          difficultyLevel: 'beginner'
        }
      });

      // Verify vocabulary words are properly mapped to VocabularyWord interface
      expect(result.vocabularyWords[0]).toHaveProperty('id');
      expect(result.vocabularyWords[0]).toHaveProperty('german');
      expect(result.vocabularyWords[0]).toHaveProperty('english');
      expect(result.vocabularyWords[0]).toHaveProperty('difficulty');
    });

    it('should map vocabulary analysis response to VocabularyAnalysisResult domain model', async () => {
      const mockApiResponse = {
        success: true,
        message: 'Vocabulary analysis completed',
        results: [
          {
            word: 'Guten Tag',
            translation: 'Good day',
            frequency: 8,
            is_relevant: true,
            affected_subtitles: 5
          },
          {
            word: 'schwierig',
            translation: 'difficult',
            frequency: 2,
            is_relevant: false,
            affected_subtitles: 1
          }
        ]
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockApiResponse,
      } as Response);

      const result = await service.requestVocabularyAnalysis('test-video.mp4');

      // Verify it returns a domain model with statistics
      expect(result.success).toBe(true);
      expect(result.vocabularyWords).toHaveLength(2);
      expect(result.statistics.totalWords).toBe(2);
      expect(result.statistics.averageFrequency).toBe(5); // (8 + 2) / 2
      expect(result.statistics.difficultyDistribution).toEqual({
        'A1': 1,
        'A2': 1
      });
    });

    it('should handle API errors gracefully and return domain models with error info', async () => {
      const mockErrorResponse = {
        success: false,
        error: 'Processing failed',
        message: 'Video file not found'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockErrorResponse,
      } as Response);

      const result = await service.requestSubtitleCreation('invalid-video.mp4', 'en');

      // Verify error is properly mapped to domain model
      expect(result).toEqual({
        success: false,
        message: 'Processing failed',
        error: 'Processing failed'
      });
    });

    it('should map health check response to HealthStatus domain model', async () => {
      const mockHealthResponse = {
        status: 'healthy',
        version: '1.0.0',
        dependencies: {
          'whisper': true,
          'torch': true
        }
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockHealthResponse,
      } as Response);

      const result = await service.getDetailedHealthStatus();

      expect(result).toEqual({
        isHealthy: true,
        version: '1.0.0',
        dependencies: {
          'whisper': true,
          'torch': true
        },
        message: 'healthy'
      });
    });
  });

  describe('Backward Compatibility', () => {
    it('should maintain boolean return for checkBackendHealth method', async () => {
      const mockHealthResponse = {
        status: 'healthy',
        version: '1.0.0'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockHealthResponse,
      } as Response);

      const result = await service.checkBackendHealth();

      // Verify it still returns a boolean for backward compatibility
      expect(typeof result).toBe('boolean');
      expect(result).toBe(true);
    });
  });
});