from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_neo_service
from app.core.errors import ExternalServiceError, InvalidDateRangeError
from app.schemas.neo import NeoFeedResponse, NeoSortBy, SortOrder
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