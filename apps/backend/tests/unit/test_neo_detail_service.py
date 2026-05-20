from datetime import date
from typing import Any

import pytest

from app.services.neo_service import NeoService


class StaticDetailNasaClient:
    """Fake NASA client returning fixed detail data."""

    async def get_feed(self, start_date: date, end_date: date) -> dict[str, Any]:
        return {"near_earth_objects": {}}

    async def get_neo_by_id(self, neo_id: str) -> dict[str, Any]:
        return {
            "id": neo_id,
            "name": "(2010 PK9)",
            "designation": "2010 PK9",
            "nasa_jpl_url": "https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/?sstr=3542519",
            "absolute_magnitude_h": 21.5,
            "is_potentially_hazardous_asteroid": False,
            "is_sentry_object": False,
            "estimated_diameter": {
                "meters": {
                    "estimated_diameter_min": 100.0,
                    "estimated_diameter_max": 200.0,
                }
            },
            "orbital_data": {
                "orbit_id": "42",
                "orbit_determination_date": "2025-01-01 00:00:00",
                "first_observation_date": "2010-08-01",
                "last_observation_date": "2025-01-01",
                "data_arc_in_days": "5267",
                "observations_used": "123",
                "orbit_class": {
                    "orbit_class_type": "APO",
                    "orbit_class_description": "Near-Earth asteroid orbits similar to that of 1862 Apollo",
                    "orbit_class_range": "a (semi-major axis) > 1.0 AU; q (perihelion) < 1.017 AU",
                },
            },
            "close_approach_data": [
                {
                    "close_approach_date": "2026-05-20",
                    "close_approach_date_full": "2026-May-20 12:00",
                    "epoch_date_close_approach": 1779278400000,
                    "relative_velocity": {
                        "kilometers_per_hour": "54321.0",
                    },
                    "miss_distance": {
                        "kilometers": "12345.67",
                    },
                    "orbiting_body": "Earth",
                }
            ],
        }


@pytest.mark.asyncio
async def test_get_neo_detail_normalizes_nasa_payload() -> None:
    service = NeoService(
        nasa_client=StaticDetailNasaClient(),
        max_chunk_days=7,
        max_query_range_days=90,
    )

    response = await service.get_neo_detail(neo_id="3542519")

    assert response.id == "3542519"
    assert response.name == "(2010 PK9)"
    assert response.designation == "2010 PK9"

    assert response.diameter_min_m == 100.0
    assert response.diameter_max_m == 200.0
    assert response.diameter_avg_m == 150.0

    assert response.orbital_data is not None
    assert response.orbital_data.orbit_id == "42"
    assert response.orbital_data.first_observation_date == date(2010, 8, 1)
    assert response.orbital_data.last_observation_date == date(2025, 1, 1)
    assert response.orbital_data.data_arc_in_days == 5267
    assert response.orbital_data.observations_used == 123
    assert response.orbital_data.orbit_class_type == "APO"

    assert len(response.close_approaches) == 1
    assert response.close_approaches[0].close_approach_date == date(2026, 5, 20)
    assert response.close_approaches[0].miss_distance_km == 12345.67
    assert response.close_approaches[0].relative_velocity_kmh == 54321.0
    assert response.close_approaches[0].orbiting_body == "Earth"