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