from typing import Any

from pydantic import BaseModel


class ApiError(BaseModel):
    """
    Standard API error payload.

    The frontend can rely on this shape for all handled backend errors.
    """

    code: str
    message: str
    details: Any | None = None


class ApiErrorResponse(BaseModel):
    """Standard API error response envelope."""

    error: ApiError