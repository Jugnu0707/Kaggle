"""Integration tests for investigation timeline API."""

import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.evidence import Evidence
from app.models.incident import Incident


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


def test_get_incident_timeline(client: TestClient, db_session: Session) -> None:
  """GET /incidents/{id}/timeline returns a chronologically ordered timeline."""
  created = _create_incident(client)
  incident_id = uuid.UUID(created["id"])

  incident = db_session.get(Incident, incident_id)
  assert incident is not None

  db_session.add(
    Evidence(
      incident_id=incident_id,
      evidence_type="PowerShell Transcript",
      filename="powershell.log",
      raw_data=(
        "2026-06-24T08:15:10Z EVENT=NetworkConnect DEST=1.2.3.4:443\n"
        "2026-06-24T08:15:02Z EVENT=ProcessCreate PROCESS=powershell.exe\n"
      ),
    )
  )
  db_session.commit()

  response = client.get(f"/api/v1/incidents/{incident_id}/timeline")
  assert response.status_code == 200
  body = response.json()
  assert body["success"] is True
  data = body["data"]
  assert data["incident_id"] == created["id"]
  assert data["total_events"] == len(data["timeline"])
  assert data["total_events"] > 0
  assert "investigation_summary" in data

  timestamps = [item["timestamp"] for item in data["timeline"]]
  assert timestamps == sorted(timestamps)


def test_export_incident_timeline_json(client: TestClient) -> None:
  """Timeline JSON export returns downloadable JSON content."""
  created = _create_incident(client)
  response = client.get(
    f"/api/v1/incidents/{created['id']}/timeline/export?format=json",
  )
  assert response.status_code == 200
  assert "application/json" in response.headers["content-type"]
  assert "attachment" in response.headers["content-disposition"]
  payload = response.json()
  assert payload["incident_id"] == created["id"]
  assert "timeline" in payload


def test_export_incident_timeline_markdown(client: TestClient) -> None:
  """Timeline Markdown export returns downloadable Markdown content."""
  created = _create_incident(client)
  response = client.get(
    f"/api/v1/incidents/{created['id']}/timeline/export?format=markdown",
  )
  assert response.status_code == 200
  assert "text/markdown" in response.headers["content-type"]
  assert response.text.startswith("# Investigation Timeline")


def test_get_incident_timeline_not_found(client: TestClient) -> None:
  """Unknown incidents return 404 for timeline requests."""
  response = client.get(f"/api/v1/incidents/{uuid.uuid4()}/timeline")
  assert response.status_code == 404
