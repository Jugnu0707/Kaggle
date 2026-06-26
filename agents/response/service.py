"""Response Planning Agent — AI-first planning with automatic fallback."""

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
from agents.mitre.models import MappedTechnique
from agents.response.fallback import plan_response_fallback
from agents.response.models import ResponsePlanInput, ResponsePlanResult
from agents.response.schemas import (
    AIResponsePlanResponse,
    IncidentContext,
    ResponsePlanningContext,
    ResponsePlanSource,
    RiskAssessmentContext,
)
from agents.risk.models import RiskAssessmentInput
from agents.risk.service import RiskAssessmentService
from agents.threat_intelligence.service import ThreatIntelligenceService
from app.core.ai_config import ai_settings
from app.core.exceptions import NotFoundException
from app.core.logging import get_logger
from app.models.log_file import LogFile
from app.repositories.incident_repository import IncidentRepository
from app.repositories.mitre_finding_repository import MitreFindingRepository
from app.repositories.risk_assessment_repository import RiskAssessmentRepository

logger = get_logger(__name__)

PROMPT_PATH = Path(__file__).with_name("prompt.md")
AI_REQUEST_TIMEOUT_SECONDS = 30


class ResponsePlanningService:
    """Generates incident response plans using Gemini with automatic fallback."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.incident_repository = IncidentRepository(db)
        self.mitre_repository = MitreFindingRepository(db)
        self.risk_repository = RiskAssessmentRepository(db)
        self.evidence_service = EvidenceCollectionService(db)
        self.threat_intelligence_service = ThreatIntelligenceService(db)
        self.risk_service = RiskAssessmentService(db)

    def plan(self, request: ResponsePlanInput) -> ResponsePlanResult:
        """Generate an incident response plan using AI first, then fallback rules."""
        context = self._gather_context(request.incident_id)
        logger.info("Response planning started: incident_id=%s", request.incident_id)

        ai_result = self._try_ai_plan(context)
        if ai_result is not None:
            logger.info("Response generated: source=AI incident_id=%s", request.incident_id)
            return ai_result

        logger.warning("Fallback activated: incident_id=%s", request.incident_id)
        result = plan_response_fallback(context)
        logger.info(
            "Response generated: source=FALLBACK incident_id=%s priority=%s",
            request.incident_id,
            result.priority,
        )
        return result

    def _gather_context(self, incident_id: uuid.UUID) -> ResponsePlanningContext:
        incident = self.incident_repository.get_by_id(incident_id)
        if incident is None:
            raise NotFoundException("Incident not found")

        evidence_summaries = []
        threat_reports = []
        suspicious_indicators: list[str] = []
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
            suspicious_indicators.extend(ti_result.report.suspicious_indicators)

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
                summary=risk_record.summary,
                reasoning=risk_record.reasoning,
            )
        else:
            risk_result = self.risk_service.assess(RiskAssessmentInput(incident_id=incident_id))
            risk_context = RiskAssessmentContext(
                overall_risk=risk_result.overall_risk,
                risk_score=risk_result.risk_score,
                priority=risk_result.priority,
                summary=risk_result.summary,
                reasoning=risk_result.reasoning,
            )

        return ResponsePlanningContext(
            incident=IncidentContext(
                id=incident.id,
                title=incident.title,
                description=incident.description,
                severity=incident.severity.value,
                status=incident.status.value,
                source=incident.source,
                confidence_score=incident.confidence_score,
            ),
            evidence_summaries=evidence_summaries,
            mitre_techniques=mitre_techniques,
            threat_intelligence_reports=threat_reports,
            risk_assessment=risk_context,
            total_iocs=total_iocs,
            suspicious_indicators=sorted(set(suspicious_indicators)),
        )

    def _try_ai_plan(self, context: ResponsePlanningContext) -> ResponsePlanResult | None:
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
            logger.warning("AI failure reason: request timed out after %ss", AI_REQUEST_TIMEOUT_SECONDS)
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

        logger.info("AI response received: incident_id=%s priority=%s", context.incident.id, response.priority)
        return ResponsePlanResult(
            source=ResponsePlanSource.AI,
            priority=response.priority,
            containment=response.containment,
            eradication=response.eradication,
            recovery=response.recovery,
            monitoring=response.monitoring,
            executive_summary=response.executive_summary,
        )

    def _call_gemini(
        self,
        api_key: str,
        model: str,
        context: ResponsePlanningContext,
    ) -> AIResponsePlanResponse | None:
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
            return AIResponsePlanResponse.model_validate(payload)
        except (json.JSONDecodeError, ValueError) as exc:
            logger.warning("AI failure reason: invalid JSON response (%s)", exc)
            return None

    def _build_prompt(self, context: ResponsePlanningContext) -> str:
        system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
        context_json = context.model_dump(mode="json")
        return (
            f"{system_prompt}\n\n"
            "Generate an incident response plan for the following context and return ONLY valid JSON:\n"
            f"{json.dumps(context_json, indent=2)}"
        )
