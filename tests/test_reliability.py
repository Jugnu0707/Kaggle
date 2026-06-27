"""Sprint 3 reliability and fallback validation tests."""

from __future__ import annotations

from io import BytesIO
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.database import init_db

INCIDENT = {
    "title": "Reliability Test Incident",
    "description": "Fallback validation",
    "severity": "Medium",
    "source": "Test",
}

LOG_BYTES = b"2026-06-24T08:15:03Z EVENT=4625 RESULT=Failure USER=admin\n"


@pytest.fixture
def upload_dir(tmp_path, monkeypatch):
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
    response = client.post("/api/v1/incidents", json=INCIDENT)
    assert response.status_code == 201
    return response.json()["data"]["id"]


def _upload_log(client: TestClient, incident_id: str) -> None:
    response = client.post(
        "/api/v1/logs/upload",
        data={"incident_id": incident_id},
        files={"file": ("reliability.log", BytesIO(LOG_BYTES), "text/plain")},
    )
    assert response.status_code == 201


def test_investigation_when_ai_unavailable(client: TestClient, upload_dir) -> None:
    """Investigation completes using fallback engines when Gemini is unavailable."""
    incident_id = _create_incident(client)
    _upload_log(client, incident_id)

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
    assert data["status"] in {"completed", "partial"}
    fallback_steps = [s for s in data["stages"] if s.get("fallback_used")]
    assert len(fallback_steps) >= 1


def test_investigation_when_gemini_raises_quota_error(
    client: TestClient, upload_dir
) -> None:
    """Gemini quota errors trigger fallback without crashing the workflow."""
    incident_id = _create_incident(client)
    _upload_log(client, incident_id)

    def _quota_error(*_args, **_kwargs):
        raise RuntimeError("Gemini quota exceeded")

    with patch(
        "agents.risk.service.RiskAssessmentService._call_gemini",
        side_effect=_quota_error,
    ):
        response = client.post(
            "/api/v1/investigations/run",
            json={"incident_id": incident_id},
        )

    assert response.status_code == 200
    assert response.json()["data"]["duration_ms"] > 0


def test_investigation_with_invalid_ai_response(client: TestClient, upload_dir) -> None:
    """Invalid AI JSON responses fall back to rule-based engines."""
    incident_id = _create_incident(client)
    _upload_log(client, incident_id)

    with patch(
        "agents.response.service.ResponsePlanningService._call_gemini",
        return_value={"invalid": "not-a-valid-response"},
    ):
        response = client.post(
            "/api/v1/investigations/run",
            json={"incident_id": incident_id},
        )

    assert response.status_code == 200


def test_investigation_without_log_uses_skipped_stages(client: TestClient) -> None:
    """Investigation without logs skips evidence-dependent stages gracefully."""
    incident_id = _create_incident(client)
    response = client.post(
        "/api/v1/investigations/run",
        json={"incident_id": incident_id},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert "Evidence" in data["agents_failed"]
    assert "Risk" in data["agents_completed"] or "Timeline" in data["agents_completed"]


def test_database_reinitialization(client: TestClient, db_session: Session) -> None:
    """Database tables can be reinitialized without error."""
    init_db()
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["data"]["database_connected"] is True


def test_investigation_unknown_incident_returns_404(client: TestClient) -> None:
    """Running investigation for missing incident returns 404."""
    response = client.post(
        "/api/v1/investigations/run",
        json={"incident_id": "00000000-0000-0000-0000-000000000099"},
    )
    assert response.status_code == 404
