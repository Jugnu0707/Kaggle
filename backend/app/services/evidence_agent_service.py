"""Evidence Agent API service."""

from __future__ import annotations

import time
import uuid
from datetime import UTC, datetime

from agents.evidence.models import EvidenceInput
from sqlalchemy.orm import Session

from app.core.evidence_runtime import get_evidence_agent
from app.core.logging import get_logger
from app.models.agent_execution import AgentExecution
from app.models.enums import AgentExecutionStatus
from app.repositories.agent_execution_repository import AgentExecutionRepository
from app.schemas.evidence_agent import EvidenceCollectRequest, EvidenceCollectResponse

logger = get_logger(__name__)

EVIDENCE_AGENT_NAME = "Evidence Agent"


class EvidenceAgentService:
    """Runs Evidence Agent collection and persists execution records."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.execution_repository = AgentExecutionRepository(db)

    def collect(
        self,
        request: EvidenceCollectRequest,
        *,
        workflow_id: uuid.UUID | None = None,
    ) -> EvidenceCollectResponse:
        """Collect evidence and record an AgentExecution entry."""
        agent = get_evidence_agent()
        resolved_workflow_id = workflow_id or uuid.uuid4()
        started_at = datetime.now(UTC)
        timer_start = time.perf_counter()

        result = agent.collect(
            EvidenceInput(
                incident_id=request.incident_id,
                log_file_id=request.log_file_id,
            ),
            self.db,
        )
        duration_ms = int((time.perf_counter() - timer_start) * 1000)
        completed_at = datetime.now(UTC)

        execution = AgentExecution(
            incident_id=request.incident_id,
            workflow_id=resolved_workflow_id,
            agent_name=EVIDENCE_AGENT_NAME,
            status=AgentExecutionStatus.COMPLETED,
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=duration_ms,
            message=(
                f"Evidence collected: {result.evidence_package.number_of_lines} entries"
            ),
        )
        self.execution_repository.create(execution)
        self.db.commit()

        logger.info(
            "Evidence Agent execution recorded: workflow_id=%s duration_ms=%s",
            resolved_workflow_id,
            duration_ms,
        )
        return EvidenceCollectResponse.model_validate(result.model_dump())
