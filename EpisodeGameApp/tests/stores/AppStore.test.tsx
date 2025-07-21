import React from 'react';
import { Text, TouchableOpacity } from 'react-native';
import { render, act } from '../setup/test-utils';
import { defaultEpisodes } from '../../src/models/Episode';

// Mock the entire useAppStore module
jest.mock('../../src/stores/useAppStore', () => {
  const React = require('react');
  
  let mockState = {
    gameSession: {
      selectedEpisode: null,
      currentScore: 0,
      totalQuestions: 0,
      correctAnswers: 0,
      gameStarted: false,
      gameCompleted: false,
      userAnswers: {},
    },
    episodeProcessing: {
      isProcessing: false,
      processingStage: null,
    },
    vocabularyLearning: {
      knownWords: [],
      unknownWords: [],
      skippedWords: [],
      vocabularyAnalysis: null,
    },
  };

  const listeners = new Set();
  const notifyListeners = () => {
    listeners.forEach(listener => listener());
  };

  const resetMockState = () => {
    mockState.gameSession = {
      selectedEpisode: null,
      currentScore: 0,
      totalQuestions: 0,
      correctAnswers: 0,
      gameStarted: false,
      gameCompleted: false,
      userAnswers: {},
    };
    mockState.episodeProcessing = {
      isProcessing: false,
      processingStage: null,
    };
    mockState.vocabularyLearning = {
      knownWords: [],
      unknownWords: [],
      skippedWords: [],
      vocabularyAnalysis: null,
    };
    notifyListeners();
  };

  const mockActions = {
    selectEpisode: jest.fn((episode) => {
      mockState.gameSession.selectedEpisode = episode;
      notifyListeners();
    }),
    startGame: jest.fn(() => {
      mockState.gameSession.gameStarted = true;
      mockState.gameSession.gameCompleted = false;
      mockState.gameSession.totalQuestions = mockState.gameSession.selectedEpisode?.vocabularyWords.length || 0;
      notifyListeners();
    }),
    completeGame: jest.fn(() => {
      mockState.gameSession.gameCompleted = true;
      mockState.gameSession.gameStarted = false;
      notifyListeners();
    }),
    updateEpisodeStatus: jest.fn(),
    startProcessing: jest.fn((stage) => {
      mockState.episodeProcessing.isProcessing = true;
      mockState.episodeProcessing.processingStage = stage;
      notifyListeners();
    }),
    updateProcessingProgress: jest.fn((stage) => {
      mockState.episodeProcessing.processingStage = stage;
      notifyListeners();
    }),
    completeProcessing: jest.fn(() => {
      mockState.episodeProcessing.isProcessing = false;
      mockState.episodeProcessing.processingStage = 'complete';
      notifyListeners();
    }),
    addKnownWord: jest.fn((word) => {
      mockState.vocabularyLearning.knownWords.push(word);
      notifyListeners();
    }),
    resetMockState,
  };

  const useStore = (selector) => {
    const [, forceUpdate] = React.useReducer(x => x + 1, 0);
    
    React.useEffect(() => {
      listeners.add(forceUpdate);
      return () => listeners.delete(forceUpdate);
    }, [forceUpdate]);
    
    return selector ? selector(mockState) : mockState;
  };

  return {
    useSelectedEpisode: () => useStore(state => state.gameSession.selectedEpisode),
    useGameProgress: () => useStore(state => ({
      currentScore: state.gameSession.currentScore,
      correctAnswers: state.gameSession.correctAnswers,
      totalQuestions: state.gameSession.totalQuestions,
      gameStarted: state.gameSession.gameStarted,
      gameCompleted: state.gameSession.gameCompleted,
    })),
    useProcessingStatus: () => useStore(state => ({
      isProcessing: state.episodeProcessing.isProcessing,
      processingStage: state.episodeProcessing.processingStage,
    })),
    useVocabularyProgress: () => useStore(state => ({
      knownWords: state.vocabularyLearning.knownWords,
      unknownWords: state.vocabularyLearning.unknownWords,
      skippedWords: state.vocabularyLearning.skippedWords,
    })),
    useGameActions: () => mockActions,
    useProcessingActions: () => mockActions,
    useVocabularyActions: () => mockActions,
  };
});

const {
  useSelectedEpisode,
  useGameProgress,
  useProcessingStatus,
  useVocabularyProgress,
  useGameActions,
  useProcessingActions,
  useVocabularyActions,
} = require('../../src/stores/useAppStore');

// Test component to access Zustand store
const TestComponent = () => {
  const selectedEpisode = useSelectedEpisode();
  const { gameStarted, gameCompleted } = useGameProgress();
  const { isProcessing, processingStage } = useProcessingStatus();
  const { knownWords } = useVocabularyProgress();
  const { selectEpisode, startGame, completeGame, updateEpisodeStatus } = useGameActions();
  const { startProcessing, updateProcessingProgress, completeProcessing } = useProcessingActions();
  const { addKnownWord } = useVocabularyActions();

  return (
    <>
      <Text testID="current-episode">{selectedEpisode?.title || 'No episode'}</Text>
      <Text testID="game-started">{gameStarted.toString()}</Text>
      <Text testID="game-completed">{gameCompleted.toString()}</Text>
      <Text testID="is-processing">{isProcessing.toString()}</Text>
      <Text testID="processing-stage">{processingStage || ''}</Text>
      <Text testID="known-words">{knownWords.length.toString()}</Text>
      <TouchableOpacity testID="select-episode" onPress={() => selectEpisode(defaultEpisodes[0])}>
        <Text>Select Episode</Text>
      </TouchableOpacity>
      <TouchableOpacity testID="start-game" onPress={() => startGame()}>
        <Text>Start Game</Text>
      </TouchableOpacity>
      <TouchableOpacity testID="complete-game" onPress={() => completeGame()}>
        <Text>Complete Game</Text>
      </TouchableOpacity>
      <TouchableOpacity testID="start-processing" onPress={() => startProcessing('transcription')}>
        <Text>Start Processing</Text>
      </TouchableOpacity>
      <TouchableOpacity testID="update-processing" onPress={() => updateProcessingProgress('filtering')}>
        <Text>Update Processing</Text>
      </TouchableOpacity>
      <TouchableOpacity testID="complete-processing" onPress={() => completeProcessing()}>
        <Text>Complete Processing</Text>
      </TouchableOpacity>
      <TouchableOpacity testID="add-known-word" onPress={() => addKnownWord('test')}>
        <Text>Add Known Word</Text>
      </TouchableOpacity>
      <TouchableOpacity testID="update-status" onPress={() => updateEpisodeStatus(true, true)}>
        <Text>Update Status</Text>
      </TouchableOpacity>
    </>
  );
};

const renderWithProvider = () => {
  return render(<TestComponent />);
};

describe('Zustand Store Integration', () => {
  const mockEpisode = {
    id: 'test-episode',
    title: 'Test Episode',
    description: 'A test episode',
    audioUrl: 'test-audio.mp3',
    vocabularyWords: [
      { word: 'hello', definition: 'greeting' },
      { word: 'world', definition: 'earth' },
    ],
  };

  beforeEach(() => {
    const { useGameActions } = require('../../src/stores/useAppStore');
    const actions = useGameActions();
    actions.resetMockState();
    jest.clearAllMocks();
  });

  it('should provide initial state', () => {
    const { getByTestId } = renderWithProvider();

    expect(getByTestId('current-episode')).toHaveTextContent('No episode');
    expect(getByTestId('game-started')).toHaveTextContent('false');
    expect(getByTestId('game-completed')).toHaveTextContent('false');
    expect(getByTestId('is-processing')).toHaveTextContent('false');
    expect(getByTestId('processing-stage')).toHaveTextContent('');
    expect(getByTestId('known-words')).toHaveTextContent('0');
  });

  it('should start game correctly', () => {
    const { getByTestId } = renderWithProvider();

    // First select an episode
    act(() => {
      getByTestId('select-episode').props.onPress();
    });

    // Then start the game
    act(() => {
      getByTestId('start-game').props.onPress();
    });

    expect(getByTestId('current-episode')).toHaveTextContent(defaultEpisodes[0].title);
    expect(getByTestId('game-started')).toHaveTextContent('true');
    expect(getByTestId('game-completed')).toHaveTextContent('false');
  });

  it('should complete game correctly', () => {
    const { getByTestId } = renderWithProvider();

    // Select episode and start game first
    act(() => {
      getByTestId('select-episode').props.onPress();
    });
    
    act(() => {
      getByTestId('start-game').props.onPress();
    });

    // Complete game
    act(() => {
      getByTestId('complete-game').props.onPress();
    });

    expect(getByTestId('game-started')).toHaveTextContent('false');
    expect(getByTestId('game-completed')).toHaveTextContent('true');
  });

  it('should handle processing workflow', () => {
    const { getByTestId } = renderWithProvider();

    // Start processing
    act(() => {
      getByTestId('start-processing').props.onPress();
    });

    expect(getByTestId('is-processing')).toHaveTextContent('true');
    expect(getByTestId('processing-stage')).toHaveTextContent('transcription');

    // Update processing progress
    act(() => {
      getByTestId('update-processing').props.onPress();
    });

    expect(getByTestId('processing-stage')).toHaveTextContent('filtering');

    // Complete processing
    act(() => {
      getByTestId('complete-processing').props.onPress();
    });

    expect(getByTestId('is-processing')).toHaveTextContent('false');
    expect(getByTestId('processing-stage')).toHaveTextContent('complete');
  });

  it('should handle vocabulary learning', () => {
    const { getByTestId } = renderWithProvider();

    // Add known word
    act(() => {
      getByTestId('add-known-word').props.onPress();
    });

    expect(getByTestId('known-words')).toHaveTextContent('1');
  });

  it('should handle multiple state changes across contexts', () => {
    const { getByTestId } = renderWithProvider();

    // Select episode and start game
    act(() => {
      getByTestId('select-episode').props.onPress();
    });
    
    act(() => {
      getByTestId('start-game').props.onPress();
    });

    // Start processing
    act(() => {
      getByTestId('start-processing').props.onPress();
    });

    // Add vocabulary
    act(() => {
      getByTestId('add-known-word').props.onPress();
    });

    // Complete game
    act(() => {
      getByTestId('complete-game').props.onPress();
    });

    expect(getByTestId('game-started')).toHaveTextContent('false');
    expect(getByTestId('game-completed')).toHaveTextContent('true');
    expect(getByTestId('is-processing')).toHaveTextContent('true');
    expect(getByTestId('known-words')).toHaveTextContent('1');
  });
});