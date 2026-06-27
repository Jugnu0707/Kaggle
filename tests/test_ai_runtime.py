"""AI runtime and MCP integration tests."""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.ai.metrics import get_runtime_metrics
from app.ai.runtime import get_ai_runtime


def test_ai_runtime_initialized(client: TestClient) -> None:
    """AI runtime is ready after application startup."""
    runtime = get_ai_runtime()
    status = runtime.get_status()

    assert status["runtime"] is True
    assert status["adk"] is True
    assert status["registered_agents"] == 8
    assert status["registered_tools"] == 5
    assert len(runtime.discover_tools()) == 5


def test_health_endpoint_runtime_fields(client: TestClient) -> None:
    """Health endpoint reports runtime, agent, and tool registration counts."""
    response = client.get("/api/v1/health")
    data = response.json()["data"]

    assert data["runtime"] is True
    assert data["registered_agents"] == 8
    assert data["registered_tools"] == 5


def test_mcp_tools_executed_via_runtime(client: TestClient) -> None:
    """Evidence collection invokes MCP tools through the AI runtime."""
    get_runtime_metrics().reset()

    incident_response = client.post(
        "/api/v1/incidents",
        json={
            "title": "Runtime MCP Test",
            "description": "Verify MCP tool execution",
            "severity": "Medium",
            "source": "test",
        },
    )
    incident_id = incident_response.json()["data"]["id"]

    upload_response = client.post(
        "/api/v1/logs/upload",
        files={"file": ("runtime-test.log", b"2024-01-01 10:00:00 login failed", "text/plain")},
        data={"incident_id": incident_id},
    )
    log_id = upload_response.json()["data"]["file_id"]

    evidence_response = client.post(
        "/api/v1/agents/evidence",
        json={"incident_id": incident_id, "log_file_id": log_id},
    )

    assert evidence_response.status_code == 200
    metrics = get_runtime_metrics().snapshot()
    assert metrics.tool_execution_count >= 2


def test_coordinator_uses_mcp_incident_details(client: TestClient) -> None:
    """Coordinator orchestration validates incidents through MCP."""
    get_runtime_metrics().reset()

    incident_response = client.post(
        "/api/v1/incidents",
        json={
            "title": "Coordinator MCP Test",
            "description": "Orchestration via runtime",
            "severity": "Low",
            "source": "test",
        },
    )
    incident_id = incident_response.json()["data"]["id"]

    orchestrate_response = client.post(
        "/api/v1/agents/orchestrate",
        json={"incident_id": incident_id},
    )

    assert orchestrate_response.status_code == 200
    assert orchestrate_response.json()["data"]["status"] == "accepted"
    metrics = get_runtime_metrics().snapshot()
    assert metrics.tool_execution_count >= 1
    assert metrics.adk_session_count >= 1


def test_evaluation_overview_includes_runtime_metrics(client: TestClient) -> None:
    """Evaluation overview exposes MCP and ADK session runtime metrics."""
    response = client.get("/api/v1/evaluation")
    assert response.status_code == 200
    data = response.json()["data"]

    assert "tool_execution_count" in data
    assert "tool_failure_count" in data
    assert "mean_adk_session_duration_ms" in data


def test_ai_fallback_without_api_key(client: TestClient) -> None:
    """Risk assessment falls back when no Gemini API key is configured."""
    incident_response = client.post(
        "/api/v1/incidents",
        json={
            "title": "Fallback Test",
            "description": "No API key fallback path",
            "severity": "High",
            "source": "test",
        },
    )
    incident_id = incident_response.json()["data"]["id"]

    with patch("app.ai.provider.GeminiProvider.has_api_key", return_value=False):
        risk_response = client.post(
            "/api/v1/agents/risk",
            json={"incident_id": incident_id},
        )

    assert risk_response.status_code == 200
    assert risk_response.json()["success"] is True
