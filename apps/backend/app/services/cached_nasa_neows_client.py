from collections.abc import Awaitable, Callable
from datetime import date
from typing import Any, Protocol

import structlog

from app.repositories.cache_repository import CacheRepository


logger = structlog.get_logger(__name__)


class NasaNeoWsRawClient(Protocol):
    """Protocol implemented by clients capable of calling NASA NeoWs."""

    def get_feed(self, start_date: date, end_date: date) -> Awaitable[dict[str, Any]]:
        """Fetch raw NASA feed data for an inclusive date range."""

    def get_neo_by_id(self, neo_id: str) -> Awaitable[dict[str, Any]]:
        """Fetch raw NASA detail data for one NEO."""


class CachedNasaNeoWsClient:
    """Cache-aware NASA NeoWs client.

    This class keeps caching out of the service layer. From the service point of
    view, this object behaves like the real NASA client.
    """

    def __init__(
        self,
        *,
        nasa_client: NasaNeoWsRawClient,
        cache_repository: CacheRepository,
        ttl_seconds: int,
    ) -> None:
        self._nasa_client = nasa_client
        self._cache_repository = cache_repository
        self._ttl_seconds = ttl_seconds

    async def get_feed(self, start_date: date, end_date: date) -> dict[str, Any]:
        """Return NASA feed data using cache when available."""
        cache_key = _feed_cache_key(start_date=start_date, end_date=end_date)

        return await self._get_or_set(
            cache_key=cache_key,
            fetcher=lambda: self._nasa_client.get_feed(start_date, end_date),
        )

    async def get_neo_by_id(self, neo_id: str) -> dict[str, Any]:
        """Return NASA NEO detail data using cache when available."""
        cache_key = _neo_detail_cache_key(neo_id)

        return await self._get_or_set(
            cache_key=cache_key,
            fetcher=lambda: self._nasa_client.get_neo_by_id(neo_id),
        )

    async def _get_or_set(
        self,
        *,
        cache_key: str,
        fetcher: Callable[[], Awaitable[dict[str, Any]]],
    ) -> dict[str, Any]:
        cached_payload = await self._cache_repository.get_json(cache_key)

        if cached_payload is not None:
            logger.info(
                "cache.hit",
                cache_key=cache_key,
            )
            return cached_payload

        logger.info(
            "cache.miss",
            cache_key=cache_key,
        )

        payload = await fetcher()

        await self._cache_repository.set_json(
            cache_key,
            payload,
            ttl_seconds=self._ttl_seconds,
        )

        logger.info(
            "cache.stored",
            cache_key=cache_key,
            ttl_seconds=self._ttl_seconds,
        )

        return payload


def _feed_cache_key(*, start_date: date, end_date: date) -> str:
    """Build a stable cache key for NASA feed requests."""
    return (
        "nasa-neows:feed:v1:"
        f"{start_date.isoformat()}:"
        f"{end_date.isoformat()}"
    )


def _neo_detail_cache_key(neo_id: str) -> str:
    """Build a stable cache key for NASA NEO detail requests."""
    return f"nasa-neows:neo-detail:v1:{neo_id}"