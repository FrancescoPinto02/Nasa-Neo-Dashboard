from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.api.deps import get_neo_service
from app.core.errors import ExternalServiceError, InvalidDateRangeError
from app.schemas.neo import NeoDetailResponse, NeoFeedResponse, NeoSortBy, SortOrder, NeoStatsResponse
from app.services.neo_service import NeoService


router = APIRouter()


@router.get("/neos", response_model=NeoFeedResponse)
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
    try:
        return await neo_service.list_neos(
            start_date=start_date,
            end_date=end_date,
            hazardous=hazardous,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    except InvalidDateRangeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except ExternalServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


@router.get("/neos/stats", response_model=NeoStatsResponse)
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
    try:
        return await neo_service.get_neo_stats(
            start_date=start_date,
            end_date=end_date,
        )
    except InvalidDateRangeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except ExternalServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


@router.get("/neos/{neo_id}", response_model=NeoDetailResponse)
async def get_neo_detail(
    neo_id: str = Path(
        ...,
        min_length=1,
        description="NASA/JPL Small-Body database ID.",
    ),
    neo_service: NeoService = Depends(get_neo_service),
) -> NeoDetailResponse:
    """Return detailed normalized information for one Near Earth Object."""
    try:
        return await neo_service.get_neo_detail(neo_id=neo_id)
    except ExternalServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc