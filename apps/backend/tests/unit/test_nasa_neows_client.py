from datetime import date

import httpx
import pytest

from app.clients.nasa_neows_client import NasaNeoWsClient


@pytest.mark.asyncio
async def test_get_feed_builds_expected_nasa_url() -> None:
    captured_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request

        return httpx.Response(
            status_code=200,
            json={"near_earth_objects": {}},
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
        base_url="https://api.nasa.gov/neo/rest/v1/",
        transport=transport,
    ) as http_client:
        client = NasaNeoWsClient(
            base_url="https://api.nasa.gov/neo/rest/v1",
            api_key="DEMO_KEY",
            timeout_seconds=10,
            client=http_client,
        )

        await client.get_feed(
            start_date=date(2026, 5, 20),
            end_date=date(2026, 5, 26),
        )

    assert captured_request is not None
    assert str(captured_request.url).startswith(
        "https://api.nasa.gov/neo/rest/v1/feed"
    )
    assert captured_request.url.params["start_date"] == "2026-05-20"
    assert captured_request.url.params["end_date"] == "2026-05-26"
    assert captured_request.url.params["api_key"] == "DEMO_KEY"