import { describe, it, expect, beforeEach } from 'vitest'
import { act } from '@testing-library/react'
import { useGameUIStore } from '../useGameUIStore'

describe('useGameUIStore', () => {
  beforeEach(() => {
    // Reset store to initial state
    act(() => {
      useGameUIStore.getState().reset()
    })
  })

  describe('initial state', () => {
    it('should have correct initial state', () => {
      const state = useGameUIStore.getState()

      expect(state.gameSession).toBeNull()
      expect(state.currentWordIndex).toBe(0)
      expect(state.showSubtitles).toBe(false)
      expect(state.isProcessing).toBe(false)
    })
  })

  describe('startGame', () => {
    it('should initialize game session with video path', () => {
      const store = useGameUIStore.getState()

      act(() => {
        store.startGame('/videos/dark/S01E01.mp4')
      })

      const { gameSession } = useGameUIStore.getState()

      expect(gameSession).toBeTruthy()
      expect(gameSession?.video_path).toBe('/videos/dark/S01E01.mp4')
      expect(gameSession?.current_segment).toBe(0)
      expect(gameSession?.segments).toEqual([])
      expect(gameSession?.user_progress).toEqual({})
      expect(gameSession?.completed).toBe(false)
    })

    it('should reset word index and flags when starting game', () => {
      const store = useGameUIStore.getState()

      // Set some state
      act(() => {
        store.setCurrentWordIndex(5)
        store.toggleSubtitles()
        store.setProcessing(true)
      })

      // Start new game
      act(() => {
        store.startGame('/videos/test.mp4')
      })

      const state = useGameUIStore.getState()

      expect(state.currentWordIndex).toBe(0)
      expect(state.showSubtitles).toBe(false)
      expect(state.isProcessing).toBe(false)
    })

    it('should replace existing game session', () => {
      const store = useGameUIStore.getState()

      act(() => {
        store.startGame('/videos/first.mp4')
      })

      const firstSession = useGameUIStore.getState().gameSession

      act(() => {
        store.startGame('/videos/second.mp4')
      })

      const secondSession = useGameUIStore.getState().gameSession

      expect(firstSession?.video_path).toBe('/videos/first.mp4')
      expect(secondSession?.video_path).toBe('/videos/second.mp4')
    })
  })

  describe('setCurrentWordIndex', () => {
    it('should update current word index', () => {
      const store = useGameUIStore.getState()

      act(() => {
        store.setCurrentWordIndex(5)
      })

      expect(useGameUIStore.getState().currentWordIndex).toBe(5)
    })

    it('should allow setting to zero', () => {
      const store = useGameUIStore.getState()

      act(() => {
        store.setCurrentWordIndex(10)
        store.setCurrentWordIndex(0)
      })

      expect(useGameUIStore.getState().currentWordIndex).toBe(0)
    })

    it('should handle large indices', () => {
      const store = useGameUIStore.getState()

      act(() => {
        store.setCurrentWordIndex(999)
      })

      expect(useGameUIStore.getState().currentWordIndex).toBe(999)
    })
  })

  describe('nextWord', () => {
    it('should increment word index by 1', () => {
      const store = useGameUIStore.getState()

      act(() => {
        store.nextWord()
      })

      expect(useGameUIStore.getState().currentWordIndex).toBe(1)
    })

    it('should increment multiple times', () => {
      const store = useGameUIStore.getState()

      act(() => {
        store.nextWord()
        store.nextWord()
        store.nextWord()
      })

      expect(useGameUIStore.getState().currentWordIndex).toBe(3)
    })

    it('should work after manual index set', () => {
      const store = useGameUIStore.getState()

      act(() => {
        store.setCurrentWordIndex(5)
        store.nextWord()
      })

      expect(useGameUIStore.getState().currentWordIndex).toBe(6)
    })
  })

  describe('toggleSubtitles', () => {
    it('should toggle subtitles from false to true', () => {
      const store = useGameUIStore.getState()

      act(() => {
        store.toggleSubtitles()
      })

      expect(useGameUIStore.getState().showSubtitles).toBe(true)
    })

    it('should toggle subtitles from true to false', () => {
      const store = useGameUIStore.getState()

      act(() => {
        store.toggleSubtitles()
        store.toggleSubtitles()
      })

      expect(useGameUIStore.getState().showSubtitles).toBe(false)
    })

    it('should toggle multiple times', () => {
      const store = useGameUIStore.getState()

      act(() => {
        store.toggleSubtitles() // true
        store.toggleSubtitles() // false
        store.toggleSubtitles() // true
      })

      expect(useGameUIStore.getState().showSubtitles).toBe(true)
    })
  })

  describe('nextSegment', () => {
    it('should increment segment and reset word index', () => {
      const store = useGameUIStore.getState()

      act(() => {
        store.startGame('/videos/test.mp4')
        store.setCurrentWordIndex(5)
        store.nextSegment()
      })

      const { gameSession, currentWordIndex } = useGameUIStore.getState()

      expect(gameSession?.current_segment).toBe(1)
      expect(currentWordIndex).toBe(0)
    })

    it('should do nothing if no game session exists', () => {
      const store = useGameUIStore.getState()

      act(() => {
        store.nextSegment()
      })

      const { gameSession, currentWordIndex } = useGameUIStore.getState()

      expect(gameSession).toBeNull()
      expect(currentWordIndex).toBe(0) // Should remain unchanged
    })

    it('should increment segment multiple times', () => {
      const store = useGameUIStore.getState()

      act(() => {
        store.startGame('/videos/test.mp4')
        store.nextSegment()
        store.nextSegment()
        store.nextSegment()
      })

      const { gameSession } = useGameUIStore.getState()

      expect(gameSession?.current_segment).toBe(3)
    })

    it('should preserve other session properties', () => {
      const store = useGameUIStore.getState()

      act(() => {
        store.startGame('/videos/test.mp4')
      })

      const initialSession = useGameUIStore.getState().gameSession

      act(() => {
        store.nextSegment()
      })

      const updatedSession = useGameUIStore.getState().gameSession

      expect(updatedSession?.video_path).toBe(initialSession?.video_path)
      expect(updatedSession?.segments).toEqual(initialSession?.segments)
      expect(updatedSession?.user_progress).toEqual(initialSession?.user_progress)
      expect(updatedSession?.completed).toBe(initialSession?.completed)
    })
  })

  describe('setProcessing', () => {
    it('should set processing to true', () => {
      const store = useGameUIStore.getState()

      act(() => {
        store.setProcessing(true)
      })

      expect(useGameUIStore.getState().isProcessing).toBe(true)
    })

    it('should set processing to false', () => {
      const store = useGameUIStore.getState()

      act(() => {
        store.setProcessing(true)
        store.setProcessing(false)
      })

      expect(useGameUIStore.getState().isProcessing).toBe(false)
    })

    it('should toggle processing state', () => {
      const store = useGameUIStore.getState()

      act(() => {
        store.setProcessing(true)
      })
      expect(useGameUIStore.getState().isProcessing).toBe(true)

      act(() => {
        store.setProcessing(false)
      })
      expect(useGameUIStore.getState().isProcessing).toBe(false)

      act(() => {
        store.setProcessing(true)
      })
      expect(useGameUIStore.getState().isProcessing).toBe(true)
    })
  })

  describe('resetGame', () => {
    it('should reset all game state to initial values', () => {
      const store = useGameUIStore.getState()

      // Set various state
      act(() => {
        store.startGame('/videos/test.mp4')
        store.setCurrentWordIndex(10)
        store.toggleSubtitles()
        store.setProcessing(true)
      })

      // Reset
      act(() => {
        store.resetGame()
      })

      const state = useGameUIStore.getState()

      expect(state.gameSession).toBeNull()
      expect(state.currentWordIndex).toBe(0)
      expect(state.showSubtitles).toBe(false)
      expect(state.isProcessing).toBe(false)
    })

    it('should be idempotent', () => {
      const store = useGameUIStore.getState()

      act(() => {
        store.startGame('/videos/test.mp4')
        store.resetGame()
        store.resetGame()
        store.resetGame()
      })

      const state = useGameUIStore.getState()

      expect(state.gameSession).toBeNull()
      expect(state.currentWordIndex).toBe(0)
    })
  })

  describe('reset', () => {
    it('should reset all state to initial values', () => {
      const store = useGameUIStore.getState()

      // Set various state
      act(() => {
        store.startGame('/videos/test.mp4')
        store.setCurrentWordIndex(15)
        store.toggleSubtitles()
        store.setProcessing(true)
      })

      // Reset
      act(() => {
        store.reset()
      })

      const state = useGameUIStore.getState()

      expect(state.gameSession).toBeNull()
      expect(state.currentWordIndex).toBe(0)
      expect(state.showSubtitles).toBe(false)
      expect(state.isProcessing).toBe(false)
    })

    it('should work identically to resetGame', () => {
      const store = useGameUIStore.getState()

      act(() => {
        store.startGame('/videos/test.mp4')
      })

      act(() => {
        store.reset()
      })

      const stateAfterReset = useGameUIStore.getState()

      act(() => {
        store.startGame('/videos/test.mp4')
      })

      act(() => {
        store.resetGame()
      })

      const stateAfterResetGame = useGameUIStore.getState()

      expect(stateAfterReset).toEqual(stateAfterResetGame)
    })
  })

  describe('integration scenarios', () => {
    it('should handle complete game flow', () => {
      const store = useGameUIStore.getState()

      // Start game
      act(() => {
        store.startGame('/videos/dark/S01E01.mp4')
      })
      expect(useGameUIStore.getState().gameSession?.video_path).toBe('/videos/dark/S01E01.mp4')

      // Advance through words
      act(() => {
        store.nextWord()
        store.nextWord()
        store.nextWord()
      })
      expect(useGameUIStore.getState().currentWordIndex).toBe(3)

      // Show subtitles
      act(() => {
        store.toggleSubtitles()
      })
      expect(useGameUIStore.getState().showSubtitles).toBe(true)

      // Process next segment
      act(() => {
        store.setProcessing(true)
      })
      expect(useGameUIStore.getState().isProcessing).toBe(true)

      act(() => {
        store.nextSegment()
        store.setProcessing(false)
      })

      const finalState = useGameUIStore.getState()
      expect(finalState.gameSession?.current_segment).toBe(1)
      expect(finalState.currentWordIndex).toBe(0) // Reset on new segment
      expect(finalState.isProcessing).toBe(false)
    })

    it('should handle rapid state changes', () => {
      const store = useGameUIStore.getState()

      act(() => {
        store.startGame('/videos/test.mp4')
        store.nextWord()
        store.toggleSubtitles()
        store.setProcessing(true)
        store.nextWord()
        store.toggleSubtitles()
        store.setProcessing(false)
        store.nextSegment()
        store.toggleSubtitles()
      })

      const state = useGameUIStore.getState()

      expect(state.gameSession?.current_segment).toBe(1)
      expect(state.currentWordIndex).toBe(0) // Reset on segment change
      expect(state.showSubtitles).toBe(true) // Toggled 3 times (odd)
      expect(state.isProcessing).toBe(false)
    })
  })
})
