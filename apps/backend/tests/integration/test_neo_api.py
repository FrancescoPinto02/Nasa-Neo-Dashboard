from collections.abc import Iterator
from datetime import date
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_neo_service
from app.main import app
from app.services.neo_service import NeoService


@pytest.fixture
def client() -> Iterator[tuple[TestClient, "FakeNasaClient"]]:
    """Create a test client with the NASA dependency replaced by a fake client.

    These tests exercise the real FastAPI routes, dependency injection,
    service layer and response serialization, without calling the real NASA API.
    """
    fake_nasa_client = FakeNasaClient()

    def override_get_neo_service() -> NeoService:
        return NeoService(
            nasa_client=fake_nasa_client,
            max_chunk_days=7,
            max_query_range_days=90,
        )

    app.dependency_overrides[get_neo_service] = override_get_neo_service

    with TestClient(app) as test_client:
        yield test_client, fake_nasa_client

    app.dependency_overrides.clear()


def test_health_endpoint_returns_ok(
    client: tuple[TestClient, "FakeNasaClient"],
) -> None:
    test_client, _fake_nasa_client = client

    response = test_client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "environment" in response.json()
    assert "version" in response.json()


def test_list_neos_endpoint_returns_normalized_results(
    client: tuple[TestClient, "FakeNasaClient"],
) -> None:
    test_client, fake_nasa_client = client

    response = test_client.get(
        "/api/v1/neos",
        params={
            "start_date": "2026-05-20",
            "end_date": "2026-05-22",
            "sort_by": "date",
            "sort_order": "asc",
        },
    )

    payload = response.json()

    assert response.status_code == 200

    assert payload["start_date"] == "2026-05-20"
    assert payload["end_date"] == "2026-05-22"
    assert payload["count"] == 3

    assert payload["results"][0]["id"] == "closest"
    assert payload["results"][0]["name"] == "Closest asteroid"
    assert payload["results"][0]["is_potentially_hazardous"] is True
    assert payload["results"][0]["close_approach_date"] == "2026-05-20"
    assert payload["results"][0]["miss_distance_km"] == 1000.0
    assert payload["results"][0]["relative_velocity_kmh"] == 20000.0
    assert payload["results"][0]["diameter_avg_m"] == 150.0

    assert fake_nasa_client.feed_calls == [
        (date(2026, 5, 20), date(2026, 5, 22)),
    ]


def test_list_neos_endpoint_filters_hazardous_results(
    client: tuple[TestClient, "FakeNasaClient"],
) -> None:
    test_client, _fake_nasa_client = client

    response = test_client.get(
        "/api/v1/neos",
        params={
            "start_date": "2026-05-20",
            "end_date": "2026-05-22",
            "hazardous": "true",
        },
    )

    payload = response.json()

    assert response.status_code == 200
    assert payload["count"] == 1
    assert payload["results"][0]["id"] == "closest"
    assert payload["results"][0]["is_potentially_hazardous"] is True


def test_list_neos_endpoint_returns_standard_error_for_invalid_range(
    client: tuple[TestClient, "FakeNasaClient"],
) -> None:
    test_client, _fake_nasa_client = client

    response = test_client.get(
        "/api/v1/neos",
        params={
            "start_date": "2026-05-22",
            "end_date": "2026-05-20",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "invalid_date_range",
            "message": "start_date must be less than or equal to end_date.",
        }
    }


def test_list_neos_endpoint_returns_standard_error_for_validation_failure(
    client: tuple[TestClient, "FakeNasaClient"],
) -> None:
    test_client, _fake_nasa_client = client

    response = test_client.get(
        "/api/v1/neos",
        params={
            "start_date": "not-a-date",
            "end_date": "2026-05-20",
        },
    )

    payload = response.json()

    assert response.status_code == 422
    assert payload["error"]["code"] == "validation_error"
    assert payload["error"]["message"] == "Request validation failed."
    assert isinstance(payload["error"]["details"], list)


def test_neo_stats_endpoint_returns_dashboard_aggregations(
    client: tuple[TestClient, "FakeNasaClient"],
) -> None:
    test_client, _fake_nasa_client = client

    response = test_client.get(
        "/api/v1/neos/stats",
        params={
            "start_date": "2026-05-20",
            "end_date": "2026-05-22",
        },
    )

    payload = response.json()

    assert response.status_code == 200

    assert payload["start_date"] == "2026-05-20"
    assert payload["end_date"] == "2026-05-22"

    assert payload["total_count"] == 3
    assert payload["hazardous_count"] == 1
    assert payload["non_hazardous_count"] == 2

    assert payload["average_diameter_m"] == 216.66666666666666
    assert payload["min_miss_distance_km"] == 1000.0
    assert payload["max_relative_velocity_kmh"] == 80000.0

    assert payload["closest_neo"]["id"] == "closest"
    assert payload["fastest_neo"]["id"] == "fastest"
    assert payload["largest_neo"]["id"] == "largest"

    assert payload["daily_counts"] == [
        {
            "date": "2026-05-20",
            "count": 2,
        },
        {
            "date": "2026-05-21",
            "count": 1,
        },
        {
            "date": "2026-05-22",
            "count": 0,
        },
    ]

    assert payload["hazardous_distribution"] == [
        {
            "label": "Hazardous",
            "value": 1,
        },
        {
            "label": "Non hazardous",
            "value": 2,
        },
    ]


def test_neo_detail_endpoint_returns_normalized_detail(
    client: tuple[TestClient, "FakeNasaClient"],
) -> None:
    test_client, fake_nasa_client = client

    response = test_client.get("/api/v1/neos/3542519")

    payload = response.json()

    assert response.status_code == 200

    assert payload["id"] == "3542519"
    assert payload["name"] == "(2010 PK9)"
    assert payload["designation"] == "2010 PK9"

    assert payload["is_potentially_hazardous"] is False
    assert payload["is_sentry_object"] is False

    assert payload["diameter_min_m"] == 100.0
    assert payload["diameter_max_m"] == 200.0
    assert payload["diameter_avg_m"] == 150.0

    assert payload["orbital_data"]["orbit_id"] == "42"
    assert payload["orbital_data"]["first_observation_date"] == "2010-08-01"
    assert payload["orbital_data"]["last_observation_date"] == "2025-01-01"
    assert payload["orbital_data"]["data_arc_in_days"] == 5267
    assert payload["orbital_data"]["observations_used"] == 123
    assert payload["orbital_data"]["orbit_class_type"] == "APO"

    assert payload["close_approaches"] == [
        {
            "close_approach_date": "2026-05-20",
            "close_approach_date_full": "2026-May-20 12:00",
            "epoch_date_close_approach": 1779278400000,
            "relative_velocity_kmh": 54321.0,
            "miss_distance_km": 12345.67,
            "orbiting_body": "Earth",
        }
    ]

    assert fake_nasa_client.detail_calls == ["3542519"]


def test_stats_route_is_not_captured_by_detail_route(
    client: tuple[TestClient, "FakeNasaClient"],
) -> None:
    test_client, fake_nasa_client = client

    response = test_client.get(
        "/api/v1/neos/stats",
        params={
            "start_date": "2026-05-20",
            "end_date": "2026-05-22",
        },
    )

    assert response.status_code == 200
    assert fake_nasa_client.detail_calls == []


class FakeNasaClient:
    """Fake NASA client used by API integration tests."""

    def __init__(self) -> None:
        self.feed_calls: list[tuple[date, date]] = []
        self.detail_calls: list[str] = []

    async def get_feed(self, start_date: date, end_date: date) -> dict[str, Any]:
        self.feed_calls.append((start_date, end_date))

        return {
            "near_earth_objects": {
                "2026-05-20": [
                    _raw_feed_neo(
                        neo_id="closest",
                        name="Closest asteroid",
                        close_approach_date=date(2026, 5, 20),
                        hazardous=True,
                        miss_distance_km="1000.0",
                        relative_velocity_kmh="20000.0",
                        diameter_min_m=100.0,
                        diameter_max_m=200.0,
                    ),
                    _raw_feed_neo(
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
                    _raw_feed_neo(
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
        self.detail_calls.append(neo_id)

        return {
            "id": neo_id,
            "name": "(2010 PK9)",
            "designation": "2010 PK9",
            "nasa_jpl_url": (
                "https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/?sstr=3542519"
            ),
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
                    "orbit_class_description": (
                        "Near-Earth asteroid orbits similar to that of 1862 Apollo"
                    ),
                    "orbit_class_range": (
                        "a (semi-major axis) > 1.0 AU; "
                        "q (perihelion) < 1.017 AU"
                    ),
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


def _raw_feed_neo(
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
        "nasa_jpl_url": (
            f"https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/?sstr={neo_id}"
        ),
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