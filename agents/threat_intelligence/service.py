"""Threat intelligence enrichment from evidence packages."""

from __future__ import annotations

from sqlalchemy.orm import Session

from agents.evidence.models import EvidenceInput, EvidencePackage
from agents.evidence.service import EvidenceCollectionService
from agents.threat_intelligence.extractor import (
    IOC_TYPE_TO_BREAKDOWN,
    IOCExtractor,
    detect_suspicious_indicators,
)
from agents.threat_intelligence.models import (
    IOCBreakdown,
    ThreatIntelligenceInput,
    ThreatIntelligenceReport,
    ThreatIntelligenceResult,
)
from app.core.exceptions import AppException, NotFoundException
from app.core.logging import get_logger

logger = get_logger(__name__)


class ThreatIntelligenceService:
    """Enriches evidence packages with deterministic IOC extraction."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.evidence_service = EvidenceCollectionService(db)

    def enrich(self, request: ThreatIntelligenceInput) -> ThreatIntelligenceResult:
        """Collect evidence and produce a threat intelligence report."""
        logger.info(
            "Evidence received for threat intelligence: incident_id=%s evidence_id=%s",
            request.incident_id,
            request.evidence_id,
        )

        evidence_result = self.evidence_service.collect(
            EvidenceInput(
                incident_id=request.incident_id,
                log_file_id=request.evidence_id,
            )
        )
        package = evidence_result.evidence_package
        self._validate_evidence_package(package, request)

        logger.info("IOC extraction started: log_type=%s", package.detected_log_type)
        text = self._build_extraction_text(package)
        extractor = IOCExtractor(source_hint=package.detected_log_type)
        iocs = extractor.extract(text)
        logger.info("IOC extraction completed: count=%s", len(iocs))

        report = self._build_report(package, text, iocs)
        logger.info("Threat intelligence report generated: total_iocs=%s", report.total_iocs)

        return ThreatIntelligenceResult(
            status="completed",
            ioc_count=len(iocs),
            report=report,
            iocs=iocs,
            evidence_package=package,
        )

    def enrich_from_package(
        self,
        package: EvidencePackage,
    ) -> ThreatIntelligenceResult:
        """Enrich a pre-collected evidence package without reloading from disk."""
        logger.info(
            "Evidence received for threat intelligence: incident_id=%s evidence_id=%s",
            package.incident_id,
            package.uploaded_file_id,
        )
        logger.info("IOC extraction started: log_type=%s", package.detected_log_type)
        text = self._build_extraction_text(package)
        extractor = IOCExtractor(source_hint=package.detected_log_type)
        iocs = extractor.extract(text)
        logger.info("IOC extraction completed: count=%s", len(iocs))
        report = self._build_report(package, text, iocs)
        logger.info("Threat intelligence report generated: total_iocs=%s", report.total_iocs)
        return ThreatIntelligenceResult(
            status="completed",
            ioc_count=len(iocs),
            report=report,
            iocs=iocs,
            evidence_package=package,
        )

    def _validate_evidence_package(
        self,
        package: EvidencePackage,
        request: ThreatIntelligenceInput,
    ) -> None:
        if package.incident_id != request.incident_id:
            raise AppException(
                "Evidence package does not belong to the specified incident",
                status_code=400,
            )
        if package.uploaded_file_id != request.evidence_id:
            raise NotFoundException("Evidence not found")

    def _build_extraction_text(self, package: EvidencePackage) -> str:
        filename = package.file_metadata.original_filename
        header = (
            f"filename={filename} log_type={package.detected_log_type} "
            f"entries={package.number_of_lines}"
        )
        body = "\n".join(package.sample_entries)
        return f"{header}\n{body}"

    def _build_report(
        self,
        package: EvidencePackage,
        text: str,
        iocs: list,
    ) -> ThreatIntelligenceReport:
        breakdown = IOCBreakdown()
        for ioc in iocs:
            field_name = IOC_TYPE_TO_BREAKDOWN[ioc.type]
            current = getattr(breakdown, field_name)
            setattr(breakdown, field_name, current + 1)

        suspicious = detect_suspicious_indicators(text, iocs)
        interesting = self._build_interesting_findings(package, iocs)
        quality_notes: list[str] = []
        if package.parse_notes:
            quality_notes.append(package.parse_notes)
        if package.number_of_lines == 0:
            quality_notes.append("No parseable evidence entries available for IOC extraction")
        elif not package.sample_entries:
            quality_notes.append("Evidence package contains no sample entries")
        else:
            quality_notes.append("Sample entries were used for IOC extraction")

        if package.timestamp_range.start and package.timestamp_range.end:
            quality_notes.append("Timestamps detected in source evidence")

        return ThreatIntelligenceReport(
            total_iocs=len(iocs),
            ioc_breakdown=breakdown,
            suspicious_indicators=suspicious,
            interesting_findings=interesting,
            data_quality_notes=quality_notes,
        )

    def _build_interesting_findings(
        self,
        package: EvidencePackage,
        iocs: list,
    ) -> list[str]:
        findings: list[str] = []
        if iocs:
            findings.append(f"{len(iocs)} unique IOCs extracted from evidence sample")
        else:
            findings.append("No IOCs extracted from the available evidence sample")

        if package.timestamp_range.start and package.timestamp_range.end:
            findings.append(
                "Evidence spans "
                f"{package.timestamp_range.start} to {package.timestamp_range.end}"
            )

        external_ips = {
            ioc.value for ioc in iocs if ioc.type == "IPv4" and ioc.confidence >= 85
        }
        if len(external_ips) > 1:
            findings.append(f"{len(external_ips)} distinct external IPv4 addresses identified")

        return findings
