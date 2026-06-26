"""Threat Intelligence Agent API integration tests."""

import uuid
from io import BytesIO

import pytest
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

POWERSHELL_LOG = (
    b"2026-06-24T08:15:03Z HOST=WS-FIN-042 USER=DOMAIN\\jsmith "
    b"EVENT=NetworkConnect DEST=185.234.72.19:443 LOCAL=192.168.10.25\n"
    b"2026-06-24T08:15:08Z URL=http://malicious.example.com/stage.ps1 "
    b"EMAIL=security@example.com\n"
    b"2026-06-24T08:15:10Z HASH="
    b"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855\n"
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


def test_threat_intelligence_agent_initializes_on_startup() -> None:
    """Threat Intelligence Agent is loaded with ADK configuration."""
    from app.core.threat_intelligence_runtime import get_threat_intelligence_agent

    agent = get_threat_intelligence_agent()
    assert agent.is_loaded is True
    assert agent.name == "threat_intelligence"


def test_threat_intelligence_endpoint_returns_report(
    client: TestClient, db_session: Session, upload_dir
) -> None:
    """POST /agents/threat-intelligence returns IOCs and a structured report."""
    incident_id = _create_incident(client)
    log_id = _upload_log(client, "powershell_execution.log", POWERSHELL_LOG, incident_id)

    response = client.post(
        "/api/v1/agents/threat-intelligence",
        json={"incident_id": incident_id, "evidence_id": log_id},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Threat intelligence enrichment completed"

    data = body["data"]
    assert data["status"] == "completed"
    assert data["ioc_count"] >= 3
    assert data["report"]["total_iocs"] == data["ioc_count"]
    assert any(ioc["type"] == "IPv4" for ioc in data["iocs"])

    executions = list(
        db_session.scalars(
            select(AgentExecution).where(
                AgentExecution.agent_name == "Threat Intelligence Agent"
            )
        ).all()
    )
    assert len(executions) == 1
    assert executions[0].status == AgentExecutionStatus.COMPLETED


def test_threat_intelligence_missing_evidence_returns_404(client: TestClient) -> None:
    """Unknown evidence IDs return a not-found error."""
    incident_id = _create_incident(client)

    response = client.post(
        "/api/v1/agents/threat-intelligence",
        json={"incident_id": incident_id, "evidence_id": str(uuid.uuid4())},
    )

    assert response.status_code == 404
    assert response.json()["message"] == "Log file not found"


def test_orchestrate_invokes_threat_intelligence_agent(
    client: TestClient, db_session: Session, upload_dir
) -> None:
    """Coordinator orchestration invokes Threat Intelligence Agent after Evidence Agent."""
    incident_id = _create_incident(client)
    log_id = _upload_log(client, "powershell_execution.log", POWERSHELL_LOG, incident_id)

    response = client.post(
        "/api/v1/agents/orchestrate",
        json={"incident_id": incident_id, "log_id": log_id},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["evidence_result"] is not None
    assert data["threat_intelligence_result"] is not None
    assert data["threat_intelligence_result"]["ioc_count"] >= 1

    executions = list(db_session.scalars(select(AgentExecution)).all())
    agent_names = {execution.agent_name for execution in executions}
    assert "Coordinator Agent" in agent_names
    assert "Evidence Agent" in agent_names
    assert "Threat Intelligence Agent" in agent_names
