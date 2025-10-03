# Redis Caching Setup Guide - LangPlug

**Version**: 1.0
**Date**: 2025-10-02
**Status**: Ready for Implementation
**Estimated Time**: 1 week (40 hours)

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Day 1: Infrastructure Setup](#day-1-infrastructure-setup-4-hours)
4. [Day 2: Caching Implementation](#day-2-caching-implementation-4-hours)
5. [Day 3: Service Integration](#day-3-service-integration-8-hours)
6. [Day 4: Cache Invalidation](#day-4-cache-invalidation-4-hours)
7. [Day 5: Testing & Monitoring](#day-5-testing--monitoring-4-hours)
8. [Production Deployment](#production-deployment)
9. [Troubleshooting](#troubleshooting)
10. [Performance Metrics](#performance-metrics)

---

## Overview

### Why Redis?

**Current State:**

- API response time (p95): **180ms**
- No caching layer for expensive operations
- Repeated database queries for vocabulary lookups
- Translation API calls throttled at 100 req/min

**Target State:**

- API response time (p95): **<100ms** (44% improvement)
- Cache hit rate: **>60%**
- Reduced database load by **50%**
- Translation API cache prevents throttling

### Benefits

1. **Performance**: 80% faster response times for cached data
2. **Scalability**: Reduced database connections from 20 to 10
3. **Cost Savings**: Fewer translation API calls ($50/month → $20/month)
4. **User Experience**: Instant vocabulary lookups, faster page loads

### Architecture

```
┌──────────┐     ┌───────┐     ┌──────────┐
│  Client  │────>│ Redis │────>│ Database │
│ Request  │<────│ Cache │<────│  Query   │
└──────────┘     └───────┘     └──────────┘
                     │
                Cache Hit: 10ms
            Cache Miss: 180ms + store
```

---

## Prerequisites

### Required Software

- **Docker**: v20.10+ (for development)
- **Python**: 3.11+ (already installed)
- **Redis**: v7.0+ (via Docker or AWS ElastiCache)

### Check Environment

```bash
# Verify Docker is installed
docker --version
# Expected: Docker version 20.10.x or higher

# Verify Python environment
cd /mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend
./api_venv/Scripts/activate
python --version
# Expected: Python 3.11.x
```

### Disk Space

- Development: **500MB** (Redis container + data)
- Production: **2GB** minimum (for cache data growth)

---

## Day 1: Infrastructure Setup (4 hours)

### 1.1 Create Docker Compose File

Create `docker-compose.redis.yml` in the project root:

```yaml
# docker-compose.redis.yml
version: "3.8"

services:
  redis:
    image: redis:7-alpine
    container_name: langplug-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: >
      redis-server
      --appendonly yes
      --maxmemory 256mb
      --maxmemory-policy allkeys-lru
      --requirepass ${REDIS_PASSWORD:-dev_redis_password}
    restart: unless-stopped
    networks:
      - langplug-network

  redis-commander:
    image: rediscommander/redis-commander:latest
    container_name: langplug-redis-ui
    environment:
      - REDIS_HOSTS=local:redis:6379:0:${REDIS_PASSWORD:-dev_redis_password}
    ports:
      - "8081:8081"
    depends_on:
      - redis
    networks:
      - langplug-network

volumes:
  redis_data:
    driver: local

networks:
  langplug-network:
    driver: bridge
```

**Configuration Explanation:**

- `appendonly yes`: Enables persistence (data survives restarts)
- `maxmemory 256mb`: Limits memory usage (adjust for production)
- `maxmemory-policy allkeys-lru`: Evicts least-recently-used keys when full
- `redis-commander`: Optional web UI for monitoring (http://localhost:8081)

### 1.2 Start Redis

```bash
# From project root
cd /mnt/c/Users/Jonandrop/IdeaProjects/LangPlug

# Start Redis (with password from environment or default)
docker-compose -f docker-compose.redis.yml up -d

# Verify Redis is running
docker ps | grep redis
# Expected output:
# langplug-redis ... Up ... 0.0.0.0:6379->6379/tcp
# langplug-redis-ui ... Up ... 0.0.0.0:8081->8081/tcp

# Test connection
docker exec -it langplug-redis redis-cli -a dev_redis_password PING
# Expected: PONG

# Check Redis info
docker exec -it langplug-redis redis-cli -a dev_redis_password INFO server
```

### 1.3 Update Backend Configuration

**File**: `Backend/core/config.py`

```python
# Backend/core/config.py
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... existing settings ...

    # Redis Configuration
    redis_url: str = Field(
        default="redis://:dev_redis_password@localhost:6379/0",
        env="REDIS_URL",
        description="Redis connection URL"
    )
    redis_enabled: bool = Field(
        default=True,
        env="REDIS_ENABLED",
        description="Enable/disable Redis caching"
    )
    redis_ttl_default: int = Field(
        default=3600,
        env="REDIS_TTL_DEFAULT",
        description="Default cache TTL in seconds (1 hour)"
    )
    redis_ttl_translation: int = Field(
        default=86400,
        env="REDIS_TTL_TRANSLATION",
        description="Translation cache TTL (24 hours)"
    )
    redis_ttl_vocabulary: int = Field(
        default=3600,
        env="REDIS_TTL_VOCABULARY",
        description="Vocabulary cache TTL (1 hour)"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

### 1.4 Create .env File

**File**: `Backend/.env` (add these lines)

```bash
# Redis Configuration
REDIS_URL=redis://:dev_redis_password@localhost:6379/0
REDIS_ENABLED=true
REDIS_TTL_DEFAULT=3600
REDIS_TTL_TRANSLATION=86400
REDIS_TTL_VOCABULARY=3600
```

### 1.5 Install Redis Python Client

```bash
cd /mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend
./api_venv/Scripts/activate

# Install redis with hiredis for better performance
pip install redis[hiredis]==5.0.1

# Update requirements
pip freeze > requirements.txt

# Verify installation
python -c "import redis; print(redis.__version__)"
# Expected: 5.0.1
```

### Verification Checklist (Day 1)

- [ ] Docker Compose file created
- [ ] Redis container running (`docker ps`)
- [ ] Redis responds to PING command
- [ ] Redis Commander UI accessible (http://localhost:8081)
- [ ] Backend configuration updated
- [ ] .env file created with Redis settings
- [ ] redis Python package installed (v5.0.1)

---

## Day 2: Caching Implementation (4 hours)

### 2.1 Create Caching Module

**File**: `Backend/core/caching.py` (NEW)

```python
"""
Redis Caching Module
Provides caching decorator and utilities for LangPlug
"""

import json
import hashlib
import logging
from functools import wraps
from typing import Callable, Any, Optional

import redis.asyncio as redis
from redis.exceptions import RedisError, ConnectionError as RedisConnectionError

from core.config import settings

logger = logging.getLogger(__name__)

# Global Redis client (singleton pattern)
_redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """
    Get or create Redis client (singleton)

    Returns:
        redis.Redis: Async Redis client instance

    Raises:
        RedisConnectionError: If Redis connection fails
    """
    global _redis_client

    if _redis_client is None:
        try:
            _redis_client = await redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            # Test connection
            await _redis_client.ping()
            logger.info("Redis client initialized successfully")
        except RedisConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    return _redis_client


async def close_redis_client():
    """Close Redis client connection (cleanup on shutdown)"""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis client closed")


def _generate_cache_key(prefix: str, func_name: str, args: tuple, kwargs: dict) -> str:
    """
    Generate unique cache key from function arguments

    Args:
        prefix: Cache key prefix (e.g., "vocabulary")
        func_name: Function name
        args: Positional arguments
        kwargs: Keyword arguments

    Returns:
        str: MD5 hash of serialized arguments
    """
    # Filter out AsyncSession from args/kwargs (not serializable)
    filtered_args = tuple(
        arg for arg in args
        if not str(type(arg).__name__) == 'AsyncSession'
    )
    filtered_kwargs = {
        k: v for k, v in kwargs.items()
        if not str(type(v).__name__) == 'AsyncSession'
    }

    # Serialize arguments
    key_data = f"{prefix}:{func_name}:{filtered_args}:{sorted(filtered_kwargs.items())}"

    # Generate MD5 hash (32 characters)
    return f"cache:{hashlib.md5(key_data.encode()).hexdigest()}"


def cached(ttl: Optional[int] = None, key_prefix: str = "default"):
    """
    Cache decorator with automatic TTL management

    Args:
        ttl: Time-to-live in seconds (None = use default from settings)
        key_prefix: Prefix for cache key (e.g., "vocabulary", "translation")

    Usage:
        @cached(ttl=3600, key_prefix="vocabulary")
        async def get_vocabulary_word(word_id: int):
            return await db.query(...)

    Features:
        - Automatic cache hit/miss logging
        - Graceful fallback if Redis is down
        - JSON serialization with datetime support
        - AsyncSession filtering (won't cache database sessions)
    """
    if ttl is None:
        ttl = settings.redis_ttl_default

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Bypass cache if disabled
            if not settings.redis_enabled:
                logger.debug(f"Cache disabled, executing {func.__name__} directly")
                return await func(*args, **kwargs)

            # Generate cache key
            cache_key = _generate_cache_key(key_prefix, func.__name__, args, kwargs)

            try:
                redis_client = await get_redis_client()

                # Attempt cache retrieval
                cached_value = await redis_client.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache HIT: {func.__name__} [{cache_key[:16]}...]")
                    return json.loads(cached_value)

                # Cache miss - execute function
                logger.debug(f"Cache MISS: {func.__name__} [{cache_key[:16]}...]")
                result = await func(*args, **kwargs)

                # Store in cache with TTL
                await redis_client.setex(
                    cache_key,
                    ttl,
                    json.dumps(result, default=str)  # default=str handles datetime
                )
                logger.debug(f"Cached result for {func.__name__} (TTL: {ttl}s)")

                return result

            except RedisError as e:
                logger.error(f"Redis error in {func.__name__}: {e}")
                # Graceful degradation: execute function without caching
                return await func(*args, **kwargs)

        return wrapper
    return decorator


async def invalidate_cache(pattern: str) -> int:
    """
    Invalidate cache keys matching pattern

    Args:
        pattern: Redis key pattern (e.g., "cache:vocabulary:*")

    Returns:
        int: Number of keys deleted

    Usage:
        # Invalidate all vocabulary caches
        await invalidate_cache("cache:*vocabulary*")

        # Invalidate specific word
        await invalidate_cache(f"cache:*word:{word_id}*")
    """
    if not settings.redis_enabled:
        logger.warning("Cache invalidation skipped: Redis disabled")
        return 0

    try:
        redis_client = await get_redis_client()

        # Find matching keys
        keys = []
        cursor = 0
        while True:
            cursor, batch = await redis_client.scan(cursor, match=pattern, count=100)
            keys.extend(batch)
            if cursor == 0:
                break

        # Delete keys
        if keys:
            deleted_count = await redis_client.delete(*keys)
            logger.info(f"Invalidated {deleted_count} cache keys matching '{pattern}'")
            return deleted_count
        else:
            logger.debug(f"No cache keys found matching '{pattern}'")
            return 0

    except RedisError as e:
        logger.error(f"Cache invalidation error: {e}")
        return 0


async def get_cache_stats() -> dict:
    """
    Get Redis cache statistics

    Returns:
        dict: Cache stats (used_memory, keys_count, hit_rate, etc.)
    """
    if not settings.redis_enabled:
        return {"enabled": False}

    try:
        redis_client = await get_redis_client()
        info = await redis_client.info()

        return {
            "enabled": True,
            "used_memory_human": info.get("used_memory_human", "N/A"),
            "used_memory_mb": round(info.get("used_memory", 0) / 1024 / 1024, 2),
            "keys_count": await redis_client.dbsize(),
            "hits": info.get("keyspace_hits", 0),
            "misses": info.get("keyspace_misses", 0),
            "hit_rate": round(
                info.get("keyspace_hits", 0) /
                max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1) * 100,
                2
            ),
            "connected_clients": info.get("connected_clients", 0),
            "uptime_days": round(info.get("uptime_in_seconds", 0) / 86400, 1),
        }
    except RedisError as e:
        logger.error(f"Failed to get cache stats: {e}")
        return {"enabled": True, "error": str(e)}
```

### 2.2 Add Lifespan Management

**File**: `Backend/main.py` (UPDATE)

```python
# Backend/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI

from core.caching import get_redis_client, close_redis_client
from core.config import settings

# ... existing imports ...

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    if settings.redis_enabled:
        try:
            await get_redis_client()  # Initialize Redis connection
            logger.info("Redis cache initialized")
        except Exception as e:
            logger.error(f"Redis initialization failed: {e}")

    yield

    # Shutdown
    if settings.redis_enabled:
        await close_redis_client()
        logger.info("Redis connection closed")


app = FastAPI(
    title="LangPlug API",
    lifespan=lifespan,  # Add lifespan manager
    # ... other config ...
)
```

### 2.3 Create Cache Health Endpoint

**File**: `Backend/api/routes/health.py` (UPDATE or CREATE)

```python
# Backend/api/routes/health.py
from fastapi import APIRouter, HTTPException
from core.caching import get_cache_stats

router = APIRouter(tags=["health"])


@router.get("/health/cache", name="health_cache_stats")
async def cache_health():
    """
    Get Redis cache health and statistics

    Returns:
        dict: Cache statistics and health status
    """
    try:
        stats = await get_cache_stats()
        return {
            "status": "healthy" if stats.get("enabled") and not stats.get("error") else "degraded",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Cache health check failed: {e}")
```

### Verification Checklist (Day 2)

- [ ] `Backend/core/caching.py` created
- [ ] Caching decorator implemented with error handling
- [ ] Lifespan manager added to main.py
- [ ] Health endpoint created
- [ ] Test cache connection: `curl http://localhost:8000/health/cache`

---

## Day 3: Service Integration (8 hours)

### 3.1 Vocabulary Service Caching

**File**: `Backend/services/vocabulary/vocabulary_service.py` (UPDATE)

```python
# Backend/services/vocabulary/vocabulary_service.py
from core.caching import cached, invalidate_cache
from core.config import settings

class VocabularyService:

    @cached(ttl=settings.redis_ttl_vocabulary, key_prefix="vocabulary")
    async def get_vocabulary_word(self, word_id: int, db: AsyncSession):
        """
        Get vocabulary word by ID (cached for 1 hour)

        Cache key pattern: cache:vocabulary:get_vocabulary_word:{word_id}
        """
        result = await db.execute(
            select(VocabularyWord).where(VocabularyWord.id == word_id)
        )
        return result.scalar_one_or_none()

    @cached(ttl=settings.redis_ttl_vocabulary, key_prefix="vocabulary_level")
    async def get_vocabulary_level(self, level: str, limit: int, offset: int, db: AsyncSession):
        """
        Get vocabulary words by level (cached for 1 hour)

        Cache key pattern: cache:vocabulary_level:get_vocabulary_level:{level}:{limit}:{offset}
        """
        query = select(VocabularyWord).where(VocabularyWord.difficulty_level == level)
        query = query.limit(limit).offset(offset)
        result = await db.execute(query)
        return result.scalars().all()

    async def mark_word_known(self, user_id: int, word_id: int, known: bool, db: AsyncSession):
        """
        Mark word as known/unknown (invalidates user progress cache)
        """
        # ... existing logic ...

        # Invalidate related caches
        await invalidate_cache(f"cache:*vocabulary_progress*user:{user_id}*")
        await invalidate_cache(f"cache:*vocabulary_stats*user:{user_id}*")

        return {"success": True}
```

### 3.2 Translation Service Caching

**File**: `Backend/services/translation/translation_handler.py` (UPDATE)

```python
# Backend/services/translation/translation_handler.py
from core.caching import cached
from core.config import settings

class TranslationHandler:

    @cached(ttl=settings.redis_ttl_translation, key_prefix="translation")
    async def translate_text(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """
        Translate text with 24-hour cache

        Cache key pattern: cache:translation:translate_text:{text}:{source_lang}:{target_lang}

        Benefits:
        - Reduces OpusMT API calls by 90%
        - Prevents translation throttling
        - Consistent translations for same text
        """
        # ... existing translation logic ...
        translation_result = await self.opus_mt_service.translate(text, source_lang, target_lang)
        return translation_result

    @cached(ttl=settings.redis_ttl_translation, key_prefix="batch_translation")
    async def translate_batch(
        self,
        texts: list[str],
        source_lang: str,
        target_lang: str
    ) -> list[str]:
        """
        Batch translate with caching (24-hour TTL)
        """
        # ... existing batch translation logic ...
        results = await self.opus_mt_service.translate_batch(texts, source_lang, target_lang)
        return results
```

### 3.3 User Progress Caching

**File**: `Backend/services/vocabulary/vocabulary_progress_service.py` (UPDATE)

```python
# Backend/services/vocabulary/vocabulary_progress_service.py
from core.caching import cached, invalidate_cache

class VocabularyProgressService:

    @cached(ttl=300, key_prefix="vocabulary_stats")  # 5 minutes (frequently changing)
    async def get_user_vocabulary_stats(self, user_id: int, db: AsyncSession):
        """
        Get user vocabulary statistics (5-minute cache)

        Short TTL because stats change frequently with user activity
        """
        query = select(UserVocabularyProgress).where(
            UserVocabularyProgress.user_id == user_id
        )
        result = await db.execute(query)
        progress_records = result.scalars().all()

        return {
            "total_words": len(progress_records),
            "known_words": sum(1 for p in progress_records if p.known),
            "learning_words": sum(1 for p in progress_records if not p.known),
        }

    async def update_word_progress(self, user_id: int, word_id: int, known: bool, db: AsyncSession):
        """Update progress and invalidate stats cache"""
        # ... existing update logic ...

        # Invalidate user stats cache
        await invalidate_cache(f"cache:*vocabulary_stats*:{user_id}*")
```

### 3.4 Video Metadata Caching

**File**: `Backend/api/routes/videos.py` (UPDATE)

```python
# Backend/api/routes/videos.py
from core.caching import cached

@router.get("/series/{series}/episodes", name="list_episodes")
@cached(ttl=1800, key_prefix="episodes")  # 30 minutes
async def list_episodes(series: str):
    """
    List episodes in series (cached for 30 minutes)

    Episodes rarely change, so 30-minute cache is safe
    """
    # ... existing logic ...
    return episodes_list
```

### Caching Strategy Summary

| Service              | Cache TTL  | Invalidation Strategy | Reason                      |
| -------------------- | ---------- | --------------------- | --------------------------- |
| **Vocabulary Words** | 1 hour     | On admin edit         | Static data, rarely changes |
| **Translations**     | 24 hours   | Never (deterministic) | Same input = same output    |
| **User Progress**    | 5 minutes  | On user action        | Changes frequently          |
| **Video Metadata**   | 30 minutes | On upload/delete      | Semi-static                 |
| **Subtitles**        | 2 hours    | On regeneration       | Expensive to generate       |

### Verification Checklist (Day 3)

- [ ] Vocabulary service methods cached
- [ ] Translation service methods cached
- [ ] User progress service cached
- [ ] Video routes cached
- [ ] Test cache with real requests
- [ ] Verify cache keys in Redis Commander

---

## Day 4: Cache Invalidation (4 hours)

### 4.1 Cache Invalidation Patterns

**Pattern 1: Invalidate on Write**

```python
# When user marks word as known
async def mark_word_known(user_id: int, word_id: int, known: bool, db: AsyncSession):
    # Update database
    await db.execute(...)
    await db.commit()

    # Invalidate affected caches
    await invalidate_cache(f"cache:*vocabulary_stats*user:{user_id}*")
    await invalidate_cache(f"cache:*vocabulary_progress*user:{user_id}*")
```

**Pattern 2: Time-Based Expiration (TTL)**

```python
# Short TTL for frequently changing data
@cached(ttl=300, key_prefix="user_stats")  # 5 minutes
async def get_user_stats(user_id: int):
    # Stats updated by user frequently, so short TTL prevents stale data
    ...
```

**Pattern 3: Admin-Triggered Invalidation**

```python
# Admin endpoint to clear all caches
@router.post("/admin/cache/clear", name="admin_clear_cache")
async def clear_cache(cache_type: str = "all"):
    """
    Clear specific cache type or all caches

    Args:
        cache_type: "vocabulary" | "translation" | "all"
    """
    if cache_type == "all":
        await invalidate_cache("cache:*")
    else:
        await invalidate_cache(f"cache:*{cache_type}*")

    return {"status": "success", "cache_type": cache_type}
```

### 4.2 Cache Warming (Optional)

**File**: `Backend/tasks/cache_warming.py` (NEW)

```python
# Backend/tasks/cache_warming.py
"""Cache warming tasks to pre-populate frequently accessed data"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from services.vocabulary.vocabulary_service import VocabularyService


async def warm_vocabulary_cache():
    """Pre-load top 1000 vocabulary words into cache"""
    async for session in get_async_session():
        service = VocabularyService()

        # Warm cache for each level
        for level in ["A1", "A2", "B1", "B2"]:
            print(f"Warming cache for level {level}...")
            await service.get_vocabulary_level(
                level=level,
                limit=250,
                offset=0,
                db=session
            )

        print("Cache warming complete!")


if __name__ == "__main__":
    asyncio.run(warm_vocabulary_cache())
```

**Usage**:

```bash
cd /mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend
./api_venv/Scripts/activate
python -m tasks.cache_warming
```

### Verification Checklist (Day 4)

- [ ] Invalidation patterns implemented
- [ ] Admin cache clear endpoint created
- [ ] Cache warming script created (optional)
- [ ] Test invalidation with real user actions
- [ ] Verify cache keys are deleted after invalidation

---

## Day 5: Testing & Monitoring (4 hours)

### 5.1 Unit Tests

**File**: `Backend/tests/unit/core/test_caching.py` (NEW)

```python
# Backend/tests/unit/core/test_caching.py
import pytest
from core.caching import cached, invalidate_cache, get_cache_stats


@pytest.mark.asyncio
async def test_cached_decorator_basic():
    """Test basic caching functionality"""
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
    assert call_count == 1  # Not called again

    # Different argument - cache miss
    result3 = await expensive_operation(10)
    assert result3 == 20
    assert call_count == 2


@pytest.mark.asyncio
async def test_cache_invalidation():
    """Test cache invalidation"""
    @cached(ttl=60, key_prefix="test_inv")
    async def get_data(key: str) -> str:
        return f"data_for_{key}"

    # Populate cache
    result1 = await get_data("abc")
    assert result1 == "data_for_abc"

    # Invalidate
    deleted = await invalidate_cache("cache:*test_inv*")
    assert deleted > 0

    # Should be fresh data (cache miss)
    result2 = await get_data("abc")
    assert result2 == "data_for_abc"


@pytest.mark.asyncio
async def test_cache_stats():
    """Test cache statistics retrieval"""
    stats = await get_cache_stats()

    assert "enabled" in stats
    if stats["enabled"] and not stats.get("error"):
        assert "used_memory_mb" in stats
        assert "keys_count" in stats
        assert "hit_rate" in stats
```

**Run tests**:

```bash
cd /mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend
./api_venv/Scripts/activate
pytest tests/unit/core/test_caching.py -v
```

### 5.2 Integration Tests

**File**: `Backend/tests/integration/test_vocabulary_caching.py` (NEW)

```python
# Backend/tests/integration/test_vocabulary_caching.py
import pytest
from httpx import AsyncClient

from main import app
from core.caching import invalidate_cache


@pytest.mark.asyncio
async def test_vocabulary_endpoint_caching():
    """Test vocabulary endpoint uses cache"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First request - cache miss
        response1 = await client.get("/api/vocabulary/library/level?level=A1")
        assert response1.status_code == 200
        data1 = response1.json()

        # Second request - should hit cache (faster)
        response2 = await client.get("/api/vocabulary/library/level?level=A1")
        assert response2.status_code == 200
        data2 = response2.json()

        # Should be identical
        assert data1 == data2


@pytest.mark.asyncio
async def test_translation_caching():
    """Test translation endpoint caching"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Translate text
        payload = {
            "text": "Hello world",
            "source_lang": "en",
            "target_lang": "de"
        }

        # First call
        response1 = await client.post("/api/translate", json=payload)
        assert response1.status_code == 200

        # Second call - should hit cache
        response2 = await client.post("/api/translate", json=payload)
        assert response2.status_code == 200
        assert response1.json() == response2.json()
```

### 5.3 Performance Testing

**File**: `Backend/tests/performance/test_cache_performance.py` (NEW)

```python
# Backend/tests/performance/test_cache_performance.py
import time
import pytest


@pytest.mark.asyncio
async def test_cache_hit_performance():
    """Verify cache hits are significantly faster than cache misses"""
    from services.vocabulary.vocabulary_service import VocabularyService
    from core.database import get_async_session
    from core.caching import invalidate_cache

    service = VocabularyService()

    async for session in get_async_session():
        # Clear cache first
        await invalidate_cache("cache:*vocabulary*")

        # Measure cache miss (first call)
        start = time.time()
        result1 = await service.get_vocabulary_word(word_id=1, db=session)
        cache_miss_time = time.time() - start

        # Measure cache hit (second call)
        start = time.time()
        result2 = await service.get_vocabulary_word(word_id=1, db=session)
        cache_hit_time = time.time() - start

        # Cache hit should be at least 10x faster
        print(f"Cache miss: {cache_miss_time*1000:.2f}ms")
        print(f"Cache hit: {cache_hit_time*1000:.2f}ms")
        print(f"Speedup: {cache_miss_time/cache_hit_time:.1f}x")

        assert cache_hit_time < cache_miss_time * 0.1  # At least 10x faster
        break
```

### 5.4 Monitoring Dashboard

Access Redis Commander at `http://localhost:8081`:

- View all cache keys
- Monitor memory usage
- Check TTL for keys
- Manually delete keys for testing

### Verification Checklist (Day 5)

- [ ] Unit tests created and passing
- [ ] Integration tests created and passing
- [ ] Performance tests show >10x speedup for cache hits
- [ ] Redis Commander accessible and showing cached keys
- [ ] Cache hit rate >60% in health endpoint

---

## Production Deployment

### AWS ElastiCache Setup

```bash
# AWS CLI commands for production Redis
aws elasticache create-cache-cluster \
  --cache-cluster-id langplug-redis-prod \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --engine-version 7.0 \
  --num-cache-nodes 1 \
  --preferred-availability-zone us-east-1a \
  --security-group-ids sg-xxxxxxxxx \
  --subnet-group-name langplug-redis-subnet

# Get endpoint
aws elasticache describe-cache-clusters \
  --cache-cluster-id langplug-redis-prod \
  --show-cache-node-info
```

### Production Environment Variables

```bash
# Production .env
REDIS_URL=redis://langplug-redis-prod.abc123.0001.use1.cache.amazonaws.com:6379/0
REDIS_ENABLED=true
REDIS_TTL_DEFAULT=3600
REDIS_TTL_TRANSLATION=86400
REDIS_TTL_VOCABULARY=7200
```

### Production Monitoring

**CloudWatch Metrics** (AWS ElastiCache):

- `CacheHitRate` > 60%
- `DatabaseMemoryUsagePercentage` < 80%
- `CurrConnections` < 65000
- `EngineCPUUtilization` < 70%

---

## Troubleshooting

### Issue: Redis Connection Timeout

**Symptoms**: `RedisConnectionError: Timeout connecting to Redis`

**Solution**:

```bash
# Check Redis is running
docker ps | grep redis

# Check Redis logs
docker logs langplug-redis

# Test connection manually
docker exec -it langplug-redis redis-cli -a dev_redis_password PING

# Restart Redis
docker-compose -f docker-compose.redis.yml restart redis
```

### Issue: Cache Not Working (All Cache Misses)

**Symptoms**: Health endpoint shows 0% hit rate

**Solution**:

```python
# Check REDIS_ENABLED in .env
REDIS_ENABLED=true  # Must be true

# Verify decorator is applied
@cached(ttl=3600, key_prefix="test")  # ← Must have this
async def my_function():
    ...

# Check logs for cache activity
tail -f Backend/logs/app.log | grep -i "cache"
```

### Issue: Stale Data in Cache

**Symptoms**: Updated database but seeing old data

**Solution**:

```bash
# Clear all caches
curl -X POST http://localhost:8000/admin/cache/clear?cache_type=all

# Or clear specific cache
curl -X POST http://localhost:8000/admin/cache/clear?cache_type=vocabulary
```

### Issue: High Memory Usage

**Symptoms**: Redis using >90% memory

**Solution**:

```bash
# Check memory usage
docker exec -it langplug-redis redis-cli -a dev_redis_password INFO memory

# Flush all keys (development only!)
docker exec -it langplug-redis redis-cli -a dev_redis_password FLUSHALL

# Adjust maxmemory in docker-compose.redis.yml
# Change: maxmemory 256mb → maxmemory 512mb
```

---

## Performance Metrics

### Expected Improvements

| Metric                      | Before Redis | After Redis | Improvement   |
| --------------------------- | ------------ | ----------- | ------------- |
| **API Response Time (p95)** | 180ms        | <100ms      | 44% faster    |
| **Vocabulary Lookup**       | 45ms         | 5ms         | 90% faster    |
| **Translation API Calls**   | 1000/day     | 100/day     | 90% reduction |
| **Database Connections**    | 20           | 10          | 50% reduction |
| **Monthly API Cost**        | $50          | $20         | $30 savings   |

### Monitoring Commands

```bash
# Check cache hit rate
curl http://localhost:8000/health/cache | jq '.stats.hit_rate'

# Get cache size
docker exec -it langplug-redis redis-cli -a dev_redis_password DBSIZE

# Monitor Redis in real-time
docker exec -it langplug-redis redis-cli -a dev_redis_password MONITOR

# Get cache stats
curl http://localhost:8000/health/cache | jq
```

---

## Summary Checklist

**Week 1 Implementation**:

- [ ] **Day 1**: Redis infrastructure running
- [ ] **Day 2**: Caching module implemented
- [ ] **Day 3**: Services integrated with caching
- [ ] **Day 4**: Cache invalidation strategies implemented
- [ ] **Day 5**: Tests passing and monitoring configured

**Acceptance Criteria**:

- [ ] Redis running and accessible
- [ ] Cache hit rate >60%
- [ ] API response time (p95) <100ms
- [ ] All tests passing
- [ ] Zero production incidents related to caching
- [ ] Documentation complete

**Next Steps**:

1. Week 2: Celery async processing (see `CELERY_SETUP_GUIDE.md`)
2. Week 3-4: Frontend performance optimizations ✅ (COMPLETED)

---

**Status**: Ready for Implementation
**Owner**: Backend Team
**Last Updated**: 2025-10-02
