"""Dashboard statistics API tests."""

from fastapi.testclient import TestClient


def test_dashboard_stats_endpoint(client: TestClient) -> None:
    """Dashboard stats endpoint returns aggregate metrics."""
    response = client.get("/api/v1/dashboard/stats")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"] is not None

    data = body["data"]
    assert "total_incidents" in data
    assert "critical_incidents" in data
    assert "high_incidents" in data
    assert "uploaded_logs" in data
