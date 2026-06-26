"""Health endpoint tests."""

from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient) -> None:
    """Health endpoint returns the standard response envelope and health data."""
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()

    assert body["success"] is True
    assert body["message"] == "Healthy"
    assert body["data"] is not None

    data = body["data"]
    assert data["application_name"] == "Oz AI"
    assert data["version"] == "0.1.0"
    assert isinstance(data["uptime_seconds"], (int, float))
    assert data["uptime_seconds"] >= 0
    assert data["database_connected"] is True
    assert "timestamp" in data
