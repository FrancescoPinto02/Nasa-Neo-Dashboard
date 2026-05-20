from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.errors import ExternalServiceError, InvalidDateRangeError
from app.schemas.errors import ApiError, ApiErrorResponse


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register application-wide exception handlers.

    Keeping exception mapping centralized makes routes smaller and ensures
    frontend clients always receive a consistent error payload.
    """

    @app.exception_handler(InvalidDateRangeError)
    async def invalid_date_range_handler(
        _request: Request,
        exc: InvalidDateRangeError,
    ) -> JSONResponse:
        return _build_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="invalid_date_range",
            message=str(exc),
        )

    @app.exception_handler(ExternalServiceError)
    async def external_service_error_handler(
        _request: Request,
        exc: ExternalServiceError,
    ) -> JSONResponse:
        return _build_error_response(
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="external_service_error",
            message=str(exc),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return _build_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            code="validation_error",
            message="Request validation failed.",
            details=exc.errors(),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        _request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        return _build_error_response(
            status_code=exc.status_code,
            code=_http_error_code(exc.status_code),
            message=str(exc.detail),
            headers=exc.headers,
        )


def _build_error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    details: Any | None = None,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    """Build a JSONResponse using the standard API error envelope."""
    payload = ApiErrorResponse(
        error=ApiError(
            code=code,
            message=message,
            details=details,
        )
    )

    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(payload.model_dump(exclude_none=True)),
        headers=headers,
    )

def _http_error_code(status_code: int) -> str:
    """Return a stable error code for generic HTTP errors."""
    if status_code == status.HTTP_404_NOT_FOUND:
        return "not_found"

    if status_code == status.HTTP_401_UNAUTHORIZED:
        return "unauthorized"

    if status_code == status.HTTP_403_FORBIDDEN:
        return "forbidden"

    if status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
        return "method_not_allowed"

    return "http_error"