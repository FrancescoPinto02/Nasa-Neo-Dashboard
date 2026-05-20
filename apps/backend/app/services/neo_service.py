from collections.abc import Awaitable
from datetime import date
from typing import Any, Protocol

from app.schemas.neo import (
    NeoCloseApproach,
    NeoDetailResponse,
    NeoFeedResponse,
    NeoOrbitalData,
    NeoSortBy,
    NeoSummary,
    SortOrder,
)
from app.utils.dates import iter_date_chunks, validate_date_range


class NasaNeoClient(Protocol):
    """Protocol used to keep NeoService independent from concrete NASA clients."""

    def get_feed(self, start_date: date, end_date: date) -> Awaitable[dict[str, Any]]:
        """Fetch raw NASA feed data for an inclusive date range."""

    def get_neo_by_id(self, neo_id: str) -> Awaitable[dict[str, Any]]:
        """Fetch raw NASA detail data for one Near Earth Object."""


class NeoService:
    """Application service responsible for NEO orchestration and normalization."""

    def __init__(
        self,
        *,
        nasa_client: NasaNeoClient,
        max_chunk_days: int,
        max_query_range_days: int,
    ) -> None:
        self._nasa_client = nasa_client
        self._max_chunk_days = max_chunk_days
        self._max_query_range_days = max_query_range_days

    async def list_neos(
        self,
        *,
        start_date: date,
        end_date: date,
        hazardous: bool | None,
        sort_by: NeoSortBy,
        sort_order: SortOrder,
    ) -> NeoFeedResponse:
        """Return normalized NEOs for a date range.

        The range is validated against application limits, split into NASA-safe
        chunks, fetched sequentially, normalized, filtered and sorted.
        """
        validate_date_range(
            start_date=start_date,
            end_date=end_date,
            max_range_days=self._max_query_range_days,
        )

        results: list[NeoSummary] = []

        for chunk_start, chunk_end in iter_date_chunks(
            start_date=start_date,
            end_date=end_date,
            max_days=self._max_chunk_days,
        ):
            payload = await self._nasa_client.get_feed(chunk_start, chunk_end)
            results.extend(_extract_summaries(payload))

        if hazardous is not None:
            results = [
                neo
                for neo in results
                if neo.is_potentially_hazardous is hazardous
            ]

        results = _sort_results(
            results=results,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        return NeoFeedResponse(
            start_date=start_date,
            end_date=end_date,
            count=len(results),
            results=results,
        )

    async def get_neo_detail(self, *, neo_id: str) -> NeoDetailResponse:
        """Return normalized detail information for a single NEO."""
        payload = await self._nasa_client.get_neo_by_id(neo_id)

        return _to_neo_detail(payload)


def _extract_summaries(payload: dict[str, Any]) -> list[NeoSummary]:
    """Extract and normalize NEO summaries from a raw NASA feed payload."""
    near_earth_objects = payload.get("near_earth_objects")

    if not isinstance(near_earth_objects, dict):
        return []

    summaries: list[NeoSummary] = []

    for raw_date, raw_neos in near_earth_objects.items():
        if not isinstance(raw_date, str) or not isinstance(raw_neos, list):
            continue

        try:
            close_approach_date = date.fromisoformat(raw_date)
        except ValueError:
            continue

        for raw_neo in raw_neos:
            if isinstance(raw_neo, dict):
                summaries.append(_to_neo_summary(raw_neo, close_approach_date))

    return summaries


def _to_neo_summary(raw_neo: dict[str, Any], close_approach_date: date) -> NeoSummary:
    """Convert one NASA feed object into our frontend-friendly summary schema."""
    approach = _select_close_approach(raw_neo, close_approach_date)

    miss_distance = approach.get("miss_distance", {})
    relative_velocity = approach.get("relative_velocity", {})

    diameter_min_m, diameter_max_m = _extract_diameter_meters(raw_neo)
    diameter_avg_m = _average_optional(diameter_min_m, diameter_max_m)

    return NeoSummary(
        id=str(raw_neo.get("id", "")),
        name=str(raw_neo.get("name", "")),
        nasa_jpl_url=_to_optional_str(raw_neo.get("nasa_jpl_url")),
        absolute_magnitude_h=_to_float(raw_neo.get("absolute_magnitude_h")),
        is_potentially_hazardous=bool(
            raw_neo.get("is_potentially_hazardous_asteroid", False)
        ),
        close_approach_date=close_approach_date,
        miss_distance_km=_to_float(miss_distance.get("kilometers")),
        relative_velocity_kmh=_to_float(
            relative_velocity.get("kilometers_per_hour")
        ),
        diameter_min_m=diameter_min_m,
        diameter_max_m=diameter_max_m,
        diameter_avg_m=diameter_avg_m,
    )


def _to_neo_detail(raw_neo: dict[str, Any]) -> NeoDetailResponse:
    """Convert one NASA detail object into our frontend-friendly detail schema."""
    diameter_min_m, diameter_max_m = _extract_diameter_meters(raw_neo)
    diameter_avg_m = _average_optional(diameter_min_m, diameter_max_m)

    return NeoDetailResponse(
        id=str(raw_neo.get("id", "")),
        name=str(raw_neo.get("name", "")),
        designation=_to_optional_str(raw_neo.get("designation")),
        nasa_jpl_url=_to_optional_str(raw_neo.get("nasa_jpl_url")),
        absolute_magnitude_h=_to_float(raw_neo.get("absolute_magnitude_h")),
        is_potentially_hazardous=bool(
            raw_neo.get("is_potentially_hazardous_asteroid", False)
        ),
        is_sentry_object=bool(raw_neo.get("is_sentry_object", False)),
        diameter_min_m=diameter_min_m,
        diameter_max_m=diameter_max_m,
        diameter_avg_m=diameter_avg_m,
        orbital_data=_to_orbital_data(raw_neo.get("orbital_data")),
        close_approaches=_extract_close_approaches(raw_neo),
    )


def _to_orbital_data(raw_orbital_data: Any) -> NeoOrbitalData | None:
    """Normalize NASA orbital data if available."""
    if not isinstance(raw_orbital_data, dict):
        return None

    orbit_class = raw_orbital_data.get("orbit_class")

    if not isinstance(orbit_class, dict):
        orbit_class = {}

    return NeoOrbitalData(
        orbit_id=_to_optional_str(raw_orbital_data.get("orbit_id")),
        orbit_determination_date=_to_optional_str(
            raw_orbital_data.get("orbit_determination_date")
        ),
        first_observation_date=_to_date(
            raw_orbital_data.get("first_observation_date")
        ),
        last_observation_date=_to_date(
            raw_orbital_data.get("last_observation_date")
        ),
        data_arc_in_days=_to_int(raw_orbital_data.get("data_arc_in_days")),
        observations_used=_to_int(raw_orbital_data.get("observations_used")),
        orbit_class_type=_to_optional_str(orbit_class.get("orbit_class_type")),
        orbit_class_description=_to_optional_str(
            orbit_class.get("orbit_class_description")
        ),
        orbit_class_range=_to_optional_str(orbit_class.get("orbit_class_range")),
    )


def _extract_close_approaches(raw_neo: dict[str, Any]) -> list[NeoCloseApproach]:
    """Extract and normalize all close approach records for a NEO."""
    approaches = raw_neo.get("close_approach_data")

    if not isinstance(approaches, list):
        return []

    normalized_approaches: list[NeoCloseApproach] = []

    for approach in approaches:
        if not isinstance(approach, dict):
            continue

        relative_velocity = approach.get("relative_velocity")
        miss_distance = approach.get("miss_distance")

        if not isinstance(relative_velocity, dict):
            relative_velocity = {}

        if not isinstance(miss_distance, dict):
            miss_distance = {}

        normalized_approaches.append(
            NeoCloseApproach(
                close_approach_date=_to_date(approach.get("close_approach_date")),
                close_approach_date_full=_to_optional_str(
                    approach.get("close_approach_date_full")
                ),
                epoch_date_close_approach=_to_int(
                    approach.get("epoch_date_close_approach")
                ),
                relative_velocity_kmh=_to_float(
                    relative_velocity.get("kilometers_per_hour")
                ),
                miss_distance_km=_to_float(miss_distance.get("kilometers")),
                orbiting_body=_to_optional_str(approach.get("orbiting_body")),
            )
        )

    return sorted(
        normalized_approaches,
        key=lambda item: item.close_approach_date or date.max,
    )


def _select_close_approach(
    raw_neo: dict[str, Any],
    expected_date: date,
) -> dict[str, Any]:
    """Select the close approach matching the feed date, falling back safely."""
    approaches = raw_neo.get("close_approach_data")

    if not isinstance(approaches, list):
        return {}

    expected_date_value = expected_date.isoformat()

    for approach in approaches:
        if (
            isinstance(approach, dict)
            and approach.get("close_approach_date") == expected_date_value
        ):
            return approach

    first_approach = approaches[0] if approaches else {}

    return first_approach if isinstance(first_approach, dict) else {}


def _extract_diameter_meters(raw_neo: dict[str, Any]) -> tuple[float | None, float | None]:
    """Extract estimated min/max diameter in meters from a raw NASA object."""
    estimated_diameter = raw_neo.get("estimated_diameter")

    if not isinstance(estimated_diameter, dict):
        return None, None

    meters = estimated_diameter.get("meters")

    if not isinstance(meters, dict):
        return None, None

    return (
        _to_float(meters.get("estimated_diameter_min")),
        _to_float(meters.get("estimated_diameter_max")),
    )


def _sort_results(
    *,
    results: list[NeoSummary],
    sort_by: NeoSortBy,
    sort_order: SortOrder,
) -> list[NeoSummary]:
    """Sort NEOs while always keeping null values at the end."""
    field_name = _sort_field_name(sort_by)
    reverse = sort_order == SortOrder.DESC

    with_value = [neo for neo in results if getattr(neo, field_name) is not None]
    without_value = [neo for neo in results if getattr(neo, field_name) is None]

    with_value.sort(
        key=lambda neo: getattr(neo, field_name),
        reverse=reverse,
    )

    return [*with_value, *without_value]


def _sort_field_name(sort_by: NeoSortBy) -> str:
    """Map public sort options to internal NeoSummary field names."""
    field_map = {
        NeoSortBy.DATE: "close_approach_date",
        NeoSortBy.DISTANCE: "miss_distance_km",
        NeoSortBy.VELOCITY: "relative_velocity_kmh",
        NeoSortBy.DIAMETER: "diameter_avg_m",
    }

    return field_map[sort_by]


def _to_float(value: Any) -> float | None:
    """Convert NASA string/number values to float, returning None on failure."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> int | None:
    """Convert NASA string/number values to int, returning None on failure."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _to_date(value: Any) -> date | None:
    """Convert an ISO date string to date, returning None on failure."""
    if not isinstance(value, str):
        return None

    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _to_optional_str(value: Any) -> str | None:
    """Convert a value to string unless it is empty or missing."""
    if value is None:
        return None

    text = str(value).strip()

    return text or None


def _average_optional(left: float | None, right: float | None) -> float | None:
    """Average two optional floats only when both are available."""
    if left is None or right is None:
        return None

    return (left + right) / 2