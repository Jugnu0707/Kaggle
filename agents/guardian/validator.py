"""Guardian validation pipeline for AI agent outputs."""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from agents.evidence.models import EvidenceResult
from agents.executive_report.models import ExecutiveReportResult
from agents.guardian.confidence import validate_confidence
from agents.guardian.pii_detector import detect_pii, mask_pii_in_response
from agents.guardian.prompt_injection import scan_response_for_injection
from agents.guardian.schemas import (
    GuardianAgentName,
    GuardianValidateInput,
    GuardianValidationResult,
    ValidationStatus,
)
from agents.guardian.secret_detector import detect_secrets, mask_secrets_in_response
from agents.mitre.models import MitreMappingResult
from agents.response.models import ResponsePlanResult
from agents.risk.models import RiskAssessmentResult
from agents.threat_intelligence.models import ThreatIntelligenceFinding
from app.core.guardian_config import guardian_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ThreatIntelligenceGuardianSchema(BaseModel):
    """Minimal threat intelligence schema for Guardian validation."""

    status: str
    ioc_count: int = Field(ge=0)
    findings: list[ThreatIntelligenceFinding]


AGENT_SCHEMAS: dict[GuardianAgentName, type[BaseModel]] = {
    GuardianAgentName.EVIDENCE: EvidenceResult,
    GuardianAgentName.THREAT_INTELLIGENCE: ThreatIntelligenceGuardianSchema,
    GuardianAgentName.MITRE: MitreMappingResult,
    GuardianAgentName.RISK: RiskAssessmentResult,
    GuardianAgentName.RESPONSE: ResponsePlanResult,
    GuardianAgentName.EXECUTIVE_REPORT: ExecutiveReportResult,
}

MANDATORY_FIELDS: dict[GuardianAgentName, tuple[str, ...]] = {
    GuardianAgentName.EVIDENCE: ("status", "evidence_summary"),
    GuardianAgentName.THREAT_INTELLIGENCE: ("status", "findings"),
    GuardianAgentName.MITRE: ("status", "techniques"),
    GuardianAgentName.RISK: ("risk_score", "overall_risk", "priority"),
    GuardianAgentName.RESPONSE: ("priority", "containment", "executive_summary"),
    GuardianAgentName.EXECUTIVE_REPORT: ("executive_summary", "business_impact"),
}


def _is_empty_response(response: dict[str, Any]) -> bool:
    if not response:
        return True

    meaningful_values = [
        value for value in response.values() if value not in (None, "", [], {})
    ]
    return len(meaningful_values) == 0


def _validate_schema(agent: GuardianAgentName, response: dict[str, Any]) -> list[str]:
    schema = AGENT_SCHEMAS.get(agent)
    if schema is None:
        return []

    try:
        schema.model_validate(response)
        return []
    except ValidationError as exc:
        return [f"Schema validation failed: {error['msg']}" for error in exc.errors()]


def _validate_mandatory_fields(
    agent: GuardianAgentName, response: dict[str, Any]
) -> list[str]:
    issues: list[str] = []
    for field in MANDATORY_FIELDS.get(agent, ()):
        value = response.get(field)
        if value is None or value == "" or value == []:
            issues.append(f"Mandatory field missing or empty: {field}")
    return issues


def _serialize_response(response: dict[str, Any]) -> str:
    return json.dumps(response, default=str)


class GuardianValidator:
    """Runs security and governance checks against agent outputs."""

    def validate(self, request: GuardianValidateInput) -> GuardianValidationResult:
        """Validate an agent response and return approval, warning, or rejection."""
        if not guardian_settings.guardian_enabled:
            return GuardianValidationResult(
                status=ValidationStatus.APPROVED,
                masked_response=request.response,
                actions_taken=["guardian_disabled"],
            )

        issues: list[str] = []
        actions: list[str] = []
        response = dict(request.response)

        if _is_empty_response(response):
            return GuardianValidationResult(
                status=ValidationStatus.REJECTED,
                issues=["Empty response detected"],
                fallback_triggered=True,
                actions_taken=["reject_empty_response"],
            )

        schema_issues = _validate_schema(request.agent, response)
        if schema_issues:
            if request.retry_attempt == 0:
                return GuardianValidationResult(
                    status=ValidationStatus.REJECTED,
                    issues=schema_issues,
                    retry_recommended=True,
                    actions_taken=["request_json_retry"],
                )
            return GuardianValidationResult(
                status=ValidationStatus.REJECTED,
                issues=schema_issues,
                fallback_triggered=True,
                actions_taken=["trigger_fallback_after_invalid_json"],
            )

        mandatory_issues = _validate_mandatory_fields(request.agent, response)
        if mandatory_issues:
            issues.extend(mandatory_issues)
            return GuardianValidationResult(
                status=ValidationStatus.REJECTED,
                issues=issues,
                fallback_triggered=True,
                actions_taken=["reject_missing_mandatory_fields"],
            )

        injection_findings = scan_response_for_injection(response)
        if injection_findings:
            issues.extend(
                [
                    f"Prompt injection detected: {phrase}"
                    for phrase in injection_findings
                ]
            )
            return GuardianValidationResult(
                status=ValidationStatus.REJECTED,
                issues=issues,
                fallback_triggered=True,
                actions_taken=["reject_prompt_injection"],
            )

        serialized = _serialize_response(response)
        secret_findings = detect_secrets(serialized)
        if secret_findings and guardian_settings.mask_secrets:
            response, masked_secret_labels = mask_secrets_in_response(response)
            if masked_secret_labels:
                actions.append("masked_secrets")
                issues.extend(
                    [
                        f"Secret detected and masked: {label}"
                        for label in masked_secret_labels
                    ]
                )

        pii_blocking: list[str] = []
        pii_warnings: list[str] = []
        if guardian_settings.mask_pii:
            response, pii_blocking, pii_warnings = mask_pii_in_response(response)
            if pii_blocking:
                actions.append("masked_pii")
                issues.extend(
                    [f"PII detected and masked: {label}" for label in pii_blocking]
                )
            if pii_warnings:
                issues.extend([f"PII warning: {label}" for label in pii_warnings])
        else:
            blocking, warnings = detect_pii(serialized)
            pii_blocking.extend(blocking)
            pii_warnings.extend(warnings)
            if pii_warnings:
                issues.extend([f"PII warning: {label}" for label in pii_warnings])

        source = str(response.get("source", ""))
        confidence_issues = validate_confidence(
            response,
            min_confidence=guardian_settings.min_ai_confidence,
            source=source or None,
        )
        if confidence_issues:
            return GuardianValidationResult(
                status=ValidationStatus.REJECTED,
                issues=confidence_issues,
                fallback_triggered=True,
                actions_taken=["trigger_fallback_low_confidence"],
            )

        if pii_warnings and not pii_blocking and not secret_findings:
            actions.append("approved_with_warnings")
            return GuardianValidationResult(
                status=ValidationStatus.WARNING,
                issues=issues,
                masked_response=response,
                actions_taken=actions or ["approved_with_warnings"],
            )

        if issues:
            actions.append("approved_with_masking")
            return GuardianValidationResult(
                status=ValidationStatus.WARNING,
                issues=issues,
                masked_response=response,
                actions_taken=actions,
            )

        logger.info("Guardian validation approved: agent=%s", request.agent.value)
        return GuardianValidationResult(
            status=ValidationStatus.APPROVED,
            issues=[],
            masked_response=response,
            actions_taken=["approved"],
        )
