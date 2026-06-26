"""Executive Report Agent API integration tests."""

import uuid
from io import BytesIO
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from google.genai import errors as genai_errors
from sqlalchemy import select
from sqlalchemy.orm import Session

from agents.executive_report.schemas import AIExecutiveReportResponse
from app.models.agent_execution import AgentExecution
from app.models.enums import AgentExecutionStatus
from app.models.executive_report import ExecutiveReport

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


def test_executive_report_agent_initializes_on_startup() -> None:
    """Executive Report Agent is loaded with ADK configuration."""
    from app.core.executive_report_runtime import (
        get_executive_report_agent,
        initialize_executive_report_runtime,
    )

    initialize_executive_report_runtime()
    agent = get_executive_report_agent()
    assert agent.is_loaded is True
    assert agent.name == "executive_report"


def test_executive_report_endpoint_fallback_on_quota_exceeded(
    client: TestClient, db_session: Session, upload_dir
) -> None:
    """POST /agents/executive-report falls back when Gemini returns 429."""
    incident_id = _create_incident(client)
    _upload_log(client, "powershell_execution.log", POWERSHELL_LOG, incident_id)
    client.post("/api/v1/agents/mitre", json={"incident_id": incident_id})
    client.post("/api/v1/agents/risk", json={"incident_id": incident_id})
    client.post("/api/v1/agents/response", json={"incident_id": incident_id})

    with patch(
        "agents.executive_report.service.ExecutiveReportService._call_gemini",
        side_effect=genai_errors.ClientError(
            429,
            {"error": {"message": "Quota exceeded"}},
            None,
        ),
    ):
        response = client.post(
            "/api/v1/agents/executive-report",
            json={"incident_id": incident_id},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["source"] == "FALLBACK"
    assert data["title"] == "Executive Incident Report"
    assert len(data["key_findings"]) >= 1
    assert len(data["recommended_actions"]) >= 1
    assert "# Executive Incident Report" in data["markdown"]

    reports = list(db_session.scalars(select(ExecutiveReport)).all())
    assert len(reports) == 1
    assert reports[0].source == "FALLBACK"
    assert reports[0].markdown_report

    executions = list(
        db_session.scalars(
            select(AgentExecution).where(
                AgentExecution.agent_name == "Executive Report Agent"
            )
        ).all()
    )
    assert len(executions) == 1
    assert executions[0].status == AgentExecutionStatus.COMPLETED


def test_executive_report_endpoint_ai_success(
    client: TestClient, db_session: Session, upload_dir
) -> None:
    """POST /agents/executive-report persists AI report when Gemini succeeds."""
    incident_id = _create_incident(client)
    _upload_log(client, "powershell_execution.log", POWERSHELL_LOG, incident_id)

    ai_response = AIExecutiveReportResponse(
        title="Executive Incident Report",
        executive_summary="Leadership review is required for suspicious activity.",
        business_impact="Finance operations may face temporary disruption.",
        incident_timeline_summary="Activity was detected during the morning window.",
        key_findings=["Suspicious script execution detected"],
        mitre_summary="Observed behavior aligns with script-based execution techniques.",
        risk_summary="Enterprise risk remains elevated pending containment approval.",
        recommended_actions=["Approve endpoint isolation for affected systems"],
        lessons_learned=["Review script execution controls on critical endpoints"],
    )

    with patch(
        "agents.executive_report.service.ExecutiveReportService._call_gemini",
        return_value=ai_response,
    ):
        response = client.post(
            "/api/v1/agents/executive-report",
            json={"incident_id": incident_id},
        )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["source"] == "AI"
    assert "Leadership review" in data["executive_summary"]
    assert "Suspicious script execution detected" in data["key_findings"]

    report = db_session.scalar(select(ExecutiveReport))
    assert report is not None
    assert report.source == "AI"


def test_get_incident_executive_report_returns_persisted_report(
    client: TestClient, upload_dir
) -> None:
    """GET /incidents/{id}/executive-report returns the latest persisted report."""
    incident_id = _create_incident(client)
    _upload_log(client, "powershell_execution.log", POWERSHELL_LOG, incident_id)

    with patch(
        "agents.executive_report.service.ExecutiveReportService._call_gemini",
        return_value=None,
    ):
        client.post(
            "/api/v1/agents/executive-report",
            json={"incident_id": incident_id},
        )

    response = client.get(f"/api/v1/incidents/{incident_id}/executive-report")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["source"] == "FALLBACK"
    assert len(body["data"]["key_findings"]) >= 1
    assert body["data"]["markdown_report"]


def test_executive_report_missing_incident_returns_404(client: TestClient) -> None:
    """Unknown incident IDs return a not-found error."""
    response = client.post(
        "/api/v1/agents/executive-report",
        json={"incident_id": str(uuid.uuid4())},
    )

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Incident not found"
