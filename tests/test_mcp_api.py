"""MCP API endpoint tests."""

from fastapi.testclient import TestClient
from mcp.registry import get_registry

EXPECTED_TOOLS = [
    "health",
    "incident_details",
    "list_incidents",
    "list_logs",
    "system_info",
]


def test_mcp_status_endpoint(client: TestClient) -> None:
    """MCP status endpoint returns running state and registered tools."""
    response = client.get("/api/v1/system/mcp")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "MCP status retrieved"

    data = body["data"]
    assert data["mcp"] is True
    assert data["tool_count"] == 5
    assert data["tools"] == EXPECTED_TOOLS


def test_health_endpoint_includes_mcp_status(client: TestClient) -> None:
    """Health endpoint reports MCP server status."""
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["data"]["mcp"] is True


def test_health_tool_invocation(client: TestClient, db_session) -> None:
    """Health MCP tool executes without AI calls."""
    result = get_registry().invoke("health", {}, db_session)

    assert result.success is True
    assert result.data is not None
    assert result.data.status == "healthy"
    assert result.error is None
