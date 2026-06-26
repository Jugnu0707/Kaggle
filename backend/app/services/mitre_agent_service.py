"""MITRE Mapping Agent API service."""

from __future__ import annotations

import time
import uuid
from datetime import UTC, datetime

from agents.evidence.models import EvidencePackage
from agents.mitre.models import MitreMappingInput, MitreMappingResult
from agents.mitre.service import MitreMappingService
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.core.logging import get_logger
from app.core.mitre_runtime import get_mitre_agent
from app.models.agent_execution import AgentExecution
from app.models.enums import AgentExecutionStatus
from app.models.mitre_finding import MitreFinding
from app.repositories.agent_execution_repository import AgentExecutionRepository
from app.repositories.incident_repository import IncidentRepository
from app.repositories.mitre_finding_repository import MitreFindingRepository
from app.schemas.mitre_agent import (
    MitreFindingListResponse,
    MitreFindingResponse,
    MitreMappingRequest,
    MitreMappingResponse,
)

logger = get_logger(__name__)

MITRE_AGENT_NAME = "MITRE Mapping Agent"


class MitreAgentService:
    """Runs MITRE mapping and persists findings and execution records."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.execution_repository = AgentExecutionRepository(db)
        self.finding_repository = MitreFindingRepository(db)
        self.incident_repository = IncidentRepository(db)

    def list_findings(self, incident_id: uuid.UUID) -> MitreFindingListResponse:
        """Return persisted MITRE findings for an incident."""
        incident = self.incident_repository.get_by_id(incident_id)
        if incident is None:
            raise NotFoundException("Incident not found")

        findings = self.finding_repository.list_by_incident_id(incident_id)
        items = [MitreFindingResponse.model_validate(finding) for finding in findings]
        return MitreFindingListResponse(items=items, total=len(items))

    def map_incident(
        self,
        request: MitreMappingRequest,
        *,
        workflow_id: uuid.UUID | None = None,
    ) -> MitreMappingResponse:
        """Map incident evidence to MITRE techniques and persist findings."""
        get_mitre_agent()
        resolved_workflow_id = workflow_id or uuid.uuid4()
        started_at = datetime.now(UTC)
        timer_start = time.perf_counter()

        result = MitreMappingService(self.db).map_incident(
            MitreMappingInput(incident_id=request.incident_id)
        )
        return self._finalize_execution(
            incident_id=request.incident_id,
            workflow_id=resolved_workflow_id,
            started_at=started_at,
            timer_start=timer_start,
            result=result,
        )

    def map_from_package(
        self,
        package: EvidencePackage,
        *,
        workflow_id: uuid.UUID | None = None,
    ) -> MitreMappingResponse:
        """Map a pre-collected evidence package and persist findings."""
        get_mitre_agent()
        resolved_workflow_id = workflow_id or uuid.uuid4()
        started_at = datetime.now(UTC)
        timer_start = time.perf_counter()

        result = MitreMappingService(self.db).map_from_package(package)
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
        result: MitreMappingResult,
    ) -> MitreMappingResponse:
        self._persist_findings(incident_id, result)

        duration_ms = int((time.perf_counter() - timer_start) * 1000)
        completed_at = datetime.now(UTC)
        execution = AgentExecution(
            incident_id=incident_id,
            workflow_id=workflow_id,
            agent_name=MITRE_AGENT_NAME,
            status=AgentExecutionStatus.COMPLETED,
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=duration_ms,
            message=(
                f"MITRE mapping completed: {len(result.techniques)} techniques"
                if result.techniques
                else "MITRE mapping completed: No mapping found."
            ),
        )
        self.execution_repository.create(execution)
        self.db.commit()

        logger.info(
            "MITRE Mapping Agent execution recorded: workflow_id=%s duration_ms=%s",
            workflow_id,
            duration_ms,
        )
        return MitreMappingResponse(
            status=result.status,
            techniques=result.techniques,
            message=result.message,
        )

    def _persist_findings(
        self,
        incident_id: uuid.UUID,
        result: MitreMappingResult,
    ) -> None:
        self.finding_repository.delete_by_incident_id(incident_id)
        for technique in result.techniques:
            finding = MitreFinding(
                incident_id=incident_id,
                technique_id=technique.technique_id,
                technique_name=technique.technique_name,
                tactic=technique.tactic,
                confidence=technique.confidence,
                evidence=technique.matched_evidence,
            )
            self.finding_repository.create(finding)
