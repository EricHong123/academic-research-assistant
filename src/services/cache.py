"""Cache service using Redis."""
import json
import hashlib
from typing import Any, Optional
import redis.asyncio as redis
import os


class CacheService:
    """Redis cache service."""

    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._client: Optional[redis.Redis] = None
        self.default_ttl = 3600  # 1 hour

    async def get_client(self) -> redis.Redis:
        """Get or create Redis client."""
        if self._client is None:
            self._client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
        return self._client

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            client = await self.get_client()
            value = await client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> bool:
        """Set value in cache."""
        try:
            client = await self.get_client()
            serialized = json.dumps(value)
            await client.setex(key, ttl or self.default_ttl, serialized)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            client = await self.get_client()
            await client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            client = await self.get_client()
            return await client.exists(key) > 0
        except Exception:
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        try:
            client = await self.get_client()
            keys = []
            async for key in client.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                return await client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache clear error: {e}")
            return 0

    @staticmethod
    def make_key(*parts: str) -> str:
        """Create a cache key from parts."""
        return ":".join(parts)

    @staticmethod
    def hash_key(key: str) -> str:
        """Hash a key for consistent length."""
        return hashlib.md5(key.encode()).hexdigest()


# Singleton instance
_cache: Optional[CacheService] = None


def get_cache() -> CacheService:
    """Get cache service singleton."""
    global _cache
    if _cache is None:
        _cache = CacheService()
    return _cache


# Decorator for caching
def cached(ttl: int = 3600, key_prefix: str = "cache"):
    """Decorator for caching function results."""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            cache = get_cache()

            # Create cache key
            key_parts = [key_prefix, func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            cache_key = cache.make_key(*key_parts)

            # Try to get from cache
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Call function and cache result
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator
