from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.errors import ExternalServiceError, InvalidDateRangeError
from app.core.exception_handlers import register_exception_handlers


def test_invalid_date_range_error_returns_standard_payload() -> None:
    app = _create_test_app()
    client = TestClient(app)

    response = client.get("/invalid-date-range")

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "invalid_date_range",
            "message": "Invalid date range.",
        }
    }


def test_external_service_error_returns_standard_payload() -> None:
    app = _create_test_app()
    client = TestClient(app)

    response = client.get("/external-service-error")

    assert response.status_code == 502
    assert response.json() == {
        "error": {
            "code": "external_service_error",
            "message": "NASA NeoWs request failed.",
        }
    }


def test_validation_error_returns_standard_payload() -> None:
    app = _create_test_app()
    client = TestClient(app)

    response = client.get("/validation-error?value=not-an-int")

    payload = response.json()

    assert response.status_code == 422
    assert payload["error"]["code"] == "validation_error"
    assert payload["error"]["message"] == "Request validation failed."
    assert isinstance(payload["error"]["details"], list)
    assert payload["error"]["details"][0]["loc"] == ["query", "value"]


def test_http_404_returns_standard_payload() -> None:
    app = _create_test_app()
    client = TestClient(app)

    response = client.get("/missing-route")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "not_found",
            "message": "Not Found",
        }
    }


def _create_test_app() -> FastAPI:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/invalid-date-range")
    async def invalid_date_range() -> dict[str, str]:
        raise InvalidDateRangeError("Invalid date range.")

    @app.get("/external-service-error")
    async def external_service_error() -> dict[str, str]:
        raise ExternalServiceError("NASA NeoWs request failed.")

    @app.get("/validation-error")
    async def validation_error(value: int) -> dict[str, int]:
        return {"value": value}

    return app