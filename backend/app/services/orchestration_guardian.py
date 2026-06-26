"""Guardian integration helpers for orchestration."""

from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Any
from unittest.mock import patch

from agents.guardian.schemas import GuardianAgentName
from sqlalchemy.orm import Session

from app.schemas.guardian_agent import GuardianValidateRequest, GuardianValidateResponse
from app.services.guardian_agent_service import GuardianAgentService

AI_PATCH_PATHS: dict[GuardianAgentName, str] = {
    GuardianAgentName.THREAT_INTELLIGENCE: (
        "agents.threat_intelligence.service.ThreatIntelligenceService._call_gemini"
    ),
    GuardianAgentName.RISK: "agents.risk.service.RiskAssessmentService._call_gemini",
    GuardianAgentName.RESPONSE: "agents.response.service.ResponsePlanningService._call_gemini",
    GuardianAgentName.EXECUTIVE_REPORT: (
        "agents.executive_report.service.ExecutiveReportService._call_gemini"
    ),
}


def validate_agent_output(
    db: Session,
    *,
    incident_id: uuid.UUID,
    workflow_id: uuid.UUID,
    agent: GuardianAgentName,
    response: dict[str, Any],
    retry_attempt: int = 0,
) -> GuardianValidateResponse:
    """Validate a specialist agent output and persist a Guardian audit record."""
    return GuardianAgentService(db).validate(
        GuardianValidateRequest(
            agent=agent,
            response=response,
            incident_id=incident_id,
            retry_attempt=retry_attempt,
        ),
        workflow_id=workflow_id,
    )


def run_stage_with_guardian(
    db: Session,
    *,
    incident_id: uuid.UUID,
    workflow_id: uuid.UUID,
    agent: GuardianAgentName,
    run_callable: Callable[[], Any],
) -> tuple[Any, GuardianValidateResponse]:
    """Run a pipeline stage and validate its output with Guardian."""
    result = run_callable()
    validation = validate_agent_output(
        db,
        incident_id=incident_id,
        workflow_id=workflow_id,
        agent=agent,
        response=result.model_dump(mode="json"),
    )

    if validation.retry_recommended or validation.fallback_triggered:
        patch_path = AI_PATCH_PATHS.get(agent)
        if patch_path is not None:
            with patch(patch_path, return_value=None):
                result = run_callable()
            validation = validate_agent_output(
                db,
                incident_id=incident_id,
                workflow_id=workflow_id,
                agent=agent,
                response=result.model_dump(mode="json"),
                retry_attempt=1,
            )

    return result, validation
