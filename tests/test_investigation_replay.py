"""Tests for investigation replay and explainability."""

from io import BytesIO

import pytest
from fastapi.testclient import TestClient

CREATE_PAYLOAD = {
    "title": "Replay Test Incident",
    "description": "Investigation replay validation incident.",
    "severity": "High",
    "source": "Test",
}

POWERSHELL_LOG = (
    b"2026-06-24T08:15:03Z HOST=WS-FIN-042 PROCESS=powershell.exe "
    b"CMD=-EncodedCommand ABC123\n"
)


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
    response = client.post("/api/v1/incidents", json=CREATE_PAYLOAD)
    assert response.status_code == 201
    return response.json()["data"]["id"]


def _upload_log(client: TestClient, incident_id: str) -> None:
    response = client.post(
        "/api/v1/logs/upload",
        data={"incident_id": incident_id},
        files={
            "file": ("powershell_execution.log", BytesIO(POWERSHELL_LOG), "text/plain")
        },
    )
    assert response.status_code == 201


def _run_investigation(client: TestClient, incident_id: str) -> str:
    response = client.post(
        "/api/v1/investigations/run",
        json={"incident_id": incident_id},
    )
    assert response.status_code == 200
    return response.json()["data"]["execution_id"]


def test_replay_generation_after_investigation(client: TestClient, upload_dir) -> None:
    """Replay steps are persisted when an investigation completes."""
    incident_id = _create_incident(client)
    _upload_log(client, incident_id)
    run_id = _run_investigation(client, incident_id)

    response = client.get(f"/api/v1/investigations/{run_id}/replay")
    assert response.status_code == 200
    data = response.json()["data"]

    assert data["run_id"] == run_id
    assert data["incident_id"] == incident_id
    assert len(data["steps"]) >= 8
    assert data["steps"][0]["agent"] == "Investigation Coordinator"
    agents = [step["agent"] for step in data["steps"]]
    assert "Evidence Agent" in agents
    assert "Timeline Engine" in agents
    assert "Evaluation Engine" in agents


def test_explainability_output(client: TestClient, upload_dir) -> None:
    """Explain endpoint returns decision chain and AI usage metrics."""
    incident_id = _create_incident(client)
    _upload_log(client, incident_id)
    run_id = _run_investigation(client, incident_id)

    response = client.get(f"/api/v1/investigations/{run_id}/explain")
    assert response.status_code == 200
    data = response.json()["data"]

    assert data["run_id"] == run_id
    assert data["overall_risk"]
    assert data["overall_investigation_summary"]
    assert len(data["decision_chain"]) >= 8
    assert len(data["agent_reasoning"]) >= 8
    assert data["confidence_distribution"]["steps_with_confidence"] >= 1


def test_replay_export_json_and_markdown(client: TestClient, upload_dir) -> None:
    """Export endpoints return JSON and Markdown replay documents."""
    incident_id = _create_incident(client)
    _upload_log(client, incident_id)
    run_id = _run_investigation(client, incident_id)

    json_response = client.get(
        f"/api/v1/investigations/{run_id}/replay/export",
        params={"format": "json"},
    )
    assert json_response.status_code == 200
    json_data = json_response.json()["data"]
    assert json_data["format"] == "json"
    assert str(run_id) in json_data["content"]
    assert "execution_order" in json_data["content"]

    markdown_response = client.get(
        f"/api/v1/investigations/{run_id}/replay/export",
        params={"format": "markdown"},
    )
    assert markdown_response.status_code == 200
    markdown_data = markdown_response.json()["data"]
    assert markdown_data["format"] == "markdown"
    assert "# Investigation Replay Export" in markdown_data["content"]


def test_replay_timing_accuracy(client: TestClient, upload_dir) -> None:
    """Replay steps include non-negative duration values."""
    incident_id = _create_incident(client)
    _upload_log(client, incident_id)
    run_id = _run_investigation(client, incident_id)

    response = client.get(f"/api/v1/investigations/{run_id}/replay")
    steps = response.json()["data"]["steps"]
    for step in steps:
        assert step["duration_ms"] >= 0


def test_replay_not_found(client: TestClient) -> None:
    """Unknown run IDs return 404 for replay endpoints."""
    missing_id = "00000000-0000-0000-0000-000000000099"
    response = client.get(f"/api/v1/investigations/{missing_id}/replay")
    assert response.status_code == 404

    explain_response = client.get(f"/api/v1/investigations/{missing_id}/explain")
    assert explain_response.status_code == 404
