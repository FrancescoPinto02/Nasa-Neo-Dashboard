from datetime import date

from fastapi import APIRouter, Depends, Path, Query

from app.api.deps import get_neo_service
from app.schemas.errors import ApiErrorResponse
from app.schemas.neo import (
    NeoDetailResponse,
    NeoFeedResponse,
    NeoSortBy,
    NeoStatsResponse,
    SortOrder,
)
from app.services.neo_service import NeoService


router = APIRouter()


@router.get(
    "/neos",
    response_model=NeoFeedResponse,
    responses={
        400: {"model": ApiErrorResponse},
        422: {"model": ApiErrorResponse},
        502: {"model": ApiErrorResponse},
    },
)
async def list_neos(
    start_date: date = Query(
        ...,
        description="First date included in the search range. Format: YYYY-MM-DD.",
    ),
    end_date: date = Query(
        ...,
        description="Last date included in the search range. Format: YYYY-MM-DD.",
    ),
    hazardous: bool | None = Query(
        default=None,
        description="Filter by potentially hazardous asteroids. Omit to include all.",
    ),
    sort_by: NeoSortBy = Query(
        default=NeoSortBy.DATE,
        description="Field used to sort the results.",
    ),
    sort_order: SortOrder = Query(
        default=SortOrder.ASC,
        description="Sort direction.",
    ),
    neo_service: NeoService = Depends(get_neo_service),
) -> NeoFeedResponse:
    """Return normalized Near Earth Objects for a date range."""
    return await neo_service.list_neos(
        start_date=start_date,
        end_date=end_date,
        hazardous=hazardous,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get(
    "/neos/stats",
    response_model=NeoStatsResponse,
    responses={
        400: {"model": ApiErrorResponse},
        422: {"model": ApiErrorResponse},
        502: {"model": ApiErrorResponse},
    },
)
async def get_neo_stats(
    start_date: date = Query(
        ...,
        description="First date included in the statistics range. Format: YYYY-MM-DD.",
    ),
    end_date: date = Query(
        ...,
        description="Last date included in the statistics range. Format: YYYY-MM-DD.",
    ),
    neo_service: NeoService = Depends(get_neo_service),
) -> NeoStatsResponse:
    """Return aggregated NEO statistics for dashboard charts and summary cards."""
    return await neo_service.get_neo_stats(
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/neos/{neo_id}",
    response_model=NeoDetailResponse,
    responses={
        422: {"model": ApiErrorResponse},
        502: {"model": ApiErrorResponse},
    },
)
async def get_neo_detail(
    neo_id: str = Path(
        ...,
        min_length=1,
        description="NASA/JPL Small-Body database ID.",
    ),
    neo_service: NeoService = Depends(get_neo_service),
) -> NeoDetailResponse:
    """Return detailed normalized information for one Near Earth Object."""
    return await neo_service.get_neo_detail(neo_id=neo_id)