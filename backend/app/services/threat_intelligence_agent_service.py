"""Threat Intelligence Agent API service."""

from __future__ import annotations

import time
import uuid
from datetime import UTC, datetime

from agents.evidence.models import EvidencePackage
from agents.threat_intelligence.models import ThreatIntelligenceInput, ThreatIntelligenceResult
from agents.threat_intelligence.service import ThreatIntelligenceService
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.core.logging import get_logger
from app.core.threat_intelligence_runtime import get_threat_intelligence_agent
from app.models.agent_execution import AgentExecution
from app.models.enums import AgentExecutionStatus
from app.models.threat_intelligence_finding import ThreatIntelligenceFinding as ThreatIntelligenceFindingORM
from app.repositories.agent_execution_repository import AgentExecutionRepository
from app.repositories.incident_repository import IncidentRepository
from app.repositories.threat_intelligence_finding_repository import (
    ThreatIntelligenceFindingRepository,
)
from app.schemas.threat_intelligence_agent import (
    ThreatIntelligenceFindingListResponse,
    ThreatIntelligenceFindingRecordResponse,
    ThreatIntelligenceRequest,
    ThreatIntelligenceResponse,
)

logger = get_logger(__name__)

THREAT_INTELLIGENCE_AGENT_NAME = "Threat Intelligence Agent"


class ThreatIntelligenceAgentService:
    """Runs threat intelligence enrichment and persists findings and execution records."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.execution_repository = AgentExecutionRepository(db)
        self.finding_repository = ThreatIntelligenceFindingRepository(db)
        self.incident_repository = IncidentRepository(db)

    def list_findings(self, incident_id: uuid.UUID) -> ThreatIntelligenceFindingListResponse:
        """Return persisted threat intelligence findings for an incident."""
        incident = self.incident_repository.get_by_id(incident_id)
        if incident is None:
            raise NotFoundException("Incident not found")

        findings = self.finding_repository.list_by_incident_id(incident_id)
        items = [
            ThreatIntelligenceFindingRecordResponse.model_validate(finding)
            for finding in findings
        ]
        return ThreatIntelligenceFindingListResponse(items=items, total=len(items))

    def enrich(
        self,
        request: ThreatIntelligenceRequest,
        *,
        workflow_id: uuid.UUID | None = None,
    ) -> ThreatIntelligenceResponse:
        """Enrich incident evidence and record an AgentExecution entry."""
        get_threat_intelligence_agent()
        resolved_workflow_id = workflow_id or uuid.uuid4()
        started_at = datetime.now(UTC)
        timer_start = time.perf_counter()

        result = ThreatIntelligenceService(self.db).enrich(
            ThreatIntelligenceInput(incident_id=request.incident_id)
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
        result: ThreatIntelligenceResult,
    ) -> ThreatIntelligenceResponse:
        self._persist_findings(incident_id, result)

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
            findings=result.findings,
        )

    def _persist_findings(
        self,
        incident_id: uuid.UUID,
        result: ThreatIntelligenceResult,
    ) -> None:
        self.finding_repository.delete_by_incident_id(incident_id)
        for finding in result.findings:
            record = ThreatIntelligenceFindingORM(
                incident_id=incident_id,
                indicator=finding.indicator,
                indicator_type=finding.indicator_type,
                reputation=finding.reputation,
                confidence=finding.confidence,
                source=finding.source.value,
                description=finding.description,
                analyst_notes=finding.analyst_notes,
            )
            self.finding_repository.create(record)
