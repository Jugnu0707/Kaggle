"""Threat Intelligence Agent API service."""

from __future__ import annotations

import time
import uuid
from datetime import UTC, datetime

from agents.evidence.models import EvidencePackage
from agents.threat_intelligence.models import ThreatIntelligenceInput
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.threat_intelligence_runtime import get_threat_intelligence_agent
from app.models.agent_execution import AgentExecution
from app.models.enums import AgentExecutionStatus
from app.repositories.agent_execution_repository import AgentExecutionRepository
from app.schemas.threat_intelligence_agent import (
    ThreatIntelligenceRequest,
    ThreatIntelligenceResponse,
)
from agents.threat_intelligence.service import ThreatIntelligenceService

logger = get_logger(__name__)

THREAT_INTELLIGENCE_AGENT_NAME = "Threat Intelligence Agent"


class ThreatIntelligenceAgentService:
    """Runs Threat Intelligence enrichment and persists execution records."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.execution_repository = AgentExecutionRepository(db)

    def enrich(
        self,
        request: ThreatIntelligenceRequest,
        *,
        workflow_id: uuid.UUID | None = None,
    ) -> ThreatIntelligenceResponse:
        """Enrich evidence and record an AgentExecution entry."""
        get_threat_intelligence_agent()
        resolved_workflow_id = workflow_id or uuid.uuid4()
        started_at = datetime.now(UTC)
        timer_start = time.perf_counter()

        result = ThreatIntelligenceService(self.db).enrich(
            ThreatIntelligenceInput(
                incident_id=request.incident_id,
                evidence_id=request.evidence_id,
            )
        )
        return self._finalize_execution(
            incident_id=request.incident_id,
            workflow_id=resolved_workflow_id,
            started_at=started_at,
            timer_start=timer_start,
            result=result,
        )

    def enrich_from_package(
        self,
        package: EvidencePackage,
        *,
        workflow_id: uuid.UUID | None = None,
    ) -> ThreatIntelligenceResponse:
        """Enrich a pre-collected evidence package and record execution metadata."""
        get_threat_intelligence_agent()
        resolved_workflow_id = workflow_id or uuid.uuid4()
        started_at = datetime.now(UTC)
        timer_start = time.perf_counter()

        result = ThreatIntelligenceService(self.db).enrich_from_package(package)
        return self._finalize_execution(
            incident_id=package.incident_id,
            workflow_id=resolved_workflow_id,
            started_at=started_at,
            timer_start=timer_start,
            result=result,
        )

    def _finalize_execution(
        self,
        *,
        incident_id: uuid.UUID,
        workflow_id: uuid.UUID,
        started_at: datetime,
        timer_start: float,
        result,
    ) -> ThreatIntelligenceResponse:
        duration_ms = int((time.perf_counter() - timer_start) * 1000)
        completed_at = datetime.now(UTC)

        execution = AgentExecution(
            incident_id=incident_id,
            workflow_id=workflow_id,
            agent_name=THREAT_INTELLIGENCE_AGENT_NAME,
            status=AgentExecutionStatus.COMPLETED,
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=duration_ms,
            message=f"Threat intelligence enrichment completed: {result.ioc_count} IOCs",
        )
        self.execution_repository.create(execution)
        self.db.commit()

        logger.info(
            "Threat Intelligence Agent execution recorded: workflow_id=%s duration_ms=%s",
            workflow_id,
            duration_ms,
        )
        return ThreatIntelligenceResponse(
            status=result.status,
            ioc_count=result.ioc_count,
            report=result.report,
            iocs=result.iocs,
        )
