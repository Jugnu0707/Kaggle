"""Risk Assessment Agent API service."""

from __future__ import annotations

import time
import uuid
from datetime import UTC, datetime

from agents.risk.models import RiskAssessmentInput, RiskAssessmentResult
from agents.risk.service import RiskAssessmentService
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.core.logging import get_logger
from app.core.risk_runtime import get_risk_agent
from app.models.agent_execution import AgentExecution
from app.models.enums import AgentExecutionStatus
from app.models.risk_assessment import RiskAssessment
from app.repositories.agent_execution_repository import AgentExecutionRepository
from app.repositories.incident_repository import IncidentRepository
from app.repositories.risk_assessment_repository import RiskAssessmentRepository
from app.schemas.risk_agent import (
    RiskAssessmentRecordResponse,
    RiskAssessmentRequest,
    RiskAssessmentResponse,
)

logger = get_logger(__name__)

RISK_AGENT_NAME = "Risk Assessment Agent"


class RiskAgentService:
    """Runs risk assessments and persists results and execution records."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.execution_repository = AgentExecutionRepository(db)
        self.assessment_repository = RiskAssessmentRepository(db)
        self.incident_repository = IncidentRepository(db)

    def assess(
        self,
        request: RiskAssessmentRequest,
        *,
        workflow_id: uuid.UUID | None = None,
    ) -> RiskAssessmentResponse:
        """Assess incident risk and record an AgentExecution entry."""
        get_risk_agent()
        resolved_workflow_id = workflow_id or uuid.uuid4()
        started_at = datetime.now(UTC)
        timer_start = time.perf_counter()

        result = RiskAssessmentService(self.db).assess(
            RiskAssessmentInput(incident_id=request.incident_id)
        )
        return self._finalize_execution(
            incident_id=request.incident_id,
            workflow_id=resolved_workflow_id,
            started_at=started_at,
            timer_start=timer_start,
            result=result,
        )

    def get_latest_assessment(self, incident_id: uuid.UUID) -> RiskAssessmentRecordResponse:
        """Return the latest persisted risk assessment for an incident."""
        incident = self.incident_repository.get_by_id(incident_id)
        if incident is None:
            raise NotFoundException("Incident not found")

        assessment = self.assessment_repository.get_latest_by_incident_id(incident_id)
        if assessment is None:
            raise NotFoundException("Risk assessment not found")

        return RiskAssessmentRecordResponse.model_validate(assessment)

    def _finalize_execution(
        self,
        *,
        incident_id: uuid.UUID,
        workflow_id: uuid.UUID,
        started_at: datetime,
        timer_start: float,
        result: RiskAssessmentResult,
    ) -> RiskAssessmentResponse:
        self._persist_assessment(incident_id, result)

        duration_ms = int((time.perf_counter() - timer_start) * 1000)
        completed_at = datetime.now(UTC)
        execution = AgentExecution(
            incident_id=incident_id,
            workflow_id=workflow_id,
            agent_name=RISK_AGENT_NAME,
            status=AgentExecutionStatus.COMPLETED,
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=duration_ms,
            message=(
                f"Risk assessment completed via {result.source.value}: "
                f"{result.overall_risk} ({result.priority})"
            ),
        )
        self.execution_repository.create(execution)
        self.db.commit()

        logger.info(
            "Risk Assessment Agent execution recorded: workflow_id=%s duration_ms=%s source=%s",
            workflow_id,
            duration_ms,
            result.source.value,
        )
        return RiskAssessmentResponse.model_validate(result.model_dump())

    def _persist_assessment(
        self,
        incident_id: uuid.UUID,
        result: RiskAssessmentResult,
    ) -> None:
        self.assessment_repository.delete_by_incident_id(incident_id)
        assessment = RiskAssessment(
            incident_id=incident_id,
            source=result.source.value,
            overall_risk=result.overall_risk,
            risk_score=result.risk_score,
            likelihood=result.likelihood,
            business_impact=result.business_impact,
            confidence=result.confidence,
            priority=result.priority,
            summary=result.summary,
            reasoning=result.reasoning,
        )
        self.assessment_repository.create(assessment)
