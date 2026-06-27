"""MITRE Mapping Agent API integration tests."""

import uuid
from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.agent_execution import AgentExecution
from app.models.enums import AgentExecutionStatus
from app.models.mitre_finding import MitreFinding

CREATE_PAYLOAD = {
    "title": "Suspicious PowerShell Execution",
    "description": "PowerShell launched from Word process.",
    "severity": "High",
    "source": "Windows Defender",
}

POWERSHELL_LOG = (
    b"2026-06-24T08:15:03Z HOST=WS-FIN-042 PROCESS=powershell.exe "
    b"CMD=-EncodedCommand ABC123\n"
)

FAILED_LOGIN_LOG = (
    b"2026-06-24T09:00:00Z EVENT=4625 failed logon user=admin bad password\n"
)

UNKNOWN_LOG = b"2026-06-24T10:00:00Z INFO application started normally\n"


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


def test_mitre_agent_initializes_on_startup() -> None:
    """MITRE Mapping Agent is loaded with ADK configuration."""
    from app.core.mitre_runtime import get_mitre_agent

    agent = get_mitre_agent()
    assert agent.is_loaded is True
    assert agent.name == "mitre_mapping"


def test_mitre_endpoint_maps_powershell_logs(
    client: TestClient, db_session: Session, upload_dir
) -> None:
    """POST /agents/mitre maps PowerShell evidence to ATT&CK techniques."""
    incident_id = _create_incident(client)
    _upload_log(client, "powershell_execution.log", POWERSHELL_LOG, incident_id)

    response = client.post(
        "/api/v1/agents/mitre",
        json={"incident_id": incident_id},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "MITRE mapping completed"

    data = body["data"]
    assert data["status"] == "completed"
    assert any(item["technique_id"] == "T1059.001" for item in data["techniques"])

    findings = list(
        db_session.scalars(
            select(MitreFinding).where(
                MitreFinding.incident_id == uuid.UUID(incident_id)
            )
        ).all()
    )
    assert len(findings) >= 1

    executions = list(
        db_session.scalars(
            select(AgentExecution).where(
                AgentExecution.agent_name == "MITRE Mapping Agent"
            )
        ).all()
    )
    assert len(executions) == 1
    assert executions[0].status == AgentExecutionStatus.COMPLETED


def test_mitre_endpoint_maps_failed_login_logs(client: TestClient, upload_dir) -> None:
    """POST /agents/mitre maps failed login evidence to T1110."""
    incident_id = _create_incident(client)
    _upload_log(client, "failed_login.log", FAILED_LOGIN_LOG, incident_id)

    response = client.post(
        "/api/v1/agents/mitre",
        json={"incident_id": incident_id},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert any(item["technique_id"] == "T1110" for item in data["techniques"])


def test_mitre_endpoint_unknown_logs_return_no_mapping(
    client: TestClient, upload_dir
) -> None:
    """Unknown logs return an empty technique list with a no-mapping message."""
    incident_id = _create_incident(client)
    _upload_log(client, "benign.log", UNKNOWN_LOG, incident_id)

    response = client.post(
        "/api/v1/agents/mitre",
        json={"incident_id": incident_id},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "completed"
    assert data["techniques"] == []
    assert data["message"] == "No mapping found."


def test_get_incident_mitre_returns_persisted_findings(
    client: TestClient, upload_dir
) -> None:
    """GET /incidents/{id}/mitre returns persisted MITRE findings."""
    incident_id = _create_incident(client)
    _upload_log(client, "powershell_execution.log", POWERSHELL_LOG, incident_id)
    client.post("/api/v1/agents/mitre", json={"incident_id": incident_id})

    response = client.get(f"/api/v1/incidents/{incident_id}/mitre")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] >= 1
    technique_ids = {item["technique_id"] for item in body["data"]["items"]}
    assert "T1059.001" in technique_ids


def test_mitre_missing_incident_returns_404(client: TestClient) -> None:
    """Unknown incident IDs return a not-found error."""
    response = client.post(
        "/api/v1/agents/mitre",
        json={"incident_id": str(uuid.uuid4())},
    )

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Incident not found"
