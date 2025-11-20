# Interactive Subtitles Implementation

## Overview

This implementation adds interactive subtitle features to LangPlug, based on research from similar language learning projects. The system provides real-time word highlighting, hover-based translation, and intelligent vocabulary tracking.

## Features Implemented

### 1. Translation Cache Store (`useTranslationStore.ts`)

A Zustand-based persistent cache for word translations with 7-day TTL:

- **Offline support**: Translations cached locally in browser storage
- **Automatic expiration**: Entries expire after 7 days
- **Loading states**: Track ongoing translation requests
- **Error handling**: Per-word error tracking

**Usage:**
```typescript
import { useTranslationStore } from './store/useTranslationStore'

const { getWordTranslation, cacheTranslation, isWordLoading } = useTranslationStore()

// Check cache
const cached = getWordTranslation('hallo')

// Add to cache
cacheTranslation('hallo', 'hello', { level: 'A1', confidence: 1.0 })
```

### 2. Interactive Subtitle Hook (`useSubtitleHover.ts`)

React hook for hover-based word translation:

- **Automatic caching**: Fetches and caches translations on hover
- **Tooltip positioning**: Dynamic tooltip placement based on mouse position
- **Race condition handling**: Prevents stale translation updates
- **Backend integration**: Fetches from `/api/vocabulary/word-info/{word}`

**Usage:**
```typescript
import { useSubtitleHover } from './hooks/useSubtitleHover'

const { hoveredWord, translationData, onWordHover, onWordLeave, tooltipPosition } =
  useSubtitleHover('de')

// In component:
<span
  onMouseEnter={(e) => onWordHover('Hallo', e)}
  onMouseLeave={onWordLeave}
>
  Hallo
</span>

{translationData && (
  <div style={{ left: tooltipPosition.x, top: tooltipPosition.y }}>
    {translationData.translation}
  </div>
)}
```

### 3. Interactive Subtitle Component (`InteractiveSubtitle.tsx`)

Static subtitle component with hover translation:

- **Word tokenization**: Preserves German special characters (äöüß)
- **Known/unknown highlighting**: Green for known, orange for unknown words
- **Hover translation tooltip**: Shows translation, CEFR level, part of speech
- **Punctuation handling**: Separates words from punctuation

**Usage:**
```typescript
import InteractiveSubtitle from './components/InteractiveSubtitle'

const knownWords = new Set(['hallo', 'wie', 'geht'])

<InteractiveSubtitle
  text="Hallo, wie geht es dir?"
  language="de"
  knownWords={knownWords}
  showTranslation={true}
/>
```

### 4. Subtitle Sync Service (`subtitleSyncService.ts`)

Service for word-level timestamp generation and synchronization:

- **Word timestamp interpolation**: Distributes words evenly within segments
- **SRT parsing**: Converts SRT files to SubtitleSegment format
- **Active word detection**: Finds currently spoken word based on time
- **Navigation helpers**: Previous/next segment seeking

**Key Methods:**
```typescript
import { subtitleSyncService } from './services/subtitleSyncService'

// Parse SRT content
const segments = subtitleSyncService.parseSRT(srtContent)

// Get active word at timestamp
const activeWord = subtitleSyncService.getActiveWordAtTime(segments, currentTime)

// Get active segment
const segment = subtitleSyncService.getActiveSegmentAtTime(segments, currentTime)

// Navigation
const prev = subtitleSyncService.getPreviousSegment(segments, currentTime)
const next = subtitleSyncService.getNextSegment(segments, currentTime)
```

### 5. Synced Subtitle Display (`SyncedSubtitleDisplay.tsx`)

Real-time subtitle component with video synchronization:

- **50ms update interval**: 20 FPS highlighting for smooth transitions
- **Active word highlighting**: Currently spoken word lights up
- **Hover translation**: Same tooltip system as InteractiveSubtitle
- **Seek event handling**: Updates on video seek operations
- **Word click callbacks**: Trigger custom actions on word clicks

**Usage:**
```typescript
import SyncedSubtitleDisplay from './components/SyncedSubtitleDisplay'

const videoRef = useRef<HTMLVideoElement>(null)

<video ref={videoRef} src="/video.mp4" />

<SyncedSubtitleDisplay
  segments={segments}
  videoRef={videoRef}
  knownWords={knownWords}
  language="de"
  showTranslation={true}
  onWordClick={(word) => console.log('Clicked:', word)}
/>
```

### 6. Subtitle Seeking Hook (`useSubtitleSeek.ts`)

Navigation controls for subtitle-based video seeking:

- **Seek to word**: Jump to first occurrence of word
- **Seek to segment**: Navigate by segment index
- **Previous/next segment**: Keyboard navigation support
- **Seek to time**: Direct timestamp navigation

**Usage:**
```typescript
import { useSubtitleSeek } from './hooks/useSubtitleSeek'

const { seekToWord, seekPreviousSegment, seekNextSegment, seekToSegment } =
  useSubtitleSeek(videoRef, segments)

// Keyboard controls
useEffect(() => {
  const handleKey = (e: KeyboardEvent) => {
    if (e.code === 'ArrowLeft') seekPreviousSegment()
    if (e.code === 'ArrowRight') seekNextSegment()
  }
  window.addEventListener('keydown', handleKey)
  return () => window.removeEventListener('keydown', handleKey)
}, [])
```

## Styling

Two CSS files provide consistent styling:

### `InteractiveSubtitle.css`
- Hover effects with smooth transitions
- Known/unknown word color coding
- Floating translation tooltip
- Responsive font sizes
- Dark/light mode support

### `SyncedSubtitleDisplay.css`
- Active word pulsing effect
- Smooth highlight transitions
- Tooltip positioning
- Reduced motion support for accessibility

## Backend Integration

The system uses existing backend endpoints:

### `/api/vocabulary/word-info/{word}`
- **Method**: GET
- **Query params**: `language` (default: "de")
- **Returns**:
  ```json
  {
    "word": "Hallo",
    "lemma": "hallo",
    "level": "A1",
    "translations": ["Hello", "Hi"],
    "examples": ["Hallo, wie geht es dir?"]
  }
  ```
- **Authentication**: Not required

## Example Component

`InteractiveSubtitleExample.tsx` demonstrates complete integration:

- Video player with subtitle overlay
- Real-time word highlighting
- Keyboard navigation (←/→ for prev/next sentence)
- Segment list with click-to-seek
- Mode switching (static vs. synced)

## Integration into Existing Components

### LearningPlayer / ChunkedLearningPlayer

Add synced subtitles to existing video players:

```typescript
import SyncedSubtitleDisplay from './SyncedSubtitleDisplay'
import { subtitleSyncService } from '../services/subtitleSyncService'

// In component:
const [segments, setSegments] = useState<SubtitleSegment[]>([])

// Load SRT on mount
useEffect(() => {
  fetch(`/api/videos/${videoId}/subtitles.srt`)
    .then(res => res.text())
    .then(srt => {
      const parsed = subtitleSyncService.parseSRT(srt)
      setSegments(parsed)
    })
}, [videoId])

// Render over video
<div style={{ position: 'relative' }}>
  <video ref={videoRef} />
  <div style={{ position: 'absolute', bottom: 60, left: '50%', transform: 'translateX(-50%)' }}>
    <SyncedSubtitleDisplay
      segments={segments}
      videoRef={videoRef}
      knownWords={userKnownWords}
      language="de"
    />
  </div>
</div>
```

### VocabularyGame

Use InteractiveSubtitle for static text display:

```typescript
import InteractiveSubtitle from './InteractiveSubtitle'

<InteractiveSubtitle
  text={currentSentence}
  language="de"
  knownWords={learnedWords}
  showTranslation={true}
/>
```

## Performance Considerations

### Translation Cache
- **Cache size**: Unlimited (browser storage)
- **TTL**: 7 days (configurable in `useTranslationStore.ts`)
- **Pruning**: Automatic on app startup
- **Storage**: IndexedDB via Zustand persist middleware

### Highlight Update Rate
- **Interval**: 50ms (20 FPS)
- **CPU impact**: Low (simple timestamp comparison)
- **Optimization**: Uses `window.requestAnimationFrame` implicitly

### Network Requests
- **Caching**: All translations cached after first lookup
- **Debouncing**: Automatic via hover delay (no explicit debounce needed)
- **Race condition prevention**: Request tracking in `useSubtitleHover`

## Future Enhancements

### Phase 2 Features (from RESEARCH_FINDINGS.md)

1. **Parallel Transcription**
   - Implement chunked Whisper processing
   - 10x speed improvement for large videos
   - Background job status polling

2. **Spaced Repetition**
   - SM-2 algorithm for vocabulary review
   - Database schema for repetition tracking
   - Quiz generation with smart word selection

3. **Advanced Synchronization**
   - Forced alignment for precise word timestamps (Montreal Forced Aligner)
   - Confidence scores from Whisper
   - Multi-speaker detection and color coding

4. **Enhanced UI**
   - Sentence-by-sentence replay mode
   - Slow-motion playback for difficult words
   - Click word to add to practice list
   - Word frequency indicators

## Testing

### Manual Testing Checklist

- [ ] Hover over words shows translation tooltip
- [ ] Tooltip follows mouse cursor
- [ ] Known words display in green, unknown in orange
- [ ] Active word highlights during video playback
- [ ] Keyboard navigation (←/→) changes segments
- [ ] Click word in SyncedSubtitleDisplay triggers callback
- [ ] Translation cache persists after page reload
- [ ] Expired cache entries (>7 days) are removed
- [ ] SRT parsing handles various formats correctly
- [ ] Word tokenization preserves German characters (äöüß)

### Unit Test Recommendations

```typescript
// Test translation cache expiration
test('expired cache entries are removed', () => {
  const { cacheTranslation, getWordTranslation } = useTranslationStore.getState()

  // Mock Date.now() to simulate 8 days passing
  cacheTranslation('test', 'translation')
  // ... advance time ...
  expect(getWordTranslation('test')).toBeNull()
})

// Test word tokenization
test('tokenizes German text correctly', () => {
  const result = subtitleSyncService.parseSRT(germanSRT)
  expect(result[0].words).toContainEqual(
    expect.objectContaining({ word: 'Größe' })
  )
})

// Test active word detection
test('finds active word at timestamp', () => {
  const word = subtitleSyncService.getActiveWordAtTime(segments, 1.5)
  expect(word).not.toBeNull()
  expect(word!.word).toBe('Hallo')
})
```

## Files Created

### Frontend
```
src/frontend/src/
├── store/
│   └── useTranslationStore.ts          # Translation cache Zustand store
├── hooks/
│   ├── useSubtitleHover.ts             # Hover translation hook
│   └── useSubtitleSeek.ts              # Video seeking hook
├── services/
│   └── subtitleSyncService.ts          # Timestamp generation & sync
├── components/
│   ├── InteractiveSubtitle.tsx         # Static subtitle component
│   ├── InteractiveSubtitle.css         # Subtitle styles
│   ├── SyncedSubtitleDisplay.tsx       # Real-time synced component
│   ├── SyncedSubtitleDisplay.css       # Synced subtitle styles
│   └── examples/
│       └── InteractiveSubtitleExample.tsx  # Full demo
```

### Documentation
```
/
├── RESEARCH_FINDINGS.md               # Research analysis (7+ projects)
├── INTERACTIVE_SUBTITLES.md           # This file
```

## API Compatibility

This implementation uses existing LangPlug backend endpoints without modifications. The only requirement is that `/api/vocabulary/word-info/{word}` returns word information with translations.

## Browser Support

- **Chrome/Edge**: Full support
- **Firefox**: Full support
- **Safari**: Full support (requires Zustand persist polyfill)
- **Mobile**: Responsive, touch-optimized tooltips recommended

## Dependencies

- `zustand` - Already in project
- `zustand/middleware` - persist, devtools (already installed)

No additional dependencies required.

## Quick Start

1. Import components in your video player:
   ```typescript
   import SyncedSubtitleDisplay from './components/SyncedSubtitleDisplay'
   import { subtitleSyncService } from './services/subtitleSyncService'
   ```

2. Parse SRT file:
   ```typescript
   const segments = subtitleSyncService.parseSRT(srtContent)
   ```

3. Render over video:
   ```typescript
   <SyncedSubtitleDisplay
     segments={segments}
     videoRef={videoRef}
     knownWords={knownWords}
     language="de"
   />
   ```

4. Add keyboard controls (optional):
   ```typescript
   const { seekPreviousSegment, seekNextSegment } = useSubtitleSeek(videoRef, segments)

   useEffect(() => {
     const handleKey = (e: KeyboardEvent) => {
       if (e.code === 'ArrowLeft') seekPreviousSegment()
       if (e.code === 'ArrowRight') seekNextSegment()
     }
     window.addEventListener('keydown', handleKey)
     return () => window.removeEventListener('keydown', handleKey)
   }, [])
   ```

## License

Part of LangPlug project. See main LICENSE file.

## Authors

Implementation based on research findings from:
- language-learning-player (ratmirslv)
- React Speech Highlight Demo (albirrkarim)
- Fast Audio/Video Transcribe (mharrvic)

See `RESEARCH_FINDINGS.md` for full attribution.
