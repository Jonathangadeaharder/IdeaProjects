import { renderHook, act } from '@testing-library/react-native';
import { useGameLogic } from '../../src/hooks/useGameLogic';

// Mock timers for testing
jest.useFakeTimers();

describe('useGameLogic Hook', () => {
  const mockQuestions = [
    {
      id: '1',
      text: 'What is the capital of Germany?',
      options: ['Berlin', 'Munich', 'Hamburg', 'Frankfurt'],
      correctAnswer: 0,
      explanation: 'Berlin is the capital and largest city of Germany.'
    },
    {
      id: '2',
      text: 'Which language is spoken in Germany?',
      options: ['English', 'French', 'German', 'Spanish'],
      correctAnswer: 2,
      explanation: 'German is the official language of Germany.'
    },
    {
      id: '3',
      text: 'What is the currency of Germany?',
      options: ['Dollar', 'Euro', 'Pound', 'Yen'],
      correctAnswer: 1,
      explanation: 'Germany uses the Euro as its currency.'
    }
  ];

  const mockOnGameComplete = jest.fn();
  const mockOnQuestionAnswered = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    jest.clearAllTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
  });

  describe('Initial State', () => {
    it('should initialize with correct default values', () => {
      const { result } = renderHook(() =>
        useGameLogic({
          questions: mockQuestions,
          timeLimit: 300,
          onGameComplete: mockOnGameComplete,
          onQuestionAnswered: mockOnQuestionAnswered,
        })
      );

      expect(result.current.currentQuestionIndex).toBe(0);
      expect(result.current.currentQuestion).toEqual(mockQuestions[0]);
      expect(result.current.selectedAnswer).toBeNull();
      expect(result.current.isAnswerSubmitted).toBe(false);
      expect(result.current.isCorrect).toBeNull();
      expect(result.current.timeRemaining).toBe(300);
      expect(result.current.isTimerActive).toBe(false);
      expect(result.current.isGameComplete).toBe(false);
      expect(result.current.isGameStarted).toBe(false);
      expect(result.current.gameStats).toEqual({
        correct: 0,
        incorrect: 0,
        total: 0,
        score: 0,
        timeSpent: 0,
      });
    });

    it('should handle empty questions array', () => {
      const { result } = renderHook(() =>
        useGameLogic({
          questions: [],
          timeLimit: 300,
        })
      );

      expect(result.current.currentQuestion).toBeNull();
      expect(result.current.currentQuestionIndex).toBe(0);
    });
  });

  describe('Game Flow', () => {
    it('should start game correctly', () => {
      const { result } = renderHook(() =>
        useGameLogic({
          questions: mockQuestions,
          timeLimit: 300,
          onGameComplete: mockOnGameComplete,
        })
      );

      act(() => {
        result.current.startGame();
      });

      expect(result.current.isGameStarted).toBe(true);
      expect(result.current.isTimerActive).toBe(true);
      expect(result.current.currentQuestionIndex).toBe(0);
      expect(result.current.selectedAnswer).toBeNull();
      expect(result.current.isAnswerSubmitted).toBe(false);
      expect(result.current.isCorrect).toBeNull();
      expect(result.current.isGameComplete).toBe(false);
    });

    it('should reset game state when starting new game', () => {
      const { result } = renderHook(() =>
        useGameLogic({
          questions: mockQuestions,
          timeLimit: 300,
        })
      );

      // Start game and make some progress
      act(() => {
        result.current.startGame();
        result.current.selectAnswer(1);
        result.current.submitAnswer();
      });

      // Start new game
      act(() => {
        result.current.startGame();
      });

      expect(result.current.currentQuestionIndex).toBe(0);
      expect(result.current.selectedAnswer).toBeNull();
      expect(result.current.isAnswerSubmitted).toBe(false);
      expect(result.current.gameStats.total).toBe(0);
    });
  });

  describe('Answer Selection and Submission', () => {
    it('should select answer correctly', () => {
      const { result } = renderHook(() =>
        useGameLogic({
          questions: mockQuestions,
          timeLimit: 300,
        })
      );

      act(() => {
        result.current.startGame();
        result.current.selectAnswer(2);
      });

      expect(result.current.selectedAnswer).toBe(2);
    });

    it('should not allow answer selection after submission', () => {
      const { result } = renderHook(() =>
        useGameLogic({
          questions: mockQuestions,
          timeLimit: 300,
        })
      );

      act(() => {
        result.current.startGame();
        result.current.selectAnswer(1);
        result.current.submitAnswer();
        result.current.selectAnswer(2); // This should be ignored
      });

      expect(result.current.selectedAnswer).toBe(1);
    });

    it('should submit correct answer and update stats', () => {
      const { result } = renderHook(() =>
        useGameLogic({
          questions: mockQuestions,
          timeLimit: 300,
          onQuestionAnswered: mockOnQuestionAnswered,
        })
      );

      act(() => {
        result.current.startGame();
        result.current.selectAnswer(0); // Correct answer for first question
        result.current.submitAnswer();
      });

      expect(result.current.isAnswerSubmitted).toBe(true);
      expect(result.current.isCorrect).toBe(true);
      expect(result.current.gameStats.correct).toBe(1);
      expect(result.current.gameStats.incorrect).toBe(0);
      expect(result.current.gameStats.total).toBe(1);
      expect(result.current.gameStats.score).toBe(100);
      expect(mockOnQuestionAnswered).toHaveBeenCalledWith('1', true);
    });

    it('should submit incorrect answer and update stats', () => {
      const { result } = renderHook(() =>
        useGameLogic({
          questions: mockQuestions,
          timeLimit: 300,
          onQuestionAnswered: mockOnQuestionAnswered,
        })
      );

      act(() => {
        result.current.startGame();
        result.current.selectAnswer(1); // Incorrect answer for first question
        result.current.submitAnswer();
      });

      expect(result.current.isAnswerSubmitted).toBe(true);
      expect(result.current.isCorrect).toBe(false);
      expect(result.current.gameStats.correct).toBe(0);
      expect(result.current.gameStats.incorrect).toBe(1);
      expect(result.current.gameStats.total).toBe(1);
      expect(result.current.gameStats.score).toBe(0);
      expect(mockOnQuestionAnswered).toHaveBeenCalledWith('1', false);
    });

    it('should not submit answer when none is selected', () => {
      const { result } = renderHook(() =>
        useGameLogic({
          questions: mockQuestions,
          timeLimit: 300,
        })
      );

      act(() => {
        result.current.startGame();
        result.current.submitAnswer(); // No answer selected
      });

      expect(result.current.isAnswerSubmitted).toBe(false);
      expect(result.current.isCorrect).toBeNull();
      expect(result.current.gameStats.total).toBe(0);
    });

    it('should not submit answer twice', () => {
      const { result } = renderHook(() =>
        useGameLogic({
          questions: mockQuestions,
          timeLimit: 300,
        })
      );

      act(() => {
        result.current.startGame();
        result.current.selectAnswer(0);
        result.current.submitAnswer();
        result.current.submitAnswer(); // Second submission should be ignored
      });

      expect(result.current.gameStats.total).toBe(1); // Should still be 1
    });
  });

  describe('Question Navigation', () => {
    it('should move to next question correctly', () => {
      const { result } = renderHook(() =>
        useGameLogic({
          questions: mockQuestions,
          timeLimit: 300,
        })
      );

      act(() => {
        result.current.startGame();
        result.current.selectAnswer(0);
        result.current.submitAnswer();
        result.current.nextQuestion();
      });

      expect(result.current.currentQuestionIndex).toBe(1);
      expect(result.current.currentQuestion).toEqual(mockQuestions[1]);
      expect(result.current.selectedAnswer).toBeNull();
      expect(result.current.isAnswerSubmitted).toBe(false);
      expect(result.current.isCorrect).toBeNull();
    });

    it('should complete game when reaching last question', () => {
      const { result } = renderHook(() =>
        useGameLogic({
          questions: mockQuestions,
          timeLimit: 300,
          onGameComplete: mockOnGameComplete,
        })
      );

      act(() => {
        result.current.startGame();
      });

      // Answer all questions
      for (let i = 0; i < mockQuestions.length; i++) {
        act(() => {
          result.current.selectAnswer(0);
          result.current.submitAnswer();
          if (i < mockQuestions.length - 1) {
            result.current.nextQuestion();
          } else {
            result.current.nextQuestion(); // This should complete the game
          }
        });
      }

      expect(result.current.isGameComplete).toBe(true);
      expect(result.current.isTimerActive).toBe(false);
      expect(mockOnGameComplete).toHaveBeenCalled();
    });

    it('should skip question and mark as incorrect', () => {
      const { result } = renderHook(() =>
        useGameLogic({
          questions: mockQuestions,
          timeLimit: 300,
          onQuestionAnswered: mockOnQuestionAnswered,
        })
      );

      act(() => {
        result.current.startGame();
        result.current.skipQuestion();
      });

      expect(result.current.currentQuestionIndex).toBe(1);
      expect(result.current.gameStats.incorrect).toBe(1);
      expect(result.current.gameStats.total).toBe(1);
      expect(result.current.gameStats.score).toBe(0);
      expect(mockOnQuestionAnswered).toHaveBeenCalledWith('1', false);
    });
  });

  describe('Timer Functionality', () => {
    it('should countdown timer when active', () => {
      const { result } = renderHook(() =>
        useGameLogic({
          questions: mockQuestions,
          timeLimit: 10,
        })
      );

      act(() => {
        result.current.startGame();
      });

      expect(result.current.timeRemaining).toBe(10);
      expect(result.current.isTimerActive).toBe(true);

      // Advance timer by 3 seconds
      act(() => {
        jest.advanceTimersByTime(3000);
      });

      expect(result.current.timeRemaining).toBe(7);
    });

    it('should complete game when timer reaches zero', () => {
      const { result } = renderHook(() =>
        useGameLogic({
          questions: mockQuestions,
          timeLimit: 5,
          onGameComplete: mockOnGameComplete,
        })
      );

      act(() => {
        result.current.startGame();
      });

      // Advance timer to completion
      act(() => {
        jest.advanceTimersByTime(5000);
      });

      expect(result.current.timeRemaining).toBe(0);
      expect(result.current.isGameComplete).toBe(true);
      expect(result.current.isTimerActive).toBe(false);
      expect(mockOnGameComplete).toHaveBeenCalled();
    });

    it('should pause and resume timer', () => {
      const { result } = renderHook(() =>
        useGameLogic({
          questions: mockQuestions,
          timeLimit: 10,
        })
      );

      act(() => {
        result.current.startGame();
      });

      expect(result.current.isTimerActive).toBe(true);

      act(() => {
        result.current.pauseTimer();
      });

      expect(result.current.isTimerActive).toBe(false);

      // Timer should not advance when paused
      act(() => {
        jest.advanceTimersByTime(2000);
      });

      expect(result.current.timeRemaining).toBe(10);

      act(() => {
        result.current.resumeTimer();
      });

      expect(result.current.isTimerActive).toBe(true);
    });

    it('should not run timer when game is complete', () => {
      const { result } = renderHook(() =>
        useGameLogic({
          questions: [mockQuestions[0]], // Only one question
          timeLimit: 10,
        })
      );

      act(() => {
        result.current.startGame();
        result.current.selectAnswer(0);
        result.current.submitAnswer();
        result.current.nextQuestion(); // Complete the game
      });

      expect(result.current.isGameComplete).toBe(true);
      expect(result.current.isTimerActive).toBe(false);

      // Timer should not advance when game is complete
      const timeBeforeAdvance = result.current.timeRemaining;
      act(() => {
        jest.advanceTimersByTime(2000);
      });

      expect(result.current.timeRemaining).toBe(timeBeforeAdvance);
    });
  });

  describe('Game Reset', () => {
    it('should reset all game state', () => {
      const { result } = renderHook(() =>
        useGameLogic({
          questions: mockQuestions,
          timeLimit: 300,
        })
      );

      // Start game and make progress
      act(() => {
        result.current.startGame();
        result.current.selectAnswer(1);
        result.current.submitAnswer();
        result.current.nextQuestion();
      });

      // Reset game
      act(() => {
        result.current.resetGame();
      });

      expect(result.current.currentQuestionIndex).toBe(0);
      expect(result.current.selectedAnswer).toBeNull();
      expect(result.current.isAnswerSubmitted).toBe(false);
      expect(result.current.isCorrect).toBeNull();
      expect(result.current.isGameStarted).toBe(false);
      expect(result.current.isGameComplete).toBe(false);
      expect(result.current.timeRemaining).toBe(300);
      expect(result.current.isTimerActive).toBe(false);
    });
  });

  describe('Score Calculation', () => {
    it('should calculate score correctly with mixed answers', () => {
      const { result } = renderHook(() =>
        useGameLogic({
          questions: mockQuestions,
          timeLimit: 300,
        })
      );

      act(() => {
        result.current.startGame();
      });

      // Answer first question correctly
      act(() => {
        result.current.selectAnswer(0); // Correct
        result.current.submitAnswer();
        result.current.nextQuestion();
      });

      expect(result.current.gameStats.score).toBe(100);

      // Answer second question incorrectly
      act(() => {
        result.current.selectAnswer(0); // Incorrect (correct is 2)
        result.current.submitAnswer();
        result.current.nextQuestion();
      });

      expect(result.current.gameStats.score).toBe(50); // 1 correct out of 2 total

      // Answer third question correctly
      act(() => {
        result.current.selectAnswer(1); // Correct
        result.current.submitAnswer();
      });

      expect(result.current.gameStats.score).toBe(67); // 2 correct out of 3 total (rounded)
    });
  });

  describe('Edge Cases', () => {
    it('should handle single question game', () => {
      const singleQuestion = [mockQuestions[0]];
      const { result } = renderHook(() =>
        useGameLogic({
          questions: singleQuestion,
          timeLimit: 300,
          onGameComplete: mockOnGameComplete,
        })
      );

      act(() => {
        result.current.startGame();
        result.current.selectAnswer(0);
        result.current.submitAnswer();
        result.current.nextQuestion();
      });

      expect(result.current.isGameComplete).toBe(true);
      expect(mockOnGameComplete).toHaveBeenCalled();
    });

    it('should handle zero time limit', () => {
      const { result } = renderHook(() =>
        useGameLogic({
          questions: mockQuestions,
          timeLimit: 0,
          onGameComplete: mockOnGameComplete,
        })
      );

      act(() => {
        result.current.startGame();
      });

      expect(result.current.timeRemaining).toBe(0);
      expect(result.current.isGameComplete).toBe(true);
      expect(mockOnGameComplete).toHaveBeenCalled();
    });

    it('should handle callback functions being undefined', () => {
      const { result } = renderHook(() =>
        useGameLogic({
          questions: mockQuestions,
          timeLimit: 300,
          // No callbacks provided
        })
      );

      // Should not throw errors when callbacks are undefined
      expect(() => {
        act(() => {
          result.current.startGame();
          result.current.selectAnswer(0);
          result.current.submitAnswer();
          result.current.nextQuestion();
        });
      }).not.toThrow();
    });
  });
});