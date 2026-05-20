import asyncio
import json
from typing import Any, Protocol

from diskcache import Cache  # type: ignore[import-untyped]
from redis.asyncio import Redis


class CacheRepository(Protocol):
    """Storage abstraction for cached JSON-compatible dictionaries."""

    async def get_json(self, key: str) -> dict[str, Any] | None:
        """Return a cached JSON object or None when the key does not exist."""

    async def set_json(
        self,
        key: str,
        value: dict[str, Any],
        *,
        ttl_seconds: int,
    ) -> None:
        """Store a JSON object with a time-to-live."""

    async def close(self) -> None:
        """Release cache resources."""


class DiskCacheRepository:
    """
    Disk-based cache repository.

    This implementation is useful for local development because it requires no
    external service and still survives application restarts.
    """

    def __init__(self, directory: str) -> None:
        self._cache = Cache(directory)

    async def get_json(self, key: str) -> dict[str, Any] | None:
        value = await asyncio.to_thread(self._cache.get, key)

        if isinstance(value, dict):
            return value

        return None

    async def set_json(
        self,
        key: str,
        value: dict[str, Any],
        *,
        ttl_seconds: int,
    ) -> None:
        await asyncio.to_thread(
            self._cache.set,
            key,
            value,
            expire=ttl_seconds,
        )

    async def close(self) -> None:
        await asyncio.to_thread(self._cache.close)


class RedisCacheRepository:
    """
    Redis-backed cache repository.

    This implementation is better suited for production deployments because the
    cache can be shared across multiple backend instances.
    """

    def __init__(self, redis_url: str) -> None:
        self._redis: Redis = Redis.from_url(
            redis_url,
            decode_responses=True,
        )

    async def get_json(self, key: str) -> dict[str, Any] | None:
        raw_value = await self._redis.get(key)

        if raw_value is None:
            return None

        try:
            value = json.loads(raw_value)
        except json.JSONDecodeError:
            return None

        if isinstance(value, dict):
            return value

        return None

    async def set_json(
        self,
        key: str,
        value: dict[str, Any],
        *,
        ttl_seconds: int,
    ) -> None:
        raw_value = json.dumps(value)
        await self._redis.set(key, raw_value, ex=ttl_seconds)

    async def close(self) -> None:
        await self._redis.aclose()