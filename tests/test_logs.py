"""Log upload API tests."""

import uuid
from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.audit_log import AuditLog
from app.models.enums import UploadStatus


@pytest.fixture
def upload_dir(tmp_path, monkeypatch):
    """Use an isolated upload directory for each test."""
    upload_path = tmp_path / "uploads"
    upload_path.mkdir()
    monkeypatch.setattr(
        "app.services.log_service.get_upload_path",
        lambda: upload_path,
    )
    return upload_path


def test_valid_upload(client: TestClient, upload_dir, db_session: Session) -> None:
    """Valid log files are stored and metadata is persisted."""
    content = b"2026-06-26 ERROR suspicious process started"
    response = client.post(
        "/api/v1/logs/upload",
        files={"file": ("events.log", BytesIO(content), "text/plain")},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Log file uploaded successfully"

    data = body["data"]
    assert data["filename"] == "events.log"
    assert data["size"] == len(content)
    assert "file_id" in data
    assert "upload_timestamp" in data

    stored_files = list(upload_dir.iterdir())
    assert len(stored_files) == 1

    audit_logs = list(db_session.scalars(select(AuditLog)).all())
    assert any(log.action == "UPLOAD" for log in audit_logs)


def test_invalid_extension(client: TestClient, upload_dir) -> None:
    """Unsupported file extensions are rejected."""
    response = client.post(
        "/api/v1/logs/upload",
        files={"file": ("malware.exe", BytesIO(b"bad"), "application/octet-stream")},
    )

    assert response.status_code == 400
    assert response.json()["success"] is False
    assert "extension" in response.json()["message"].lower()
    assert list(upload_dir.iterdir()) == []


def test_file_too_large(client: TestClient, upload_dir, monkeypatch) -> None:
    """Files exceeding the configured size limit are rejected."""
    monkeypatch.setattr(settings, "max_upload_size_bytes", 10)
    response = client.post(
        "/api/v1/logs/upload",
        files={"file": ("large.log", BytesIO(b"x" * 20), "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["success"] is False
    assert "maximum allowed size" in response.json()["message"]
    assert list(upload_dir.iterdir()) == []


def test_list_log_files(client: TestClient, upload_dir) -> None:
    """GET /logs returns paginated uploaded file metadata."""
    for index in range(2):
        client.post(
            "/api/v1/logs/upload",
            files={
                "file": (
                    f"file-{index}.txt",
                    BytesIO(f"log {index}".encode()),
                    "text/plain",
                )
            },
        )

    response = client.get("/api/v1/logs?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert data["items"][0]["original_filename"].startswith("file-")


def test_get_log_metadata(client: TestClient, upload_dir) -> None:
    """GET /logs/{id} returns metadata without file content."""
    upload_response = client.post(
        "/api/v1/logs/upload",
        files={
            "file": ("audit.json", BytesIO(b'{"event":"test"}'), "application/json")
        },
    )
    file_id = upload_response.json()["data"]["file_id"]

    response = client.get(f"/api/v1/logs/{file_id}")
    assert response.status_code == 200
    data = response.json()["data"]

    assert data["id"] == file_id
    assert data["original_filename"] == "audit.json"
    assert data["file_extension"] == ".json"
    assert data["mime_type"] == "application/json"
    assert data["upload_status"] == UploadStatus.COMPLETED.value
    assert "checksum_sha256" in data
    assert "raw_data" not in data


def test_delete_log_file(client: TestClient, upload_dir, db_session: Session) -> None:
    """DELETE /logs/{id} soft deletes the record but keeps the physical file."""
    upload_response = client.post(
        "/api/v1/logs/upload",
        files={"file": ("remove.log", BytesIO(b"delete me"), "text/plain")},
    )
    file_id = upload_response.json()["data"]["file_id"]
    stored_files_before = list(upload_dir.iterdir())
    assert len(stored_files_before) == 1

    response = client.delete(f"/api/v1/logs/{file_id}")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["upload_status"] == UploadStatus.DELETED.value
    assert data["deleted_at"] is not None

    assert list(upload_dir.iterdir()) == stored_files_before

    get_response = client.get(f"/api/v1/logs/{file_id}")
    assert get_response.status_code == 404

    list_response = client.get("/api/v1/logs")
    assert list_response.json()["data"]["total"] == 0

    delete_audits = list(
        db_session.scalars(select(AuditLog).where(AuditLog.action == "DELETE")).all()
    )
    assert len(delete_audits) == 1


def test_metadata_update_audit_on_linked_upload(
    client: TestClient,
    upload_dir,
    db_session: Session,
) -> None:
    """Uploading with an incident_id records a metadata update audit entry."""
    incident_id = uuid.uuid4()
    response = client.post(
        "/api/v1/logs/upload",
        data={"incident_id": str(incident_id)},
        files={"file": ("linked.log", BytesIO(b"linked"), "text/plain")},
    )
    assert response.status_code == 201

    audit_logs = list(db_session.scalars(select(AuditLog)).all())
    assert any(log.action == "METADATA_UPDATE" for log in audit_logs)
