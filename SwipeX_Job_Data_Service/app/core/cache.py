import json
import time
import logging
from typing import Any, Optional
import redis
from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Hybrid cache manager that uses Redis if available,
    falling back seamlessly to an in-memory dictionary cache with TTL.
    """
    def __init__(self):
        self._redis_client: Optional[redis.Redis] = None
        self._memory_cache: dict[str, tuple[Any, float]] = {}  # key -> (value, expiry_timestamp)
        self._is_redis_available = False

        if settings.CACHE_ENABLED:
            try:
                client = redis.from_url(
                    settings.REDIS_URL,
                    socket_connect_timeout=1,
                    decode_responses=True
                )
                client.ping()
                self._redis_client = client
                self._is_redis_available = True
                logger.info("Connected successfully to Redis cache.")
            except Exception as e:
                logger.warning(f"Redis is not available ({e}). Using in-memory fallback cache.")
                self._is_redis_available = False

    def get(self, key: str) -> Optional[Any]:
        if not settings.CACHE_ENABLED:
            return None

        # Try Redis
        if self._is_redis_available and self._redis_client:
            try:
                cached = self._redis_client.get(key)
                if cached:
                    return json.loads(cached)
                return None
            except Exception as e:
                logger.warning(f"Redis get failed: {e}. Falling back to in-memory.")

        # In-memory lookup
        if key in self._memory_cache:
            val, expiry = self._memory_cache[key]
            if time.time() < expiry:
                return val
            else:
                del self._memory_cache[key]
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if not settings.CACHE_ENABLED:
            return

        ttl_seconds = ttl if ttl is not None else settings.CACHE_TTL_SECONDS
        json_data = json.dumps(value)

        # Try Redis
        if self._is_redis_available and self._redis_client:
            try:
                self._redis_client.setex(key, ttl_seconds, json_data)
                return
            except Exception as e:
                logger.warning(f"Redis set failed: {e}. Storing in memory.")

        # In-memory storage
        self._memory_cache[key] = (value, time.time() + ttl_seconds)

    def delete(self, key: str) -> None:
        if self._is_redis_available and self._redis_client:
            try:
                self._redis_client.delete(key)
            except Exception:
                pass
        self._memory_cache.pop(key, None)

    def clear(self) -> None:
        if self._is_redis_available and self._redis_client:
            try:
                self._redis_client.flushdb()
            except Exception:
                pass
        self._memory_cache.clear()


# Global cache instance
cache_manager = CacheManager()
