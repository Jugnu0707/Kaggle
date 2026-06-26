"""Threat Intelligence Agent API integration tests."""

import uuid
from io import BytesIO
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from google.genai import errors as genai_errors
from sqlalchemy import select
from sqlalchemy.orm import Session

from agents.threat_intelligence.schemas import (
    AIEnrichedFinding,
    AIThreatIntelligenceResponse,
)
from app.models.agent_execution import AgentExecution
from app.models.enums import AgentExecutionStatus
from app.models.threat_intelligence_finding import ThreatIntelligenceFinding

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


def test_threat_intelligence_endpoint_returns_findings(
    client: TestClient, db_session: Session, upload_dir
) -> None:
    """POST /agents/threat-intelligence returns enriched findings."""
    incident_id = _create_incident(client)
    _upload_log(client, "powershell_execution.log", POWERSHELL_LOG, incident_id)

    response = client.post(
        "/api/v1/agents/threat-intelligence",
        json={"incident_id": incident_id},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Threat intelligence enrichment completed"

    data = body["data"]
    assert data["status"] == "completed"
    assert data["ioc_count"] >= 3
    assert len(data["findings"]) == data["ioc_count"]
    assert any(finding["indicator_type"] == "IPv4" for finding in data["findings"])
    assert all(finding["source"] == "FALLBACK" for finding in data["findings"])

    records = list(db_session.scalars(select(ThreatIntelligenceFinding)).all())
    assert len(records) == data["ioc_count"]

    executions = list(
        db_session.scalars(
            select(AgentExecution).where(
                AgentExecution.agent_name == "Threat Intelligence Agent"
            )
        ).all()
    )
    assert len(executions) == 1
    assert executions[0].status == AgentExecutionStatus.COMPLETED


def test_threat_intelligence_fallback_on_quota_exceeded(
    client: TestClient, upload_dir
) -> None:
    """POST /agents/threat-intelligence falls back when Gemini returns 429."""
    incident_id = _create_incident(client)
    _upload_log(client, "powershell_execution.log", POWERSHELL_LOG, incident_id)

    with patch(
        "agents.threat_intelligence.service.ThreatIntelligenceService._call_gemini",
        side_effect=genai_errors.ClientError(
            429,
            {"error": {"message": "Quota exceeded"}},
            None,
        ),
    ):
        response = client.post(
            "/api/v1/agents/threat-intelligence",
            json={"incident_id": incident_id},
        )

    assert response.status_code == 200
    data = response.json()["data"]
    assert all(finding["source"] == "FALLBACK" for finding in data["findings"])


def test_threat_intelligence_endpoint_ai_success(
    client: TestClient, db_session: Session, upload_dir
) -> None:
    """POST /agents/threat-intelligence persists AI findings when Gemini succeeds."""
    incident_id = _create_incident(client)
    _upload_log(client, "powershell_execution.log", POWERSHELL_LOG, incident_id)

    def fake_gemini(_api_key, _model, iocs, _context_text):
        return AIThreatIntelligenceResponse(
            findings=[
                AIEnrichedFinding(
                    indicator=ioc.value,
                    indicator_type=ioc.type,
                    description=f"AI enrichment for {ioc.type} indicator.",
                    analyst_notes="Review surrounding evidence entries.",
                    confidence=ioc.confidence,
                )
                for ioc in iocs
            ]
        )

    with patch(
        "agents.threat_intelligence.service.ThreatIntelligenceService._call_gemini",
        side_effect=fake_gemini,
    ):
        response = client.post(
            "/api/v1/agents/threat-intelligence",
            json={"incident_id": incident_id},
        )

    assert response.status_code == 200
    findings = response.json()["data"]["findings"]
    assert findings
    assert all(finding["source"] == "AI" for finding in findings)

    records = list(db_session.scalars(select(ThreatIntelligenceFinding)).all())
    assert all(record.source == "AI" for record in records)


def test_get_incident_threat_intelligence_returns_persisted_findings(
    client: TestClient, upload_dir
) -> None:
    """GET /incidents/{id}/threat-intelligence returns persisted findings."""
    incident_id = _create_incident(client)
    _upload_log(client, "powershell_execution.log", POWERSHELL_LOG, incident_id)
    client.post(
        "/api/v1/agents/threat-intelligence",
        json={"incident_id": incident_id},
    )

    response = client.get(f"/api/v1/incidents/{incident_id}/threat-intelligence")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] >= 3


def test_threat_intelligence_missing_incident_returns_404(client: TestClient) -> None:
    """Unknown incident IDs return a not-found error."""
    response = client.post(
        "/api/v1/agents/threat-intelligence",
        json={"incident_id": str(uuid.uuid4())},
    )

    assert response.status_code == 404
    assert response.json()["message"] == "Incident not found"


def test_orchestrate_invokes_threat_intelligence_before_mitre(
    client: TestClient, db_session: Session, upload_dir
) -> None:
    """Coordinator orchestration invokes Threat Intelligence before MITRE Mapping."""
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
    assert data["mitre_result"] is not None

    executions = list(db_session.scalars(select(AgentExecution)).all())
    agent_names = [execution.agent_name for execution in executions]
    ti_index = agent_names.index("Threat Intelligence Agent")
    mitre_index = agent_names.index("MITRE Mapping Agent")
    assert ti_index < mitre_index
