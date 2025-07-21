// Jest setup for React Native

// Define __DEV__ global for React Native
global.__DEV__ = true;

// Set global test timeout
jest.setTimeout(10000);

// Mock environment variables
process.env.NODE_ENV = 'test';

// Mock Zustand for testing
jest.mock('zustand', () => ({
  create: () => {
    // Return a simple mock store
    const mockState = {
      gameSession: {
        selectedEpisode: {
          id: 'test-episode',
          title: 'Test Episode',
          description: 'A test episode',
          audioUrl: 'test-audio.mp3',
          vocabularyWords: [
            { word: 'hello', definition: 'greeting' },
            { word: 'world', definition: 'earth' },
          ],
        },
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
      // Mock actions
      selectEpisode: jest.fn(),
      startGame: jest.fn(),
      answerQuestion: jest.fn(),
      completeGame: jest.fn(),
      resetGame: jest.fn(),
      updateEpisodeStatus: jest.fn(),
      startProcessing: jest.fn(),
      updateProcessingProgress: jest.fn(),
      completeProcessing: jest.fn(),
      addKnownWord: jest.fn(),
      addUnknownWord: jest.fn(),
      addSkippedWord: jest.fn(),
      setVocabularyAnalysis: jest.fn(),
    };
    
    return () => mockState;
  }
}));

// Mock the specific useAppStore hooks
jest.mock('../../src/stores/useAppStore', () => ({
  useAppStore: () => ({
    gameSession: {
      selectedEpisode: {
        id: 'test-episode',
        title: 'Test Episode',
        description: 'A test episode',
        audioUrl: 'test-audio.mp3',
        vocabularyWords: [
          { word: 'hello', definition: 'greeting' },
          { word: 'world', definition: 'earth' },
        ],
      },
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
    selectEpisode: jest.fn(),
    startGame: jest.fn(),
    answerQuestion: jest.fn(),
    completeGame: jest.fn(),
    resetGame: jest.fn(),
    updateEpisodeStatus: jest.fn(),
    startProcessing: jest.fn(),
    updateProcessingProgress: jest.fn(),
    completeProcessing: jest.fn(),
    addKnownWord: jest.fn(),
    addUnknownWord: jest.fn(),
    addSkippedWord: jest.fn(),
    setVocabularyAnalysis: jest.fn(),
  }),
  useGameAndProcessingOptimized: () => ({
    selectedEpisode: {
      id: 'test-episode',
      title: 'Test Episode',
      description: 'A test episode',
      audioUrl: 'test-audio.mp3',
      vocabularyWords: [
        { word: 'hello', definition: 'greeting' },
        { word: 'world', definition: 'earth' },
      ],
    },
    gameStarted: false,
    gameCompleted: false,
    isProcessing: true,
    processingStage: 'transcription',
  }),
  useGameActions: () => ({
    selectEpisode: jest.fn(),
    startGame: jest.fn(),
    answerQuestion: jest.fn(),
    completeGame: jest.fn(),
    resetGame: jest.fn(),
    updateEpisodeStatus: jest.fn(),
  }),
  useProcessingActions: () => ({
    startProcessing: jest.fn(),
    updateProcessingProgress: jest.fn(),
    completeProcessing: jest.fn(),
  }),
  useVocabularyActions: () => ({
    addKnownWord: jest.fn(),
    addUnknownWord: jest.fn(),
    addSkippedWord: jest.fn(),
    setVocabularyAnalysis: jest.fn(),
  }),
  useSelectedEpisode: () => ({
    id: 'test-episode',
    title: 'Test Episode',
    description: 'A test episode',
    audioUrl: 'test-audio.mp3',
    vocabularyWords: [
      { word: 'hello', definition: 'greeting' },
      { word: 'world', definition: 'earth' },
    ],
  }),
}));

// Mock Zustand middleware
jest.mock('zustand/middleware', () => ({
  devtools: (fn) => fn,
}));

// Mock Zustand shallow
jest.mock('zustand/react/shallow', () => ({
  useShallow: (selector) => selector,
}));

// Mock console methods to reduce noise in tests
global.console = {
  ...console,
  log: jest.fn(),
  debug: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
};

// Mock React Native modules
jest.mock('react-native', () => {
  const React = require('react');
  
  const MockComponent = (props) => React.createElement('View', props, props.children);
  const MockText = (props) => React.createElement('Text', props, props.children);
  const MockScrollComponent = (props) => React.createElement('ScrollView', props, props.children);
  const MockFlatList = (props) => {
    const { data, renderItem } = props;
    return React.createElement('View', { testID: 'flatlist' }, 
      data && data.map ? data.map((item, index) => renderItem({ item, index })) : null
    );
  };
  
  return {
    Alert: {
      alert: jest.fn(),
    },
    Platform: {
      OS: 'ios',
      select: jest.fn((obj) => obj.ios),
    },
    Animated: {
      Value: jest.fn(() => ({
        setValue: jest.fn(),
        addListener: jest.fn(),
        removeListener: jest.fn(),
      })),
      timing: jest.fn(() => ({
        start: jest.fn(),
      })),
      View: MockComponent,
      Text: MockText,
    },
    View: MockComponent,
    Text: MockText,
    TextInput: MockComponent,
    ScrollView: MockScrollComponent,
    FlatList: MockFlatList,
    TouchableOpacity: MockComponent,
    TouchableHighlight: MockComponent,
    Image: MockComponent,
    ActivityIndicator: MockComponent,
    SafeAreaView: MockComponent,
    StyleSheet: {
      create: jest.fn((styles) => styles),
      flatten: jest.fn((style) => style),
      hairlineWidth: 1,
      absoluteFill: {
        position: 'absolute',
        left: 0,
        right: 0,
        top: 0,
        bottom: 0,
      },
    },
    Dimensions: {
      get: jest.fn(() => ({ width: 375, height: 667 })),
    },
  };
});

// Mock @react-navigation/native
jest.mock('@react-navigation/native', () => {
  return {
    useNavigation: () => ({
      navigate: jest.fn(),
      goBack: jest.fn(),
      reset: jest.fn(),
    }),
    useRoute: () => ({
      params: {},
    }),
    NavigationContainer: ({ children }) => children,
  };
});

// Mock @react-navigation/stack
jest.mock('@react-navigation/stack', () => {
  const React = require('react');
  return {
    createStackNavigator: () => ({
      Navigator: ({ children }) => React.createElement('View', {}, children),
      Screen: ({ children }) => React.createElement('View', {}, children),
    }),
    TransitionPresets: {},
    CardStyleInterpolators: {},
  };
});





// Mock theme provider and useTheme hook
jest.mock('../../src/theme/ThemeProvider', () => {
  const lightTheme = {
    colors: {
      primary: '#2196F3',
      primaryLight: '#E3F2FD',
      primaryDark: '#1976D2',
      secondary: '#4CAF50',
      secondaryLight: '#E8F5E8',
      secondaryDark: '#388E3C',
      success: '#4CAF50',
      successLight: '#E8F5E8',
      warning: '#FF9800',
      warningLight: '#FFF3E0',
      error: '#F44336',
      errorLight: '#FFEBEE',
      info: '#2196F3',
      infoLight: '#E3F2FD',
      background: '#F5F5F5',
      surface: '#FFFFFF',
      surfaceVariant: '#F8F9FA',
      outline: '#E0E0E0',
      outlineVariant: '#EEEEEE',
      onBackground: '#333333',
      onSurface: '#333333',
      onSurfaceVariant: '#666666',
      onPrimary: '#FFFFFF',
      onSecondary: '#FFFFFF',
      disabled: '#CCCCCC',
      disabledText: '#999999',
      shadow: '#000000',
    },
    typography: {
      fontFamily: {
        regular: 'System',
        medium: 'System',
        bold: 'System',
      },
      fontSize: {
        xs: 10,
        sm: 12,
        base: 14,
        md: 16,
        lg: 18,
        xl: 20,
        '2xl': 24,
        '3xl': 28,
        '4xl': 32,
        '5xl': 36,
      },
      fontWeight: {
        normal: '400',
        medium: '500',
        semibold: '600',
        bold: '700',
      },
      lineHeight: {
        tight: 1.2,
        normal: 1.5,
        relaxed: 1.8,
      },
    },
    spacing: {
      xs: 4,
      sm: 8,
      md: 12,
      lg: 16,
      xl: 20,
      '2xl': 24,
      '3xl': 32,
      '4xl': 40,
      '5xl': 48,
      '6xl': 64,
    },
    borderRadius: {
      none: 0,
      sm: 4,
      md: 8,
      lg: 12,
      xl: 16,
      full: 9999,
    },
    shadows: {
      sm: {
        shadowColor: '#000000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.1,
        shadowRadius: 2,
        elevation: 2,
      },
      md: {
        shadowColor: '#000000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
      },
      lg: {
        shadowColor: '#000000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.15,
        shadowRadius: 8,
        elevation: 5,
      },
    },
  };
  
  return {
     useTheme: () => ({
        theme: lightTheme,
        isDark: false,
        toggleTheme: jest.fn(),
      }),
      ThemeProvider: ({ children }) => children,
    };
  });

// Mock components separately
jest.mock('../../src/components', () => {
  const React = require('react');
  const MockComponent = (props) => React.createElement('View', { testID: props.testID || 'mock-component' }, props.children);
  
  return {
    ProcessingStatusIndicator: MockComponent,
    ProgressBar: MockComponent,
    VocabularyCard: MockComponent,
    StatsSummary: MockComponent,
    ActionButtonsRow: MockComponent,
    useTheme: () => ({
      theme: {
        colors: { primary: '#2196F3', surface: '#FFFFFF', onSurface: '#333333' },
        spacing: { xl: 20 },
        typography: { fontSize: { '2xl': 24 } },
      },
    }),
    createGameStats: jest.fn(() => ({})),
    createCommonButtons: jest.fn(() => []),
    createCommonStyles: jest.fn(() => ({})),
    getSemanticColors: jest.fn(() => ({})),
  };
});

// Mock the processing workflow hook
jest.mock('../../src/hooks/useProcessingWorkflow', () => {
  return jest.fn(() => ({
    currentStage: 'transcription',
    overallProgress: 50,
    currentStep: { message: 'Processing...' },
    isProcessing: true,
    startProcessing: jest.fn(),
    updateStepProgress: jest.fn(),
    completeStep: jest.fn(),
    failStep: jest.fn(),
  }));
});

// Services are mocked in individual test files as needed

// Mock fetch for API calls
import fetchMock from 'jest-fetch-mock';
fetchMock.enableMocks();

// Note: afterEach cleanup should be done in individual test files