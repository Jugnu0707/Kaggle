"""Threat Intelligence service tests."""

import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy.orm import Session

from agents.evidence.models import EvidencePackage, FileMetadata, TimestampRange
from agents.threat_intelligence.models import ThreatIntelligenceInput
from agents.threat_intelligence.service import ThreatIntelligenceService
from app.core.exceptions import NotFoundException


def _build_package(
    *,
    incident_id: uuid.UUID | None = None,
    uploaded_file_id: uuid.UUID | None = None,
    sample_entries: list[str] | None = None,
    number_of_lines: int = 1,
) -> EvidencePackage:
    incident = incident_id or uuid.uuid4()
    uploaded = uploaded_file_id or uuid.uuid4()
    return EvidencePackage(
        incident_id=incident,
        uploaded_file_id=uploaded,
        file_metadata=FileMetadata(
            original_filename="powershell_execution.log",
            stored_filename=f"{uploaded}.log",
            file_extension=".log",
            mime_type="text/plain",
            upload_status="Completed",
            uploaded_at=datetime.now(UTC),
            checksum_sha256="abc123",
        ),
        file_size=128,
        number_of_lines=number_of_lines,
        detected_log_type="application_log",
        timestamp_range=TimestampRange(
            start="2026-06-24T08:15:01Z",
            end="2026-06-24T08:15:42Z",
        ),
        sample_entries=sample_entries or [],
        collection_timestamp=datetime.now(UTC),
        parse_notes=None,
    )


def test_enrich_from_package_extracts_iocs(db_session: Session) -> None:
    package = _build_package(
        sample_entries=[
            "HOST=WS-FIN-042 USER=DOMAIN\\jsmith EVENT=NetworkConnect DEST=185.234.72.19:443",
            "HASH e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        ]
    )
    result = ThreatIntelligenceService(db_session).enrich_from_package(package)
    assert result.status == "completed"
    assert result.ioc_count >= 2
    assert result.report.total_iocs == result.ioc_count
    assert any(ioc.type == "IPv4" for ioc in result.iocs)


def test_enrich_from_empty_package(db_session: Session) -> None:
    package = _build_package(sample_entries=[], number_of_lines=0)
    result = ThreatIntelligenceService(db_session).enrich_from_package(package)
    assert result.status == "completed"
    assert result.ioc_count == 0
    assert "No IOCs extracted" in result.report.interesting_findings[0]


def test_enrich_invalid_evidence_returns_not_found(db_session: Session) -> None:
    incident_id = uuid.uuid4()
    with pytest.raises(NotFoundException):
        ThreatIntelligenceService(db_session).enrich(
            ThreatIntelligenceInput(
                incident_id=incident_id,
                evidence_id=uuid.uuid4(),
            )
        )
