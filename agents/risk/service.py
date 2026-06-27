"""Risk Assessment Agent — AI-first assessment with automatic fallback."""

from __future__ import annotations

import json
import uuid
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from pathlib import Path

from google.genai import errors as genai_errors
from sqlalchemy import select
from sqlalchemy.orm import Session

from agents.evidence.models import EvidenceInput
from agents.evidence.service import EvidenceCollectionService
from agents.mitre.models import MappedTechnique
from agents.risk.fallback import assess_risk_fallback
from agents.risk.models import RiskAssessmentInput, RiskAssessmentResult
from agents.risk.schemas import (
    AIRiskAssessmentResponse,
    IncidentContext,
    RiskAssessmentContext,
    RiskAssessmentSource,
)
from agents.threat_intelligence.service import ThreatIntelligenceService
from app.ai.runtime import get_ai_runtime
from app.core.exceptions import NotFoundException
from app.core.logging import get_logger
from app.models.log_file import LogFile
from app.repositories.incident_repository import IncidentRepository
from app.repositories.mitre_finding_repository import MitreFindingRepository

logger = get_logger(__name__)

PROMPT_PATH = Path(__file__).with_name("prompt.md")
AI_REQUEST_TIMEOUT_SECONDS = 30


class RiskAssessmentService:
    """Assesses enterprise risk using Gemini with automatic rule-based fallback."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.incident_repository = IncidentRepository(db)
        self.mitre_repository = MitreFindingRepository(db)
        self.evidence_service = EvidenceCollectionService(db)
        self.threat_intelligence_service = ThreatIntelligenceService(db)

    def assess(self, request: RiskAssessmentInput) -> RiskAssessmentResult:
        """Assess incident risk using AI first, then fallback rules if needed."""
        runtime = get_ai_runtime()
        system_result = runtime.invoke_tool("system_info", {}, self.db)
        if system_result.success:
            logger.info("MCP system_info tool executed via runtime for risk assessment")

        context = self._gather_context(request.incident_id)
        logger.info("Risk assessment started: incident_id=%s", request.incident_id)

        ai_result = self._try_ai_assessment(context)
        if ai_result is not None:
            logger.info("Risk assessment completed: source=AI incident_id=%s", request.incident_id)
            return ai_result

        logger.warning("Fallback activated: incident_id=%s", request.incident_id)
        result = assess_risk_fallback(context)
        logger.info(
            "Risk assessment completed: source=FALLBACK incident_id=%s overall_risk=%s",
            request.incident_id,
            result.overall_risk,
        )
        return result

    def _gather_context(self, incident_id: uuid.UUID) -> RiskAssessmentContext:
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

        return RiskAssessmentContext(
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
            total_iocs=total_iocs,
            suspicious_indicators=sorted(set(suspicious_indicators)),
        )

    def _try_ai_assessment(
        self,
        context: RiskAssessmentContext,
    ) -> RiskAssessmentResult | None:
        api_key = get_ai_runtime().provider.get_api_key()
        model = get_ai_runtime().provider.get_model()
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

        logger.info("AI success: incident_id=%s overall_risk=%s", context.incident.id, response.overall_risk)
        return RiskAssessmentResult(
            source=RiskAssessmentSource.AI,
            overall_risk=response.overall_risk.value,
            risk_score=response.risk_score,
            likelihood=response.likelihood,
            business_impact=response.business_impact,
            confidence=response.confidence,
            priority=response.priority,
            summary=response.summary,
            reasoning=response.reasoning,
        )

    def _call_gemini(
        self,
        api_key: str,
        model: str,
        context: RiskAssessmentContext,
    ) -> AIRiskAssessmentResponse | None:
        _ = api_key
        prompt = self._build_prompt(context)
        raw_text = get_ai_runtime().provider.generate_json(prompt, model=model)
        if not raw_text:
            logger.warning("AI failure reason: empty response from Gemini")
            return None

        try:
            payload = json.loads(raw_text)
            return AIRiskAssessmentResponse.model_validate(payload)
        except (json.JSONDecodeError, ValueError) as exc:
            logger.warning("AI failure reason: invalid JSON response (%s)", exc)
            return None

    def _build_prompt(self, context: RiskAssessmentContext) -> str:
        system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
        context_json = context.model_dump(mode="json")
        return (
            f"{system_prompt}\n\n"
            "Assess the following incident context and return ONLY valid JSON:\n"
            f"{json.dumps(context_json, indent=2)}"
        )
