"""Integration tests for evaluation API endpoints."""

from fastapi.testclient import TestClient


def test_get_evaluation_overview(client: TestClient) -> None:
    """GET /evaluation returns overall score and agent summaries."""
    response = client.get("/api/v1/evaluation")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert "overall_score" in data
    assert isinstance(data["overall_score"], int)
    assert 0 <= data["overall_score"] <= 100
    assert isinstance(data["agents"], list)
    assert len(data["agents"]) >= 1
    assert data["total_executions"] > 0
    assert "mean_investigation_duration_ms" in data
    assert "mean_agent_execution_time_ms" in data
    assert "mean_mcp_latency_ms" in data


def test_get_agent_evaluation_detail(client: TestClient) -> None:
    """GET /evaluation/{agent_name} returns detailed agent statistics."""
    overview = client.get("/api/v1/evaluation").json()["data"]
    agent_name = overview["agents"][0]["agent_name"]

    response = client.get(f"/api/v1/evaluation/{agent_name}")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["agent_name"] == agent_name
    assert "health_score" in data
    assert "recent_executions" in data
    assert isinstance(data["recent_executions"], list)


def test_get_agent_evaluation_not_found(client: TestClient) -> None:
    """Unknown agents return 404."""
    response = client.get("/api/v1/evaluation/Unknown Agent")

    assert response.status_code == 404
