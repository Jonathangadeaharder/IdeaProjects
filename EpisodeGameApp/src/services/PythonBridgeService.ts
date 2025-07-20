import { VocabularyWord } from '../models/Episode';

// Raw API response interfaces - no business logic transformation
// Updated to match Python FastAPI response structure
export interface RawApiResponse<T = any> {
  success: boolean;
  message?: string;
  results?: T;
  error?: string;
}

// Domain model interfaces (what we return to the UI)
export interface ProcessingResult {
  success: boolean;
  message: string;
  outputFile?: string;
  duration?: number;
  totalSegments?: number;
  error?: string;
}

export interface A1DeciderResult {
  success: boolean;
  message: string;
  filteredSubtitleFile?: string;
  vocabularyWords: VocabularyWord[];
  statistics: {
    totalWords: number;
    knownCount: number;
    unknownCount: number;
    difficultyLevel: 'beginner' | 'intermediate' | 'advanced';
  };
  error?: string;
}

export interface TranslationResult {
  success: boolean;
  message: string;
  translatedFile?: string;
  translationCount: number;
  error?: string;
}

export interface VocabularyAnalysisResult {
  success: boolean;
  message: string;
  vocabularyWords: VocabularyWord[];
  statistics: {
    totalWords: number;
    averageFrequency: number;
    difficultyDistribution: Record<string, number>;
  };
  error?: string;
}

export interface HealthStatus {
  isHealthy: boolean;
  version?: string;
  dependencies?: Record<string, boolean>;
  message?: string;
}

export interface PipelineConfiguration {
  name: string;
  description: string;
  steps: string[];
  isAvailable: boolean;
}

// Python API Health Response
export interface PythonHealthResponse {
  status: string;
  version: string;
  dependencies: Record<string, boolean>;
}

// Python API Processing Response
export interface PythonProcessingResponse {
  success: boolean;
  message: string;
  results?: {
    video_file: string;
    audio_file?: string;
    preview_srt?: string;
    full_srt?: string;
    filtered_srt?: string;
    translated_srt?: string;
    metadata?: any;
  };
  error?: string;
}

export interface RawVocabularyWord {
  word: string;
  frequency: number;
  translation: string;
  is_relevant: boolean;
  affected_subtitles: number;
}

export interface RawA1DeciderResult {
  subtitle_file: string;
  total_subtitles: number;
  skipped_subtitles: number;
  skipped_hard: number;
  total_unknown_words: number;
  relevant_vocabulary_count: number;
  vocabulary: RawVocabularyWord[];
  filtered_subtitle_file?: string;
}

export interface RawTranslationResult {
  success: boolean;
  output_path?: string;
  source_file: string;
  target_language: string;
}

export interface RawSubtitleCreationResult {
  success: boolean;
  output_path?: string;
  video_file: string;
  language: string;
}

/**
 * PythonBridgeService - Responsible ONLY for HTTP communication with the Python API
 * 
 * Single Responsibility: Low-level HTTP requests and raw response handling
 * - Makes HTTP requests directly to Python FastAPI endpoints
 * - Handles network errors and timeouts
 * - Returns raw API responses without transformation
 * - No business logic or data transformation
 * - Eliminates Node.js BFF dependency for simplified architecture
 */
export class PythonBridgeService {
  private static instance: PythonBridgeService;
  private readonly pythonApiUrl = 'http://localhost:8000';
  private readonly healthUrl = 'http://localhost:8000/health';
  private readonly defaultTimeout = 30000; // 30 seconds

  static getInstance(): PythonBridgeService {
    if (!PythonBridgeService.instance) {
      PythonBridgeService.instance = new PythonBridgeService();
    }
    return PythonBridgeService.instance;
  }

  // Data mapping functions - transform raw API responses to domain models
  private mapToProcessingResult(rawResponse: RawApiResponse<RawSubtitleCreationResult>): ProcessingResult {
    if (!rawResponse.success || !rawResponse.results) {
      return {
        success: false,
        message: rawResponse.error || rawResponse.message || 'Processing failed',
        error: rawResponse.error
      };
    }

    const data = rawResponse.results;
    return {
      success: true,
      message: rawResponse.message || 'Processing completed successfully',
      outputFile: data.output_path,
      duration: undefined,
      totalSegments: undefined
    };
  }

  private mapToA1DeciderResult(rawResponse: RawApiResponse<RawA1DeciderResult>): A1DeciderResult {
    if (!rawResponse.success || !rawResponse.results) {
      return {
        success: false,
        message: rawResponse.error || rawResponse.message || 'A1 processing failed',
        vocabularyWords: [],
        statistics: {
          totalWords: 0,
          knownCount: 0,
          unknownCount: 0,
          difficultyLevel: 'beginner'
        },
        error: rawResponse.error
      };
    }

    const data = rawResponse.results;
    const vocabularyWords = data.vocabulary?.map((word, index) => ({
      id: `word_${index}`,
      german: word.word,
      english: word.translation,
      difficulty: word.is_relevant ? 'A1' : 'A2' as 'A1' | 'A2',
      frequency: word.frequency,
      context: `Found in ${word.affected_subtitles} subtitle${word.affected_subtitles !== 1 ? 's' : ''}`
    })) || [];

    return {
      success: true,
      message: rawResponse.message || 'A1 processing completed successfully',
      filteredSubtitleFile: data.filtered_subtitle_file,
      vocabularyWords,
      statistics: {
        totalWords: data.total_unknown_words || 0,
        knownCount: (data.total_subtitles || 0) - (data.skipped_subtitles || 0),
        unknownCount: data.total_unknown_words || 0,
        difficultyLevel: this.mapDifficultyLevel(undefined)
      }
    };
  }

  private mapToTranslationResult(rawResponse: RawApiResponse<RawTranslationResult>): TranslationResult {
    if (!rawResponse.success || !rawResponse.results) {
      return {
        success: false,
        message: rawResponse.error || rawResponse.message || 'Translation failed',
        translationCount: 0,
        error: rawResponse.error
      };
    }

    const data = rawResponse.results;
    return {
      success: true,
      message: rawResponse.message || 'Translation completed successfully',
      translatedFile: data.output_path,
      translationCount: 0
    };
  }

  private mapToVocabularyAnalysisResult(rawResponse: RawApiResponse<RawVocabularyWord[]>): VocabularyAnalysisResult {
    if (!rawResponse.success || !rawResponse.results) {
      return {
        success: false,
        message: rawResponse.error || rawResponse.message || 'Vocabulary analysis failed',
        vocabularyWords: [],
        statistics: {
          totalWords: 0,
          averageFrequency: 0,
          difficultyDistribution: {}
        },
        error: rawResponse.error
      };
    }

    const vocabularyWords = rawResponse.results.map((word, index) => ({
      id: `vocab_${index}`,
      german: word.word,
      english: word.translation,
      difficulty: word.is_relevant ? 'A1' : 'A2' as 'A1' | 'A2',
      frequency: word.frequency,
      context: `Found in ${word.affected_subtitles} subtitle${word.affected_subtitles !== 1 ? 's' : ''}`
    }));

    const totalFrequency = vocabularyWords.reduce((sum, word) => sum + word.frequency, 0);
    const difficultyDistribution = vocabularyWords.reduce((dist, word) => {
      dist[word.difficulty] = (dist[word.difficulty] || 0) + 1;
      return dist;
    }, {} as Record<string, number>);

    return {
      success: true,
      message: rawResponse.message || 'Vocabulary analysis completed successfully',
      vocabularyWords,
      statistics: {
        totalWords: vocabularyWords.length,
        averageFrequency: vocabularyWords.length > 0 ? totalFrequency / vocabularyWords.length : 0,
        difficultyDistribution
      }
    };
  }

  private mapToHealthStatus(rawResponse: PythonHealthResponse): HealthStatus {
    return {
      isHealthy: rawResponse.status === 'healthy',
      version: rawResponse.version,
      dependencies: rawResponse.dependencies,
      message: rawResponse.status
    };
  }

  private mapToPipelineConfigurations(rawResponse: RawApiResponse<any[]>): PipelineConfiguration[] {
    if (!rawResponse.success || !rawResponse.results) {
      return [];
    }

    return rawResponse.results.map(pipeline => ({
      name: pipeline.name || 'Unknown Pipeline',
      description: pipeline.description || 'No description available',
      steps: pipeline.steps || [],
      isAvailable: pipeline.available !== false
    }));
  }

  private mapDifficultyLevel(level?: string): 'beginner' | 'intermediate' | 'advanced' {
    switch (level?.toLowerCase()) {
      case 'a1':
      case 'a2':
      case 'beginner':
        return 'beginner';
      case 'b1':
      case 'b2':
      case 'intermediate':
        return 'intermediate';
      case 'c1':
      case 'c2':
      case 'advanced':
        return 'advanced';
      default:
        return 'beginner';
    }
  }

  /**
   * Make HTTP request to create subtitles endpoint
   * Returns domain model instead of raw API response
   */
  async requestSubtitleCreation(videoPath: string, language: string = 'de'): Promise<ProcessingResult> {
    const rawResponse = await this.makeRequest('/api/process', {
      method: 'POST',
      body: JSON.stringify({
        video_file_path: videoPath,
        language: language,
        pipeline_config: 'full'
      })
    });
    return this.mapToProcessingResult(rawResponse);
  }

  /**
   * Make HTTP request to process subtitles with A1 Decider
   * Returns domain model instead of raw API response
   */
  async requestA1Processing(subtitlePath: string, vocabularyOnly: boolean = false): Promise<A1DeciderResult> {
    // For existing subtitle files, we need to use a different approach
    // The Python API processes video files, not subtitle files directly
    // This method may need to be redesigned or the Python API extended
    const pipelineConfig = vocabularyOnly ? 'learning' : 'full';
    const rawResponse = await this.makeRequest('/api/process', {
      method: 'POST',
      body: JSON.stringify({
        video_file_path: subtitlePath, // This may need adjustment
        pipeline_config: pipelineConfig
      })
    });
    return this.mapToA1DeciderResult(rawResponse);
  }

  /**
   * Make HTTP request to translate subtitles endpoint
   * Translation is now handled as part of the unified pipeline
   * Returns domain model instead of raw API response
   */
  async requestSubtitleTranslation(
    videoPath: string,
    sourceLang: string = 'de',
    targetLang: string = 'es'
  ): Promise<TranslationResult> {
    const rawResponse = await this.makeRequest('/api/process', {
      method: 'POST',
      body: JSON.stringify({
        video_file_path: videoPath,
        src_lang: sourceLang,
        tgt_lang: targetLang,
        pipeline_config: 'batch'
      })
    });
    return this.mapToTranslationResult(rawResponse);
  }

  /**
   * Make HTTP request to check backend dependencies
   * Returns domain model instead of raw API response
   */
  async requestDependencyCheck(): Promise<HealthStatus> {
    const rawResponse = await this.makeRequest('/health', {
      method: 'GET'
    });
    return this.mapToHealthStatus(rawResponse);
  }

  /**
   * Make HTTP request to get vocabulary analysis
   * Returns domain model instead of raw API response
   */
  async requestVocabularyAnalysis(videoPath: string): Promise<VocabularyAnalysisResult> {
    const rawResponse = await this.makeRequest('/api/process', {
      method: 'POST',
      body: JSON.stringify({
        video_file_path: videoPath,
        pipeline_config: 'learning'
      })
    });
    return this.mapToVocabularyAnalysisResult(rawResponse);
  }

  /**
   * Get available pipeline configurations
   * Returns domain model instead of raw API response
   */
  async requestPipelineConfigurations(): Promise<PipelineConfiguration[]> {
    const rawResponse = await this.makeRequest('/api/pipelines', {
      method: 'GET'
    });
    return this.mapToPipelineConfigurations(rawResponse);
  }

  /**
   * Check Python API server health
   * Returns boolean indicating if Python API is reachable
   */
  async checkBackendHealth(): Promise<boolean> {
    try {
      const healthStatus = await this.requestDependencyCheck();
      return healthStatus.isHealthy;
    } catch (error) {
      console.error('Python API health check failed:', error);
      return false;
    }
  }

  /**
   * Get detailed health status information
   * Returns full health status domain model
   */
  async getDetailedHealthStatus(): Promise<HealthStatus> {
    try {
      return await this.requestDependencyCheck();
    } catch (error) {
      console.error('Detailed health check failed:', error);
      return {
        isHealthy: false,
        message: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Core HTTP request method - handles all API communication
   * Returns raw response without business logic transformation
   */
  private async makeRequest<T = any>(
    endpoint: string,
    options: {
      method: 'GET' | 'POST' | 'PUT' | 'DELETE';
      body?: string;
      headers?: Record<string, string>;
      timeout?: number;
    }
  ): Promise<RawApiResponse<T>> {
    const { method, body, headers = {}, timeout = this.defaultTimeout } = options;
    
    try {
      const response = await fetch(`${this.pythonApiUrl}${endpoint}`, {
        method,
        headers: {
          'Content-Type': 'application/json',
          ...headers
        },
        body,
        signal: AbortSignal.timeout(timeout)
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ 
          success: false,
          message: 'Unknown error',
          error: 'Unknown error' 
        }));
        return {
          success: false,
          message: errorData.message || `HTTP ${response.status}: ${response.statusText}`,
          error: errorData.error || errorData.detail || `HTTP ${response.status}: ${response.statusText}`
        };
      }
      
      const data = await response.json();
      return data; // Return the Python API response directly
      
    } catch (error) {
      return {
        success: false,
        message: 'Network request failed',
        error: error instanceof Error ? error.message : 'Network request failed'
      };
    }
  }
}

// Export both the class and singleton instance
export { PythonBridgeService };
export default PythonBridgeService.getInstance();