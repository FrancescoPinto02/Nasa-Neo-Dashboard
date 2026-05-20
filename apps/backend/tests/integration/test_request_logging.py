from fastapi.testclient import TestClient

from app.main import app


def test_response_includes_generated_request_id() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert "x-request-id" in response.headers
    assert response.headers["x-request-id"]


def test_response_reuses_incoming_request_id() -> None:
    client = TestClient(app)

    response = client.get(
        "/api/v1/health",
        headers={"X-Request-ID": "test-request-id"},
    )

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "test-request-id"