from time import perf_counter
from uuid import uuid4

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from structlog.contextvars import bind_contextvars, clear_contextvars


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Add request-scoped logging context and log HTTP request outcomes.

    Each request receives a request ID. If the client sends X-Request-ID, we
    reuse it; otherwise we generate a new UUID. The value is also returned in
    the response header so frontend and backend logs can be correlated.
    """

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
        request_id = request.headers.get("X-Request-ID") or str(uuid4())

        clear_contextvars()
        bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        logger = structlog.get_logger(__name__)
        started_at = perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = _elapsed_ms(started_at)

            logger.exception(
                "request.failed",
                duration_ms=duration_ms,
                query_string=request.url.query or None,
            )

            raise
        else:
            duration_ms = _elapsed_ms(started_at)
            response.headers["X-Request-ID"] = request_id

            logger.info(
                "request.completed",
                status_code=response.status_code,
                duration_ms=duration_ms,
                query_string=request.url.query or None,
            )

            return response
        finally:
            clear_contextvars()


def _elapsed_ms(started_at: float) -> float:
    """Return elapsed time in milliseconds rounded to two decimals."""
    return round((perf_counter() - started_at) * 1000, 2)