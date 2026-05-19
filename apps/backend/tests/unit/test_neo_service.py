from datetime import date
from typing import Any

import pytest

from app.schemas.neo import NeoSortBy, SortOrder
from app.services.neo_service import NeoService


class FakeNasaClient:
    """Small in-memory NASA client used to test the service without real HTTP calls."""

    def __init__(self) -> None:
        self.calls: list[tuple[date, date]] = []

    async def get_feed(self, start_date: date, end_date: date) -> dict[str, Any]:
        self.calls.append((start_date, end_date))

        return {
            "near_earth_objects": {
                start_date.isoformat(): [
                    _raw_neo(
                        neo_id=f"neo-{start_date.isoformat()}",
                        name=f"Asteroid {start_date.isoformat()}",
                        close_approach_date=start_date,
                        hazardous=False,
                        miss_distance_km="12345.67",
                        relative_velocity_kmh="54321.0",
                    )
                ]
            }
        }


@pytest.mark.asyncio
async def test_list_neos_chunks_requests_and_normalizes_results() -> None:
    nasa_client = FakeNasaClient()

    service = NeoService(
        nasa_client=nasa_client,
        max_chunk_days=7,
        max_query_range_days=90,
    )

    response = await service.list_neos(
        start_date=date(2026, 5, 1),
        end_date=date(2026, 5, 10),
        hazardous=None,
        sort_by=NeoSortBy.DATE,
        sort_order=SortOrder.ASC,
    )

    assert nasa_client.calls == [
        (date(2026, 5, 1), date(2026, 5, 7)),
        (date(2026, 5, 8), date(2026, 5, 10)),
    ]

    assert response.count == 2
    assert response.results[0].id == "neo-2026-05-01"
    assert response.results[0].name == "Asteroid 2026-05-01"
    assert response.results[0].miss_distance_km == 12345.67
    assert response.results[0].relative_velocity_kmh == 54321.0
    assert response.results[0].diameter_avg_m == 150.0


@pytest.mark.asyncio
async def test_list_neos_filters_hazardous_results() -> None:
    service = NeoService(
        nasa_client=StaticPayloadNasaClient(
            payload={
                "near_earth_objects": {
                    "2026-05-01": [
                        _raw_neo(
                            neo_id="safe",
                            name="Safe asteroid",
                            close_approach_date=date(2026, 5, 1),
                            hazardous=False,
                        ),
                        _raw_neo(
                            neo_id="hazardous",
                            name="Hazardous asteroid",
                            close_approach_date=date(2026, 5, 1),
                            hazardous=True,
                        ),
                    ]
                }
            }
        ),
        max_chunk_days=7,
        max_query_range_days=90,
    )

    response = await service.list_neos(
        start_date=date(2026, 5, 1),
        end_date=date(2026, 5, 1),
        hazardous=True,
        sort_by=NeoSortBy.DATE,
        sort_order=SortOrder.ASC,
    )

    assert response.count == 1
    assert response.results[0].id == "hazardous"


class StaticPayloadNasaClient:
    """Fake NASA client returning a fixed payload."""

    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    async def get_feed(self, start_date: date, end_date: date) -> dict[str, Any]:
        return self._payload


def _raw_neo(
    *,
    neo_id: str,
    name: str,
    close_approach_date: date,
    hazardous: bool,
    miss_distance_km: str = "1000.0",
    relative_velocity_kmh: str = "2000.0",
) -> dict[str, Any]:
    return {
        "id": neo_id,
        "name": name,
        "nasa_jpl_url": f"https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/?sstr={neo_id}",
        "absolute_magnitude_h": 21.5,
        "is_potentially_hazardous_asteroid": hazardous,
        "estimated_diameter": {
            "meters": {
                "estimated_diameter_min": 100.0,
                "estimated_diameter_max": 200.0,
            }
        },
        "close_approach_data": [
            {
                "close_approach_date": close_approach_date.isoformat(),
                "miss_distance": {
                    "kilometers": miss_distance_km,
                },
                "relative_velocity": {
                    "kilometers_per_hour": relative_velocity_kmh,
                },
            }
        ],
    }