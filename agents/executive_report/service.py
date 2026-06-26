"""Executive Report Agent — AI-first reporting with automatic fallback."""

from __future__ import annotations

import json
import uuid
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from pathlib import Path

from google import genai
from google.genai import errors as genai_errors
from google.genai import types as genai_types
from sqlalchemy import select
from sqlalchemy.orm import Session

from agents.evidence.models import EvidenceInput
from agents.evidence.service import EvidenceCollectionService
from agents.executive_report.fallback import generate_executive_report_fallback
from agents.executive_report.markdown_generator import generate_markdown_report
from agents.executive_report.models import ExecutiveReportInput, ExecutiveReportResult
from agents.executive_report.schemas import (
    AIExecutiveReportResponse,
    ExecutiveReportContext,
    ExecutiveReportSource,
    IncidentContext,
    ReportSections,
    ResponsePlanContext,
    RiskAssessmentContext,
)
from agents.mitre.models import MappedTechnique
from agents.response.models import ResponsePlanInput
from agents.response.service import ResponsePlanningService
from agents.risk.models import RiskAssessmentInput
from agents.risk.service import RiskAssessmentService
from agents.threat_intelligence.service import ThreatIntelligenceService
from app.core.ai_config import ai_settings
from app.core.exceptions import NotFoundException
from app.core.logging import get_logger
from app.models.log_file import LogFile
from app.repositories.incident_repository import IncidentRepository
from app.repositories.mitre_finding_repository import MitreFindingRepository
from app.repositories.response_plan_repository import ResponsePlanRepository
from app.repositories.risk_assessment_repository import RiskAssessmentRepository

logger = get_logger(__name__)

PROMPT_PATH = Path(__file__).with_name("prompt.md")
AI_REQUEST_TIMEOUT_SECONDS = 30


class ExecutiveReportService:
    """Generates executive incident reports using Gemini with automatic fallback."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.incident_repository = IncidentRepository(db)
        self.mitre_repository = MitreFindingRepository(db)
        self.risk_repository = RiskAssessmentRepository(db)
        self.response_repository = ResponsePlanRepository(db)
        self.evidence_service = EvidenceCollectionService(db)
        self.threat_intelligence_service = ThreatIntelligenceService(db)
        self.risk_service = RiskAssessmentService(db)
        self.response_service = ResponsePlanningService(db)

    def generate(self, request: ExecutiveReportInput) -> ExecutiveReportResult:
        """Generate an executive report using AI first, then fallback templates."""
        context = self._gather_context(request.incident_id)
        logger.info("Executive report generation started: incident_id=%s", request.incident_id)

        ai_result = self._try_ai_report(context)
        if ai_result is not None:
            logger.info(
                "Executive report completed: source=AI incident_id=%s",
                request.incident_id,
            )
            return ai_result

        logger.warning("Fallback activated: incident_id=%s", request.incident_id)
        result = generate_executive_report_fallback(context)
        logger.info(
            "Executive report completed: source=FALLBACK incident_id=%s",
            request.incident_id,
        )
        return result

    def _gather_context(self, incident_id: uuid.UUID) -> ExecutiveReportContext:
        incident = self.incident_repository.get_by_id(incident_id)
        if incident is None:
            raise NotFoundException("Incident not found")

        evidence_summaries = []
        threat_reports = []
        suspicious_indicator_count = 0
        total_iocs = 0

        log_files = list(
            self.db.scalars(
                select(LogFile).where(
                    LogFile.incident_id == incident_id,
                    LogFile.deleted_at.is_(None),
                )
            ).all()
        )
        for log_file in log_files:
            evidence_result = self.evidence_service.collect(
                EvidenceInput(incident_id=incident_id, log_file_id=log_file.id)
            )
            evidence_summaries.append(evidence_result.evidence_summary)
            ti_result = self.threat_intelligence_service.enrich_from_package(
                evidence_result.evidence_package
            )
            threat_reports.append(ti_result.report)
            total_iocs += ti_result.ioc_count
            suspicious_indicator_count += len(ti_result.report.suspicious_indicators)

        mitre_techniques = [
            MappedTechnique(
                technique_id=finding.technique_id,
                technique_name=finding.technique_name,
                tactic=finding.tactic,
                confidence=finding.confidence,
                matched_evidence=finding.evidence,
            )
            for finding in self.mitre_repository.list_by_incident_id(incident_id)
        ]

        risk_record = self.risk_repository.get_latest_by_incident_id(incident_id)
        risk_context: RiskAssessmentContext | None = None
        if risk_record is not None:
            risk_context = RiskAssessmentContext(
                overall_risk=risk_record.overall_risk,
                risk_score=risk_record.risk_score,
                priority=risk_record.priority,
                likelihood=risk_record.likelihood,
                business_impact=risk_record.business_impact,
                summary=risk_record.summary,
                reasoning=risk_record.reasoning,
            )
        else:
            risk_result = self.risk_service.assess(RiskAssessmentInput(incident_id=incident_id))
            risk_context = RiskAssessmentContext(
                overall_risk=risk_result.overall_risk,
                risk_score=risk_result.risk_score,
                priority=risk_result.priority,
                likelihood=risk_result.likelihood,
                business_impact=risk_result.business_impact,
                summary=risk_result.summary,
                reasoning=risk_result.reasoning,
            )

        response_record = self.response_repository.get_latest_by_incident_id(incident_id)
        response_context: ResponsePlanContext | None = None
        if response_record is not None:
            response_context = ResponsePlanContext(
                priority=response_record.priority,
                containment=response_record.containment,
                eradication=response_record.eradication,
                recovery=response_record.recovery,
                monitoring=response_record.monitoring,
                executive_summary=response_record.executive_summary,
            )
        else:
            response_result = self.response_service.plan(
                ResponsePlanInput(incident_id=incident_id)
            )
            response_context = ResponsePlanContext(
                priority=response_result.priority,
                containment=response_result.containment,
                eradication=response_result.eradication,
                recovery=response_result.recovery,
                monitoring=response_result.monitoring,
                executive_summary=response_result.executive_summary,
            )

        return ExecutiveReportContext(
            incident=IncidentContext(
                id=incident.id,
                title=incident.title,
                description=incident.description,
                severity=incident.severity.value,
                status=incident.status.value,
                source=incident.source,
                confidence_score=incident.confidence_score,
                created_at=incident.created_at.isoformat() if incident.created_at else None,
            ),
            evidence_summaries=evidence_summaries,
            mitre_techniques=mitre_techniques,
            threat_intelligence_reports=threat_reports,
            risk_assessment=risk_context,
            response_plan=response_context,
            total_iocs=total_iocs,
            suspicious_indicator_count=suspicious_indicator_count,
        )

    def _try_ai_report(self, context: ExecutiveReportContext) -> ExecutiveReportResult | None:
        api_key = ai_settings.google_api_key.strip()
        model = ai_settings.google_model.strip() or "gemini-2.0-flash"
        if not api_key:
            logger.warning("AI failure reason: GOOGLE_API_KEY is not configured")
            return None

        logger.info("AI request started: model=%s incident_id=%s", model, context.incident.id)
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self._call_gemini, api_key, model, context)
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

        sections = ReportSections.model_validate(response.model_dump())
        markdown = generate_markdown_report(sections)
        logger.info("AI response received: incident_id=%s", context.incident.id)
        return ExecutiveReportResult(
            source=ExecutiveReportSource.AI,
            title=sections.title,
            executive_summary=sections.executive_summary,
            business_impact=sections.business_impact,
            key_findings=sections.key_findings,
            recommended_actions=sections.recommended_actions,
            lessons_learned=sections.lessons_learned,
            markdown=markdown,
        )

    def _call_gemini(
        self,
        api_key: str,
        model: str,
        context: ExecutiveReportContext,
    ) -> AIExecutiveReportResponse | None:
        prompt = self._build_prompt(context)
        client = genai.Client(api_key=api_key)
        generation = client.models.generate_content(
            model=model,
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        raw_text = (generation.text or "").strip()
        if not raw_text:
            logger.warning("AI failure reason: empty response from Gemini")
            return None

        try:
            payload = json.loads(raw_text)
            return AIExecutiveReportResponse.model_validate(payload)
        except (json.JSONDecodeError, ValueError) as exc:
            logger.warning("AI failure reason: invalid JSON response (%s)", exc)
            return None

    def _build_prompt(self, context: ExecutiveReportContext) -> str:
        system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
        context_json = context.model_dump(mode="json")
        return (
            f"{system_prompt}\n\n"
            "Generate an executive incident report for the following context and return ONLY valid JSON:\n"
            f"{json.dumps(context_json, indent=2)}"
        )
