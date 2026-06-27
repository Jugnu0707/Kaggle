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
    assert isinstance(data["uptime_seconds"], int | float)
    assert data["uptime_seconds"] >= 0
    assert data["database_connected"] is True
    assert data["status"] == "healthy"
    assert data["adk"] is True
    assert data["coordinator"] is True
    assert data["mcp"] is True
    assert data["runtime"] is True
    assert data["registered_agents"] == 8
    assert data["registered_tools"] == 5
    assert "timestamp" in data
