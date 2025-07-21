import React from 'react';
import { render, fireEvent, waitFor, act } from '../setup/test-utils';
import A1DeciderGameScreen from '../../src/screens/A1DeciderGameScreen';
import { useAppStore } from '../../src/stores/useAppStore';
import { SubtitleService } from '../../src/services/SubtitleService';

// Mock services
jest.mock('../../src/services/SubtitleService');

// Mock Alert - get it from the global mock
const { Alert } = require('react-native');
const mockAlert = Alert;

const mockSubtitleService = SubtitleService as jest.Mocked<typeof SubtitleService>;

// Mock navigation
const mockNavigate = jest.fn();
jest.mock('@react-navigation/native', () => ({
  useNavigation: () => ({
    navigate: mockNavigate,
  }),
  useRoute: () => ({
    params: {
      episode: {
        id: 'test-episode',
        title: 'Test Episode',
        description: 'A test episode',
        audioUrl: 'test-audio.mp3',
        vocabularyWords: [
          { word: 'hello', definition: 'greeting' },
          { word: 'world', definition: 'earth' },
        ],
      },
    },
  }),
}));

const renderWithProvider = () => {
  // The Zustand mock is already set up in jest.setup.js
  // We don't need to initialize it here since it's mocked
  return render(<A1DeciderGameScreen />);
};

describe('A1DeciderGameScreen', () => {
  let mockSubtitleServiceInstance: any;

  beforeEach(() => {
    jest.clearAllMocks();
    
    mockSubtitleServiceInstance = {
      processEpisodeSimulated: jest.fn(),
      loadRealVocabulary: jest.fn(),
    };
    
    mockSubtitleService.getInstance = jest.fn().mockReturnValue(mockSubtitleServiceInstance);
    
    // Mock vocabulary data
    mockSubtitleServiceInstance.loadRealVocabulary.mockResolvedValue([
      {
        word: 'schwierig',
        translation: 'difficult',
        frequency: 5,
        isRelevant: true,
        affectedSubtitles: 3,
      },
      {
        word: 'kompliziert',
        translation: 'complicated',
        frequency: 3,
        isRelevant: true,
        affectedSubtitles: 2,
      },
    ]);
    
    // Mock processing result
    mockSubtitleServiceInstance.processEpisodeSimulated.mockImplementation(
      (episode: any, onProgress: any) => {
        // Simulate progress updates
        setTimeout(() => onProgress({ stage: 'transcription', progress: 25, message: 'Transcribing...' }), 100);
        setTimeout(() => onProgress({ stage: 'filtering', progress: 50, message: 'Filtering...' }), 200);
        setTimeout(() => onProgress({ stage: 'translation', progress: 75, message: 'Translating...' }), 300);
        setTimeout(() => onProgress({ stage: 'complete', progress: 100, message: 'Complete!' }), 400);
        
        return Promise.resolve({
          isTranscribed: true,
          hasFilteredSubtitles: true,
          hasTranslatedSubtitles: true,
        });
      }
    );
  });

  it('should render initial processing screen', () => {
    const { getByText, getByTestId, queryByText } = renderWithProvider();

    // Should show the episode title (using queryByText for debugging)
    const episodeTitle = queryByText('Test Episode');
    expect(episodeTitle).toBeTruthy();
    
    // Should show the processing status indicator (mocked component)
    expect(getByTestId('mock-component')).toBeTruthy();
  });

  it('should show processing progress', async () => {
    const { getByText } = renderWithProvider();

    await waitFor(() => {
      expect(getByText('Transcription: ✅ Complete')).toBeTruthy();
    }, { timeout: 5000 });
  });

  it('should transition to vocabulary check after processing', async () => {
    const { getByText, queryByText } = renderWithProvider();

    await waitFor(() => {
      expect(queryByText('Processing Episode')).toBeFalsy();
      expect(getByText('Vocabulary Check')).toBeTruthy();
    }, { timeout: 6000 });
  });

  it('should handle word knowledge selection', async () => {
    const { getByText, getByTestId } = renderWithProvider();

    // Wait for vocabulary check phase
    await waitFor(() => {
      expect(getByText('Vocabulary Check')).toBeTruthy();
    }, { timeout: 6000 });

    // Should show first word
    expect(getByText('schwierig')).toBeTruthy();
    expect(getByText('difficult')).toBeTruthy();

    // Click "I know this word"
    const knowButton = getByTestId('know-word-button');
    fireEvent.press(knowButton);

    // Should move to next word
    await waitFor(() => {
      expect(getByText('kompliziert')).toBeTruthy();
    });
  });

  it('should handle word skip', async () => {
    const { getByText, getByTestId } = renderWithProvider();

    // Wait for vocabulary check phase
    await waitFor(() => {
      expect(getByText('Vocabulary Check')).toBeTruthy();
    }, { timeout: 6000 });

    // Click "Skip"
    const skipButton = getByTestId('skip-word-button');
    fireEvent.press(skipButton);

    // Should move to next word
    await waitFor(() => {
      expect(getByText('kompliziert')).toBeTruthy();
    });
  });

  it('should complete vocabulary check and show summary', async () => {
    const { getByText, getByTestId } = renderWithProvider();

    // Wait for vocabulary check phase
    await waitFor(() => {
      expect(getByText('Vocabulary Check')).toBeTruthy();
    }, { timeout: 6000 });

    // Go through all words
    const knowButton = getByTestId('know-word-button');
    
    // First word
    fireEvent.press(knowButton);
    
    // Second word (last word)
    await waitFor(() => {
      expect(getByText('kompliziert')).toBeTruthy();
    });
    fireEvent.press(knowButton);

    // Should show completion alert
    await waitFor(() => {
      expect(mockAlert.alert).toHaveBeenCalledWith(
        'Vocabulary Check Complete!',
        expect.stringContaining('You knew'),
        expect.arrayContaining([
          expect.objectContaining({ text: 'Watch Video' }),
          expect.objectContaining({ text: 'View Results' }),
        ])
      );
    });
  });

  it('should handle watch video navigation', async () => {
    const { getByText, getByTestId } = renderWithProvider();

    // Complete vocabulary check
    await waitFor(() => {
      expect(getByText('Vocabulary Check')).toBeTruthy();
    }, { timeout: 6000 });

    const knowButton = getByTestId('know-word-button');
    fireEvent.press(knowButton);
    
    await waitFor(() => {
      expect(getByText('kompliziert')).toBeTruthy();
    });
    fireEvent.press(knowButton);

    // Simulate pressing "Watch Video" in alert
    await waitFor(() => {
      expect(mockAlert.alert).toHaveBeenCalled();
    });

    // Get the alert call and simulate pressing "Watch Video"
    const alertCall = mockAlert.alert.mock.calls[0];
    const watchVideoButton = alertCall[2]?.find((button: any) => button.text === 'Watch Video');
    
    act(() => {
      watchVideoButton?.onPress();
    });

    expect(mockNavigate).toHaveBeenCalledWith('VideoPlayer', {
      episode: {
        id: 'test-episode',
        title: 'Test Episode',
        description: 'A test episode',
        audioUrl: 'test-audio.mp3',
        vocabularyWords: [
          { word: 'hello', definition: 'greeting' },
          { word: 'world', definition: 'earth' },
        ],
      },
    });
  });

  it('should handle view results navigation', async () => {
    const { getByText, getByTestId } = renderWithProvider();

    // Complete vocabulary check
    await waitFor(() => {
      expect(getByText('Vocabulary Check')).toBeTruthy();
    }, { timeout: 6000 });

    const knowButton = getByTestId('know-word-button');
    fireEvent.press(knowButton);
    
    await waitFor(() => {
      expect(getByText('kompliziert')).toBeTruthy();
    });
    fireEvent.press(knowButton);

    // Simulate pressing "View Results" in alert
    await waitFor(() => {
      expect(mockAlert.alert).toHaveBeenCalled();
    });

    const alertCall = mockAlert.alert.mock.calls[0];
    const viewResultsButton = alertCall[2]?.find((button: any) => button.text === 'View Results');
    
    act(() => {
      viewResultsButton?.onPress();
    });

    expect(mockNavigate).toHaveBeenCalledWith('GameResults', {
      episode: {
        id: 'test-episode',
        title: 'Test Episode',
        description: 'A test episode',
        audioUrl: 'test-audio.mp3',
        vocabularyWords: [
          { word: 'hello', definition: 'greeting' },
          { word: 'world', definition: 'earth' },
        ],
      },
      knownWords: ['schwierig', 'kompliziert'],
      unknownWords: [],
    });
  });

  it('should handle processing errors', async () => {
    mockSubtitleServiceInstance.processEpisodeSimulated.mockRejectedValue(
      new Error('Processing failed')
    );

    const { getByText } = renderWithProvider();

    await waitFor(() => {
      expect(getByText('Error processing episode')).toBeTruthy();
    }, { timeout: 2000 });
  });

  it('should handle vocabulary loading errors', async () => {
    mockSubtitleServiceInstance.loadRealVocabulary.mockRejectedValue(
      new Error('Vocabulary loading failed')
    );

    const { getByText } = renderWithProvider();

    await waitFor(() => {
      expect(getByText('Error loading vocabulary')).toBeTruthy();
    }, { timeout: 6000 });
  });

  it('should display correct progress percentages', async () => {
    const { getByText } = renderWithProvider();

    // Check initial state
    expect(getByText('Transcription: ⏳ Pending')).toBeTruthy();
    expect(getByText('A1 Filtering: ⏳ Pending')).toBeTruthy();
    expect(getByText('Translation: ⏳ Pending')).toBeTruthy();

    // Wait for completion
    await waitFor(() => {
      expect(getByText('Transcription: ✅ Complete')).toBeTruthy();
      expect(getByText('A1 Filtering: ✅ Complete')).toBeTruthy();
      expect(getByText('Translation: ✅ Complete')).toBeTruthy();
    }, { timeout: 5000 });
  });
});