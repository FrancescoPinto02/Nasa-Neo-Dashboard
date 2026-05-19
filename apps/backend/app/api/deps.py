from collections.abc import AsyncIterator

from fastapi import Depends

from app.clients.nasa_neows_client import NasaNeoWsClient
from app.core.config import Settings, get_settings
from app.services.neo_service import NeoService


async def get_nasa_client(
    settings: Settings = Depends(get_settings),
) -> AsyncIterator[NasaNeoWsClient]:
    """Provide a request-scoped NASA client.

    The client is closed after the request is completed.
    """
    client = NasaNeoWsClient(
        base_url=settings.nasa_neows_base_url,
        api_key=settings.nasa_api_key,
        timeout_seconds=settings.nasa_request_timeout_seconds,
    )

    try:
        yield client
    finally:
        await client.close()


def get_neo_service(
    settings: Settings = Depends(get_settings),
    nasa_client: NasaNeoWsClient = Depends(get_nasa_client),
) -> NeoService:
    """Build the NEO application service with configured dependencies."""
    return NeoService(
        nasa_client=nasa_client,
        max_chunk_days=settings.nasa_max_chunk_days,
        max_query_range_days=settings.app_max_query_range_days,
    )