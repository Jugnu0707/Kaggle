"""Response Planning Agent API integration tests."""

import uuid
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from google.genai import errors as genai_errors
from sqlalchemy import select
from sqlalchemy.orm import Session

from agents.response.schemas import AIResponsePlanResponse
from app.models.agent_execution import AgentExecution
from app.models.enums import AgentExecutionStatus
from app.models.response_plan import ResponsePlan

CREATE_PAYLOAD = {
    "title": "Possible Ransomware Activity",
    "description": "Rapid file encryption activity detected across directories.",
    "severity": "Critical",
    "source": "CrowdStrike Falcon",
}

POWERSHELL_LOG = (
    b"2026-06-24T08:15:03Z HOST=WS-FIN-042 PROCESS=powershell.exe "
    b"CMD=-EncodedCommand ABC123\n"
)


@pytest.fixture
def upload_dir(tmp_path, monkeypatch):
    """Use an isolated upload directory for each test."""
    upload_path = tmp_path / "uploads"
    upload_path.mkdir()
    monkeypatch.setattr(
        "app.services.log_service.get_upload_path",
        lambda: upload_path,
    )
    monkeypatch.setattr(
        "agents.evidence.service.get_upload_path",
        lambda: upload_path,
    )
    return upload_path


def _create_incident(client: TestClient) -> str:
    response = client.post("/api/v1/incidents", json=CREATE_PAYLOAD)
    assert response.status_code == 201
    return response.json()["data"]["id"]


def _upload_log(
    client: TestClient,
    filename: str,
    content: bytes,
    incident_id: str,
) -> str:
    response = client.post(
        "/api/v1/logs/upload",
        data={"incident_id": incident_id},
        files={"file": (filename, BytesIO(content), "text/plain")},
    )
    assert response.status_code == 201
    return response.json()["data"]["file_id"]


def test_response_agent_initializes_on_startup() -> None:
    """Response Planning Agent is loaded with ADK configuration."""
    from app.core.response_runtime import get_response_agent

    agent = get_response_agent()
    assert agent.is_loaded is True
    assert agent.name == "response_planning"


def test_response_endpoint_fallback_on_quota_exceeded(
    client: TestClient, db_session: Session, upload_dir
) -> None:
    """POST /agents/response falls back when Gemini returns 429."""
    incident_id = _create_incident(client)
    _upload_log(client, "powershell_execution.log", POWERSHELL_LOG, incident_id)
    client.post("/api/v1/agents/mitre", json={"incident_id": incident_id})
    client.post("/api/v1/agents/risk", json={"incident_id": incident_id})

    with patch(
        "agents.response.service.ResponsePlanningService._call_gemini",
        side_effect=genai_errors.ClientError(
            429,
            {"error": {"message": "Quota exceeded"}},
            None,
        ),
    ):
        response = client.post(
            "/api/v1/agents/response",
            json={"incident_id": incident_id},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["source"] == "FALLBACK"
    assert data["priority"] in {"P1", "P2", "P3", "P4"}
    assert len(data["containment"]) >= 1

    plans = list(db_session.scalars(select(ResponsePlan)).all())
    assert len(plans) == 1
    assert plans[0].source == "FALLBACK"

    executions = list(
        db_session.scalars(
            select(AgentExecution).where(
                AgentExecution.agent_name == "Response Planning Agent"
            )
        ).all()
    )
    assert len(executions) == 1
    assert executions[0].status == AgentExecutionStatus.COMPLETED


def test_response_endpoint_ai_success(
    client: TestClient, db_session: Session, upload_dir
) -> None:
    """POST /agents/response persists AI plan when Gemini succeeds."""
    incident_id = _create_incident(client)
    _upload_log(client, "powershell_execution.log", POWERSHELL_LOG, incident_id)

    ai_response = AIResponsePlanResponse(
        priority="P1",
        containment=["Isolate affected host immediately"],
        eradication=["Remove ransomware persistence mechanisms"],
        recovery=["Restore from verified offline backups"],
        monitoring=["Monitor for re-encryption activity"],
        executive_summary="Critical ransomware response plan prioritizing containment.",
    )

    mock_provider = MagicMock()
    mock_provider.get_api_key.return_value = "test-key"
    mock_provider.get_model.return_value = "gemini-2.5-pro"

    with patch("agents.response.service.get_ai_runtime") as mock_runtime:
        mock_runtime.return_value.provider = mock_provider
        with patch(
            "agents.response.service.ResponsePlanningService._call_gemini",
            return_value=ai_response,
        ):
            response = client.post(
                "/api/v1/agents/response",
                json={"incident_id": incident_id},
            )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["source"] == "AI"
    assert data["priority"] == "P1"
    assert "Isolate affected host immediately" in data["containment"]

    plan = db_session.scalar(select(ResponsePlan))
    assert plan is not None
    assert plan.source == "AI"


def test_get_incident_response_returns_persisted_plan(
    client: TestClient, upload_dir
) -> None:
    """GET /incidents/{id}/response returns the latest persisted plan."""
    incident_id = _create_incident(client)
    _upload_log(client, "powershell_execution.log", POWERSHELL_LOG, incident_id)

    with patch(
        "agents.response.service.ResponsePlanningService._call_gemini",
        return_value=None,
    ):
        client.post("/api/v1/agents/response", json={"incident_id": incident_id})

    response = client.get(f"/api/v1/incidents/{incident_id}/response")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["source"] == "FALLBACK"
    assert len(body["data"]["containment"]) >= 1


def test_response_missing_incident_returns_404(client: TestClient) -> None:
    """Unknown incident IDs return a not-found error."""
    response = client.post(
        "/api/v1/agents/response",
        json={"incident_id": str(uuid.uuid4())},
    )

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Incident not found"
