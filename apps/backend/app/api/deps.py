from collections.abc import AsyncIterator

from fastapi import Depends

from app.clients.nasa_neows_client import NasaNeoWsClient
from app.core.config import Settings, get_settings
from app.repositories.cache_repository import CacheRepository, DiskCacheRepository, RedisCacheRepository
from app.services.cached_nasa_neows_client import CachedNasaNeoWsClient
from app.services.neo_service import NeoService


async def get_cache_repository(
    settings: Settings = Depends(get_settings),
) -> AsyncIterator[CacheRepository]:
    """Provide the configured cache repository.

    Local development defaults to DiskCache. Production can switch to Redis by
    setting CACHE_BACKEND=redis.
    """
    if settings.cache_backend == "redis":
        repository: CacheRepository = RedisCacheRepository(
            redis_url=settings.redis_url,
        )
    else:
        repository = DiskCacheRepository(
            directory=settings.cache_disk_directory,
        )

    try:
        yield repository
    finally:
        await repository.close()


async def get_raw_nasa_client(
    settings: Settings = Depends(get_settings),
) -> AsyncIterator[NasaNeoWsClient]:
    """Provide a request-scoped raw NASA client."""
    client = NasaNeoWsClient(
        base_url=settings.nasa_neows_base_url,
        api_key=settings.nasa_api_key,
        timeout_seconds=settings.nasa_request_timeout_seconds,
    )

    try:
        yield client
    finally:
        await client.close()


def get_cached_nasa_client(
    settings: Settings = Depends(get_settings),
    raw_nasa_client: NasaNeoWsClient = Depends(get_raw_nasa_client),
    cache_repository: CacheRepository = Depends(get_cache_repository),
) -> CachedNasaNeoWsClient:
    """Wrap the raw NASA client with server-side caching."""
    return CachedNasaNeoWsClient(
        nasa_client=raw_nasa_client,
        cache_repository=cache_repository,
        ttl_seconds=settings.cache_ttl_seconds,
    )


def get_neo_service(
    settings: Settings = Depends(get_settings),
    nasa_client: CachedNasaNeoWsClient = Depends(get_cached_nasa_client),
) -> NeoService:
    """Build the NEO application service with configured dependencies."""
    return NeoService(
        nasa_client=nasa_client,
        max_chunk_days=settings.nasa_max_chunk_days,
        max_query_range_days=settings.app_max_query_range_days,
    )