import { renderHook, act } from '@testing-library/react-native';
import { useGameLogic } from '../../src/hooks/useGameLogic';

// Mock data for testing
const mockQuestions = [
  {
    id: '1',
    text: 'What does "Hallo" mean?',
    options: ['Hello', 'Goodbye', 'Thank you', 'Please'],
    correctAnswer: 0,
    difficulty: 'easy',
    category: 'greetings'
  },
  {
    id: '2', 
    text: 'What does "Danke" mean?',
    options: ['Hello', 'Goodbye', 'Thank you', 'Please'],
    correctAnswer: 2,
    difficulty: 'easy',
    category: 'greetings'
  },
  {
    id: '3',
    text: 'What does "Entschuldigung" mean?',
    options: ['Excuse me', 'Good morning', 'Good night', 'See you later'],
    correctAnswer: 0,
    difficulty: 'medium',
    category: 'politeness'
  }
];

describe('useGameLogic - Advanced Tests', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  describe('Complex Game Flow Scenarios', () => {
    it('should handle rapid answer selection and submission', () => {
      const onGameComplete = jest.fn();
      const { result } = renderHook(() => 
        useGameLogic(mockQuestions, { timeLimit: 30, onGameComplete })
      );

      // Start game
      act(() => {
        result.current.startGame();
      });

      // Rapidly select and submit multiple answers
      for (let i = 0; i < 3; i++) {
        act(() => {
          result.current.selectAnswer(i % 4);
        });
        
        act(() => {
          result.current.submitAnswer();
        });
        
        if (i < 2) {
          act(() => {
            result.current.nextQuestion();
          });
        }
      }

      expect(result.current.currentQuestionIndex).toBe(2);
      expect(result.current.score).toBeGreaterThanOrEqual(0);
      expect(result.current.answeredQuestions).toHaveLength(3);
    });

    it('should handle game completion with mixed correct/incorrect answers', () => {
      const onGameComplete = jest.fn();
      const { result } = renderHook(() => 
        useGameLogic(mockQuestions, { timeLimit: 30, onGameComplete })
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

      // Answer second question incorrectly
      act(() => {
        result.current.selectAnswer(1); // Incorrect
        result.current.submitAnswer();
        result.current.nextQuestion();
      });

      // Answer third question correctly
      act(() => {
        result.current.selectAnswer(0); // Correct
        result.current.submitAnswer();
        result.current.completeGame();
      });

      expect(result.current.score).toBe(2);
      expect(result.current.isGameComplete).toBe(true);
      expect(onGameComplete).toHaveBeenCalledWith({
        score: 2,
        totalQuestions: 3,
        timeElapsed: expect.any(Number),
        answeredQuestions: expect.any(Array)
      });
    });

    it('should handle skipping all questions', () => {
      const onGameComplete = jest.fn();
      const { result } = renderHook(() => 
        useGameLogic(mockQuestions, { timeLimit: 30, onGameComplete })
      );

      act(() => {
        result.current.startGame();
      });

      // Skip all questions
      for (let i = 0; i < mockQuestions.length; i++) {
        act(() => {
          result.current.skipQuestion();
        });
        
        if (i < mockQuestions.length - 1) {
          act(() => {
            result.current.nextQuestion();
          });
        }
      }

      act(() => {
        result.current.completeGame();
      });

      expect(result.current.score).toBe(0);
      expect(result.current.answeredQuestions.every(q => q.skipped)).toBe(true);
    });
  });

  describe('Timer Edge Cases', () => {
    it('should handle timer expiration during answer selection', () => {
      const onTimeUp = jest.fn();
      const { result } = renderHook(() => 
        useGameLogic(mockQuestions, { timeLimit: 5, onTimeUp })
      );

      act(() => {
        result.current.startGame();
      });

      // Select answer but don't submit
      act(() => {
        result.current.selectAnswer(1);
      });

      // Advance timer to expiration
      act(() => {
        jest.advanceTimersByTime(5000);
      });

      expect(result.current.timeRemaining).toBe(0);
      expect(result.current.isGameActive).toBe(false);
      expect(onTimeUp).toHaveBeenCalled();
    });

    it('should handle multiple pause/resume cycles', () => {
      const { result } = renderHook(() => 
        useGameLogic(mockQuestions, { timeLimit: 30 })
      );

      act(() => {
        result.current.startGame();
      });

      // Multiple pause/resume cycles
      for (let i = 0; i < 5; i++) {
        act(() => {
          result.current.pauseTimer();
        });
        
        expect(result.current.isTimerPaused).toBe(true);
        
        // Advance time while paused (shouldn't affect timer)
        act(() => {
          jest.advanceTimersByTime(2000);
        });
        
        act(() => {
          result.current.resumeTimer();
        });
        
        expect(result.current.isTimerPaused).toBe(false);
      }

      // Timer should still have most of its time
      expect(result.current.timeRemaining).toBeGreaterThan(20);
    });

    it('should handle timer with zero time limit', () => {
      const { result } = renderHook(() => 
        useGameLogic(mockQuestions, { timeLimit: 0 })
      );

      act(() => {
        result.current.startGame();
      });

      // With zero time limit, timer should be disabled
      expect(result.current.timeRemaining).toBe(0);
      expect(result.current.isGameActive).toBe(true); // Game should still be active
      
      // Advancing time shouldn't affect anything
      act(() => {
        jest.advanceTimersByTime(10000);
      });
      
      expect(result.current.isGameActive).toBe(true);
    });

    it('should handle timer precision with fractional seconds', () => {
      const { result } = renderHook(() => 
        useGameLogic(mockQuestions, { timeLimit: 10 })
      );

      act(() => {
        result.current.startGame();
      });

      // Advance by fractional seconds
      act(() => {
        jest.advanceTimersByTime(500); // 0.5 seconds
      });

      expect(result.current.timeRemaining).toBe(9.5);

      act(() => {
        jest.advanceTimersByTime(250); // 0.25 seconds
      });

      expect(result.current.timeRemaining).toBe(9.25);
    });
  });

  describe('State Consistency and Race Conditions', () => {
    it('should maintain state consistency during rapid operations', () => {
      const { result } = renderHook(() => 
        useGameLogic(mockQuestions, { timeLimit: 30 })
      );

      act(() => {
        result.current.startGame();
      });

      // Perform rapid state changes
      for (let i = 0; i < 10; i++) {
        act(() => {
          result.current.selectAnswer(i % 4);
          result.current.pauseTimer();
          result.current.resumeTimer();
        });
      }

      // State should remain consistent
      expect(result.current.selectedAnswer).toBe(2); // 9 % 4 = 1, but last operation was 9 % 4 = 1
      expect(result.current.isTimerPaused).toBe(false);
      expect(result.current.isGameActive).toBe(true);
    });

    it('should handle simultaneous timer expiration and answer submission', () => {
      const onTimeUp = jest.fn();
      const { result } = renderHook(() => 
        useGameLogic(mockQuestions, { timeLimit: 1, onTimeUp })
      );

      act(() => {
        result.current.startGame();
        result.current.selectAnswer(0);
      });

      // Simultaneously expire timer and submit answer
      act(() => {
        jest.advanceTimersByTime(1000);
        result.current.submitAnswer();
      });

      // Should handle gracefully - timer expiration takes precedence
      expect(result.current.isGameActive).toBe(false);
      expect(onTimeUp).toHaveBeenCalled();
    });

    it('should handle reset during active game', () => {
      const { result } = renderHook(() => 
        useGameLogic(mockQuestions, { timeLimit: 30 })
      );

      act(() => {
        result.current.startGame();
        result.current.selectAnswer(1);
        result.current.submitAnswer();
      });

      // Advance timer and answer some questions
      act(() => {
        jest.advanceTimersByTime(10000);
        result.current.nextQuestion();
        result.current.selectAnswer(2);
      });

      // Reset during active game
      act(() => {
        result.current.resetGame();
      });

      // Should return to initial state
      expect(result.current.isGameActive).toBe(false);
      expect(result.current.currentQuestionIndex).toBe(0);
      expect(result.current.selectedAnswer).toBeNull();
      expect(result.current.score).toBe(0);
      expect(result.current.timeRemaining).toBe(30);
      expect(result.current.answeredQuestions).toHaveLength(0);
    });
  });

  describe('Performance and Memory', () => {
    it('should handle large question sets efficiently', () => {
      // Create large question set
      const largeQuestionSet = Array.from({ length: 1000 }, (_, i) => ({
        id: `q${i}`,
        text: `Question ${i}`,
        options: [`Option A${i}`, `Option B${i}`, `Option C${i}`, `Option D${i}`],
        correctAnswer: i % 4,
        difficulty: 'medium',
        category: 'test'
      }));

      const { result } = renderHook(() => 
        useGameLogic(largeQuestionSet, { timeLimit: 30 })
      );

      act(() => {
        result.current.startGame();
      });

      // Should handle large dataset without issues
      expect(result.current.isGameActive).toBe(true);
      expect(result.current.currentQuestion).toBeDefined();
      
      // Navigate through several questions
      for (let i = 0; i < 10; i++) {
        act(() => {
          result.current.selectAnswer(i % 4);
          result.current.submitAnswer();
          if (i < 9) result.current.nextQuestion();
        });
      }

      expect(result.current.currentQuestionIndex).toBe(9);
      expect(result.current.answeredQuestions).toHaveLength(10);
    });

    it('should cleanup timers properly on unmount', () => {
      const { result, unmount } = renderHook(() => 
        useGameLogic(mockQuestions, { timeLimit: 30 })
      );

      act(() => {
        result.current.startGame();
      });

      expect(result.current.isGameActive).toBe(true);

      // Unmount component
      unmount();

      // Advance time after unmount - should not cause issues
      act(() => {
        jest.advanceTimersByTime(35000);
      });

      // No errors should occur
    });
  });

  describe('Callback Integration', () => {
    it('should handle callback errors gracefully', () => {
      const faultyCallback = jest.fn(() => {
        throw new Error('Callback error');
      });
      
      const { result } = renderHook(() => 
        useGameLogic(mockQuestions, { 
          timeLimit: 30, 
          onGameComplete: faultyCallback,
          onTimeUp: faultyCallback,
          onAnswerSubmit: faultyCallback
        })
      );

      // Should not crash when callbacks throw errors
      act(() => {
        result.current.startGame();
        result.current.selectAnswer(0);
        result.current.submitAnswer();
      });

      expect(result.current.isGameActive).toBe(true);
      expect(faultyCallback).toHaveBeenCalled();
    });

    it('should provide detailed callback data', () => {
      const onAnswerSubmit = jest.fn();
      const onGameComplete = jest.fn();
      
      const { result } = renderHook(() => 
        useGameLogic(mockQuestions, { 
          timeLimit: 30, 
          onAnswerSubmit,
          onGameComplete
        })
      );

      act(() => {
        result.current.startGame();
      });

      // Answer first question
      act(() => {
        result.current.selectAnswer(0);
        result.current.submitAnswer();
      });

      expect(onAnswerSubmit).toHaveBeenCalledWith({
        questionId: '1',
        selectedAnswer: 0,
        correctAnswer: 0,
        isCorrect: true,
        timeElapsed: expect.any(Number),
        questionIndex: 0
      });

      // Complete game
      act(() => {
        result.current.nextQuestion();
        result.current.selectAnswer(1);
        result.current.submitAnswer();
        result.current.nextQuestion();
        result.current.selectAnswer(0);
        result.current.submitAnswer();
        result.current.completeGame();
      });

      expect(onGameComplete).toHaveBeenCalledWith({
        score: 2,
        totalQuestions: 3,
        timeElapsed: expect.any(Number),
        answeredQuestions: expect.arrayContaining([
          expect.objectContaining({
            questionId: expect.any(String),
            selectedAnswer: expect.any(Number),
            isCorrect: expect.any(Boolean),
            timeElapsed: expect.any(Number)
          })
        ])
      });
    });
  });

  describe('Edge Cases with Question Data', () => {
    it('should handle questions with missing or invalid data', () => {
      const invalidQuestions = [
        {
          id: '1',
          text: '',
          options: [],
          correctAnswer: 0,
          difficulty: 'easy',
          category: 'test'
        },
        {
          id: '2',
          text: 'Valid question',
          options: ['A', 'B'],
          correctAnswer: 5, // Invalid index
          difficulty: 'easy',
          category: 'test'
        }
      ];

      const { result } = renderHook(() => 
        useGameLogic(invalidQuestions, { timeLimit: 30 })
      );

      act(() => {
        result.current.startGame();
      });

      // Should handle gracefully
      expect(result.current.isGameActive).toBe(true);
      expect(result.current.currentQuestion).toBeDefined();
    });

    it('should handle questions with duplicate IDs', () => {
      const duplicateIdQuestions = [
        {
          id: 'duplicate',
          text: 'Question 1',
          options: ['A', 'B', 'C', 'D'],
          correctAnswer: 0,
          difficulty: 'easy',
          category: 'test'
        },
        {
          id: 'duplicate',
          text: 'Question 2',
          options: ['A', 'B', 'C', 'D'],
          correctAnswer: 1,
          difficulty: 'easy',
          category: 'test'
        }
      ];

      const { result } = renderHook(() => 
        useGameLogic(duplicateIdQuestions, { timeLimit: 30 })
      );

      act(() => {
        result.current.startGame();
        result.current.selectAnswer(0);
        result.current.submitAnswer();
        result.current.nextQuestion();
        result.current.selectAnswer(1);
        result.current.submitAnswer();
      });

      // Should handle duplicate IDs without crashing
      expect(result.current.answeredQuestions).toHaveLength(2);
    });
  });
});