"""Agent orchestration API tests."""

import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.agent_execution import AgentExecution
from app.models.enums import AgentExecutionStatus

CREATE_PAYLOAD = {
    "title": "Suspicious PowerShell Execution",
    "description": "PowerShell launched from Word process.",
    "severity": "High",
    "source": "Windows Defender",
}

EXPECTED_WORKFLOW = [
    "Evidence Agent",
    "Threat Intelligence Agent",
    "MITRE Mapping Agent",
    "Risk Assessment Agent",
    "Response Planning Agent",
    "Executive Report Agent",
    "Guardian Agent",
]


def _create_incident(client: TestClient) -> str:
    response = client.post("/api/v1/incidents", json=CREATE_PAYLOAD)
    assert response.status_code == 201
    return response.json()["data"]["id"]


def test_coordinator_initializes_on_startup() -> None:
    """Coordinator Agent is loaded with ADK configuration."""
    from app.core.adk_runtime import get_coordinator

    coordinator = get_coordinator()
    assert coordinator.is_loaded is True
    assert coordinator.name == "coordinator"
    assert coordinator.adk_agent.input_schema is not None
    assert coordinator.adk_agent.output_schema is not None


def test_orchestrate_endpoint_returns_plan(
    client: TestClient, db_session: Session
) -> None:
    """POST /agents/orchestrate returns a structured orchestration plan."""
    incident_id = _create_incident(client)

    response = client.post(
        "/api/v1/agents/orchestrate",
        json={"incident_id": incident_id},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Orchestration plan generated"

    data = body["data"]
    assert data["incident_id"] == incident_id
    assert data["status"] == "accepted"
    assert data["workflow"] == EXPECTED_WORKFLOW
    assert "workflow_id" in data

    executions = list(db_session.scalars(select(AgentExecution)).all())
    assert len(executions) == 1
    execution = executions[0]
    assert execution.agent_name == "Coordinator Agent"
    assert execution.status == AgentExecutionStatus.ACCEPTED
    assert str(execution.workflow_id) == data["workflow_id"]
    assert execution.duration_ms is not None
    assert execution.completed_at is not None


def test_orchestrate_invalid_incident_returns_404(client: TestClient) -> None:
    """Unknown incident IDs return a not-found error."""
    response = client.post(
        "/api/v1/agents/orchestrate",
        json={"incident_id": str(uuid.uuid4())},
    )

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Incident not found"


def test_orchestrate_requires_identifier(client: TestClient) -> None:
    """Requests without incident_id or log_id are rejected."""
    response = client.post("/api/v1/agents/orchestrate", json={})

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
