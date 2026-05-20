from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class NeoSortBy(str, Enum):
    """Allowed sorting fields for the NEO list endpoint."""

    DATE = "date"
    DISTANCE = "distance"
    VELOCITY = "velocity"
    DIAMETER = "diameter"


class SortOrder(str, Enum):
    """Allowed sorting directions."""

    ASC = "asc"
    DESC = "desc"


class NeoSummary(BaseModel):
    """Normalized Near Earth Object summary returned to the frontend."""

    id: str
    name: str

    nasa_jpl_url: str | None = None
    absolute_magnitude_h: float | None = None

    is_potentially_hazardous: bool

    close_approach_date: date

    miss_distance_km: float | None = Field(
        default=None,
        description="Minimum miss distance in kilometers.",
    )
    relative_velocity_kmh: float | None = Field(
        default=None,
        description="Relative velocity in kilometers per hour.",
    )

    diameter_min_m: float | None = None
    diameter_max_m: float | None = None
    diameter_avg_m: float | None = None


class NeoFeedResponse(BaseModel):
    """Response model for the NEO feed endpoint."""

    start_date: date
    end_date: date
    count: int
    results: list[NeoSummary]


class NeoCloseApproach(BaseModel):
    """Normalized close approach information for a NEO detail page."""

    close_approach_date: date | None = None
    close_approach_date_full: str | None = None
    epoch_date_close_approach: int | None = None

    relative_velocity_kmh: float | None = None
    miss_distance_km: float | None = None

    orbiting_body: str | None = None


class NeoOrbitalData(BaseModel):
    """Normalized orbital information returned by NASA NeoWs."""

    orbit_id: str | None = None
    orbit_determination_date: str | None = None

    first_observation_date: date | None = None
    last_observation_date: date | None = None

    data_arc_in_days: int | None = None
    observations_used: int | None = None

    orbit_class_type: str | None = None
    orbit_class_description: str | None = None
    orbit_class_range: str | None = None


class NeoDetailResponse(BaseModel):
    """Detailed normalized information for a single Near Earth Object."""

    id: str
    name: str
    designation: str | None = None

    nasa_jpl_url: str | None = None
    absolute_magnitude_h: float | None = None

    is_potentially_hazardous: bool
    is_sentry_object: bool

    diameter_min_m: float | None = None
    diameter_max_m: float | None = None
    diameter_avg_m: float | None = None

    orbital_data: NeoOrbitalData | None = None
    close_approaches: list[NeoCloseApproach]


class NeoDailyCount(BaseModel):
    """Number of NEOs grouped by close approach date."""

    date: date
    count: int


class NeoHazardousDistributionItem(BaseModel):
    """Chart-friendly item representing hazardous/non-hazardous distribution."""

    label: str
    value: int


class NeoStatsResponse(BaseModel):
    """Aggregated statistics for the NEO dashboard."""

    start_date: date
    end_date: date

    total_count: int
    hazardous_count: int
    non_hazardous_count: int

    average_diameter_m: float | None = None
    min_miss_distance_km: float | None = None
    max_relative_velocity_kmh: float | None = None

    closest_neo: NeoSummary | None = None
    fastest_neo: NeoSummary | None = None
    largest_neo: NeoSummary | None = None

    daily_counts: list[NeoDailyCount]
    hazardous_distribution: list[NeoHazardousDistributionItem]