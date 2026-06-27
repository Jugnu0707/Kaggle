"""End-to-end investigation workflow tests."""

import uuid
from io import BytesIO
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import InvestigationRunStatus
from app.models.investigation_run import InvestigationRun

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


def test_run_investigation_success(
    client: TestClient, db_session: Session, upload_dir
) -> None:
    """POST /investigations/run completes the full pipeline with a log file."""
    incident_id = _create_incident(client)
    _upload_log(client, "powershell_execution.log", POWERSHELL_LOG, incident_id)

    response = client.post(
        "/api/v1/investigations/run",
        json={"incident_id": incident_id},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    data = body["data"]

    assert data["incident_id"] == incident_id
    assert data["status"] in {
        InvestigationRunStatus.COMPLETED.value,
        InvestigationRunStatus.PARTIAL.value,
    }
    assert data["duration_ms"] > 0
    assert "Evidence" in data["agents_completed"]
    assert "Timeline" in data["agents_completed"]
    assert "Evaluation" in data["agents_completed"]
    assert data["evaluation_score"] is not None
    assert data["report_id"] is not None

    runs = list(db_session.scalars(select(InvestigationRun)).all())
    assert len(runs) == 1
    assert runs[0].duration_ms is not None


def test_run_investigation_ai_unavailable_uses_fallback(
    client: TestClient, db_session: Session, upload_dir
) -> None:
    """Investigation completes when Gemini calls are unavailable."""
    incident_id = _create_incident(client)
    _upload_log(client, "powershell_execution.log", POWERSHELL_LOG, incident_id)

    with patch(
        "agents.threat_intelligence.service.ThreatIntelligenceService._call_gemini",
        return_value=None,
    ):
        with patch(
            "agents.risk.service.RiskAssessmentService._call_gemini",
            return_value=None,
        ):
            with patch(
                "agents.response.service.ResponsePlanningService._call_gemini",
                return_value=None,
            ):
                with patch(
                    "agents.executive_report.service.ExecutiveReportService._call_gemini",
                    return_value=None,
                ):
                    response = client.post(
                        "/api/v1/investigations/run",
                        json={"incident_id": incident_id},
                    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] in {
        InvestigationRunStatus.COMPLETED.value,
        InvestigationRunStatus.PARTIAL.value,
    }
    fallback_stages = [stage for stage in data["stages"] if stage.get("fallback_used")]
    assert len(fallback_stages) >= 1


def test_run_investigation_partial_without_log(client: TestClient) -> None:
    """Investigation without a log file records partial failures and continues."""
    incident_id = _create_incident(client)

    response = client.post(
        "/api/v1/investigations/run",
        json={"incident_id": incident_id},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] in {
        InvestigationRunStatus.PARTIAL.value,
        InvestigationRunStatus.COMPLETED.value,
    }
    assert "Evidence" in data["agents_failed"]
    assert "Risk" in data["agents_completed"] or "Timeline" in data["agents_completed"]


def test_run_investigation_not_found(client: TestClient) -> None:
    """Unknown incidents return 404."""
    response = client.post(
        "/api/v1/investigations/run",
        json={"incident_id": str(uuid.uuid4())},
    )
    assert response.status_code == 404


def test_get_investigation_run(client: TestClient, upload_dir) -> None:
    """GET /investigations/runs/{id} returns a persisted investigation package."""
    incident_id = _create_incident(client)
    _upload_log(client, "powershell_execution.log", POWERSHELL_LOG, incident_id)

    run_response = client.post(
        "/api/v1/investigations/run",
        json={"incident_id": incident_id},
    )
    execution_id = run_response.json()["data"]["execution_id"]

    response = client.get(f"/api/v1/investigations/runs/{execution_id}")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["execution_id"] == execution_id
    assert data["incident_id"] == incident_id
