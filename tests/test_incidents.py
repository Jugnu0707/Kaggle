"""Incident management API tests."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.enums import IncidentStatus, InvestigationStatus, Severity
from app.models.evidence import Evidence
from app.models.investigation import Investigation

CREATE_PAYLOAD = {
    "title": "Suspicious PowerShell Execution",
    "description": "PowerShell launched from Word process.",
    "severity": "High",
    "source": "Windows Defender",
}


def _create_incident(client: TestClient) -> dict:
    response = client.post("/api/v1/incidents", json=CREATE_PAYLOAD)
    assert response.status_code == 201
    return response.json()["data"]


def test_create_incident(client: TestClient, db_session: Session) -> None:
    """POST /incidents creates an incident and audit log entry."""
    response = client.post("/api/v1/incidents", json=CREATE_PAYLOAD)

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Incident created successfully"

    data = body["data"]
    assert data["title"] == CREATE_PAYLOAD["title"]
    assert data["severity"] == "High"
    assert data["status"] == "New"
    assert data["source"] == "Windows Defender"
    assert data["deleted_at"] is None

    audit_logs = list(db_session.scalars(select(AuditLog)).all())
    assert len(audit_logs) == 1
    assert audit_logs[0].action == "CREATE"
    assert audit_logs[0].entity_type == "incident"


def test_list_incidents(client: TestClient) -> None:
    """GET /incidents supports pagination and filters."""
    _create_incident(client)
    second = client.post(
        "/api/v1/incidents",
        json={
            "title": "Critical Malware Detected",
            "description": "Unexpected outbound network traffic detected.",
            "severity": "Critical",
            "status": "Investigating",
            "source": "Network Monitor",
        },
    ).json()["data"]

    response = client.get("/api/v1/incidents?page=1&page_size=10")
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["total"] == 2
    assert len(body["items"]) == 2
    assert body["page"] == 1
    assert body["page_size"] == 10

    severity_response = client.get("/api/v1/incidents?severity=Critical")
    severity_items = severity_response.json()["data"]["items"]
    assert len(severity_items) == 1
    assert severity_items[0]["id"] == second["id"]

    status_response = client.get("/api/v1/incidents?status=New")
    assert len(status_response.json()["data"]["items"]) == 1

    search_response = client.get("/api/v1/incidents?search=powershell")
    assert len(search_response.json()["data"]["items"]) == 1


def test_get_incident(client: TestClient, db_session: Session) -> None:
    """GET /incidents/{id} returns investigation and evidence count."""
    created = _create_incident(client)
    incident_id = uuid.UUID(created["id"])

    investigation = Investigation(
        incident_id=incident_id,
        investigation_status=InvestigationStatus.RUNNING,
    )
    evidence = Evidence(
        incident_id=incident_id,
        evidence_type="log",
        filename="powershell.log",
        raw_data="event data",
        metadata_={"source": "windows"},
    )
    db_session.add_all([investigation, evidence])
    db_session.commit()

    response = client.get(f"/api/v1/incidents/{incident_id}")
    assert response.status_code == 200
    data = response.json()["data"]

    assert data["id"] == created["id"]
    assert data["evidence_count"] == 1
    assert data["investigation"] is not None
    assert data["investigation"]["investigation_status"] == "Running"


def test_update_incident(client: TestClient, db_session: Session) -> None:
    """PUT /incidents/{id} updates allowed fields and writes audit log."""
    created = _create_incident(client)
    incident_id = created["id"]

    response = client.put(
        f"/api/v1/incidents/{incident_id}",
        json={
            "title": "Updated Title",
            "description": "Updated description",
            "severity": "Medium",
            "status": "Investigating",
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["title"] == "Updated Title"
    assert data["severity"] == "Medium"
    assert data["status"] == "Investigating"
    assert data["created_at"] == created["created_at"]

    audit_logs = list(
        db_session.scalars(
            select(AuditLog).where(AuditLog.action == "UPDATE")
        ).all()
    )
    assert len(audit_logs) == 1


def test_delete_incident(client: TestClient, db_session: Session) -> None:
    """DELETE /incidents/{id} performs a soft delete."""
    created = _create_incident(client)
    incident_id = created["id"]

    response = client.delete(f"/api/v1/incidents/{incident_id}")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["deleted_at"] is not None

    get_response = client.get(f"/api/v1/incidents/{incident_id}")
    assert get_response.status_code == 404

    list_response = client.get("/api/v1/incidents")
    assert list_response.json()["data"]["total"] == 0

    audit_logs = list(
        db_session.scalars(
            select(AuditLog).where(AuditLog.action == "DELETE")
        ).all()
    )
    assert len(audit_logs) == 1


def test_validation_failure(client: TestClient) -> None:
    """Invalid payloads return HTTP 422."""
    response = client.post(
        "/api/v1/incidents",
        json={
            "title": "",
            "description": "Missing severity and source",
        },
    )
    assert response.status_code == 422
    assert response.json()["success"] is False
    assert response.json()["message"] == "Validation error"


def test_get_incident_not_found(client: TestClient) -> None:
    """Unknown incident IDs return HTTP 404."""
    missing_id = uuid.uuid4()
    response = client.get(f"/api/v1/incidents/{missing_id}")

    assert response.status_code == 404
    assert response.json()["success"] is False
    assert response.json()["message"] == "Incident not found"


def test_invalid_uuid_returns_422(client: TestClient) -> None:
    """Malformed UUID path parameters return HTTP 422."""
    response = client.get("/api/v1/incidents/not-a-uuid")
    assert response.status_code == 422


@pytest.mark.parametrize(
    ("method", "path_suffix"),
    [
        ("put", ""),
        ("delete", ""),
    ],
)
def test_mutations_not_found(
    client: TestClient,
    method: str,
    path_suffix: str,
) -> None:
    """Update and delete on missing incidents return HTTP 404."""
    missing_id = uuid.uuid4()
    path = f"/api/v1/incidents/{missing_id}{path_suffix}"

    if method == "put":
        response = client.put(path, json={"title": "Missing"})
    else:
        response = client.delete(path)

    assert response.status_code == 404
    assert response.json()["message"] == "Incident not found"
