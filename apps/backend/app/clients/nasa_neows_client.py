from datetime import date
from typing import Any

import httpx
import structlog

from app.core.errors import ExternalServiceError


logger = structlog.get_logger(__name__)


class NasaNeoWsClient:
    """Async client for NASA NeoWs API.

    This class only handles HTTP transport concerns:
    - URL construction;
    - request execution;
    - HTTP error handling;
    - JSON parsing.

    Business logic and data normalization belong to the service layer.
    """

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        timeout_seconds: float,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._api_key = api_key
        self._owns_client = client is None

        normalized_base_url = f"{base_url.rstrip('/')}/"

        self._client = client or httpx.AsyncClient(
            base_url=normalized_base_url,
            timeout=timeout_seconds,
        )

    async def close(self) -> None:
        """Close the underlying HTTP client if this class created it."""
        if self._owns_client:
            await self._client.aclose()

    async def get_feed(self, start_date: date, end_date: date) -> dict[str, Any]:
        """Fetch the NASA NeoWs feed for an inclusive date range."""
        return await self._get_json(
            "feed",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "api_key": self._api_key,
            },
            safe_log_context={
                "resource": "feed",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
        )

    async def get_neo_by_id(self, neo_id: str) -> dict[str, Any]:
        """Fetch NASA details for a specific Near Earth Object."""
        return await self._get_json(
            f"neo/{neo_id}",
            params={"api_key": self._api_key},
            safe_log_context={
                "resource": "neo_detail",
                "neo_id": neo_id,
            },
        )

    async def _get_json(
        self,
        path: str,
        *,
        params: dict[str, str],
        safe_log_context: dict[str, str],
    ) -> dict[str, Any]:
        logger.info(
            "nasa.request.started",
            path=path,
            **safe_log_context,
        )

        try:
            response = await self._client.get(path, params=params)
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            logger.warning(
                "nasa.request.timeout",
                path=path,
                **safe_log_context,
            )
            raise ExternalServiceError("NASA NeoWs request timed out.") from exc
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            detail = _safe_response_detail(exc.response)

            logger.warning(
                "nasa.request.failed",
                path=path,
                status_code=status_code,
                **safe_log_context,
            )

            raise ExternalServiceError(
                f"NASA NeoWs returned HTTP {status_code}. {detail}"
            ) from exc
        except httpx.HTTPError as exc:
            logger.warning(
                "nasa.request.failed",
                path=path,
                **safe_log_context,
            )
            raise ExternalServiceError("NASA NeoWs request failed.") from exc

        logger.info(
            "nasa.request.completed",
            path=path,
            status_code=response.status_code,
            **safe_log_context,
        )

        try:
            payload = response.json()
        except ValueError as exc:
            raise ExternalServiceError("NASA NeoWs returned invalid JSON.") from exc

        if not isinstance(payload, dict):
            raise ExternalServiceError("NASA NeoWs returned an unexpected payload.")

        return payload


def _safe_response_detail(response: httpx.Response) -> str:
    """Extract a readable error message from an HTTP response."""
    try:
        payload = response.json()
    except ValueError:
        return response.text[:300]

    if isinstance(payload, dict):
        message = payload.get("msg") or payload.get("message") or payload.get("error")

        if message:
            return str(message)

    return str(payload)[:300]