"""Response Planning Agent API service."""

from __future__ import annotations

import time
import uuid
from datetime import UTC, datetime

from agents.response.models import ResponsePlanInput, ResponsePlanResult
from agents.response.service import ResponsePlanningService
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.core.logging import get_logger
from app.core.response_runtime import get_response_agent
from app.models.agent_execution import AgentExecution
from app.models.enums import AgentExecutionStatus
from app.models.response_plan import ResponsePlan
from app.repositories.agent_execution_repository import AgentExecutionRepository
from app.repositories.incident_repository import IncidentRepository
from app.repositories.response_plan_repository import ResponsePlanRepository
from app.schemas.response_agent import (
    ResponsePlanRecordResponse,
    ResponsePlanRequest,
    ResponsePlanResponse,
)

logger = get_logger(__name__)

RESPONSE_AGENT_NAME = "Response Planning Agent"


class ResponseAgentService:
    """Runs response planning and persists results and execution records."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.execution_repository = AgentExecutionRepository(db)
        self.plan_repository = ResponsePlanRepository(db)
        self.incident_repository = IncidentRepository(db)

    def plan(
        self,
        request: ResponsePlanRequest,
        *,
        workflow_id: uuid.UUID | None = None,
    ) -> ResponsePlanResponse:
        """Generate an incident response plan and record an AgentExecution entry."""
        get_response_agent()
        resolved_workflow_id = workflow_id or uuid.uuid4()
        started_at = datetime.now(UTC)
        timer_start = time.perf_counter()

        result = ResponsePlanningService(self.db).plan(
            ResponsePlanInput(incident_id=request.incident_id)
        )
        return self._finalize_execution(
            incident_id=request.incident_id,
            workflow_id=resolved_workflow_id,
            started_at=started_at,
            timer_start=timer_start,
            result=result,
        )

    def get_latest_plan(self, incident_id: uuid.UUID) -> ResponsePlanRecordResponse:
        """Return the latest persisted response plan for an incident."""
        incident = self.incident_repository.get_by_id(incident_id)
        if incident is None:
            raise NotFoundException("Incident not found")

        plan = self.plan_repository.get_latest_by_incident_id(incident_id)
        if plan is None:
            raise NotFoundException("Response plan not found")

        return ResponsePlanRecordResponse.model_validate(plan)

    def _finalize_execution(
        self,
        *,
        incident_id: uuid.UUID,
        workflow_id: uuid.UUID,
        started_at: datetime,
        timer_start: float,
        result: ResponsePlanResult,
    ) -> ResponsePlanResponse:
        self._persist_plan(incident_id, result)

        duration_ms = int((time.perf_counter() - timer_start) * 1000)
        completed_at = datetime.now(UTC)
        execution = AgentExecution(
            incident_id=incident_id,
            workflow_id=workflow_id,
            agent_name=RESPONSE_AGENT_NAME,
            status=AgentExecutionStatus.COMPLETED,
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=duration_ms,
            message=(
                f"Response plan generated via {result.source.value}: "
                f"{result.priority} ({len(result.containment)} containment actions)"
            ),
        )
        self.execution_repository.create(execution)
        self.db.commit()

        logger.info(
            "Response Planning Agent execution recorded: workflow_id=%s duration_ms=%s source=%s",
            workflow_id,
            duration_ms,
            result.source.value,
        )
        return ResponsePlanResponse.model_validate(result.model_dump())

    def _persist_plan(
        self,
        incident_id: uuid.UUID,
        result: ResponsePlanResult,
    ) -> None:
        self.plan_repository.delete_by_incident_id(incident_id)
        plan = ResponsePlan(
            incident_id=incident_id,
            source=result.source.value,
            priority=result.priority,
            containment=result.containment,
            eradication=result.eradication,
            recovery=result.recovery,
            monitoring=result.monitoring,
            executive_summary=result.executive_summary,
        )
        self.plan_repository.create(plan)
