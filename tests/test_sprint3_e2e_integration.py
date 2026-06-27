"""Sprint 3 end-to-end integration test — full analyst workflow."""

from __future__ import annotations

from io import BytesIO

import pytest
from fastapi.testclient import TestClient

WORKFLOW_LOG = (
    b"2026-06-24T08:15:03Z HOST=WS-FIN-042 PROCESS=powershell.exe "
    b"CMD=-EncodedCommand ABC123\n"
    b"2026-06-24T08:15:04Z HOST=WS-FIN-042 EVENT=NetworkConnect DEST=185.234.72.19:443\n"
)

INCIDENT_PAYLOAD = {
    "title": "Sprint 3 E2E Integration Incident",
    "description": "End-to-end validation incident for Sprint 3 Task 8.",
    "severity": "High",
    "source": "Integration Test",
}


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


def test_sprint3_full_analyst_workflow(client: TestClient, upload_dir) -> None:
    """Dashboard → incident → log → investigation → agents → replay."""
    dashboard = client.get("/api/v1/dashboard/stats")
    assert dashboard.status_code == 200
    dashboard_data = dashboard.json()["data"]
    assert "total_incidents" in dashboard_data

    create = client.post("/api/v1/incidents", json=INCIDENT_PAYLOAD)
    assert create.status_code == 201
    incident_id = create.json()["data"]["id"]

    incident = client.get(f"/api/v1/incidents/{incident_id}")
    assert incident.status_code == 200
    assert incident.json()["data"]["title"] == INCIDENT_PAYLOAD["title"]

    upload = client.post(
        "/api/v1/logs/upload",
        data={"incident_id": incident_id},
        files={"file": ("e2e_workflow.log", BytesIO(WORKFLOW_LOG), "text/plain")},
    )
    assert upload.status_code == 201
    log_id = upload.json()["data"]["file_id"]

    investigation = client.post(
        "/api/v1/investigations/run",
        json={"incident_id": incident_id},
    )
    assert investigation.status_code == 200
    run_data = investigation.json()["data"]
    run_id = run_data["execution_id"]
    assert run_data["duration_ms"] > 0

    expected_stages = [
        "Evidence",
        "Threat Intelligence",
        "MITRE",
        "Risk",
        "Response",
        "Executive Report",
        "Timeline",
        "Evaluation",
    ]
    completed = set(run_data["agents_completed"])
    for stage in expected_stages:
        assert stage in completed or stage in run_data["agents_failed"]

    coordinator_executions = [
        stage for stage in run_data["stages"] if "Coordinator" in stage["agent"]
    ]
    assert len(coordinator_executions) >= 1

    mitre = client.get(f"/api/v1/incidents/{incident_id}/mitre")
    assert mitre.status_code in {200, 404}

    threat = client.get(f"/api/v1/incidents/{incident_id}/threat-intelligence")
    assert threat.status_code in {200, 404}

    risk = client.get(f"/api/v1/incidents/{incident_id}/risk")
    assert risk.status_code in {200, 404}

    response_plan = client.get(f"/api/v1/incidents/{incident_id}/response")
    assert response_plan.status_code in {200, 404}

    report = client.get(f"/api/v1/incidents/{incident_id}/executive-report")
    assert report.status_code in {200, 404}

    guardian = client.get(f"/api/v1/incidents/{incident_id}/guardian-audits")
    assert guardian.status_code == 200

    timeline = client.get(f"/api/v1/incidents/{incident_id}/timeline")
    assert timeline.status_code == 200

    evaluation = client.get("/api/v1/evaluation")
    assert evaluation.status_code == 200
    assert evaluation.json()["data"]["overall_score"] is not None

    replay = client.get(f"/api/v1/investigations/{run_id}/replay")
    assert replay.status_code == 200
    replay_steps = replay.json()["data"]["steps"]
    assert len(replay_steps) >= 8
    agent_names = [step["agent"] for step in replay_steps]
    assert "Evidence Agent" in agent_names
    assert "Timeline Engine" in agent_names
    assert "Evaluation Engine" in agent_names

    explain = client.get(f"/api/v1/investigations/{run_id}/explain")
    assert explain.status_code == 200
    assert len(explain.json()["data"]["decision_chain"]) >= 8

    export_json = client.get(
        f"/api/v1/investigations/{run_id}/replay/export",
        params={"format": "json"},
    )
    assert export_json.status_code == 200
    assert "execution_order" in export_json.json()["data"]["content"]

    logs = client.get("/api/v1/logs")
    assert logs.status_code == 200
    assert any(
        str(item["id"]) == log_id and str(item["incident_id"]) == incident_id
        for item in logs.json()["data"]["items"]
    )
