import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { VocabularyGame } from '../VocabularyGame';
import { useGameStore } from '../../store/useGameStore';

// Mock the game store
vi.mock('../../store/useGameStore');
const mockUseGameStore = vi.mocked(useGameStore);

// Mock framer-motion to avoid animation issues in tests
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    button: ({ children, ...props }: any) => <button {...props}>{children}</button>,
  },
  AnimatePresence: ({ children }: any) => children,
}));

const mockWords = [
  { id: '1', word: 'Hallo', translation: 'Hello', difficulty: 1 },
  { id: '2', word: 'Tschüss', translation: 'Goodbye', difficulty: 1 },
  { id: '3', word: 'Danke', translation: 'Thank you', difficulty: 2 }
];

const mockGameState = {
  currentWord: mockWords[0],
  score: 0,
  streak: 0,
  totalWords: mockWords.length,
  completedWords: 0,
  isGameActive: true,
  gameMode: 'swipe' as const,
};

const mockGameActions = {
  markWordKnown: vi.fn(),
  markWordUnknown: vi.fn(),
  nextWord: vi.fn(),
  resetGame: vi.fn(),
  setGameMode: vi.fn(),
};

describe('VocabularyGame Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseGameStore.mockReturnValue({
      ...mockGameState,
      ...mockGameActions,
    });
  });

  it('renders current word', () => {
    render(<VocabularyGame words={mockWords} />);
    expect(screen.getByText('Hallo')).toBeInTheDocument();
  });

  it('displays game progress', () => {
    render(<VocabularyGame words={mockWords} />);
    expect(screen.getByText(/0.*3/)).toBeInTheDocument(); // Progress indicator
  });

  it('shows translation on reveal', () => {
    render(<VocabularyGame words={mockWords} />);
    
    const revealButton = screen.getByText(/reveal/i);
    fireEvent.click(revealButton);
    
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });

  it('marks word as known when know button is clicked', () => {
    render(<VocabularyGame words={mockWords} />);
    
    const knowButton = screen.getByText(/know/i);
    fireEvent.click(knowButton);
    
    expect(mockGameActions.markWordKnown).toHaveBeenCalledWith('1');
  });

  it('marks word as unknown when dont know button is clicked', () => {
    render(<VocabularyGame words={mockWords} />);
    
    const dontKnowButton = screen.getByText(/don.*t know/i);
    fireEvent.click(dontKnowButton);
    
    expect(mockGameActions.markWordUnknown).toHaveBeenCalledWith('1');
  });

  it('displays score and streak', () => {
    const gameStateWithScore = {
      ...mockGameState,
      score: 150,
      streak: 5,
    };
    
    mockUseGameStore.mockReturnValue({
      ...gameStateWithScore,
      ...mockGameActions,
    });
    
    render(<VocabularyGame words={mockWords} />);
    
    expect(screen.getByText(/150/)).toBeInTheDocument(); // Score
    expect(screen.getByText(/5/)).toBeInTheDocument(); // Streak
  });

  it('shows game completion when all words are done', () => {
    const completedGameState = {
      ...mockGameState,
      isGameActive: false,
      completedWords: mockWords.length,
    };
    
    mockUseGameStore.mockReturnValue({
      ...completedGameState,
      ...mockGameActions,
    });
    
    render(<VocabularyGame words={mockWords} />);
    
    expect(screen.getByText(/completed/i)).toBeInTheDocument();
  });

  it('allows game reset', () => {
    const completedGameState = {
      ...mockGameState,
      isGameActive: false,
      completedWords: mockWords.length,
    };
    
    mockUseGameStore.mockReturnValue({
      ...completedGameState,
      ...mockGameActions,
    });
    
    render(<VocabularyGame words={mockWords} />);
    
    const resetButton = screen.getByText(/play again/i);
    fireEvent.click(resetButton);
    
    expect(mockGameActions.resetGame).toHaveBeenCalled();
  });
});