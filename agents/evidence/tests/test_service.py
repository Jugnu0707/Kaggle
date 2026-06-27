"""Evidence collection service unit tests."""

import uuid
from pathlib import Path

import pytest
from agents.evidence.models import EvidenceInput
from agents.evidence.service import EVTX_MESSAGE, EvidenceCollectionService
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.models.enums import IncidentStatus, Severity, UploadStatus
from app.models.incident import Incident
from app.models.log_file import LogFile


def _create_incident(db_session: Session) -> uuid.UUID:
    incident = Incident(
        title="Evidence test incident",
        description="Unit test incident",
        severity=Severity.HIGH,
        status=IncidentStatus.NEW,
        source="Unit Test",
        confidence_score=0.5,
    )
    db_session.add(incident)
    db_session.commit()
    db_session.refresh(incident)
    return incident.id


def _create_log_file(
    db_session: Session,
    *,
    incident_id: uuid.UUID,
    extension: str,
    stored_filename: str,
    upload_dir: Path,
    content: bytes = b"",
) -> uuid.UUID:
    file_path = upload_dir / stored_filename
    file_path.write_bytes(content)
    log_file = LogFile(
        incident_id=incident_id,
        original_filename=f"sample{extension}",
        stored_filename=stored_filename,
        file_extension=extension,
        mime_type="text/plain",
        file_size_bytes=len(content),
        upload_status=UploadStatus.COMPLETED,
        storage_path=f"storage/uploads/{stored_filename}",
        checksum_sha256="0" * 64,
    )
    db_session.add(log_file)
    db_session.commit()
    db_session.refresh(log_file)
    return log_file.id


@pytest.fixture
def upload_dir(tmp_path, monkeypatch):
    """Use an isolated upload directory for Evidence service tests."""
    upload_path = tmp_path / "uploads"
    upload_path.mkdir()
    monkeypatch.setattr(
        "agents.evidence.service.get_upload_path",
        lambda: upload_path,
    )
    return upload_path


def test_collects_log_file(upload_dir, db_session: Session) -> None:
    """Valid .log files produce a completed evidence package."""
    incident_id = _create_incident(db_session)
    log_id = _create_log_file(
        db_session,
        incident_id=incident_id,
        extension=".log",
        stored_filename="events.log",
        upload_dir=upload_dir,
        content=(
            b"2026-06-26T10:00:00 ERROR suspicious process started\n"
            b"2026-06-26T11:00:00 INFO process ended\n"
        ),
    )

    result = EvidenceCollectionService(db_session).collect(
        EvidenceInput(incident_id=incident_id, log_file_id=log_id)
    )

    assert result.status == "completed"
    assert result.evidence_package.detected_log_type == "application_log"
    assert result.evidence_package.number_of_lines == 2
    assert len(result.evidence_package.sample_entries) == 2


def test_collects_json_file(upload_dir, db_session: Session) -> None:
    """JSON logs are parsed into normalized entries."""
    incident_id = _create_incident(db_session)
    log_id = _create_log_file(
        db_session,
        incident_id=incident_id,
        extension=".json",
        stored_filename="events.json",
        upload_dir=upload_dir,
        content=b'[{"event":"login"},{"event":"logout"}]',
    )

    result = EvidenceCollectionService(db_session).collect(
        EvidenceInput(incident_id=incident_id, log_file_id=log_id)
    )

    assert result.evidence_package.detected_log_type == "json"
    assert result.evidence_package.number_of_lines == 2


def test_collects_csv_file(upload_dir, db_session: Session) -> None:
    """CSV logs are parsed into row entries."""
    incident_id = _create_incident(db_session)
    log_id = _create_log_file(
        db_session,
        incident_id=incident_id,
        extension=".csv",
        stored_filename="events.csv",
        upload_dir=upload_dir,
        content=b"timestamp,message\n2026-06-26T10:00:00,started\n",
    )

    result = EvidenceCollectionService(db_session).collect(
        EvidenceInput(incident_id=incident_id, log_file_id=log_id)
    )

    assert result.evidence_package.detected_log_type == "csv"
    assert result.evidence_package.number_of_lines == 2


def test_collects_txt_file(upload_dir, db_session: Session) -> None:
    """TXT logs are parsed as line-based text."""
    incident_id = _create_incident(db_session)
    log_id = _create_log_file(
        db_session,
        incident_id=incident_id,
        extension=".txt",
        stored_filename="events.txt",
        upload_dir=upload_dir,
        content=b"plain text entry one\nplain text entry two\n",
    )

    result = EvidenceCollectionService(db_session).collect(
        EvidenceInput(incident_id=incident_id, log_file_id=log_id)
    )

    assert result.evidence_package.detected_log_type == "text"
    assert result.evidence_package.number_of_lines == 2


def test_evtx_file_returns_parse_note(upload_dir, db_session: Session) -> None:
    """EVTX files complete without parsing failure."""
    incident_id = _create_incident(db_session)
    log_id = _create_log_file(
        db_session,
        incident_id=incident_id,
        extension=".evtx",
        stored_filename="events.evtx",
        upload_dir=upload_dir,
        content=b"binary-evtx-content",
    )

    result = EvidenceCollectionService(db_session).collect(
        EvidenceInput(incident_id=incident_id, log_file_id=log_id)
    )

    assert result.status == "completed"
    assert result.evidence_package.parse_notes == EVTX_MESSAGE
    assert result.evidence_package.number_of_lines == 0


def test_missing_file_on_disk_raises_not_found(upload_dir, db_session: Session) -> None:
    """Missing on-disk files return a not-found error."""
    incident_id = _create_incident(db_session)
    log_file = LogFile(
        incident_id=incident_id,
        original_filename="missing.log",
        stored_filename="missing.log",
        file_extension=".log",
        mime_type="text/plain",
        file_size_bytes=10,
        upload_status=UploadStatus.COMPLETED,
        storage_path="storage/uploads/missing.log",
        checksum_sha256="0" * 64,
    )
    db_session.add(log_file)
    db_session.commit()
    db_session.refresh(log_file)

    with pytest.raises(NotFoundException, match="Log file not found on disk"):
        EvidenceCollectionService(db_session).collect(
            EvidenceInput(incident_id=incident_id, log_file_id=log_file.id)
        )


def test_empty_file_produces_zero_entries(upload_dir, db_session: Session) -> None:
    """Empty readable files complete with zero entries."""
    incident_id = _create_incident(db_session)
    log_id = _create_log_file(
        db_session,
        incident_id=incident_id,
        extension=".txt",
        stored_filename="empty.txt",
        upload_dir=upload_dir,
        content=b"",
    )

    result = EvidenceCollectionService(db_session).collect(
        EvidenceInput(incident_id=incident_id, log_file_id=log_id)
    )

    assert result.status == "completed"
    assert result.evidence_package.number_of_lines == 0
    assert (
        "no parseable entries"
        in result.evidence_summary.data_quality_observations[0].lower()
    )
