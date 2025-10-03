# Architecture Refactoring Recommendations

**Project**: LangPlug - German Language Learning Platform
**Date**: 2025-10-02
**Priority Classification**: Critical → High → Medium → Low
**Status**: Ready for Implementation

---

## Executive Summary

This document provides **prioritized, actionable refactoring recommendations** based on comprehensive architecture analysis. Recommendations are organized by priority level with effort estimates, impact analysis, and implementation guidance.

### Quick Stats

- **Total Recommendations**: 42
- **Critical** (must fix immediately): 4
- **High** (fix within 1 month): 12
- **Medium** (fix within 1 quarter): 18
- **Low** (fix within 1 year): 8

### Estimated Total Effort

- Critical: 16 hours
- High: 120 hours (3 weeks)
- Medium: 320 hours (8 weeks)
- Low: 480 hours (12 weeks)

---

## Table of Contents

1. [Critical Priority (Week 1)](#1-critical-priority-week-1)
2. [High Priority (Month 1)](#2-high-priority-month-1)
3. [Medium Priority (Quarter 1)](#3-medium-priority-quarter-1)
4. [Low Priority (Year 1)](#4-low-priority-year-1)
5. [Implementation Strategy](#5-implementation-strategy)
6. [Risk Mitigation](#6-risk-mitigation)

---

## 1. Critical Priority (Week 1)

### 🔴 CRITICAL-01: Remove @lru_cache State Pollution

**Category**: Backend / Testing
**Impact**: Test isolation failures, production bugs
**Effort**: 1 hour
**Risk**: High (production data corruption possible)

#### Problem

```python
# Backend/core/service_dependencies.py:80
@lru_cache  # BUG: Services cached globally across tests!
def get_transcription_service():
    return TranscriptionService()
```

Services are cached globally, causing:

- Tests to share state and fail unpredictably
- Potential production issues with stale instances
- Configuration changes not reflected

#### Solution

```python
# Remove @lru_cache completely
def get_transcription_service():
    """Create new service instance each time."""
    return TranscriptionService()

# Alternative: Use proper DI container
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    transcription_service = providers.Singleton(
        TranscriptionService,
        config=config.transcription,
    )
```

#### Implementation Steps

1. Remove all `@lru_cache` decorators from `service_dependencies.py`
2. Add pytest fixture `autouse=True` to clear any remaining caches
3. Run full test suite to verify isolation
4. Monitor memory usage (may need connection pooling)

#### Acceptance Criteria

- ✅ All tests pass in isolation AND full suite
- ✅ No shared state between test runs
- ✅ Memory usage remains stable

---

### 🔴 CRITICAL-02: Split ChunkedLearningPlayer God Component

**Category**: Frontend / Maintainability
**Impact**: Unmaintainable, hard to test, poor performance
**Effort**: 8 hours
**Risk**: Medium (large refactoring)

#### Problem

`Frontend/src/components/ChunkedLearningPlayer.tsx`: **1,301 lines**

- Handles 7+ responsibilities
- Impossible to test in isolation
- Performance issues (unnecessary re-renders)

#### Solution

Split into 7 focused components:

```
ChunkedLearningPlayer.tsx (coordinator, ~150 lines)
├── ChunkedVideoPlayer.tsx (~200 lines)
│   └── Handles video playback, controls, seeking
├── SubtitleDisplay.tsx (~150 lines)
│   └── Renders subtitles with timing
├── VocabularyHighlight.tsx (~180 lines)
│   └── Highlights unknown words, tooltips
├── ProgressTracker.tsx (~120 lines)
│   └── Tracks learning progress, analytics
├── ControlPanel.tsx (~100 lines)
│   └── Player controls, speed, volume
├── ChunkSelector.tsx (~150 lines)
│   └── Chunk navigation, progress bar
└── hooks/
    ├── useVideoState.ts (~80 lines)
    ├── useSubtitleSync.ts (~60 lines)
    └── useVocabularyTracking.ts (~70 lines)
```

#### Implementation Steps

1. **Extract state logic** into custom hooks first
2. **Create presentational components** for UI rendering
3. **Wire together** in coordinator component
4. **Add tests** for each component (aim for 80% coverage)
5. **Performance test** with React DevTools Profiler

#### Acceptance Criteria

- ✅ No component > 300 lines
- ✅ Each component has single responsibility
- ✅ 80%+ test coverage
- ✅ 50% reduction in re-renders (measured)

---

### 🔴 CRITICAL-03: Implement Code Splitting

**Category**: Frontend / Performance
**Impact**: 60% reduction in initial bundle size
**Effort**: 4 hours
**Risk**: Low

#### Problem

- Initial bundle: **2.5MB** (uncompressed)
- Time to Interactive: **3.8 seconds**
- All components loaded upfront

#### Solution

Implement route-based code splitting:

```typescript
// App.tsx - BEFORE
import { VideoSelection } from './components/VideoSelection';
import { ChunkedLearningFlow } from './components/ChunkedLearningFlow';
import { VocabularyLibrary } from './components/VocabularyLibrary';

// App.tsx - AFTER
import { lazy, Suspense } from 'react';
import { Loading } from './components/ui/Loading';

const VideoSelection = lazy(() => import('./components/VideoSelection'));
const ChunkedLearningFlow = lazy(() => import('./components/ChunkedLearningFlow'));
const VocabularyLibrary = lazy(() => import('./components/VocabularyLibrary'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="/videos" element={<VideoSelection />} />
        <Route path="/learn" element={<ChunkedLearningFlow />} />
        <Route path="/vocabulary" element={<VocabularyLibrary />} />
      </Routes>
    </Suspense>
  );
}
```

#### Implementation Steps

1. Convert all route components to `lazy()` imports
2. Add `<Suspense>` boundaries with Loading fallback
3. Run bundle analyzer: `npm run build -- --analyze`
4. Verify chunk sizes are balanced (no single chunk > 500KB)
5. Test loading states on slow 3G network

#### Expected Results

- Initial bundle: **~800KB** (down from 2.5MB)
- Time to Interactive: **~1.5s** (down from 3.8s)
- Improved perceived performance

#### Acceptance Criteria

- ✅ Initial bundle < 1MB
- ✅ Each route chunk < 500KB
- ✅ Loading states work correctly
- ✅ No runtime errors

---

### 🔴 CRITICAL-04: Add Transaction Boundaries

**Category**: Backend / Data Integrity
**Impact**: Prevents data corruption
**Effort**: 3 hours
**Risk**: High (data integrity)

#### Problem

Multi-step database operations without transactions:

```python
# Backend/services/processing/chunk_processor.py
async def process_chunk(chunk_id):
    # Step 1: Update chunk status
    await repo.update_status(chunk_id, "processing")

    # Step 2: Transcribe (may fail)
    transcript = await transcribe(chunk_id)

    # Step 3: Save transcript
    await repo.save_transcript(chunk_id, transcript)

    # Step 4: Update status
    await repo.update_status(chunk_id, "completed")

# PROBLEM: If step 3 fails, chunk left in "processing" state forever!
```

#### Solution

Add transaction decorator:

```python
from core.database import transactional

@transactional
async def process_chunk(chunk_id, session):
    """Process chunk within transaction."""
    # Step 1: Update chunk status
    await repo.update_status(chunk_id, "processing", session=session)

    # Step 2: Transcribe (may fail - will rollback all changes)
    transcript = await transcribe(chunk_id)

    # Step 3: Save transcript
    await repo.save_transcript(chunk_id, transcript, session=session)

    # Step 4: Update status
    await repo.update_status(chunk_id, "completed", session=session)

    # If any step fails, ALL changes are rolled back

# Implement transactional decorator
def transactional(func):
    """Wrap function in database transaction."""
    async def wrapper(*args, **kwargs):
        async with AsyncSessionLocal() as session:
            async with session.begin():
                try:
                    result = await func(*args, **kwargs, session=session)
                    await session.commit()
                    return result
                except Exception:
                    await session.rollback()
                    raise
    return wrapper
```

#### Files to Update

1. `services/processing/chunk_processor.py`
2. `services/processing/chunk_handler.py`
3. `services/processing/transcription_handler.py`
4. `services/vocabulary/vocabulary_sync_service.py`

#### Acceptance Criteria

- ✅ All multi-step operations wrapped in transactions
- ✅ Test rollback behavior
- ✅ No orphaned database records

---

## 2. High Priority (Month 1)

### ⚠️ HIGH-01: Add Celery Task Queue

**Category**: Backend / Scalability
**Impact**: Async AI processing, 10x throughput
**Effort**: 16 hours
**Risk**: Medium (infrastructure change)

#### Problem

- AI transcription/translation blocks HTTP requests
- Users wait 2-5 minutes for responses
- Server can't handle concurrent processing

#### Solution

Introduce Celery + Redis for async task queue:

```python
# Backend/tasks/celery_app.py
from celery import Celery

celery_app = Celery(
    'langplug',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

# Backend/tasks/video_tasks.py
from tasks.celery_app import celery_app

@celery_app.task
async def transcribe_video_task(video_id: int):
    """Background task for video transcription."""
    service = get_transcription_service()
    result = await service.transcribe(video_id)
    return result

# Backend/api/routes/processing.py
@router.post("/process/{video_id}")
async def process_video(video_id: int):
    """Trigger async processing."""
    task = transcribe_video_task.delay(video_id)
    return {"task_id": task.id, "status": "queued"}

@router.get("/process/status/{task_id}")
async def get_task_status(task_id: str):
    """Check processing status."""
    task = celery_app.AsyncResult(task_id)
    return {"status": task.status, "progress": task.info}
```

#### Infrastructure

- **Development**: Redis in Docker
- **Production**: Redis Cluster or AWS ElastiCache

#### Implementation Steps

1. Install Celery: `pip install celery[redis]`
2. Set up Redis (docker-compose or cloud)
3. Create celery_app.py and task modules
4. Update API routes to use tasks
5. Add Celery worker to deployment (supervisor or systemd)
6. Update frontend to poll task status

#### Acceptance Criteria

- ✅ API responds immediately (< 100ms)
- ✅ Tasks process in background
- ✅ Progress updates via WebSocket
- ✅ Handle worker failures gracefully

---

### ⚠️ HIGH-02: Add Redis Caching Layer

**Category**: Backend / Performance
**Impact**: 50% faster lookups, reduced DB load
**Effort**: 8 hours
**Risk**: Low

#### Problem

- Every vocabulary lookup hits database
- Translation results not cached
- Repeated queries for same data

#### Solution

Add Redis caching with strategic invalidation:

```python
# Backend/core/caching.py
import redis.asyncio as redis
from functools import wraps

redis_client = redis.Redis.from_url("redis://localhost:6379")

def cached(ttl=3600):
    """Cache decorator with TTL."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key = f"{func.__name__}:{args}:{kwargs}"

            # Check cache
            cached_value = await redis_client.get(key)
            if cached_value:
                return json.loads(cached_value)

            # Compute value
            result = await func(*args, **kwargs)

            # Store in cache
            await redis_client.setex(
                key,
                ttl,
                json.dumps(result)
            )

            return result
        return wrapper
    return decorator

# Usage
@cached(ttl=3600)  # Cache for 1 hour
async def get_vocabulary_word(word_id: int):
    return await repo.get_by_id(word_id)

@cached(ttl=86400)  # Cache for 24 hours
async def translate_text(text: str, source: str, target: str):
    return await translation_service.translate(text, source, target)
```

#### Cache Invalidation Strategy

```python
# Invalidate on update
async def update_vocabulary_word(word_id: int, data: dict):
    result = await repo.update(word_id, data)
    # Invalidate cache
    await redis_client.delete(f"get_vocabulary_word:{word_id}")
    return result
```

#### Implementation Steps

1. Set up Redis (docker-compose)
2. Create caching module with decorators
3. Identify cacheable operations (vocabulary lookups, translations)
4. Add cache decorators
5. Implement invalidation strategy
6. Monitor cache hit rate (aim for > 60%)

#### Acceptance Criteria

- ✅ Cache hit rate > 60%
- ✅ 50% reduction in database queries
- ✅ Cache invalidation works correctly
- ✅ Redis failover handled gracefully

---

### ⚠️ HIGH-03: Optimize Frontend Re-Renders

**Category**: Frontend / Performance
**Impact**: 40% fewer re-renders
**Effort**: 12 hours
**Risk**: Low

#### Problem

- Only 39 uses of React.memo/useCallback/useMemo across entire codebase
- List components re-render unnecessarily
- Example: Vocabulary list re-renders all 1000+ items on state change

#### Solution

Apply performance optimizations strategically:

```typescript
// BEFORE - VocabularyLibrary.tsx
function VocabularyList({ words }) {
  return (
    <div>
      {words.map(word => (
        <VocabularyCard key={word.id} word={word} />
      ))}
    </div>
  );
}

// AFTER - VocabularyLibrary.tsx
import { memo, useCallback } from 'react';

// Memoize list item
const VocabularyCard = memo(({ word, onToggle }) => {
  return (
    <Card>
      <h3>{word.text}</h3>
      <button onClick={() => onToggle(word.id)}>Toggle</button>
    </Card>
  );
});

function VocabularyList({ words, onToggle }) {
  // Memoize callback to prevent re-creating on every render
  const handleToggle = useCallback((id) => {
    onToggle(id);
  }, [onToggle]);

  // Only re-render if words actually change
  const wordElements = useMemo(() => {
    return words.map(word => (
      <VocabularyCard
        key={word.id}
        word={word}
        onToggle={handleToggle}
      />
    ));
  }, [words, handleToggle]);

  return <div>{wordElements}</div>;
}
```

#### Priority Components

1. **VocabularyLibrary** (1000+ items)
2. **ChunkedLearningPlayer** (frequent updates)
3. **VideoSelection** (list of videos)
4. **SubtitleDisplay** (rapid text changes)

#### Implementation Steps

1. Profile with React DevTools Profiler
2. Identify components with unnecessary re-renders
3. Add React.memo to presentational components
4. Add useCallback to event handlers
5. Add useMemo to expensive calculations
6. Re-profile and verify 40% reduction

#### Acceptance Criteria

- ✅ 40% reduction in re-renders (measured)
- ✅ No visual regressions
- ✅ Improved perceived smoothness

---

### ⚠️ HIGH-04: Increase Frontend Test Coverage to 60%

**Category**: Frontend / Quality
**Impact**: Higher confidence in refactoring
**Effort**: 20 hours
**Risk**: Low

#### Current State

- Frontend test coverage: **45%**
- Missing tests for critical flows
- Integration tests minimal

#### Target

- **60%+ coverage** (industry standard)
- All critical user flows tested
- Component integration tests

#### Implementation Strategy

**Week 1: Critical Flows (40% → 50%)**

```typescript
// tests/flows/authentication.test.tsx
describe('Authentication Flow', () => {
  it('should login successfully', async () => {
    render(<App />);

    // Navigate to login
    await userEvent.click(screen.getByText('Login'));

    // Fill form
    await userEvent.type(screen.getByLabelText('Email'), 'user@test.com');
    await userEvent.type(screen.getByLabelText('Password'), 'Password123!');

    // Submit
    await userEvent.click(screen.getByRole('button', { name: 'Login' }));

    // Assert redirect to dashboard
    await waitFor(() => {
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
    });
  });
});

// tests/flows/vocabulary-learning.test.tsx
describe('Vocabulary Learning Flow', () => {
  it('should complete vocabulary game', async () => {
    // Test full game flow
  });
});
```

**Week 2: Component Tests (50% → 55%)**

- Test all components in `components/ui/`
- Test auth components
- Test vocabulary components

**Week 3: Integration Tests (55% → 60%)**

- Test component interactions
- Test state management
- Test API client

#### Acceptance Criteria

- ✅ Coverage ≥ 60%
- ✅ All critical user flows have E2E tests
- ✅ All components have unit tests
- ✅ CI/CD blocks merges below 60%

---

### ⚠️ HIGH-05: Consolidate Duplicate API Clients

**Category**: Frontend / Maintainability
**Impact**: Reduced confusion, single source of truth
**Effort**: 6 hours
**Risk**: Medium (breaking change)

#### Problem

Two API client layers:

1. OpenAPI-generated client (`src/client/`)
2. Custom `api-client.ts` wrapper

Result: Confusion about which to use, duplicate code

#### Solution

Standardize on OpenAPI-generated client with custom interceptors:

```typescript
// src/client/api-config.ts
import { OpenAPI } from "./client";
import { getAuthToken } from "./utils/token-storage";

// Configure global OpenAPI client
OpenAPI.BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
OpenAPI.TOKEN = async () => {
  return getAuthToken() || "";
};

// Add global error handler
OpenAPI.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.status === 401) {
      // Redirect to login
      window.location.href = "/login";
    }
    throw error;
  },
);

// Export services
export * from "./client/services.gen";
export * from "./client/types.gen";
```

#### Implementation Steps

1. Create `api-config.ts` with OpenAPI configuration
2. Add request/response interceptors
3. Update all components to use OpenAPI client
4. Delete `api-client.ts`
5. Update imports across codebase
6. Test all API calls

#### Acceptance Criteria

- ✅ Single API client in use
- ✅ All interceptors working
- ✅ No import errors
- ✅ All API calls tested

---

### ⚠️ HIGH-06: Add Virtual Scrolling for Large Lists

**Category**: Frontend / Performance
**Impact**: Handle 10,000+ items smoothly
**Effort**: 8 hours
**Risk**: Low

#### Problem

- Vocabulary library renders all 1000+ words at once
- Performance degrades with large lists
- Scrolling stutters

#### Solution

Use react-window for virtual scrolling:

```typescript
// BEFORE
function VocabularyList({ words }) {
  return (
    <div>
      {words.map(word => <VocabularyCard key={word.id} word={word} />)}
    </div>
  );
}

// AFTER
import { FixedSizeList } from 'react-window';

function VocabularyList({ words }) {
  const Row = ({ index, style }) => (
    <div style={style}>
      <VocabularyCard word={words[index]} />
    </div>
  );

  return (
    <FixedSizeList
      height={600}
      itemCount={words.length}
      itemSize={80}
      width="100%"
    >
      {Row}
    </FixedSizeList>
  );
}
```

#### Components to Update

1. `VocabularyLibrary.tsx` (main priority)
2. `VideoSelection.tsx` (if many episodes)
3. `EpisodeSelection.tsx`

#### Acceptance Criteria

- ✅ Smooth scrolling with 10,000+ items
- ✅ Memory usage stable
- ✅ No visual regressions

---

### Additional High Priority Items (Summary)

- **HIGH-07**: Split large components (VocabularyLibrary, LearningPlayer)
- **HIGH-08**: Add request interceptors for auth
- **HIGH-09**: Standardize error handling
- **HIGH-10**: Add rate limiting to API
- **HIGH-11**: Implement retry logic for API calls
- **HIGH-12**: Add bundle size budget to CI/CD

---

## 3. Medium Priority (Quarter 1)

### ℹ️ MEDIUM-01: Implement RBAC (Role-Based Access Control)

**Category**: Backend / Security
**Impact**: Granular permissions beyond superuser flag
**Effort**: 24 hours

#### Current State

- Only `is_superuser` boolean
- No fine-grained permissions
- All users have same access

#### Solution

Add permission system:

```python
# Models
class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)  # e.g., "videos.create", "vocabulary.edit"
    description = Column(String)

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)  # e.g., "admin", "teacher", "student"
    permissions = relationship("Permission", secondary="role_permissions")

class User(Base):
    # ... existing fields ...
    roles = relationship("Role", secondary="user_roles")

# Permission checker
def require_permission(permission: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = get_current_user()
            if not user.has_permission(permission):
                raise HTTPException(403, "Insufficient permissions")
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@router.post("/videos")
@require_permission("videos.create")
async def create_video():
    ...
```

---

### ℹ️ MEDIUM-02: Add CDN Integration

**Category**: Infrastructure / Performance
**Impact**: Global performance, reduced bandwidth costs
**Effort**: 16 hours

#### Problem

- Videos served directly from backend
- No caching for static assets
- Poor performance for global users

#### Solution

Integrate CloudFront or Cloudflare CDN:

```python
# Backend/core/config.py
class Settings:
    cdn_url: str = Field(default="", env="CDN_URL")
    cdn_enabled: bool = Field(default=False, env="CDN_ENABLED")

# Backend/services/videoservice/video_url_service.py
def get_video_url(video_id: int) -> str:
    """Generate video URL with CDN if enabled."""
    if settings.cdn_enabled:
        return f"{settings.cdn_url}/videos/{video_id}.mp4"
    else:
        return f"{settings.api_url}/videos/{video_id}/stream"
```

#### Infrastructure

- **Development**: Direct serving
- **Production**: CloudFront with S3 origin

---

### ℹ️ MEDIUM-03: Refactor Anemic Domain Models

**Category**: Backend / Design
**Impact**: Better encapsulation, clearer business logic
**Effort**: 32 hours

#### Problem

Domain entities have no behavior:

```python
# Current - Anemic
class VocabularyWord:
    id: int
    text: str
    translation: str
    difficulty: str
    # No methods!

# Business logic scattered in services
def calculate_next_review(word):
    if word.knowledge_level == "learning":
        return datetime.now() + timedelta(days=1)
    # ...
```

#### Solution

Add business methods to domain entities:

```python
# Rich domain model
class VocabularyWord:
    id: int
    text: str
    translation: str
    difficulty: str
    knowledge_level: str
    last_reviewed: datetime

    def calculate_next_review(self) -> datetime:
        """Calculate next review date using SM-2 algorithm."""
        if self.knowledge_level == "learning":
            return self.last_reviewed + timedelta(days=1)
        elif self.knowledge_level == "reviewing":
            return self.last_reviewed + timedelta(days=3)
        else:
            return self.last_reviewed + timedelta(days=7)

    def mark_as_learned(self):
        """Mark word as learned and update knowledge level."""
        self.knowledge_level = "learned"
        self.last_reviewed = datetime.now()

    def is_due_for_review(self) -> bool:
        """Check if word is due for review."""
        return datetime.now() >= self.calculate_next_review()
```

---

### ℹ️ MEDIUM-04: Add Monitoring and Observability

**Category**: Infrastructure / Operations
**Impact**: Production insights, faster debugging
**Effort**: 24 hours

#### Solution

Integrate Sentry + DataDog/New Relic:

```python
# Backend monitoring
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=settings.sentry_dsn,
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
)

# Custom metrics
from prometheus_client import Counter, Histogram

api_requests = Counter('api_requests_total', 'Total API requests')
api_latency = Histogram('api_request_duration_seconds', 'API latency')

@router.get("/videos")
@api_latency.time()
async def get_videos():
    api_requests.inc()
    return videos
```

---

### Medium Priority Items (Summary)

- **MEDIUM-05**: Add integration tests with contract validation
- **MEDIUM-06**: Implement HLS/DASH streaming
- **MEDIUM-07**: Add database query optimization
- **MEDIUM-08**: Implement model caching (AI models loaded once)
- **MEDIUM-09**: Add batch processing for AI operations
- **MEDIUM-10**: Implement CSRF protection
- **MEDIUM-11**: Add API versioning (/api/v1/)
- **MEDIUM-12**: Create development environment automation (Makefile)
- **MEDIUM-13**: Add frontend error boundaries per feature
- **MEDIUM-14**: Implement state normalization
- **MEDIUM-15**: Add accessibility (WCAG 2.1 AA)
- **MEDIUM-16**: Add SEO optimization
- **MEDIUM-17**: Implement PWA features
- **MEDIUM-18**: Add multi-language UI support

---

## 4. Low Priority (Year 1)

### 🔮 LOW-01: Microservices Extraction (If Needed)

**Category**: Architecture / Scalability
**Impact**: Independent scaling of AI services
**Effort**: 120+ hours
**Risk**: High (major architectural change)

#### When to Consider

- If AI processing becomes bottleneck
- If different services need different scaling
- If team grows beyond 10 developers

#### Extraction Candidates

1. **Transcription Service** (Whisper, Parakeet)
2. **Translation Service** (NLLB, OPUS)
3. **Vocabulary Service** (SpaCy, filtering)

#### Implementation

```
Current Monolith:
┌─────────────────────────────┐
│      FastAPI Backend        │
│  ┌────┐ ┌────┐ ┌────┐      │
│  │ AI │ │API │ │ DB │      │
│  └────┘ └────┘ └────┘      │
└─────────────────────────────┘

After Microservices:
┌─────────────┐   ┌──────────────┐
│  API Gateway│   │Transcription │
│             ├───┤  Service     │
│             │   │  (Whisper)   │
├─────────────┤   └──────────────┘
│             │   ┌──────────────┐
│  FastAPI    ├───┤ Translation  │
│  Backend    │   │  Service     │
│             │   │  (NLLB)      │
└─────────────┘   └──────────────┘
       │
       │
   ┌───┴───┐
   │  DB   │
   └───────┘
```

---

### 🔮 LOW-02: GraphQL Layer (If Needed)

**Category**: API / Flexibility
**Impact**: Flexible frontend queries, reduced over-fetching
**Effort**: 80+ hours

#### When to Consider

- If frontend needs vary significantly
- If over-fetching becomes problem
- If mobile app is developed

#### Implementation

Add GraphQL layer alongside REST:

```python
# Backend/graphql/schema.py
import strawberry

@strawberry.type
class Vocabulary:
    id: int
    word: str
    translation: str
    difficulty: str

@strawberry.type
class Query:
    @strawberry.field
    async def vocabulary(self, word_id: int) -> Vocabulary:
        return await get_vocabulary(word_id)

schema = strawberry.Schema(query=Query)
```

---

### 🔮 LOW-03: Multi-Language Support

**Category**: Feature / Expansion
**Impact**: Support learning beyond German
**Effort**: 200+ hours

#### Implementation

- Add language pair management
- Support multiple source/target languages
- Expand AI model support
- Update vocabulary database schema

---

### Low Priority Items (Summary)

- **LOW-04**: Add video thumbnail generation
- **LOW-05**: Implement social features (sharing, leaderboards)
- **LOW-06**: Add mobile app (React Native)
- **LOW-07**: Implement offline mode (PWA)
- **LOW-08**: Add advanced analytics and reporting

---

## 5. Implementation Strategy

### Phase 1: Critical Fixes (Week 1)

```
Day 1-2: Fix @lru_cache bug + add transaction boundaries
Day 3-5: Split ChunkedLearningPlayer component
Day 6-7: Implement code splitting + bundle optimization
```

### Phase 2: High Priority (Weeks 2-4)

```
Week 2: Celery + Redis setup, cache layer
Week 3: Frontend performance optimization, virtual scrolling
Week 4: Test coverage, API client consolidation
```

### Phase 3: Medium Priority (Months 2-3)

```
Month 2: RBAC, monitoring, CDN integration
Month 3: Domain model refactoring, HLS streaming
```

### Phase 4: Low Priority (Months 4-12)

```
Ongoing: Consider microservices, GraphQL, multi-language
```

---

## 6. Risk Mitigation

### High-Risk Changes

1. **@lru_cache removal**: Test extensively in staging first
2. **Microservices**: Only if proven necessary
3. **Component splits**: Use feature flags for gradual rollout

### Rollback Strategy

- Feature flags for all major changes
- Database migrations reversible
- API versioning for breaking changes

### Testing Strategy

- Run full test suite before/after each change
- Performance testing for optimizations
- User acceptance testing for UI changes

---

## Success Metrics

### Technical Metrics

- Test coverage: 60% → 80%
- Bundle size: 2.5MB → < 1MB
- API p95 latency: 180ms → < 100ms
- Test isolation: 100% pass rate

### Business Metrics

- User satisfaction: Monitor NPS
- Performance: Time to Interactive < 2s
- Reliability: 99.9% uptime

---

## Appendix: Effort Estimation Model

**Estimation Formula**: `Base Hours × Complexity Factor × Risk Factor`

**Complexity Factors:**

- Simple (0.5x): Configuration, small refactors
- Medium (1.0x): Component splits, new features
- Complex (2.0x): Architecture changes, migrations

**Risk Factors:**

- Low (1.0x): Well-understood, isolated changes
- Medium (1.5x): Some unknowns, integration required
- High (2.0x): Major architectural changes, production risk

---

**Document Status**: ✅ Ready for Implementation
**Next Review**: 2025-11-02 (Monthly)
**Owner**: Architecture Team
