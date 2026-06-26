"""Threat Intelligence service tests."""

import uuid
from datetime import UTC, datetime
from unittest.mock import patch

import pytest
from google.genai import errors as genai_errors
from sqlalchemy.orm import Session

from agents.evidence.models import EvidencePackage, FileMetadata, TimestampRange
from agents.threat_intelligence.models import ThreatIntelligenceInput
from agents.threat_intelligence.schemas import (
    AIEnrichedFinding,
    AIThreatIntelligenceResponse,
    ThreatIntelligenceSource,
)
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
    assert len(result.findings) == result.ioc_count
    assert result.report.total_iocs == result.ioc_count
    assert any(finding.indicator_type == "IPv4" for finding in result.findings)
    assert all(finding.source == ThreatIntelligenceSource.FALLBACK for finding in result.findings)


def test_enrich_from_empty_package(db_session: Session) -> None:
    package = _build_package(sample_entries=[], number_of_lines=0)
    result = ThreatIntelligenceService(db_session).enrich_from_package(package)
    assert result.status == "completed"
    assert result.ioc_count == 0
    assert result.findings == []
    assert "No IOCs extracted" in result.report.interesting_findings[0]


def test_enrich_invalid_incident_returns_not_found(db_session: Session) -> None:
    with pytest.raises(NotFoundException):
        ThreatIntelligenceService(db_session).enrich(
            ThreatIntelligenceInput(incident_id=uuid.uuid4())
        )


def test_ai_success_returns_ai_source(db_session: Session) -> None:
    package = _build_package(
        sample_entries=[
            "HOST=WS-FIN-042 EVENT=NetworkConnect DEST=185.234.72.19:443",
        ]
    )
    service = ThreatIntelligenceService(db_session)
    ai_response = AIThreatIntelligenceResponse(
        findings=[
            AIEnrichedFinding(
                indicator="185.234.72.19",
                indicator_type="IPv4",
                description="External IPv4 observed during network connection event.",
                analyst_notes="Correlate with firewall and proxy logs.",
                confidence=88,
            ),
            AIEnrichedFinding(
                indicator="WS-FIN-042",
                indicator_type="Hostname",
                description="Source host involved in the network connection.",
                analyst_notes="Validate host activity and ownership.",
                confidence=75,
            ),
        ]
    )
    with patch.object(service, "_call_gemini", return_value=ai_response):
        result = service.enrich_from_package(package)

    assert result.findings[0].source == ThreatIntelligenceSource.AI
    assert result.findings[0].description.startswith("External IPv4")


def test_quota_exceeded_uses_fallback(db_session: Session) -> None:
    package = _build_package(
        sample_entries=["DEST=185.234.72.19 EVENT=NetworkConnect"],
    )
    service = ThreatIntelligenceService(db_session)
    with patch.object(
        service,
        "_call_gemini",
        side_effect=genai_errors.ClientError(
            429,
            {"error": {"message": "Quota exceeded"}},
            None,
        ),
    ):
        result = service.enrich_from_package(package)

    assert all(finding.source == ThreatIntelligenceSource.FALLBACK for finding in result.findings)
