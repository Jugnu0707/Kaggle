"""Threat intelligence enrichment from evidence packages."""

from __future__ import annotations

import json
import uuid
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError
from pathlib import Path

from google.genai import errors as genai_errors
from sqlalchemy import select
from sqlalchemy.orm import Session

from agents.evidence.models import EvidenceInput, EvidencePackage
from agents.evidence.service import EvidenceCollectionService
from agents.threat_intelligence.fallback import enrich_ioc_fallback
from agents.threat_intelligence.ioc_extractor import (
    IOC_TYPE_TO_BREAKDOWN,
    IOCExtractor,
    detect_suspicious_indicators,
)
from agents.threat_intelligence.models import (
    IOC,
    IOCBreakdown,
    ThreatIntelligenceFinding,
    ThreatIntelligenceInput,
    ThreatIntelligenceReport,
    ThreatIntelligenceResult,
)
from agents.threat_intelligence.reputation_engine import assess_reputation
from agents.threat_intelligence.schemas import (
    AIThreatIntelligenceResponse,
    ThreatIntelligenceSource,
)
from app.ai.runtime import get_ai_runtime
from app.core.exceptions import NotFoundException
from app.core.logging import get_logger
from app.models.log_file import LogFile

logger = get_logger(__name__)

PROMPT_PATH = Path(__file__).with_name("prompt.md")
AI_REQUEST_TIMEOUT_SECONDS = 30


class ThreatIntelligenceService:
    """Enriches incident evidence with IOC extraction and AI-first enrichment."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.evidence_service = EvidenceCollectionService(db)

    def enrich(self, request: ThreatIntelligenceInput) -> ThreatIntelligenceResult:
        """Collect incident evidence and produce enriched threat intelligence findings."""
        runtime = get_ai_runtime()
        incident_result = runtime.invoke_tool(
            "incident_details",
            {"incident_id": str(request.incident_id)},
            self.db,
        )
        if not incident_result.success:
            raise NotFoundException("Incident not found")

        packages = self._collect_incident_evidence(request.incident_id)
        return self._enrich_packages(
            incident_id=request.incident_id,
            packages=packages,
            primary_package=packages[0] if packages else None,
        )

    def enrich_from_package(self, package: EvidencePackage) -> ThreatIntelligenceResult:
        """Enrich a pre-collected evidence package without reloading from disk."""
        return self._enrich_packages(
            incident_id=package.incident_id,
            packages=[package],
            primary_package=package,
        )

    def _collect_incident_evidence(
        self, incident_id: uuid.UUID
    ) -> list[EvidencePackage]:
        log_files = list(
            self.db.scalars(
                select(LogFile).where(
                    LogFile.incident_id == incident_id,
                    LogFile.deleted_at.is_(None),
                )
            ).all()
        )
        packages: list[EvidencePackage] = []
        for log_file in log_files:
            evidence_result = self.evidence_service.collect(
                EvidenceInput(incident_id=incident_id, log_file_id=log_file.id)
            )
            packages.append(evidence_result.evidence_package)
        return packages

    def _enrich_packages(
        self,
        *,
        incident_id: uuid.UUID,
        packages: list[EvidencePackage],
        primary_package: EvidencePackage | None,
    ) -> ThreatIntelligenceResult:
        logger.info(
            "Evidence received for threat intelligence: incident_id=%s", incident_id
        )

        combined_text = self._build_combined_text(packages)
        iocs = self._extract_iocs(packages)
        logger.info("IOC extraction completed: count=%s", len(iocs))

        ai_findings = self._try_ai_enrichment(iocs, combined_text, incident_id)
        if ai_findings is not None:
            findings = ai_findings
            logger.info("Findings generated: source=AI count=%s", len(findings))
        else:
            logger.warning("Fallback activated: incident_id=%s", incident_id)
            findings = [
                enrich_ioc_fallback(ioc, context_text=combined_text) for ioc in iocs
            ]
            logger.info("Findings generated: source=FALLBACK count=%s", len(findings))

        report = self._build_report(packages, combined_text, iocs, findings)
        logger.info(
            "Threat intelligence report generated: total_iocs=%s", report.total_iocs
        )

        return ThreatIntelligenceResult(
            status="completed",
            ioc_count=len(findings),
            findings=findings,
            report=report,
            iocs=iocs,
            evidence_package=primary_package,
        )

    def _extract_iocs(self, packages: list[EvidencePackage]) -> list[IOC]:
        seen: set[tuple[str, str]] = set()
        iocs: list[IOC] = []
        for package in packages:
            text = self._build_extraction_text(package)
            extractor = IOCExtractor(source_hint=package.detected_log_type)
            for ioc in extractor.extract(text):
                key = (ioc.type, ioc.value.lower())
                if key in seen:
                    continue
                seen.add(key)
                iocs.append(ioc)
        return sorted(iocs, key=lambda item: (item.type, item.value.lower()))

    def _try_ai_enrichment(
        self,
        iocs: list[IOC],
        context_text: str,
        incident_id: uuid.UUID,
    ) -> list[ThreatIntelligenceFinding] | None:
        if not iocs:
            return []

        api_key = get_ai_runtime().provider.get_api_key()
        model = get_ai_runtime().provider.get_model()
        if not api_key:
            logger.warning("AI failure reason: GOOGLE_API_KEY is not configured")
            return None

        logger.info("AI request started: model=%s incident_id=%s", model, incident_id)
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    self._call_gemini,
                    api_key,
                    model,
                    iocs,
                    context_text,
                )
                response = future.result(timeout=AI_REQUEST_TIMEOUT_SECONDS)
        except FuturesTimeoutError:
            logger.warning(
                "AI failure reason: request timed out after %ss",
                AI_REQUEST_TIMEOUT_SECONDS,
            )
            return None
        except genai_errors.ClientError as exc:
            logger.warning("AI failure reason: %s", exc)
            return None
        except genai_errors.ServerError as exc:
            logger.warning("AI failure reason: %s", exc)
            return None
        except Exception as exc:
            logger.warning("AI failure reason: %s", exc)
            return None

        if response is None:
            return None

        logger.info("AI response received: findings=%s", len(response.findings))
        ioc_by_key = {(ioc.type, ioc.value.lower()): ioc for ioc in iocs}
        findings: list[ThreatIntelligenceFinding] = []
        for item in response.findings:
            key = (item.indicator_type, item.indicator.lower())
            ioc = ioc_by_key.get(key)
            if ioc is None:
                continue
            reputation = assess_reputation(ioc, context_text=context_text)
            findings.append(
                ThreatIntelligenceFinding(
                    indicator=item.indicator,
                    indicator_type=item.indicator_type,
                    reputation=reputation.reputation.value,
                    confidence=item.confidence,
                    source=ThreatIntelligenceSource.AI,
                    description=item.description,
                    analyst_notes=item.analyst_notes,
                )
            )

        if len(findings) != len(iocs):
            logger.warning("AI failure reason: incomplete finding coverage")
            return None

        return findings

    def _call_gemini(
        self,
        api_key: str,
        model: str,
        iocs: list[IOC],
        context_text: str,
    ) -> AIThreatIntelligenceResponse | None:
        _ = api_key
        prompt = self._build_prompt(iocs, context_text)
        raw_text = get_ai_runtime().provider.generate_json(prompt, model=model)
        if not raw_text:
            logger.warning("AI failure reason: empty response from Gemini")
            return None

        try:
            payload = json.loads(raw_text)
            return AIThreatIntelligenceResponse.model_validate(payload)
        except (json.JSONDecodeError, ValueError) as exc:
            logger.warning("AI failure reason: invalid JSON response (%s)", exc)
            return None

    def _build_prompt(self, iocs: list[IOC], context_text: str) -> str:
        system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
        payload = {
            "iocs": [ioc.model_dump() for ioc in iocs],
            "evidence_context": context_text[:4000],
        }
        return (
            f"{system_prompt}\n\n"
            "Enrich the following extracted IOCs and return ONLY valid JSON:\n"
            f"{json.dumps(payload, indent=2)}"
        )

    def _build_combined_text(self, packages: list[EvidencePackage]) -> str:
        return "\n\n".join(self._build_extraction_text(package) for package in packages)

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
        packages: list[EvidencePackage],
        text: str,
        iocs: list[IOC],
        findings: list[ThreatIntelligenceFinding],
    ) -> ThreatIntelligenceReport:
        breakdown = IOCBreakdown()
        for ioc in iocs:
            field_name = IOC_TYPE_TO_BREAKDOWN[ioc.type]
            current = getattr(breakdown, field_name)
            setattr(breakdown, field_name, current + 1)

        suspicious = detect_suspicious_indicators(text, iocs)
        interesting = self._build_interesting_findings(packages, iocs, findings)
        quality_notes: list[str] = []
        if not packages:
            quality_notes.append("No evidence packages available for IOC extraction")
        else:
            quality_notes.append("Sample entries were used for IOC extraction")
            if any(package.timestamp_range.start for package in packages):
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
        packages: list[EvidencePackage],
        iocs: list[IOC],
        findings: list[ThreatIntelligenceFinding],
    ) -> list[str]:
        results: list[str] = []
        if findings:
            results.append(f"{len(findings)} IOCs enriched with threat intelligence")
            malicious = sum(
                1 for finding in findings if finding.reputation == "Malicious"
            )
            suspicious = sum(
                1 for finding in findings if finding.reputation == "Suspicious"
            )
            if malicious:
                results.append(f"{malicious} indicator(s) classified as Malicious")
            if suspicious:
                results.append(f"{suspicious} indicator(s) classified as Suspicious")
        else:
            results.append("No IOCs extracted from the available evidence sample")

        if (
            packages
            and packages[0].timestamp_range.start
            and packages[0].timestamp_range.end
        ):
            results.append(
                "Evidence spans "
                f"{packages[0].timestamp_range.start} to {packages[0].timestamp_range.end}"
            )

        external_ips = {
            ioc.value for ioc in iocs if ioc.type == "IPv4" and ioc.confidence >= 85
        }
        if len(external_ips) > 1:
            results.append(
                f"{len(external_ips)} distinct external IPv4 addresses identified"
            )

        return results
