# ChunkedLearningPlayer Refactoring Guide

**File**: `src/components/ChunkedLearningPlayer.tsx`
**Current Size**: 1,301 lines (GOD COMPONENT 🔴)
**Target**: 7 focused components (< 200 lines each)
**Priority**: CRITICAL
**Effort**: 8 hours

---

## Problem

ChunkedLearningPlayer violates Single Responsibility Principle with 7+ responsibilities:

1. Video playback control
2. Subtitle rendering & synchronization
3. Vocabulary highlighting
4. Learning progress tracking
5. Player UI controls
6. Chunk navigation
7. WebSocket progress updates

---

## Refactoring Strategy

### New Component Structure

```
ChunkedLearningPlayer.tsx (Coordinator, ~150 lines)
├── VideoPlayer.tsx (~200 lines)
│   └── Handles video playback, seeking, buffering
├── SubtitleDisplay.tsx (~150 lines)
│   └── Renders timed subtitles
├── VocabularyHighlighter.tsx (~180 lines)
│   └── Highlights unknown words, tooltips
├── ProgressTracker.tsx (~120 lines)
│   └── Tracks learning metrics
├── PlayerControls.tsx (~100 lines)
│   └── Play/pause, speed, volume
├── ChunkNavigator.tsx (~150 lines)
│   └── Chunk selection, progress bar
└── hooks/
    ├── useVideoPlayback.ts (~80 lines)
    ├── useSubtitleSync.ts (~60 lines)
    └── useVocabularyTracking.ts (~70 lines)
```

---

## Step-by-Step Implementation

### Step 1: Extract Custom Hooks (2 hours)

#### `hooks/useVideoPlayback.ts`

```typescript
export const useVideoPlayback = (videoRef: RefObject<HTMLVideoElement>) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  const play = useCallback(() => {
    videoRef.current?.play();
    setIsPlaying(true);
  }, []);

  const pause = useCallback(() => {
    videoRef.current?.pause();
    setIsPlaying(false);
  }, []);

  const seek = useCallback((time: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = time;
    }
  }, []);

  return { isPlaying, currentTime, duration, play, pause, seek };
};
```

#### `hooks/useSubtitleSync.ts`

```typescript
export const useSubtitleSync = (currentTime: number, subtitles: Subtitle[]) => {
  const [currentSubtitle, setCurrentSubtitle] = useState<Subtitle | null>(null);

  useEffect(() => {
    const subtitle = subtitles.find(
      (sub) => currentTime >= sub.startTime && currentTime <= sub.endTime,
    );
    setCurrentSubtitle(subtitle || null);
  }, [currentTime, subtitles]);

  return { currentSubtitle };
};
```

---

### Step 2: Create Presentational Components (3 hours)

#### `VideoPlayer.tsx`

```typescript
interface VideoPlayerProps {
  videoUrl: string;
  onTimeUpdate: (time: number) => void;
  onEnded: () => void;
}

export const VideoPlayer = memo(({ videoUrl, onTimeUpdate, onEnded }: VideoPlayerProps) => {
  const videoRef = useRef<HTMLVideoElement>(null);

  const handleTimeUpdate = useCallback(() => {
    if (videoRef.current) {
      onTimeUpdate(videoRef.current.currentTime);
    }
  }, [onTimeUpdate]);

  return (
    <video
      ref={videoRef}
      src={videoUrl}
      onTimeUpdate={handleTimeUpdate}
      onEnded={onEnded}
    />
  );
});
```

#### `SubtitleDisplay.tsx`

```typescript
interface SubtitleDisplayProps {
  subtitle: Subtitle | null;
  onWordClick: (word: string) => void;
}

export const SubtitleDisplay = memo(({ subtitle, onWordClick }: SubtitleDisplayProps) => {
  if (!subtitle) return null;

  return (
    <SubtitleContainer>
      {subtitle.words.map((word, index) => (
        <Word key={index} onClick={() => onWordClick(word)}>
          {word}
        </Word>
      ))}
    </SubtitleContainer>
  );
});
```

---

### Step 3: Wire Components Together (2 hours)

#### `ChunkedLearningPlayer.tsx` (Coordinator)

```typescript
export const ChunkedLearningPlayer = ({ videoUrl, subtitles, vocabulary }: Props) => {
  const videoRef = useRef<HTMLVideoElement>(null);

  // Custom hooks for state management
  const { isPlaying, currentTime, duration, play, pause, seek } = useVideoPlayback(videoRef);
  const { currentSubtitle } = useSubtitleSync(currentTime, subtitles);
  const { trackWordView } = useVocabularyTracking();

  const handleWordClick = useCallback((word: string) => {
    trackWordView(word);
  }, [trackWordView]);

  return (
    <PlayerContainer>
      <VideoPlayer
        ref={videoRef}
        videoUrl={videoUrl}
        onTimeUpdate={setCurrentTime}
      />

      <SubtitleDisplay
        subtitle={currentSubtitle}
        onWordClick={handleWordClick}
      />

      <VocabularyHighlighter
        subtitle={currentSubtitle}
        vocabulary={vocabulary}
      />

      <PlayerControls
        isPlaying={isPlaying}
        onPlay={play}
        onPause={pause}
      />

      <ChunkNavigator
        chunks={chunks}
        currentChunk={currentChunk}
        onSeek={seek}
      />

      <ProgressTracker
        vocabulary={vocabulary}
        watchedTime={currentTime}
      />
    </PlayerContainer>
  );
};
```

---

### Step 4: Add Tests (1 hour)

```typescript
describe('ChunkedLearningPlayer', () => {
  it('should render all sub-components', () => {
    render(<ChunkedLearningPlayer {...props} />);
    expect(screen.getByRole('video')).toBeInTheDocument();
    expect(screen.getByTestId('subtitle-display')).toBeInTheDocument();
    expect(screen.getByTestId('player-controls')).toBeInTheDocument();
  });

  it('should sync subtitles with video time', async () => {
    render(<ChunkedLearningPlayer {...props} />);

    // Simulate video time update
    fireEvent.timeUpdate(screen.getByRole('video'), { currentTime: 10 });

    await waitFor(() => {
      expect(screen.getByText('Expected subtitle at 10s')).toBeInTheDocument();
    });
  });
});
```

---

## Performance Optimizations

### Apply React.memo to prevent unnecessary re-renders

```typescript
export const VideoPlayer = memo(VideoPlayerComponent);
export const SubtitleDisplay = memo(SubtitleDisplayComponent);
export const VocabularyHighlighter = memo(VocabularyHighlighterComponent);
```

### Use useCallback for event handlers

```typescript
const handlePlay = useCallback(() => {
  videoRef.current?.play();
}, []);

const handleWordClick = useCallback(
  (word: string) => {
    trackWordView(word);
  },
  [trackWordView],
);
```

### Use useMemo for expensive calculations

```typescript
const highlightedWords = useMemo(() => {
  return vocabulary.filter((word) => word.isUnknown);
}, [vocabulary]);
```

---

## Testing Strategy

### 1. Component Unit Tests

- Test each component in isolation
- Mock props and callbacks
- Verify rendering and interactions

### 2. Integration Tests

- Test component communication
- Verify data flow between components
- Test state management

### 3. Performance Tests

```typescript
it('should not re-render VideoPlayer when subtitle changes', () => {
  const { rerender } = render(<VideoPlayer {...props} />);
  const renderCount = 1;

  rerender(<VideoPlayer {...props} subtitle="New subtitle" />);
  // VideoPlayer should not re-render (memo'd)
  expect(renderCount).toBe(1);
});
```

---

## Success Criteria

✅ No component > 300 lines
✅ Each component has single responsibility
✅ 80%+ test coverage
✅ 50% reduction in re-renders (measured with React DevTools Profiler)
✅ No visual regressions
✅ Improved maintainability score

---

## Rollback Plan

If refactoring causes issues:

1. Keep old component as `ChunkedLearningPlayer.legacy.tsx`
2. Use feature flag to toggle between versions
3. Gradual rollout: 10% → 25% → 50% → 100% users

---

**Status**: Ready for implementation
**Priority**: CRITICAL
**Owner**: Frontend Team
**Estimated Effort**: 8 hours
