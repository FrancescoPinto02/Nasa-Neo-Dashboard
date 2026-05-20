from datetime import date
from typing import Any

import pytest

from app.services.neo_service import NeoService


class StatsNasaClient:
    """Fake NASA client returning predictable feed data for stats tests."""

    async def get_feed(self, start_date: date, end_date: date) -> dict[str, Any]:
        return {
            "near_earth_objects": {
                "2026-05-20": [
                    _raw_neo(
                        neo_id="closest",
                        name="Closest asteroid",
                        close_approach_date=date(2026, 5, 20),
                        hazardous=True,
                        miss_distance_km="1000.0",
                        relative_velocity_kmh="20000.0",
                        diameter_min_m=100.0,
                        diameter_max_m=200.0,
                    ),
                    _raw_neo(
                        neo_id="fastest",
                        name="Fastest asteroid",
                        close_approach_date=date(2026, 5, 20),
                        hazardous=False,
                        miss_distance_km="3000.0",
                        relative_velocity_kmh="80000.0",
                        diameter_min_m=50.0,
                        diameter_max_m=150.0,
                    ),
                ],
                "2026-05-21": [
                    _raw_neo(
                        neo_id="largest",
                        name="Largest asteroid",
                        close_approach_date=date(2026, 5, 21),
                        hazardous=False,
                        miss_distance_km="5000.0",
                        relative_velocity_kmh="40000.0",
                        diameter_min_m=300.0,
                        diameter_max_m=500.0,
                    ),
                ],
            }
        }

    async def get_neo_by_id(self, neo_id: str) -> dict[str, Any]:
        return {"id": neo_id}


@pytest.mark.asyncio
async def test_get_neo_stats_returns_dashboard_aggregations() -> None:
    service = NeoService(
        nasa_client=StatsNasaClient(),
        max_chunk_days=7,
        max_query_range_days=90,
    )

    response = await service.get_neo_stats(
        start_date=date(2026, 5, 20),
        end_date=date(2026, 5, 22),
    )

    assert response.start_date == date(2026, 5, 20)
    assert response.end_date == date(2026, 5, 22)

    assert response.total_count == 3
    assert response.hazardous_count == 1
    assert response.non_hazardous_count == 2

    assert response.average_diameter_m == 216.66666666666666
    assert response.min_miss_distance_km == 1000.0
    assert response.max_relative_velocity_kmh == 80000.0

    assert response.closest_neo is not None
    assert response.closest_neo.id == "closest"

    assert response.fastest_neo is not None
    assert response.fastest_neo.id == "fastest"

    assert response.largest_neo is not None
    assert response.largest_neo.id == "largest"

    assert response.daily_counts[0].date == date(2026, 5, 20)
    assert response.daily_counts[0].count == 2

    assert response.daily_counts[1].date == date(2026, 5, 21)
    assert response.daily_counts[1].count == 1

    assert response.daily_counts[2].date == date(2026, 5, 22)
    assert response.daily_counts[2].count == 0

    assert response.hazardous_distribution[0].label == "Hazardous"
    assert response.hazardous_distribution[0].value == 1
    assert response.hazardous_distribution[1].label == "Non hazardous"
    assert response.hazardous_distribution[1].value == 2


def _raw_neo(
    *,
    neo_id: str,
    name: str,
    close_approach_date: date,
    hazardous: bool,
    miss_distance_km: str,
    relative_velocity_kmh: str,
    diameter_min_m: float,
    diameter_max_m: float,
) -> dict[str, Any]:
    return {
        "id": neo_id,
        "name": name,
        "nasa_jpl_url": f"https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/?sstr={neo_id}",
        "absolute_magnitude_h": 21.5,
        "is_potentially_hazardous_asteroid": hazardous,
        "estimated_diameter": {
            "meters": {
                "estimated_diameter_min": diameter_min_m,
                "estimated_diameter_max": diameter_max_m,
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