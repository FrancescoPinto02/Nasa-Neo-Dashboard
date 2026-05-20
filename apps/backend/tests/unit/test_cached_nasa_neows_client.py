from datetime import date
from typing import Any

import pytest

from app.repositories.cache_repository import CacheRepository
from app.services.cached_nasa_neows_client import CachedNasaNeoWsClient


class FakeNasaClient:
    """Fake NASA client used to verify cache behavior."""

    def __init__(self) -> None:
        self.feed_calls: list[tuple[date, date]] = []
        self.detail_calls: list[str] = []

    async def get_feed(self, start_date: date, end_date: date) -> dict[str, Any]:
        self.feed_calls.append((start_date, end_date))

        return {
            "near_earth_objects": {
                start_date.isoformat(): [],
            }
        }

    async def get_neo_by_id(self, neo_id: str) -> dict[str, Any]:
        self.detail_calls.append(neo_id)

        return {
            "id": neo_id,
            "name": "Test asteroid",
        }


class InMemoryCacheRepository(CacheRepository):
    """Small in-memory cache implementation for unit tests."""

    def __init__(self) -> None:
        self.values: dict[str, dict[str, Any]] = {}
        self.ttls: dict[str, int] = {}

    async def get_json(self, key: str) -> dict[str, Any] | None:
        return self.values.get(key)

    async def set_json(
        self,
        key: str,
        value: dict[str, Any],
        *,
        ttl_seconds: int,
    ) -> None:
        self.values[key] = value
        self.ttls[key] = ttl_seconds

    async def close(self) -> None:
        return None


@pytest.mark.asyncio
async def test_get_feed_uses_cache_after_first_request() -> None:
    nasa_client = FakeNasaClient()
    cache_repository = InMemoryCacheRepository()

    cached_client = CachedNasaNeoWsClient(
        nasa_client=nasa_client,
        cache_repository=cache_repository,
        ttl_seconds=60,
    )

    start_date = date(2026, 5, 20)
    end_date = date(2026, 5, 26)

    first_response = await cached_client.get_feed(start_date, end_date)
    second_response = await cached_client.get_feed(start_date, end_date)

    assert first_response == second_response
    assert nasa_client.feed_calls == [(start_date, end_date)]
    assert len(cache_repository.values) == 1
    assert list(cache_repository.ttls.values()) == [60]


@pytest.mark.asyncio
async def test_get_neo_by_id_uses_cache_after_first_request() -> None:
    nasa_client = FakeNasaClient()
    cache_repository = InMemoryCacheRepository()

    cached_client = CachedNasaNeoWsClient(
        nasa_client=nasa_client,
        cache_repository=cache_repository,
        ttl_seconds=60,
    )

    first_response = await cached_client.get_neo_by_id("12345")
    second_response = await cached_client.get_neo_by_id("12345")

    assert first_response == second_response
    assert nasa_client.detail_calls == ["12345"]
    assert len(cache_repository.values) == 1