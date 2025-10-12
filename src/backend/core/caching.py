"""
In-memory caching layer implementation
Provides in-memory caching with TTL and LRU eviction
"""

import hashlib
import json
import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import wraps
from typing import Any

from core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class CacheKey:
    """Structured cache key with metadata"""

    namespace: str
    identifier: str
    version: str = "v1"
    params_hash: str | None = None

    def __str__(self) -> str:
        parts = [self.namespace, self.identifier, self.version]
        if self.params_hash:
            parts.append(self.params_hash)
        return ":".join(parts)

    @classmethod
    def from_function(cls, func: Callable, *args, **kwargs) -> "CacheKey":
        """Create cache key from function and parameters"""
        namespace = f"{func.__module__}.{func.__name__}"
        identifier = func.__name__

        # Create hash of parameters (MD5 is acceptable for cache keys, not security)
        params_data = {"args": args, "kwargs": kwargs}
        params_json = json.dumps(params_data, sort_keys=True, default=str)
        params_hash = hashlib.md5(params_json.encode(), usedforsecurity=False).hexdigest()[:8]

        return cls(namespace=namespace, identifier=identifier, params_hash=params_hash)


class CacheBackend(ABC):
    """Abstract base class for cache backends"""

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        pass

    @abstractmethod
    async def clear_pattern(self, pattern: str) -> int:
        pass


class InMemoryCache(CacheBackend):
    """Enhanced in-memory cache with TTL and LRU eviction"""

    def __init__(self, max_size: int = 1000):
        self._cache: dict[str, Any] = {}
        self._ttl: dict[str, datetime] = {}
        self._access_order: list[str] = []
        self.max_size = max_size

    async def get(self, key: str) -> Any | None:
        if key not in self._cache:
            return None

        # Check TTL
        if key in self._ttl and datetime.utcnow() > self._ttl[key]:
            await self.delete(key)
            return None

        # Update access order for LRU
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

        return self._cache[key]

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        # Evict if cache is full
        if len(self._cache) >= self.max_size and key not in self._cache:
            await self._evict_lru()

        self._cache[key] = value

        if ttl:
            self._ttl[key] = datetime.utcnow() + timedelta(seconds=ttl)

        # Update access order
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

        return True

    async def delete(self, key: str) -> bool:
        deleted = key in self._cache
        self._cache.pop(key, None)
        self._ttl.pop(key, None)
        if key in self._access_order:
            self._access_order.remove(key)
        return deleted

    async def clear_pattern(self, pattern: str) -> int:
        keys_to_delete = [k for k in self._cache if pattern in k]
        for key in keys_to_delete:
            await self.delete(key)
        return len(keys_to_delete)

    async def _evict_lru(self):
        """Evict least recently used item"""
        if self._access_order:
            lru_key = self._access_order[0]
            await self.delete(lru_key)


class EnhancedCacheManager:
    """In-memory cache manager with domain-specific strategies"""

    def __init__(self):
        self._memory_cache = InMemoryCache(max_size=2000)
        self._domain_caches: dict[str, dict[str, Any]] = {}
        self._setup_domain_caches()

    def _setup_domain_caches(self):
        """Setup domain-specific cache configurations"""
        self._domain_caches = {
            "vocabulary": {
                "ttl": 3600,  # 1 hour
                "max_size": 2000,
            },
            "user_progress": {
                "ttl": 1800,  # 30 minutes
                "max_size": 1000,
            },
            "sessions": {
                "ttl": 600,  # 10 minutes
                "max_size": 500,
            },
        }

    async def get(self, key: str, domain: str = "default") -> Any | None:
        """Get value from cache"""
        return await self._memory_cache.get(key)

    async def set(self, key: str, value: Any, domain: str = "default", expire: int | None = None) -> bool:
        """Set value in cache"""
        config = self._domain_caches.get(domain, {"ttl": 300})
        ttl = expire or config["ttl"]
        return await self._memory_cache.set(key, value, ttl)

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        return await self._memory_cache.delete(key)

    async def clear_domain(self, domain: str) -> int:
        """Clear all cache entries for a domain"""
        pattern = f"{domain}:"
        return await self._memory_cache.clear_pattern(pattern)

    async def health_check(self) -> dict[str, Any]:
        """Health check for cache system"""
        return {
            "status": "healthy",
            "memory_cache": {
                "size": len(self._memory_cache._cache),
                "max_size": self._memory_cache.max_size
            },
        }


# Global enhanced cache manager instance
cache_manager = EnhancedCacheManager()


# Legacy cache manager for backward compatibility
class CacheManager(EnhancedCacheManager):
    """Legacy cache manager for backward compatibility"""

    def get(self, key: str) -> Any | None:
        """Synchronous get method for backward compatibility"""
        import asyncio

        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.get(key))
        except RuntimeError:
            # No event loop running, use simplified approach
            return self._memory_cache._cache.get(key)

    def set(self, key: str, value: Any, expire: int | timedelta | None = None) -> bool:
        """Synchronous set method for backward compatibility"""
        import asyncio

        try:
            loop = asyncio.get_event_loop()
            expire_seconds = expire.total_seconds() if isinstance(expire, timedelta) else expire
            return loop.run_until_complete(self.set(key, value, expire=int(expire_seconds) if expire_seconds else None))
        except RuntimeError:
            # No event loop running, use simplified approach
            self._memory_cache._cache[key] = value
            return True


def cache_result(key_prefix: str, expire: int | timedelta | None = None):
    """Decorator to cache function results"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{hash(str(args) + str(sorted(kwargs.items())))}"

            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache_manager.set(cache_key, result, expire)
            return result

        return wrapper

    return decorator


# Convenience functions for common cache operations
def cache_vocabulary_word(word_id: int, data: dict, expire: int = 3600):
    """Cache vocabulary word data"""
    cache_manager.set(f"vocabulary:word:{word_id}", data, expire)


def get_cached_vocabulary_word(word_id: int) -> dict | None:
    """Get cached vocabulary word data"""
    return cache_manager.get(f"vocabulary:word:{word_id}")


def cache_user_progress(user_id: int, language: str, data: dict, expire: int = 1800):
    """Cache user vocabulary progress"""
    cache_manager.set(f"progress:user:{user_id}:{language}", data, expire)


def get_cached_user_progress(user_id: int, language: str) -> dict | None:
    """Get cached user vocabulary progress"""
    return cache_manager.get(f"progress:user:{user_id}:{language}")


def invalidate_user_cache(user_id: int):
    """Invalidate all cache entries for a user"""
    # This is simplified - in production you'd use pattern matching
    cache_manager.delete(f"progress:user:{user_id}:de")
    cache_manager.delete(f"progress:user:{user_id}:en")
    cache_manager.delete(f"progress:user:{user_id}:es")
