"""API inventory validation for Sprint 3 acceptance."""

from __future__ import annotations

import uuid
from io import BytesIO

import pytest
from fastapi.testclient import TestClient

from app.main import app

# Canonical inventory of implemented REST endpoints (Sprint 3).
API_INVENTORY: list[tuple[str, str, int | set[int]]] = [
    ("GET", "/", 200),
    ("GET", "/api/v1/health", 200),
    ("GET", "/api/v1/ai/health", {200, 503}),
    ("GET", "/api/v1/ai/test", 200),
    ("GET", "/api/v1/dashboard/stats", 200),
    ("GET", "/api/v1/evaluation", 200),
    ("GET", "/api/v1/evaluation/{agent_name}", {200, 404}),
    ("GET", "/api/v1/system/tables", 200),
    ("GET", "/api/v1/system/mcp", 200),
    ("GET", "/api/v1/incidents", 200),
    ("GET", "/api/v1/logs", 200),
    ("POST", "/api/v1/investigations/run", {200, 404, 422}),
    ("GET", "/api/v1/investigations/{run_id}/replay", 404),
    ("GET", "/api/v1/investigations/{run_id}/explain", 404),
]


def test_openapi_documents_all_inventory_routes() -> None:
    """Every inventoried route exists in the OpenAPI schema."""
    paths = app.openapi()["paths"]
    for method, path, _ in API_INVENTORY:
        if "{" in path:
            continue
        normalized = path if path.startswith("/api") or path == "/" else path
        assert normalized in paths, f"Missing OpenAPI path: {normalized}"
        assert method.lower() in paths[normalized], f"Missing {method} for {normalized}"


def test_api_inventory_status_codes(client: TestClient) -> None:
    """Inventory endpoints return expected status codes."""
    incident_id = None
    create = client.post(
        "/api/v1/incidents",
        json={
            "title": "API Inventory Incident",
            "description": "API validation",
            "severity": "Low",
            "source": "Test",
        },
    )
    if create.status_code == 201:
        incident_id = create.json()["data"]["id"]

    for method, path, expected in API_INVENTORY:
        if "{agent_name}" in path:
            path = path.replace("{agent_name}", "Evidence%20Agent")
        if "{run_id}" in path:
            path = path.replace("{run_id}", str(uuid.uuid4()))
        if "{incident}" in path and incident_id:
            path = path.replace("{incident}", incident_id)
        response = client.request(method, path)
        allowed = expected if isinstance(expected, set) else {expected}
        assert (
            response.status_code in allowed
        ), f"{method} {path} returned {response.status_code}, expected {allowed}"

    eval_detail = client.get("/api/v1/evaluation/Evidence%20Agent")
    assert eval_detail.status_code in {200, 404}


def test_incident_validation_errors(client: TestClient) -> None:
    """Invalid incident payloads return 422."""
    response = client.post("/api/v1/incidents", json={"title": "missing fields"})
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False


def test_missing_incident_returns_404(client: TestClient) -> None:
    """Unknown incident IDs return 404 across read endpoints."""
    missing = str(uuid.uuid4())
    endpoints = [
        f"/api/v1/incidents/{missing}",
        f"/api/v1/incidents/{missing}/mitre",
        f"/api/v1/incidents/{missing}/threat-intelligence",
        f"/api/v1/incidents/{missing}/risk",
        f"/api/v1/incidents/{missing}/response",
        f"/api/v1/incidents/{missing}/executive-report",
        f"/api/v1/incidents/{missing}/timeline",
        f"/api/v1/incidents/{missing}/guardian-audits",
    ]
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 404


def test_log_upload_validation(client: TestClient, tmp_path, monkeypatch) -> None:
    """Invalid log uploads are rejected with proper error responses."""
    upload_path = tmp_path / "uploads"
    upload_path.mkdir()
    monkeypatch.setattr(
        "app.services.log_service.get_upload_path",
        lambda: upload_path,
    )

    empty = client.post(
        "/api/v1/logs/upload",
        files={"file": ("empty.log", BytesIO(b""), "text/plain")},
    )
    assert empty.status_code in {400, 422}

    invalid = client.post(
        "/api/v1/logs/upload",
        files={"file": ("bad.exe", BytesIO(b"data"), "application/octet-stream")},
    )
    assert invalid.status_code == 400
    assert invalid.json()["success"] is False


def test_api_response_envelope(client: TestClient) -> None:
    """Successful API responses use the standard envelope."""
    response = client.get("/api/v1/health")
    body = response.json()
    assert "success" in body
    assert "message" in body
    assert "data" in body
