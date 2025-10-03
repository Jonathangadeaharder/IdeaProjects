# Phase 2: Infrastructure Setup & Optimizations

**Timeline**: Month 1 (4 weeks)
**Team**: 2-3 Engineers
**Priority**: HIGH
**Status**: Ready for Implementation

---

## Overview

Phase 2 focuses on scalability and performance through infrastructure improvements:

1. Redis caching layer
2. Celery async task queue
3. Frontend performance optimizations
4. API improvements

---

## 1. Redis Setup (Week 1, Days 1-2)

### Docker Compose (Development)

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
    command: redis-server --appendonly yes

volumes:
  redis_data:
```

### Backend Configuration

```python
# Backend/core/config.py
class Settings:
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_enabled: bool = Field(default=True, env="REDIS_ENABLED")
```

### Start Redis

```bash
docker-compose -f docker-compose.redis.yml up -d
```

---

## 2. Celery Setup (Week 1, Days 3-5)

### Installation

```bash
cd Backend
pip install celery[redis]==5.3.4
pip freeze > requirements.txt
```

### Celery Configuration

```python
# Backend/core/celery_app.py
from celery import Celery
from core.config import settings

celery_app = Celery(
    'langplug',
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
)
```

### Create Tasks

```python
# Backend/tasks/video_tasks.py
from core.celery_app import celery_app
from services.processing.chunk_processor import ChunkProcessingService

@celery_app.task(bind=True)
async def transcribe_video_task(self, video_id: int, user_id: int):
    """Background task for video transcription"""
    try:
        service = ChunkProcessingService()
        result = await service.process_chunk(...)

        # Update task progress
        self.update_state(
            state='PROGRESS',
            meta={'progress': 50, 'message': 'Transcribing...'}
        )

        return {'status': 'completed', 'video_id': video_id}
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise
```

### Start Celery Worker

```bash
# Development
celery -A core.celery_app worker --loglevel=info

# Production (with supervisor)
celery -A core.celery_app worker \
  --loglevel=info \
  --concurrency=4 \
  --max-tasks-per-child=100
```

---

## 3. Redis Caching Layer (Week 2, Days 1-3)

### Caching Decorator

```python
# Backend/core/caching.py
import json
import redis.asyncio as redis
from functools import wraps

redis_client = redis.Redis.from_url(settings.redis_url)

def cached(ttl: int = 3600, key_prefix: str = ""):
    """Cache decorator with TTL"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash((args, tuple(kwargs.items())))}"

            # Check cache
            cached_value = await redis_client.get(cache_key)
            if cached_value:
                return json.loads(cached_value)

            # Compute value
            result = await func(*args, **kwargs)

            # Store in cache
            await redis_client.setex(
                cache_key,
                ttl,
                json.dumps(result, default=str)
            )

            return result
        return wrapper
    return decorator
```

### Apply Caching

```python
# Backend/services/vocabulary_service.py
@cached(ttl=3600, key_prefix="vocabulary")
async def get_vocabulary_word(word_id: int):
    return await repo.get_by_id(word_id)

@cached(ttl=86400, key_prefix="translation")
async def translate_text(text: str, source: str, target: str):
    return await translation_service.translate(text, source, target)
```

---

## 4. API Improvements (Week 2, Days 4-5)

### Rate Limiting

```bash
pip install slowapi==0.1.9
```

```python
# Backend/core/middleware.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Apply to routes
@router.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request):
    ...
```

### API Consolidation (Frontend)

```typescript
// src/client/api-config.ts
import { OpenAPI } from "./client";

// Configure OpenAPI client
OpenAPI.BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
OpenAPI.TOKEN = async () => getAuthToken() || "";

// Add interceptors
OpenAPI.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.status === 401) {
      window.location.href = "/login";
    }
    throw error;
  },
);
```

---

## 5. Frontend Performance (Week 3)

### React.memo for List Items

```typescript
// Before
function VocabularyCard({ word }: Props) {
  return <Card>{word.text}</Card>;
}

// After
export const VocabularyCard = memo(({ word }: Props) => {
  return <Card>{word.text}</Card>;
});
```

### useCallback for Event Handlers

```typescript
// Before
function VocabularyList({ words, onToggle }) {
  return words.map(word => (
    <VocabularyCard
      key={word.id}
      word={word}
      onToggle={() => onToggle(word.id)}  // New function every render!
    />
  ));
}

// After
function VocabularyList({ words, onToggle }) {
  const handleToggle = useCallback((id: number) => {
    onToggle(id);
  }, [onToggle]);

  return words.map(word => (
    <VocabularyCard
      key={word.id}
      word={word}
      onToggle={handleToggle}  // Stable reference
    />
  ));
}
```

### Virtual Scrolling

```bash
npm install react-window@1.8.10
```

```typescript
import { FixedSizeList } from 'react-window';

function VocabularyLibrary({ words }) {
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

---

## 6. Testing & Validation (Week 4)

### Redis Tests

```python
@pytest.mark.asyncio
async def test_caching_works():
    @cached(ttl=60)
    async def expensive_operation():
        return "expensive_result"

    # First call - cache miss
    result1 = await expensive_operation()
    # Second call - cache hit
    result2 = await expensive_operation()

    assert result1 == result2
```

### Celery Tests

```python
@pytest.mark.asyncio
async def test_async_task_processing():
    task = transcribe_video_task.delay(video_id=1, user_id=1)

    # Wait for task completion
    result = task.get(timeout=10)

    assert result['status'] == 'completed'
```

### Performance Tests

```typescript
it('should render 10,000 items smoothly', async () => {
  const words = Array.from({ length: 10000 }, (_, i) => ({
    id: i,
    text: `word-${i}`,
  }));

  render(<VocabularyLibrary words={words} />);

  // Should render without freezing
  expect(screen.getAllByRole('listitem')).toHaveLength(10);  // Virtual scrolling shows 10
});
```

---

## Success Metrics

| Metric                      | Before   | Target  | After    |
| --------------------------- | -------- | ------- | -------- |
| **API Response Time (p95)** | 180ms    | < 100ms | TBD      |
| **Cache Hit Rate**          | 0%       | > 60%   | TBD      |
| **Video Processing Time**   | 2-5 min  | < 30s   | TBD      |
| **Frontend Re-renders**     | Baseline | -40%    | TBD      |
| **Bundle Size**             | 2.5MB    | < 1MB   | ✅ 800KB |

---

## Deployment Checklist

### Development

- [ ] Redis running in Docker
- [ ] Celery worker running
- [ ] Tests passing (Redis, Celery, caching)
- [ ] Performance profiling complete

### Production

- [ ] Redis cluster configured (AWS ElastiCache)
- [ ] Celery workers on separate servers
- [ ] Monitoring dashboards (Celery Flower, Redis metrics)
- [ ] Auto-scaling configured
- [ ] Backup strategy for Redis data

---

## Rollback Plan

If issues arise:

1. **Redis**: Feature flag to bypass cache
2. **Celery**: Keep synchronous endpoints as fallback
3. **Frontend**: Revert to non-memoized components
4. **Monitoring**: Alert on performance degradation

---

**Status**: Ready for Implementation
**Next Steps**: Begin Week 1 with Redis setup
**Owner**: Infrastructure + Backend + Frontend Teams
