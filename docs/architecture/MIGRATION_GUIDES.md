# Migration Guides - LangPlug Architecture Improvements

**Version**: 1.0
**Date**: 2025-10-02
**Status**: Active Migration Guides
**Target Timeline**: Phased implementation over 3-6 months

---

## Overview

This document provides step-by-step migration guides for implementing the architecture improvements identified in the comprehensive architecture assessment. Each migration is designed to be applied incrementally with minimal disruption to ongoing development.

---

## Table of Contents

1. [Migration 1: Remove @lru_cache State Pollution](#migration-1-remove-lru_cache-state-pollution)
2. [Migration 2: Apply Transaction Boundaries](#migration-2-apply-transaction-boundaries)
3. [Migration 3: Implement Code Splitting](#migration-3-implement-code-splitting)
4. [Migration 4: Refactor ChunkedLearningPlayer](#migration-4-refactor-chunkedlearningplayer)
5. [Migration 5: Redis Caching Layer](#migration-5-redis-caching-layer)
6. [Migration 6: Celery Async Processing](#migration-6-celery-async-processing)
7. [Migration 7: Security Hardening](#migration-7-security-hardening)
8. [Migration 8: Frontend Performance Optimization](#migration-8-frontend-performance-optimization)

---

## Migration 1: Remove @lru_cache State Pollution

### Priority: CRITICAL ✅ COMPLETED

### Timeline: 1 hour

### Risk: Low (improves test reliability)

### Problem

Services cached with `@lru_cache` persist state across test runs, causing test isolation failures where tests pass individually but fail in the full suite.

### Solution Applied

**Files Modified:**

- `Backend/core/service_dependencies.py` - Removed `@lru_cache` from `get_translation_service()`
- `Backend/core/task_dependencies.py` - Removed cache clearing logic
- `Backend/tests/conftest.py` - Updated test fixture

### Verification Steps

```bash
# Run full test suite to verify isolation
cd Backend
./api_venv/Scripts/activate
pytest tests/unit/ -v

# Run tests in random order to catch state pollution
pytest tests/unit/ --random-order

# Run specific tests multiple times
pytest tests/unit/services/test_translation_service.py --count=10
```

### Expected Outcome

- ✅ All tests pass individually
- ✅ All tests pass in full suite
- ✅ Tests pass in random order
- ✅ No "cached service returned wrong instance" errors

### Rollback Plan

If issues arise, restore the `@lru_cache` decorator but add this fixture to `conftest.py`:

```python
@pytest.fixture(autouse=True)
def clear_service_cache():
    """Clear lru_cache between tests"""
    from core.service_dependencies import get_translation_service
    if hasattr(get_translation_service, 'cache_clear'):
        get_translation_service.cache_clear()
    yield
    if hasattr(get_translation_service, 'cache_clear'):
        get_translation_service.cache_clear()
```

---

## Migration 2: Apply Transaction Boundaries

### Priority: CRITICAL

### Timeline: 4-6 hours

### Risk: Medium (requires database testing)

### Problem

Multi-step database operations lack atomic transaction boundaries, risking partial commits when operations fail mid-process.

### Pre-Migration Checklist

- [ ] Review `Backend/docs/TRANSACTION_BOUNDARIES_FIX.md`
- [ ] Verify transaction infrastructure exists at `Backend/core/transaction.py`
- [ ] Identify all multi-step database operations in your codebase
- [ ] Create test database backup
- [ ] Schedule migration during low-traffic window

### Step-by-Step Migration

#### Step 1: Test Transaction Infrastructure (15 minutes)

```bash
cd Backend
./api_venv/Scripts/activate

# Run transaction infrastructure tests
pytest tests/unit/core/test_transaction.py -v
```

Create test file if it doesn't exist:

```python
# tests/unit/core/test_transaction.py
import pytest
from core.transaction import transactional
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_transactional_decorator_commits_on_success(db_session):
    """Verify transaction commits when no errors occur"""
    @transactional
    async def create_test_record(session: AsyncSession):
        # Your test logic here
        pass

    await create_test_record(db_session)
    # Add assertions to verify commit

@pytest.mark.asyncio
async def test_transactional_decorator_rolls_back_on_error(db_session):
    """Verify transaction rolls back when error occurs"""
    @transactional
    async def failing_operation(session: AsyncSession):
        # Create record
        # Then raise exception
        raise ValueError("Simulated failure")

    with pytest.raises(ValueError):
        await failing_operation(db_session)

    # Verify no data persisted
```

#### Step 2: Apply to Critical Files (Phase 1 - 2 hours)

**File: `Backend/services/processing/chunk_processor.py`**

```python
# BEFORE
class ChunkProcessingService:
    async def process_chunk(
        self,
        video_path: str,
        start_time: float,
        end_time: float,
        user_id: int,
        task_id: str,
        task_progress: dict,
    ):
        # 6-step pipeline with no transaction
        chunk = await self.create_chunk_record(...)
        transcription = await self.transcribe_audio(...)
        vocabulary = await self.extract_vocabulary(...)
        translation = await self.translate_segments(...)
        await self.save_results(...)
        await self.update_status(...)

# AFTER
from core.transaction import transactional

class ChunkProcessingService:
    @transactional
    async def process_chunk(
        self,
        video_path: str,
        start_time: float,
        end_time: float,
        user_id: int,
        task_id: str,
        task_progress: dict,
        session: AsyncSession,  # Add session parameter
    ):
        # Same 6-step pipeline, now atomic
        chunk = await self.create_chunk_record(..., session=session)
        transcription = await self.transcribe_audio(..., session=session)
        vocabulary = await self.extract_vocabulary(..., session=session)
        translation = await self.translate_segments(..., session=session)
        await self.save_results(..., session=session)
        await self.update_status(..., session=session)
```

**Important**: Update all method calls to pass `session` parameter:

```python
# In repository methods
async def create(self, data: dict, session: AsyncSession):
    obj = Model(**data)
    session.add(obj)
    await session.flush()  # Don't commit - let decorator handle it
    return obj
```

**File: `Backend/services/processing/chunk_handler.py`**

Apply same pattern to multi-step chunk operations:

- `handle_chunk_completion()`
- `merge_chunk_results()`
- `cleanup_failed_chunks()`

**File: `Backend/services/vocabulary/vocabulary_sync_service.py`**

Apply to vocabulary synchronization methods:

- `sync_user_vocabulary()`
- `bulk_update_vocabulary_status()`
- `merge_vocabulary_from_video()`

#### Step 3: Test Each Migration (1 hour)

After applying transactions to each file:

```bash
# Test the specific service
pytest tests/unit/services/test_chunk_processor.py -v

# Test rollback behavior
pytest tests/integration/test_transaction_rollback.py -v

# Run full test suite
pytest tests/unit/ tests/integration/ -v
```

Create rollback test:

```python
# tests/integration/test_transaction_rollback.py
@pytest.mark.asyncio
async def test_chunk_processing_rolls_back_on_transcription_failure(db_session):
    """Verify no data persists when transcription fails"""
    service = ChunkProcessingService(db_session)

    with pytest.raises(TranscriptionError):
        await service.process_chunk(
            video_path="/invalid/path",
            start_time=0,
            end_time=300,
            user_id=1,
            task_id="test-rollback",
            task_progress={},
            session=db_session,
        )

    # Verify NO chunk records exist
    result = await db_session.execute(
        select(Chunk).where(Chunk.task_id == "test-rollback")
    )
    chunks = result.scalars().all()
    assert len(chunks) == 0, "Rollback should remove all records"
```

#### Step 4: Apply to High Priority Files (Phase 2 - 2 hours)

- `Backend/services/authservice/auth_service.py`
  - User registration
  - Profile updates
  - Password resets

- All repository methods with multiple operations

#### Step 5: Monitoring and Validation (30 minutes)

```bash
# Check database for orphaned records
# Run this query before and after migration

# PostgreSQL
SELECT
    table_name,
    COUNT(*) as records
FROM information_schema.tables
WHERE table_schema = 'public'
GROUP BY table_name;

# Look for records with:
# - status = 'processing' older than 1 hour
# - Foreign keys pointing to non-existent records
# - Duplicate records created in same second
```

### Common Issues and Solutions

**Issue 1: "Session is already in a transaction"**

```python
# WRONG - Session already has transaction
async with session.begin():  # Don't do this
    await transactional_method(session)

# RIGHT - Let decorator manage transactions
await transactional_method(session)
```

**Issue 2: "Cannot commit, session in nested transaction"**

```python
# WRONG - Don't commit inside transactional methods
async def create_record(self, data, session):
    obj = Model(**data)
    session.add(obj)
    await session.commit()  # Don't do this!

# RIGHT - Just flush, let decorator commit
async def create_record(self, data, session):
    obj = Model(**data)
    session.add(obj)
    await session.flush()  # Flushes to DB without committing
    return obj
```

### Rollback Plan

If transactions cause issues:

1. Remove `@transactional` decorator from affected methods
2. Add feature flag to disable transactions:

```python
# core/config.py
class Settings:
    enable_transactions: bool = Field(default=True, env="ENABLE_TRANSACTIONS")

# core/transaction.py
def transactional(func):
    if not settings.enable_transactions:
        return func  # Bypass transaction management
    # ... existing code
```

3. Deploy with `ENABLE_TRANSACTIONS=false`
4. Monitor for orphaned records
5. Re-enable once issues resolved

---

## Migration 3: Implement Code Splitting

### Priority: HIGH ✅ COMPLETED

### Timeline: 2 hours

### Risk: Low (improves performance)

### Problem

Frontend bundle size is 2.5MB, causing slow initial page load (3-5 seconds on 3G).

### Solution Applied

**Files Modified:**

- `Frontend/src/App.tsx` - Implemented React.lazy() for route-based code splitting

### Verification Steps

```bash
cd Frontend

# Build production bundle
npm run build

# Check bundle sizes
ls -lh dist/assets/*.js

# Verify lazy loading in browser
# 1. Open DevTools → Network tab
# 2. Navigate to /login
# 3. Verify only login chunk loads
# 4. Navigate to /learn/:series/:episode
# 5. Verify learning chunk loads on demand
```

### Expected Bundle Sizes

| Chunk              | Before | After | Reduction |
| ------------------ | ------ | ----- | --------- |
| Main bundle        | 2.5MB  | 800KB | 68%       |
| Login chunk        | -      | 120KB | (new)     |
| Video player chunk | -      | 650KB | (new)     |
| Vocabulary chunk   | -      | 180KB | (new)     |

### Rollback Plan

If lazy loading causes issues, revert to synchronous imports:

```typescript
// Change FROM lazy imports
const LoginForm = lazy(() => import("@/components/auth/LoginForm"));

// Change TO synchronous imports
import { LoginForm } from "@/components/auth/LoginForm";

// Remove Suspense wrapper
// <Suspense fallback={<Loading />}> → Remove this
```

---

## Migration 4: Refactor ChunkedLearningPlayer

### Priority: HIGH

### Timeline: 8 hours (1 day)

### Risk: Medium (complex refactoring)

### Problem

`ChunkedLearningPlayer.tsx` is 1,301 lines (God component) with 7+ responsibilities, making it hard to maintain and test.

### Pre-Migration Checklist

- [ ] Review `Frontend/docs/CHUNKED_LEARNING_PLAYER_REFACTORING_GUIDE.md`
- [ ] Create feature branch: `git checkout -b refactor/chunked-learning-player`
- [ ] Take snapshot of current player functionality
- [ ] Write integration test for full player workflow
- [ ] Allocate 8 hours for refactoring

### Step-by-Step Migration

#### Step 1: Extract Custom Hooks (2 hours)

Create three custom hooks to extract state management:

```typescript
// src/hooks/useVideoPlayback.ts
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

```typescript
// src/hooks/useSubtitleSync.ts
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

```typescript
// src/hooks/useVocabularyTracking.ts
export const useVocabularyTracking = () => {
  const [viewedWords, setViewedWords] = useState<Set<string>>(new Set());

  const trackWordView = useCallback((word: string) => {
    setViewedWords((prev) => new Set(prev).add(word));
    // Call API to track word view
  }, []);

  return { viewedWords, trackWordView };
};
```

**Test each hook:**

```typescript
// src/hooks/__tests__/useVideoPlayback.test.ts
import { renderHook, act } from "@testing-library/react";
import { useVideoPlayback } from "../useVideoPlayback";

describe("useVideoPlayback", () => {
  it("should play and pause video", () => {
    const videoRef = { current: document.createElement("video") };
    const { result } = renderHook(() => useVideoPlayback(videoRef));

    act(() => {
      result.current.play();
    });
    expect(result.current.isPlaying).toBe(true);

    act(() => {
      result.current.pause();
    });
    expect(result.current.isPlaying).toBe(false);
  });
});
```

#### Step 2: Create Presentational Components (3 hours)

Extract 7 focused components:

**1. VideoPlayer.tsx** (~200 lines)

```typescript
interface VideoPlayerProps {
  videoUrl: string;
  onTimeUpdate: (time: number) => void;
  onEnded: () => void;
}

export const VideoPlayer = memo(({
  videoUrl,
  onTimeUpdate,
  onEnded
}: VideoPlayerProps) => {
  const videoRef = useRef<HTMLVideoElement>(null);

  const handleTimeUpdate = useCallback(() => {
    if (videoRef.current) {
      onTimeUpdate(videoRef.current.currentTime);
    }
  }, [onTimeUpdate]);

  return (
    <VideoContainer>
      <video
        ref={videoRef}
        src={videoUrl}
        onTimeUpdate={handleTimeUpdate}
        onEnded={onEnded}
      />
    </VideoContainer>
  );
});
```

**2. SubtitleDisplay.tsx** (~150 lines)
**3. VocabularyHighlighter.tsx** (~180 lines)
**4. ProgressTracker.tsx** (~120 lines)
**5. PlayerControls.tsx** (~100 lines)
**6. ChunkNavigator.tsx** (~150 lines)

#### Step 3: Wire Components Together (2 hours)

Update main coordinator component:

```typescript
// src/components/ChunkedLearningPlayer.tsx (NEW VERSION - ~150 lines)
export const ChunkedLearningPlayer = ({
  videoUrl,
  subtitles,
  vocabulary
}: Props) => {
  const videoRef = useRef<HTMLVideoElement>(null);

  // Custom hooks for state management
  const { isPlaying, currentTime, duration, play, pause, seek } =
    useVideoPlayback(videoRef);
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
        onTimeUpdate={(time) => {/* update time */}}
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

#### Step 4: Add Tests (1 hour)

```typescript
// src/components/__tests__/ChunkedLearningPlayer.test.tsx
describe('ChunkedLearningPlayer', () => {
  it('should render all sub-components', () => {
    render(<ChunkedLearningPlayer {...mockProps} />);

    expect(screen.getByRole('video')).toBeInTheDocument();
    expect(screen.getByTestId('subtitle-display')).toBeInTheDocument();
    expect(screen.getByTestId('player-controls')).toBeInTheDocument();
    expect(screen.getByTestId('vocabulary-highlighter')).toBeInTheDocument();
  });

  it('should sync subtitles with video time', async () => {
    render(<ChunkedLearningPlayer {...mockProps} />);

    // Simulate video time update to 10 seconds
    fireEvent.timeUpdate(screen.getByRole('video'), {
      target: { currentTime: 10 }
    });

    await waitFor(() => {
      expect(screen.getByText('Expected subtitle at 10s')).toBeInTheDocument();
    });
  });

  it('should track vocabulary word views', async () => {
    const mockTrackView = vi.fn();
    render(<ChunkedLearningPlayer {...mockProps} onWordView={mockTrackView} />);

    await userEvent.click(screen.getByText('Hund'));

    expect(mockTrackView).toHaveBeenCalledWith('Hund');
  });
});
```

### Validation Checklist

- [ ] All 7 components are < 300 lines
- [ ] Test coverage > 80% for each component
- [ ] No visual regressions (screenshot tests)
- [ ] React DevTools Profiler shows 50% fewer re-renders
- [ ] All existing features work identically
- [ ] Performance is same or better (measure with Lighthouse)

### Performance Measurement

```bash
# Before refactoring
npm run build
npx lighthouse http://localhost:5173/learn/superstore/s01e01 \
  --output html --output-path ./before-refactor.html

# After refactoring
npm run build
npx lighthouse http://localhost:5173/learn/superstore/s01e01 \
  --output html --output-path ./after-refactor.html

# Compare scores - Performance should be >= before
```

### Rollback Plan

1. Keep old component as `ChunkedLearningPlayer.legacy.tsx`
2. Use feature flag:

```typescript
// src/components/ChunkedLearningPage.tsx
import { ChunkedLearningPlayer } from './ChunkedLearningPlayer';
import { ChunkedLearningPlayer as LegacyPlayer } from './ChunkedLearningPlayer.legacy';

const USE_NEW_PLAYER = import.meta.env.VITE_USE_NEW_PLAYER === 'true';

export const ChunkedLearningPage = () => {
  const Player = USE_NEW_PLAYER ? ChunkedLearningPlayer : LegacyPlayer;
  return <Player {...props} />;
};
```

3. Gradual rollout:
   - Week 1: 10% of users (`Math.random() < 0.1`)
   - Week 2: 25% of users
   - Week 3: 50% of users
   - Week 4: 100% of users

4. If issues detected, set `VITE_USE_NEW_PLAYER=false`

---

## Migration 5: Redis Caching Layer

### Priority: HIGH

### Timeline: 1 week (5 days)

### Risk: Medium (new infrastructure dependency)

### Problem

API response times average 180ms (p95), with repeated expensive operations (translations, vocabulary lookups).

### Pre-Migration Checklist

- [ ] Review `docs/architecture/PHASE2_INFRASTRUCTURE_SETUP.md`
- [ ] Provision Redis instance (development: Docker, production: AWS ElastiCache)
- [ ] Update deployment pipeline to include Redis
- [ ] Plan cache invalidation strategy
- [ ] Allocate 1 week for implementation and testing

### Step-by-Step Migration

#### Day 1: Setup Redis Infrastructure (4 hours)

**Development Environment:**

```yaml
# docker-compose.redis.yml
version: "3.8"
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru

volumes:
  redis_data:
```

```bash
# Start Redis
docker-compose -f docker-compose.redis.yml up -d

# Test connection
docker exec -it langplug-redis redis-cli PING
# Should return: PONG
```

**Backend Configuration:**

```python
# Backend/core/config.py
class Settings:
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    redis_enabled: bool = Field(default=True, env="REDIS_ENABLED")
    redis_ttl_default: int = Field(default=3600, env="REDIS_TTL_DEFAULT")  # 1 hour
```

**Install Dependencies:**

```bash
cd Backend
./api_venv/Scripts/activate
pip install redis[hiredis]==5.0.1
pip freeze > requirements.txt
```

#### Day 2: Implement Caching Decorator (4 hours)

```python
# Backend/core/caching.py
import json
import hashlib
import redis.asyncio as redis
from functools import wraps
from typing import Callable, Any
from core.config import settings
import logging

logger = logging.getLogger(__name__)

# Global Redis client
_redis_client: redis.Redis | None = None

async def get_redis_client() -> redis.Redis:
    """Get or create Redis client"""
    global _redis_client
    if _redis_client is None:
        _redis_client = await redis.Redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
    return _redis_client

def cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate cache key from function arguments"""
    key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
    return hashlib.md5(key_data.encode()).hexdigest()

def cached(ttl: int = None, key_prefix: str = ""):
    """
    Cache decorator with TTL.

    Args:
        ttl: Time-to-live in seconds (default: settings.redis_ttl_default)
        key_prefix: Prefix for cache key

    Example:
        @cached(ttl=3600, key_prefix="vocabulary")
        async def get_vocabulary_word(word_id: int):
            return await repo.get_by_id(word_id)
    """
    if ttl is None:
        ttl = settings.redis_ttl_default

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            if not settings.redis_enabled:
                return await func(*args, **kwargs)

            # Generate cache key
            cache_key_str = cache_key(f"{key_prefix}:{func.__name__}", *args, **kwargs)

            try:
                redis_client = await get_redis_client()

                # Check cache
                cached_value = await redis_client.get(cache_key_str)
                if cached_value is not None:
                    logger.debug(f"Cache hit for {func.__name__}: {cache_key_str}")
                    return json.loads(cached_value)

                # Cache miss - compute value
                logger.debug(f"Cache miss for {func.__name__}: {cache_key_str}")
                result = await func(*args, **kwargs)

                # Store in cache
                await redis_client.setex(
                    cache_key_str,
                    ttl,
                    json.dumps(result, default=str)
                )

                return result

            except redis.RedisError as e:
                logger.error(f"Redis error in {func.__name__}: {e}")
                # Fallback to direct execution if Redis fails
                return await func(*args, **kwargs)

        return wrapper
    return decorator

async def invalidate_cache(pattern: str):
    """Invalidate all cache keys matching pattern"""
    if not settings.redis_enabled:
        return

    redis_client = await get_redis_client()
    keys = await redis_client.keys(pattern)
    if keys:
        await redis_client.delete(*keys)
        logger.info(f"Invalidated {len(keys)} cache keys matching {pattern}")
```

**Test Caching:**

```python
# tests/unit/core/test_caching.py
import pytest
from core.caching import cached, invalidate_cache

@pytest.mark.asyncio
async def test_cached_decorator_stores_result():
    """Verify caching decorator stores and retrieves results"""
    call_count = 0

    @cached(ttl=60, key_prefix="test")
    async def expensive_operation(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * 2

    # First call - cache miss
    result1 = await expensive_operation(5)
    assert result1 == 10
    assert call_count == 1

    # Second call - cache hit
    result2 = await expensive_operation(5)
    assert result2 == 10
    assert call_count == 1  # Function not called again

@pytest.mark.asyncio
async def test_cache_invalidation():
    """Verify cache invalidation clears cached values"""
    @cached(ttl=60, key_prefix="test")
    async def get_data() -> str:
        return "data"

    # Cache the result
    await get_data()

    # Invalidate
    await invalidate_cache("test:*")

    # Should call function again
    result = await get_data()
    assert result == "data"
```

#### Day 3: Apply Caching to Services (6 hours)

**Vocabulary Service:**

```python
# Backend/services/vocabulary/vocabulary_service.py
from core.caching import cached, invalidate_cache

class VocabularyService:
    @cached(ttl=3600, key_prefix="vocabulary:word")
    async def get_vocabulary_word(self, word_id: int) -> dict:
        """Get vocabulary word (cached for 1 hour)"""
        return await self.repo.get_by_id(word_id)

    @cached(ttl=86400, key_prefix="vocabulary:level")
    async def get_vocabulary_by_level(self, level: str, user_id: int) -> list:
        """Get vocabulary by level (cached for 24 hours)"""
        return await self.repo.get_by_level(level, user_id)

    async def update_vocabulary_status(self, word_id: int, status: str):
        """Update vocabulary status and invalidate cache"""
        await self.repo.update(word_id, {"status": status})
        # Invalidate cache for this word and user's level lists
        await invalidate_cache(f"vocabulary:word:*:{word_id}:*")
        await invalidate_cache(f"vocabulary:level:*")
```

**Translation Service:**

```python
# Backend/services/translation/translation_service.py
from core.caching import cached

class TranslationService:
    @cached(ttl=86400, key_prefix="translation")
    async def translate_text(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """Translate text (cached for 24 hours - translations don't change)"""
        return await self._perform_translation(text, source_lang, target_lang)
```

**Video Metadata Service:**

```python
# Backend/services/video/video_metadata_service.py
from core.caching import cached, invalidate_cache

class VideoMetadataService:
    @cached(ttl=3600, key_prefix="video:metadata")
    async def get_video_metadata(self, video_id: int) -> dict:
        """Get video metadata (cached for 1 hour)"""
        return await self.repo.get_video_with_relations(video_id)

    @cached(ttl=7200, key_prefix="video:list")
    async def list_videos_for_user(self, user_id: int) -> list:
        """List user's videos (cached for 2 hours)"""
        return await self.repo.list_by_user(user_id)

    async def update_video_progress(self, video_id: int, progress: float):
        """Update progress and invalidate caches"""
        await self.repo.update_progress(video_id, progress)
        await invalidate_cache(f"video:metadata:*:{video_id}:*")
        await invalidate_cache(f"video:list:*")
```

#### Day 4: Integration Testing (4 hours)

```python
# tests/integration/test_caching_integration.py
import pytest
from services.vocabulary.vocabulary_service import VocabularyService

@pytest.mark.asyncio
async def test_vocabulary_caching_reduces_db_queries(db_session, mock_redis):
    """Verify caching reduces database queries"""
    service = VocabularyService(db_session)

    # Track DB query count
    query_count = 0

    # First call - DB query
    result1 = await service.get_vocabulary_word(1)
    query_count = db_session.execute.call_count

    # Second call - should use cache
    result2 = await service.get_vocabulary_word(1)
    assert db_session.execute.call_count == query_count  # No new queries

    assert result1 == result2

@pytest.mark.asyncio
async def test_cache_invalidation_on_update(db_session, mock_redis):
    """Verify cache invalidation when data changes"""
    service = VocabularyService(db_session)

    # Cache the word
    word = await service.get_vocabulary_word(1)
    assert word["status"] == "new"

    # Update the word
    await service.update_vocabulary_status(1, "learning")

    # Fetch again - should get fresh data
    updated_word = await service.get_vocabulary_word(1)
    assert updated_word["status"] == "learning"
```

#### Day 5: Monitoring and Optimization (2 hours)

**Add Redis Monitoring:**

```python
# Backend/api/routes/health.py
from core.caching import get_redis_client

@router.get("/health/redis")
async def redis_health():
    """Check Redis connection and stats"""
    try:
        redis_client = await get_redis_client()

        # Test connection
        await redis_client.ping()

        # Get stats
        info = await redis_client.info()

        return {
            "status": "healthy",
            "connected_clients": info.get("connected_clients"),
            "used_memory": info.get("used_memory_human"),
            "hit_rate": info.get("keyspace_hits") / (info.get("keyspace_hits") + info.get("keyspace_misses")) if info.get("keyspace_misses") else 1.0
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

**Add Prometheus Metrics (Optional):**

```python
# Backend/core/metrics.py
from prometheus_client import Counter, Histogram

cache_hits = Counter("cache_hits_total", "Total cache hits")
cache_misses = Counter("cache_misses_total", "Total cache misses")
cache_latency = Histogram("cache_latency_seconds", "Cache operation latency")

# Update caching.py to record metrics
# In cached() decorator:
if cached_value is not None:
    cache_hits.inc()
else:
    cache_misses.inc()
```

### Performance Targets

| Metric                  | Before | Target  | Measurement      |
| ----------------------- | ------ | ------- | ---------------- |
| API p95 response time   | 180ms  | < 100ms | Locust load test |
| Cache hit rate          | 0%     | > 60%   | Redis INFO stats |
| Vocabulary API latency  | 85ms   | < 30ms  | Application logs |
| Translation API latency | 120ms  | < 40ms  | Application logs |

### Rollback Plan

1. Disable caching via environment variable:

   ```bash
   export REDIS_ENABLED=false
   ```

2. If Redis fails, application falls back to direct execution (already implemented in decorator)

3. If performance degrades:
   - Reduce TTL values
   - Adjust cache key strategies
   - Review cache invalidation logic

4. Complete rollback:
   - Remove `@cached` decorators
   - Stop Redis containers
   - Remove Redis from deployment pipeline

---

## Migration 6: Celery Async Processing

### Priority: HIGH

### Timeline: 1.5 weeks (7-8 days)

### Risk: High (complex infrastructure change)

### Problem

Video processing (transcription + translation) takes 2-5 minutes and blocks API requests, causing timeouts and poor UX.

### Pre-Migration Checklist

- [ ] Redis must be operational (required for Celery broker)
- [ ] Review `docs/architecture/PHASE2_INFRASTRUCTURE_SETUP.md` sections 2-4
- [ ] Plan task retry strategies
- [ ] Design progress tracking UI
- [ ] Allocate 1.5 weeks for implementation
- [ ] Schedule load testing window

### Step-by-Step Migration

#### Day 1-2: Setup Celery Infrastructure (8 hours)

**Install Dependencies:**

```bash
cd Backend
./api_venv/Scripts/activate
pip install celery[redis]==5.3.4
pip install flower==2.0.1  # Monitoring dashboard
pip freeze > requirements.txt
```

**Create Celery App:**

```python
# Backend/core/celery_app.py
from celery import Celery
from core.config import settings
import logging

logger = logging.getLogger(__name__)

celery_app = Celery(
    'langplug',
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    # Serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',

    # Timezone
    timezone='UTC',
    enable_utc=True,

    # Task execution
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3300,  # 55 minutes soft limit

    # Retry policy
    task_acks_late=True,
    task_reject_on_worker_lost=True,

    # Results
    result_expires=86400,  # Keep results for 24 hours

    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Auto-discover tasks
celery_app.autodiscover_tasks(['tasks'])

@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup"""
    logger.info(f'Request: {self.request!r}')
    return 'Celery is working!'
```

**Start Celery Worker:**

```bash
# Development
celery -A core.celery_app worker --loglevel=info --concurrency=2

# Production (with supervisor or systemd)
celery -A core.celery_app worker \
  --loglevel=info \
  --concurrency=4 \
  --max-tasks-per-child=100 \
  --time-limit=3600 \
  --soft-time-limit=3300
```

**Start Flower Monitoring:**

```bash
celery -A core.celery_app flower --port=5555
# Access at http://localhost:5555
```

#### Day 3-4: Create Async Tasks (8 hours)

**Video Processing Task:**

```python
# Backend/tasks/video_tasks.py
from core.celery_app import celery_app
from services.processing.chunk_processor import ChunkProcessingService
from database.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name='tasks.transcribe_video')
def transcribe_video_task(
    self,
    video_id: int,
    video_path: str,
    user_id: int,
    start_time: float,
    end_time: float,
):
    """
    Async task for video transcription and processing.

    Args:
        self: Celery task instance (bind=True)
        video_id: ID of video being processed
        video_path: Path to video file
        user_id: ID of user who initiated processing
        start_time: Start time in seconds
        end_time: End time in seconds

    Returns:
        dict: Processing results
    """
    try:
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'progress': 0, 'message': 'Starting video processing...'}
        )

        # Get database session
        async def process():
            async with get_session() as session:
                service = ChunkProcessingService(session)

                # Define progress callback
                def progress_callback(progress: float, message: str):
                    self.update_state(
                        state='PROGRESS',
                        meta={'progress': progress, 'message': message}
                    )

                result = await service.process_chunk(
                    video_path=video_path,
                    start_time=start_time,
                    end_time=end_time,
                    user_id=user_id,
                    task_id=self.request.id,
                    progress_callback=progress_callback,
                    session=session,
                )

                return result

        # Run async code in sync context
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(process())
        loop.close()

        self.update_state(
            state='SUCCESS',
            meta={'progress': 100, 'message': 'Processing complete!'}
        )

        return {
            'status': 'completed',
            'video_id': video_id,
            'vocabulary_count': result.get('vocabulary_count', 0),
            'segments_count': result.get('segments_count', 0),
        }

    except Exception as e:
        logger.error(f"Task {self.request.id} failed: {e}", exc_info=True)
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'progress': 0}
        )
        raise

@celery_app.task(bind=True, name='tasks.batch_translate')
def batch_translate_task(
    self,
    text_chunks: list[str],
    source_lang: str,
    target_lang: str,
):
    """Async task for batch translation"""
    try:
        async def translate():
            from services.translation.translation_service import get_translation_service
            service = get_translation_service()

            results = []
            total = len(text_chunks)

            for i, text in enumerate(text_chunks):
                translation = await service.translate(text, source_lang, target_lang)
                results.append(translation)

                # Update progress
                progress = int((i + 1) / total * 100)
                self.update_state(
                    state='PROGRESS',
                    meta={'progress': progress, 'message': f'Translated {i+1}/{total}'}
                )

            return results

        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(translate())
        loop.close()

        return {'translations': results}

    except Exception as e:
        logger.error(f"Translation task failed: {e}", exc_info=True)
        raise
```

#### Day 5: Update API Endpoints (4 hours)

**Convert Synchronous to Async:**

```python
# Backend/api/routes/video.py
from tasks.video_tasks import transcribe_video_task

# BEFORE - Synchronous blocking endpoint
@router.post("/videos/{video_id}/process")
async def process_video(video_id: int):
    # This blocks for 2-5 minutes!
    result = await process_video_sync(video_id)
    return result

# AFTER - Async non-blocking endpoint
@router.post("/videos/{video_id}/process")
async def process_video(video_id: int, user_id: int = Depends(get_current_user)):
    """Start async video processing"""
    video = await video_service.get_video(video_id)

    # Dispatch task to Celery
    task = transcribe_video_task.delay(
        video_id=video_id,
        video_path=video.file_path,
        user_id=user_id,
        start_time=0,
        end_time=video.duration,
    )

    # Return immediately with task ID
    return {
        "message": "Processing started",
        "task_id": task.id,
        "status_url": f"/api/tasks/{task.id}/status"
    }

@router.get("/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """Get task progress"""
    task = celery_app.AsyncResult(task_id)

    if task.state == 'PENDING':
        return {
            "state": "pending",
            "progress": 0,
            "message": "Task is waiting to start..."
        }
    elif task.state == 'PROGRESS':
        return {
            "state": "processing",
            "progress": task.info.get('progress', 0),
            "message": task.info.get('message', 'Processing...')
        }
    elif task.state == 'SUCCESS':
        return {
            "state": "completed",
            "progress": 100,
            "result": task.result
        }
    elif task.state == 'FAILURE':
        return {
            "state": "failed",
            "progress": 0,
            "error": str(task.info)
        }
    else:
        return {
            "state": task.state.lower(),
            "progress": 0,
            "message": f"Task is in {task.state} state"
        }
```

#### Day 6: Update Frontend (4 hours)

**Add Task Status Polling:**

```typescript
// src/hooks/useTaskStatus.ts
import { useEffect, useState } from "react";
import { TaskStatus } from "@/types";

export const useTaskStatus = (taskId: string | null) => {
  const [status, setStatus] = useState<TaskStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!taskId) return;

    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`/api/tasks/${taskId}/status`);
        const data = await response.json();

        setStatus(data);

        // Stop polling when task completes or fails
        if (data.state === "completed" || data.state === "failed") {
          clearInterval(pollInterval);
        }
      } catch (err) {
        setError("Failed to fetch task status");
        clearInterval(pollInterval);
      }
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(pollInterval);
  }, [taskId]);

  return { status, error };
};
```

**Update Video Processing UI:**

```typescript
// src/components/VideoProcessing.tsx
import { useTaskStatus } from '@/hooks/useTaskStatus';

export const VideoProcessing = ({ videoId }: { videoId: number }) => {
  const [taskId, setTaskId] = useState<string | null>(null);
  const { status } = useTaskStatus(taskId);

  const startProcessing = async () => {
    const response = await fetch(`/api/videos/${videoId}/process`, {
      method: 'POST',
    });
    const data = await response.json();
    setTaskId(data.task_id);
  };

  return (
    <div>
      {!taskId && (
        <button onClick={startProcessing}>
          Start Processing
        </button>
      )}

      {status && (
        <div>
          <ProgressBar value={status.progress} />
          <p>{status.message}</p>

          {status.state === 'completed' && (
            <div>
              <p>Processing complete!</p>
              <button onClick={() => navigate(`/learn/${videoId}`)}>
                Start Learning
              </button>
            </div>
          )}

          {status.state === 'failed' && (
            <div>
              <p>Processing failed: {status.error}</p>
              <button onClick={startProcessing}>Retry</button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
```

#### Day 7-8: Testing and Monitoring (8 hours)

**Task Tests:**

```python
# tests/integration/test_celery_tasks.py
import pytest
from tasks.video_tasks import transcribe_video_task

@pytest.mark.asyncio
async def test_transcribe_video_task_success(db_session, sample_video):
    """Test successful video transcription task"""
    task = transcribe_video_task.delay(
        video_id=sample_video.id,
        video_path=sample_video.file_path,
        user_id=1,
        start_time=0,
        end_time=300,
    )

    # Wait for task (timeout 60 seconds for tests)
    result = task.get(timeout=60)

    assert result['status'] == 'completed'
    assert result['vocabulary_count'] > 0

@pytest.mark.asyncio
async def test_task_retry_on_failure(db_session):
    """Test task retry mechanism"""
    task = transcribe_video_task.delay(
        video_id=999,  # Non-existent video
        video_path="/invalid/path",
        user_id=1,
        start_time=0,
        end_time=300,
    )

    with pytest.raises(Exception):
        task.get(timeout=30)

    assert task.state == 'FAILURE'
```

**Performance Testing:**

```python
# tests/performance/test_async_throughput.py
import time
from tasks.video_tasks import transcribe_video_task

def test_async_throughput():
    """Test that async processing improves throughput"""
    start = time.time()

    # Dispatch 10 video processing tasks
    tasks = []
    for i in range(10):
        task = transcribe_video_task.delay(
            video_id=i,
            video_path=f"/videos/video{i}.mp4",
            user_id=1,
            start_time=0,
            end_time=300,
        )
        tasks.append(task)

    dispatch_time = time.time() - start

    # Dispatching 10 tasks should take < 1 second
    assert dispatch_time < 1.0, f"Dispatch took {dispatch_time}s"

    # Wait for all tasks
    for task in tasks:
        task.get(timeout=300)

    total_time = time.time() - start

    # With 4 workers, 10 tasks should complete in ~3-4 minutes
    # vs 20-50 minutes synchronously
    assert total_time < 300, f"Processing took {total_time}s"
```

### Performance Targets

| Metric                              | Before            | Target             | Measurement         |
| ----------------------------------- | ----------------- | ------------------ | ------------------- |
| Video processing time (user-facing) | 2-5 min blocking  | < 1s dispatch      | API response time   |
| Concurrent processing capacity      | 1 video at a time | 4+ videos parallel | Celery worker count |
| API timeout rate                    | 15%               | < 1%               | Error logs          |
| User satisfaction                   | 6.5/10            | 9/10               | User surveys        |

### Rollback Plan

1. Keep synchronous endpoints as fallback:

```python
# Feature flag in config
USE_ASYNC_PROCESSING = os.getenv("USE_ASYNC_PROCESSING", "true") == "true"

@router.post("/videos/{video_id}/process")
async def process_video(video_id: int):
    if USE_ASYNC_PROCESSING:
        return await process_async(video_id)
    else:
        return await process_sync(video_id)  # Old synchronous path
```

2. If Celery fails, disable async processing:

   ```bash
   export USE_ASYNC_PROCESSING=false
   ```

3. If tasks accumulate, scale workers:

   ```bash
   # Add more workers
   celery -A core.celery_app worker --concurrency=8
   ```

4. If tasks fail frequently, investigate:
   - Check Flower dashboard: http://localhost:5555
   - Review task logs
   - Adjust retry strategies

---

## Migration 7: Security Hardening

### Priority: CRITICAL

### Timeline: 2 weeks (10 days)

### Risk: Low (improves security)

### Problem

Security analysis identified 14 critical and 23 high-priority vulnerabilities that must be addressed.

### Pre-Migration Checklist

- [ ] Review `docs/architecture/SECURITY_DEEP_DIVE_ANALYSIS.md`
- [ ] Schedule security audit window
- [ ] Plan phased rollout of security changes
- [ ] Prepare communication for users (password policy changes)
- [ ] Back up database before applying security fixes

### Critical Security Fixes (Week 1)

#### Day 1: CSRF Protection (4 hours)

**Install FastAPI CSRF:**

```bash
cd Backend
./api_venv/Scripts/activate
pip install fastapi-csrf-protect==0.3.2
pip freeze > requirements.txt
```

**Configure CSRF:**

```python
# Backend/core/security.py
from fastapi_csrf_protect import CsrfProtect
from pydantic import BaseModel

class CsrfSettings(BaseModel):
    secret_key: str = settings.secret_key
    cookie_samesite: str = "lax"
    cookie_secure: bool = settings.environment == "production"

@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()

# Add to main.py
from core.security import CsrfProtect

app = FastAPI()

@app.post("/auth/csrf-token")
async def get_csrf_token(csrf_protect: CsrfProtect = Depends()):
    """Generate CSRF token"""
    response = JSONResponse({"message": "CSRF token generated"})
    csrf_protect.set_csrf_cookie(response)
    return response

# Protect state-changing endpoints
@app.post("/api/videos/{video_id}/process")
async def process_video(
    video_id: int,
    csrf_protect: CsrfProtect = Depends()
):
    await csrf_protect.validate_csrf()  # Validates CSRF token
    # ... rest of endpoint
```

**Frontend Integration:**

```typescript
// src/utils/csrf.ts
export const getCsrfToken = async (): Promise<string> => {
  const response = await fetch("/auth/csrf-token", {
    method: "POST",
    credentials: "include",
  });

  // Token is in cookie, extract it
  const cookies = document.cookie.split(";");
  const csrfCookie = cookies.find((c) =>
    c.trim().startsWith("fastapi-csrf-token="),
  );
  return csrfCookie ? csrfCookie.split("=")[1] : "";
};

// Add to API client
import { OpenAPI } from "@/client";

OpenAPI.interceptors.request.use(async (request) => {
  if (["POST", "PUT", "DELETE", "PATCH"].includes(request.method)) {
    const csrfToken = await getCsrfToken();
    request.headers["X-CSRF-Token"] = csrfToken;
  }
  return request;
});
```

#### Day 2: Strong Password Policy (4 hours)

```python
# Backend/services/authservice/password_validator.py
import re
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class PasswordValidator:
    """Enforce strong password policy"""

    MIN_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGITS = True
    REQUIRE_SPECIAL = True

    @classmethod
    def validate(cls, password: str) -> tuple[bool, str]:
        """
        Validate password against policy.

        Returns:
            (is_valid, error_message)
        """
        if len(password) < cls.MIN_LENGTH:
            return False, f"Password must be at least {cls.MIN_LENGTH} characters"

        if cls.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"

        if cls.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"

        if cls.REQUIRE_DIGITS and not re.search(r'\d', password):
            return False, "Password must contain at least one digit"

        if cls.REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"

        # Check against common passwords list
        if cls._is_common_password(password):
            return False, "Password is too common, please choose a stronger password"

        return True, ""

    @staticmethod
    def _is_common_password(password: str) -> bool:
        """Check if password is in common passwords list"""
        common_passwords = {
            "password123", "Password123!", "Admin123!",
            # Load from file: common_passwords.txt
        }
        return password.lower() in common_passwords

    @classmethod
    def hash_password(cls, password: str) -> str:
        """Hash password using Argon2"""
        return pwd_context.hash(password)

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
```

**Update Registration:**

```python
# Backend/api/routes/auth.py
from services.authservice.password_validator import PasswordValidator

@router.post("/auth/register")
async def register(user_data: UserCreate):
    # Validate password
    is_valid, error_msg = PasswordValidator.validate(user_data.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    # Hash password
    hashed_password = PasswordValidator.hash_password(user_data.password)

    # Create user
    user = await auth_service.create_user(
        email=user_data.email,
        password_hash=hashed_password,
    )

    return user
```

#### Day 3: Path Traversal Prevention (2 hours)

```python
# Backend/core/file_security.py
from pathlib import Path
import os

class FileSecurityValidator:
    """Prevent path traversal attacks"""

    ALLOWED_UPLOAD_DIR = Path("/app/uploads")
    ALLOWED_EXTENSIONS = {".mp4", ".webm", ".mkv", ".srt", ".vtt"}
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB

    @classmethod
    def validate_file_path(cls, file_path: str) -> Path:
        """
        Validate and sanitize file path.

        Raises:
            ValueError: If path is invalid or contains traversal
        """
        # Convert to Path object
        path = Path(file_path).resolve()

        # Ensure path is within allowed directory
        if not path.is_relative_to(cls.ALLOWED_UPLOAD_DIR):
            raise ValueError(f"Path {path} is outside allowed directory")

        # Check for path traversal attempts
        if ".." in file_path or file_path.startswith("/"):
            raise ValueError("Path traversal attempt detected")

        return path

    @classmethod
    def validate_file_extension(cls, filename: str) -> bool:
        """Validate file extension"""
        ext = Path(filename).suffix.lower()
        return ext in cls.ALLOWED_EXTENSIONS

    @classmethod
    async def validate_file_upload(cls, file: UploadFile) -> Path:
        """
        Validate uploaded file.

        Returns:
            Path: Safe file path for storage
        """
        # Validate extension
        if not cls.validate_file_extension(file.filename):
            raise ValueError(f"File type not allowed: {file.filename}")

        # Generate safe filename
        safe_filename = f"{uuid.uuid4()}{Path(file.filename).suffix}"
        safe_path = cls.ALLOWED_UPLOAD_DIR / safe_filename

        # Check file size
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)

        if file_size > cls.MAX_FILE_SIZE:
            raise ValueError(f"File too large: {file_size} bytes")

        return safe_path
```

**Update Video Upload:**

```python
# Backend/api/routes/video.py
from core.file_security import FileSecurityValidator

@router.post("/videos/upload")
async def upload_video(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user)
):
    # Validate file
    safe_path = await FileSecurityValidator.validate_file_upload(file)

    # Save file
    async with aiofiles.open(safe_path, 'wb') as f:
        content = await file.read()
        await f.write(content)

    # Create video record
    video = await video_service.create_video(
        user_id=user_id,
        file_path=str(safe_path),
        filename=file.filename,
    )

    return video
```

#### Day 4-5: JWT Token Hardening (6 hours)

**Reduce Token Lifetime:**

```python
# Backend/core/config.py
class Settings:
    jwt_access_token_expire_minutes: int = Field(
        default=60,  # Changed from 24 hours to 1 hour
        env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=30,
        env="JWT_REFRESH_TOKEN_EXPIRE_DAYS"
    )
```

**Implement Refresh Token:**

```python
# Backend/services/authservice/token_service.py
from datetime import datetime, timedelta
from jose import jwt, JWTError

class TokenService:
    def create_access_token(self, user_id: int) -> str:
        """Create short-lived access token (1 hour)"""
        expires = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
        payload = {
            "sub": str(user_id),
            "exp": expires,
            "type": "access",
        }
        return jwt.encode(payload, settings.secret_key, algorithm="HS256")

    def create_refresh_token(self, user_id: int) -> str:
        """Create long-lived refresh token (30 days)"""
        expires = datetime.utcnow() + timedelta(days=settings.jwt_refresh_token_expire_days)
        payload = {
            "sub": str(user_id),
            "exp": expires,
            "type": "refresh",
        }
        return jwt.encode(payload, settings.secret_key, algorithm="HS256")

    def refresh_access_token(self, refresh_token: str) -> str:
        """Exchange refresh token for new access token"""
        try:
            payload = jwt.decode(refresh_token, settings.secret_key, algorithms=["HS256"])

            if payload.get("type") != "refresh":
                raise ValueError("Invalid token type")

            user_id = int(payload.get("sub"))
            return self.create_access_token(user_id)

        except JWTError as e:
            raise ValueError(f"Invalid refresh token: {e}")
```

**Add Refresh Endpoint:**

```python
# Backend/api/routes/auth.py
@router.post("/auth/refresh")
async def refresh_token(refresh_token: str = Cookie(None)):
    """Refresh access token using refresh token"""
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token required")

    try:
        token_service = TokenService()
        new_access_token = token_service.refresh_access_token(refresh_token)

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
```

**Frontend Token Refresh:**

```typescript
// src/utils/auth-interceptor.ts
let refreshPromise: Promise<string> | null = null;

OpenAPI.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.status === 401 && !error.config._retry) {
      error.config._retry = true;

      // Prevent multiple refresh requests
      if (!refreshPromise) {
        refreshPromise = fetch("/auth/refresh", {
          method: "POST",
          credentials: "include",
        })
          .then((res) => res.json())
          .then((data) => {
            localStorage.setItem("access_token", data.access_token);
            refreshPromise = null;
            return data.access_token;
          })
          .catch(() => {
            refreshPromise = null;
            // Redirect to login
            window.location.href = "/login";
            throw error;
          });
      }

      await refreshPromise;

      // Retry original request with new token
      return OpenAPI.request(error.config);
    }

    throw error;
  },
);
```

### Verification and Testing

```bash
# Test CSRF protection
curl -X POST http://localhost:8000/api/videos/1/process \
  -H "Authorization: Bearer <token>" \
  # Should return 403 without CSRF token

# Test password policy
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"weak"}' \
  # Should return 400 with validation error

# Test path traversal prevention
curl -X POST http://localhost:8000/videos/upload \
  -F "file=@../../etc/passwd" \
  # Should return 400 with security error

# Test token refresh
curl -X POST http://localhost:8000/auth/refresh \
  --cookie "refresh_token=<refresh_token>" \
  # Should return new access token
```

---

## Migration 8: Frontend Performance Optimization

### Priority: MEDIUM

### Timeline: 1 week (5 days)

### Risk: Low (improves UX)

### Problem

Frontend experiences unnecessary re-renders, slow list rendering with 1000+ items, and memory leaks.

### Step-by-Step Migration

#### Day 1-2: React.memo Optimization (6 hours)

**Identify Re-render Hotspots:**

```bash
# Use React DevTools Profiler
# 1. Open DevTools → Profiler tab
# 2. Start recording
# 3. Interact with vocabulary list
# 4. Stop recording
# 5. Identify components with high render counts
```

**Apply React.memo:**

```typescript
// BEFORE
export const VocabularyCard = ({ word, onToggle }: Props) => {
  return (
    <Card onClick={() => onToggle(word.id)}>
      <h3>{word.text}</h3>
      <p>{word.translation}</p>
    </Card>
  );
};

// AFTER
export const VocabularyCard = memo(({ word, onToggle }: Props) => {
  return (
    <Card onClick={() => onToggle(word.id)}>
      <h3>{word.text}</h3>
      <p>{word.translation}</p>
    </Card>
  );
}, (prevProps, nextProps) => {
  // Custom comparison - only re-render if word data changes
  return (
    prevProps.word.id === nextProps.word.id &&
    prevProps.word.text === nextProps.word.text &&
    prevProps.word.translation === nextProps.word.translation &&
    prevProps.onToggle === nextProps.onToggle
  );
});
```

#### Day 3: useCallback for Stable References (4 hours)

```typescript
// BEFORE - Creates new function every render
function VocabularyList({ words, onWordClick }) {
  return (
    <div>
      {words.map(word => (
        <VocabularyCard
          key={word.id}
          word={word}
          onToggle={() => onWordClick(word.id)}  // NEW FUNCTION EVERY RENDER!
        />
      ))}
    </div>
  );
}

// AFTER - Stable function reference
function VocabularyList({ words, onWordClick }) {
  const handleToggle = useCallback((wordId: number) => {
    onWordClick(wordId);
  }, [onWordClick]);  // Only recreate if onWordClick changes

  return (
    <div>
      {words.map(word => (
        <VocabularyCard
          key={word.id}
          word={word}
          onToggle={handleToggle}  // STABLE REFERENCE
        />
      ))}
    </div>
  );
}
```

#### Day 4: Virtual Scrolling (4 hours)

```bash
cd Frontend
npm install react-window@1.8.10
```

```typescript
// BEFORE - Renders all 10,000 items (SLOW!)
function VocabularyLibrary({ words }: { words: Word[] }) {
  return (
    <div style={{ height: '600px', overflow: 'auto' }}>
      {words.map(word => (
        <VocabularyCard key={word.id} word={word} />
      ))}
    </div>
  );
}

// AFTER - Only renders visible items (FAST!)
import { FixedSizeList } from 'react-window';

function VocabularyLibrary({ words }: { words: Word[] }) {
  const Row = ({ index, style }) => (
    <div style={style}>
      <VocabularyCard word={words[index]} />
    </div>
  );

  return (
    <FixedSizeList
      height={600}
      itemCount={words.length}
      itemSize={80}  // Height of each item
      width="100%"
    >
      {Row}
    </FixedSizeList>
  );
}
```

#### Day 5: Testing and Validation (2 hours)

**Performance Test:**

```typescript
// src/components/__tests__/VocabularyLibrary.test.tsx
it('should render 10,000 items smoothly', async () => {
  const words = Array.from({ length: 10000 }, (_, i) => ({
    id: i,
    text: `word-${i}`,
    translation: `translation-${i}`,
  }));

  const { container } = render(<VocabularyLibrary words={words} />);

  // Virtual scrolling should only render ~10 visible items
  const renderedCards = container.querySelectorAll('[data-testid="vocabulary-card"]');
  expect(renderedCards.length).toBeLessThan(20);  // Not 10,000!
});
```

**Measure Re-renders:**

```typescript
// src/utils/render-counter.ts
export const useRenderCount = (componentName: string) => {
  const renderCount = useRef(0);

  useEffect(() => {
    renderCount.current += 1;
    if (process.env.NODE_ENV === "development") {
      console.log(`${componentName} rendered ${renderCount.current} times`);
    }
  });
};

// Use in components
function VocabularyCard({ word }: Props) {
  useRenderCount("VocabularyCard");
  // ... rest of component
}
```

### Performance Targets

| Metric                             | Before            | Target   | Validation       |
| ---------------------------------- | ----------------- | -------- | ---------------- |
| Vocabulary list render time        | 2.5s (1000 items) | < 100ms  | React DevTools   |
| Re-render count (list interaction) | 50+               | < 5      | Render counter   |
| Memory usage                       | 350 MB            | < 150 MB | Browser DevTools |
| First contentful paint             | 1.8s              | < 1.0s   | Lighthouse       |

---

## General Migration Best Practices

### Before Any Migration

1. **Create feature branch**: `git checkout -b migration/<name>`
2. **Back up database**: Production database snapshot
3. **Review documentation**: Read specific migration guide thoroughly
4. **Schedule window**: Plan migration during low-traffic period
5. **Notify team**: Communication about potential disruptions

### During Migration

1. **Follow steps sequentially**: Don't skip verification steps
2. **Test frequently**: Run tests after each major change
3. **Monitor metrics**: Watch logs, error rates, performance
4. **Document issues**: Keep notes on problems encountered
5. **Have rollback ready**: Know how to revert quickly

### After Migration

1. **Verify success criteria**: Check all metrics meet targets
2. **Monitor for 24 hours**: Watch for delayed issues
3. **Gather feedback**: Ask users about experience
4. **Update documentation**: Document any deviations from plan
5. **Celebrate success**: Acknowledge team effort

### Emergency Rollback Procedure

If critical issues arise during any migration:

1. **Stop deployment immediately**
2. **Revert code changes**: `git revert <commit>` or `git reset --hard <previous-commit>`
3. **Restore database**: From backup if schema changed
4. **Clear caches**: Redis, browser caches
5. **Notify stakeholders**: Communication about rollback
6. **Post-mortem**: Document what went wrong

---

## Migration Tracking

### Checklist

- [ ] Migration 1: Remove @lru_cache State Pollution ✅ COMPLETED
- [ ] Migration 2: Apply Transaction Boundaries (Phase 1)
- [ ] Migration 2: Apply Transaction Boundaries (Phase 2)
- [ ] Migration 3: Implement Code Splitting ✅ COMPLETED
- [ ] Migration 4: Refactor ChunkedLearningPlayer
- [ ] Migration 5: Redis Caching Layer (Day 1)
- [ ] Migration 5: Redis Caching Layer (Day 2)
- [ ] Migration 5: Redis Caching Layer (Day 3)
- [ ] Migration 5: Redis Caching Layer (Day 4)
- [ ] Migration 5: Redis Caching Layer (Day 5)
- [ ] Migration 6: Celery Async Processing (Day 1-2)
- [ ] Migration 6: Celery Async Processing (Day 3-4)
- [ ] Migration 6: Celery Async Processing (Day 5)
- [ ] Migration 6: Celery Async Processing (Day 6)
- [ ] Migration 6: Celery Async Processing (Day 7-8)
- [ ] Migration 7: Security Hardening (Week 1)
- [ ] Migration 7: Security Hardening (Week 2)
- [ ] Migration 8: Frontend Performance Optimization

### Timeline Summary

| Migration                 | Priority | Duration  | Risk   | Status      |
| ------------------------- | -------- | --------- | ------ | ----------- |
| 1. @lru_cache Removal     | CRITICAL | 1 hour    | Low    | ✅ Complete |
| 2. Transaction Boundaries | CRITICAL | 4-6 hours | Medium | Ready       |
| 3. Code Splitting         | HIGH     | 2 hours   | Low    | ✅ Complete |
| 4. ChunkedLearningPlayer  | HIGH     | 8 hours   | Medium | Ready       |
| 5. Redis Caching          | HIGH     | 1 week    | Medium | Ready       |
| 6. Celery Async           | HIGH     | 1.5 weeks | High   | Ready       |
| 7. Security Hardening     | CRITICAL | 2 weeks   | Low    | Ready       |
| 8. Frontend Performance   | MEDIUM   | 1 week    | Low    | Ready       |

**Total Estimated Timeline**: 6-8 weeks for all migrations

---

## Success Metrics

Track these metrics before and after each migration:

### Performance Metrics

- API p95 response time: Target < 100ms
- Frontend initial load time: Target < 1.0s
- Video processing time: Target < 30s dispatch
- Cache hit rate: Target > 60%

### Quality Metrics

- Test pass rate: Target 100%
- Test coverage: Target 80%+
- Code quality score: Target 8.5/10
- Security vulnerabilities: Target 0 critical

### User Experience Metrics

- User satisfaction score: Target 9/10
- Task completion rate: Target > 95%
- Error rate: Target < 1%
- Support tickets: Target -50% reduction

---

## Support and Resources

### Documentation

- Architecture Assessment: `docs/architecture/COMPREHENSIVE_ARCHITECTURE_ASSESSMENT.md`
- Security Analysis: `docs/architecture/SECURITY_DEEP_DIVE_ANALYSIS.md`
- Test Strategy: `docs/architecture/COMPREHENSIVE_TEST_STRATEGY.md`
- Infrastructure Setup: `docs/architecture/PHASE2_INFRASTRUCTURE_SETUP.md`
- Transaction Fix: `Backend/docs/TRANSACTION_BOUNDARIES_FIX.md`
- Player Refactoring: `Frontend/docs/CHUNKED_LEARNING_PLAYER_REFACTORING_GUIDE.md`

### Communication Channels

- Development Team: Slack #langplug-dev
- Security Issues: security@langplug.com
- User Support: support@langplug.com

### Emergency Contacts

- Tech Lead: [Contact Info]
- DevOps: [Contact Info]
- Security: [Contact Info]

---

**Document Version**: 1.0
**Last Updated**: 2025-10-02
**Next Review**: After Phase 1 migrations complete
**Owner**: Architecture + Development Teams
