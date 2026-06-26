"""Guardian Agent API integration tests."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.guardian_audit import GuardianAudit

VALID_RISK_RESPONSE = {
    "source": "AI",
    "overall_risk": "High",
    "risk_score": 80,
    "likelihood": "Likely",
    "business_impact": "Significant disruption",
    "confidence": 85,
    "priority": "P2",
    "summary": "High-risk incident requiring leadership review.",
    "reasoning": "Multiple suspicious indicators observed.",
}


def test_guardian_agent_initializes_on_startup() -> None:
    """Guardian Agent is loaded with ADK configuration."""
    from app.core.guardian_runtime import get_guardian_agent, initialize_guardian_runtime

    initialize_guardian_runtime()
    agent = get_guardian_agent()
    assert agent.is_loaded is True
    assert agent.name == "guardian"


def test_guardian_validate_approves_valid_response(
    client: TestClient, db_session: Session
) -> None:
    """POST /agents/guardian/validate approves valid agent output."""
    response = client.post(
        "/api/v1/agents/guardian/validate",
        json={"agent": "risk", "response": VALID_RISK_RESPONSE},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "approved"
    assert body["data"]["masked_response"] is not None

    audits = list(db_session.scalars(select(GuardianAudit)).all())
    assert len(audits) == 1
    assert audits[0].validation_status == "approved"


def test_guardian_validate_rejects_empty_response(client: TestClient) -> None:
    """Empty responses are rejected with fallback triggered."""
    response = client.post(
        "/api/v1/agents/guardian/validate",
        json={"agent": "risk", "response": {}},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "rejected"
    assert data["fallback_triggered"] is True


def test_guardian_validate_masks_secret(client: TestClient) -> None:
    """Detected secrets are masked in the returned response."""
    payload = dict(VALID_RISK_RESPONSE)
    payload["summary"] = "Token Bearer abc.def.ghi was found in notes."

    response = client.post(
        "/api/v1/agents/guardian/validate",
        json={"agent": "risk", "response": payload},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] in {"approved", "warning"}
    assert "[REDACTED_SECRET]" in data["masked_response"]["summary"]


def test_guardian_validate_rejects_low_confidence(client: TestClient) -> None:
    """Low-confidence AI responses trigger fallback."""
    payload = dict(VALID_RISK_RESPONSE)
    payload["confidence"] = 20

    response = client.post(
        "/api/v1/agents/guardian/validate",
        json={"agent": "risk", "response": payload},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "rejected"
    assert data["fallback_triggered"] is True


def test_get_incident_guardian_audits_returns_records(
    client: TestClient, db_session: Session
) -> None:
    """GET /incidents/{id}/guardian-audits returns persisted audit records."""
    create = client.post(
        "/api/v1/incidents",
        json={
            "title": "Guardian Audit Test",
            "description": "Validate Guardian audit persistence.",
            "severity": "Medium",
            "source": "Unit Test",
        },
    )
    incident_id = create.json()["data"]["id"]

    client.post(
        "/api/v1/agents/guardian/validate",
        json={
            "agent": "risk",
            "incident_id": incident_id,
            "response": VALID_RISK_RESPONSE,
        },
    )

    response = client.get(f"/api/v1/incidents/{incident_id}/guardian-audits")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] == 1
    assert body["data"]["items"][0]["agent_name"] == "Risk Assessment Agent"


def test_guardian_validate_unknown_incident_returns_404(client: TestClient) -> None:
    """Unknown incident IDs return a not-found error."""
    response = client.post(
        "/api/v1/agents/guardian/validate",
        json={
            "agent": "risk",
            "incident_id": str(uuid.uuid4()),
            "response": VALID_RISK_RESPONSE,
        },
    )

    assert response.status_code == 404
    assert response.json()["success"] is False
