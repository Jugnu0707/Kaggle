"""Evidence Agent API integration tests."""

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
    mime_type: str,
    incident_id: str | None = None,
) -> str:
    data = {"incident_id": incident_id} if incident_id else None
    response = client.post(
        "/api/v1/logs/upload",
        data=data,
        files={"file": (filename, BytesIO(content), mime_type)},
    )
    assert response.status_code == 201
    return response.json()["data"]["file_id"]


def test_evidence_agent_initializes_on_startup() -> None:
    """Evidence Agent is loaded with ADK configuration."""
    from app.core.evidence_runtime import get_evidence_agent

    agent = get_evidence_agent()
    assert agent.is_loaded is True
    assert agent.name == "evidence"


def test_collect_evidence_for_log_file(
    client: TestClient, db_session: Session, upload_dir
) -> None:
    """POST /agents/evidence returns a completed evidence package."""
    incident_id = _create_incident(client)
    log_id = _upload_log(
        client,
        "events.log",
        b"2026-06-26T10:00:00 ERROR suspicious process started\n",
        "text/plain",
        incident_id=incident_id,
    )

    response = client.post(
        "/api/v1/agents/evidence",
        json={"incident_id": incident_id, "log_file_id": log_id},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Evidence collected"

    data = body["data"]
    assert data["status"] == "completed"
    assert data["evidence_package"]["incident_id"] == incident_id
    assert data["evidence_package"]["uploaded_file_id"] == log_id
    assert data["evidence_summary"]["total_entries"] == 1

    executions = list(
        db_session.scalars(
            select(AgentExecution).where(AgentExecution.agent_name == "Evidence Agent")
        ).all()
    )
    assert len(executions) == 1
    assert executions[0].status == AgentExecutionStatus.COMPLETED


def test_collect_evidence_json_log(client: TestClient, upload_dir) -> None:
    """JSON uploads are collected through the evidence API."""
    incident_id = _create_incident(client)
    log_id = _upload_log(
        client,
        "events.json",
        b'[{"event":"login"}]',
        "application/json",
        incident_id=incident_id,
    )

    response = client.post(
        "/api/v1/agents/evidence",
        json={"incident_id": incident_id, "log_file_id": log_id},
    )

    assert response.status_code == 200
    assert response.json()["data"]["evidence_summary"]["file_type"] == "json"


def test_collect_evidence_csv_log(client: TestClient, upload_dir) -> None:
    """CSV uploads are collected through the evidence API."""
    incident_id = _create_incident(client)
    log_id = _upload_log(
        client,
        "events.csv",
        b"timestamp,message\n2026-06-26T10:00:00,started\n",
        "text/csv",
        incident_id=incident_id,
    )

    response = client.post(
        "/api/v1/agents/evidence",
        json={"incident_id": incident_id, "log_file_id": log_id},
    )

    assert response.status_code == 200
    assert response.json()["data"]["evidence_summary"]["file_type"] == "csv"


def test_collect_evidence_txt_log(client: TestClient, upload_dir) -> None:
    """TXT uploads are collected through the evidence API."""
    incident_id = _create_incident(client)
    log_id = _upload_log(
        client,
        "events.txt",
        b"entry one\nentry two\n",
        "text/plain",
        incident_id=incident_id,
    )

    response = client.post(
        "/api/v1/agents/evidence",
        json={"incident_id": incident_id, "log_file_id": log_id},
    )

    assert response.status_code == 200
    assert response.json()["data"]["evidence_summary"]["file_type"] == "text"


def test_collect_evidence_evtx_log(client: TestClient, upload_dir) -> None:
    """EVTX uploads complete with a Sprint 2 parse note."""
    incident_id = _create_incident(client)
    log_id = _upload_log(
        client,
        "events.evtx",
        b"fake-evtx-binary",
        "application/octet-stream",
        incident_id=incident_id,
    )

    response = client.post(
        "/api/v1/agents/evidence",
        json={"incident_id": incident_id, "log_file_id": log_id},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "completed"
    assert "EVTX parsing not implemented" in data["evidence_package"]["parse_notes"]


def test_collect_evidence_missing_log_returns_404(client: TestClient) -> None:
    """Unknown log file IDs return a not-found error."""
    incident_id = _create_incident(client)

    response = client.post(
        "/api/v1/agents/evidence",
        json={"incident_id": incident_id, "log_file_id": str(uuid.uuid4())},
    )

    assert response.status_code == 404
    assert response.json()["message"] == "Log file not found"


def test_orchestrate_invokes_evidence_agent(
    client: TestClient, db_session: Session, upload_dir
) -> None:
    """Coordinator orchestration invokes Evidence Agent when a log is present."""
    incident_id = _create_incident(client)
    log_id = _upload_log(
        client,
        "events.log",
        b"2026-06-26T10:00:00 ERROR suspicious process started\n",
        "text/plain",
        incident_id=incident_id,
    )

    response = client.post(
        "/api/v1/agents/orchestrate",
        json={"incident_id": incident_id, "log_id": log_id},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["evidence_result"] is not None
    assert data["evidence_result"]["status"] == "completed"

    executions = list(db_session.scalars(select(AgentExecution)).all())
    agent_names = {execution.agent_name for execution in executions}
    assert "Coordinator Agent" in agent_names
    assert "Evidence Agent" in agent_names
