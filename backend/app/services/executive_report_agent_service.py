"""Executive Report Agent API service."""

from __future__ import annotations

import time
import uuid
from datetime import UTC, datetime

from agents.executive_report.markdown_generator import parse_markdown_report
from agents.executive_report.models import ExecutiveReportInput, ExecutiveReportResult
from agents.executive_report.service import ExecutiveReportService
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.core.executive_report_runtime import get_executive_report_agent
from app.core.logging import get_logger
from app.models.agent_execution import AgentExecution
from app.models.enums import AgentExecutionStatus
from app.models.executive_report import ExecutiveReport
from app.repositories.agent_execution_repository import AgentExecutionRepository
from app.repositories.executive_report_repository import ExecutiveReportRepository
from app.repositories.incident_repository import IncidentRepository
from app.schemas.executive_report_agent import (
    ExecutiveReportRecordResponse,
    ExecutiveReportRequest,
    ExecutiveReportResponse,
)

logger = get_logger(__name__)

EXECUTIVE_REPORT_AGENT_NAME = "Executive Report Agent"


class ExecutiveReportAgentService:
    """Runs executive report generation and persists results and execution records."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.execution_repository = AgentExecutionRepository(db)
        self.report_repository = ExecutiveReportRepository(db)
        self.incident_repository = IncidentRepository(db)

    def generate(
        self,
        request: ExecutiveReportRequest,
        *,
        workflow_id: uuid.UUID | None = None,
    ) -> ExecutiveReportResponse:
        """Generate an executive report and record an AgentExecution entry."""
        get_executive_report_agent()
        resolved_workflow_id = workflow_id or uuid.uuid4()
        started_at = datetime.now(UTC)
        timer_start = time.perf_counter()

        result = ExecutiveReportService(self.db).generate(
            ExecutiveReportInput(incident_id=request.incident_id)
        )
        return self._finalize_execution(
            incident_id=request.incident_id,
            workflow_id=resolved_workflow_id,
            started_at=started_at,
            timer_start=timer_start,
            result=result,
        )

    def get_latest_report(
        self, incident_id: uuid.UUID
    ) -> ExecutiveReportRecordResponse:
        """Return the latest persisted executive report for an incident."""
        incident = self.incident_repository.get_by_id(incident_id)
        if incident is None:
            raise NotFoundException("Incident not found")

        report = self.report_repository.get_latest_by_incident_id(incident_id)
        if report is None:
            raise NotFoundException("Executive report not found")

        parsed = parse_markdown_report(report.markdown_report)
        return ExecutiveReportRecordResponse(
            id=report.id,
            incident_id=report.incident_id,
            source=report.source,
            title=report.title,
            executive_summary=report.executive_summary,
            business_impact=report.business_impact,
            key_findings=parsed["key_findings"],
            recommended_actions=parsed["recommended_actions"],
            lessons_learned=parsed["lessons_learned"],
            markdown_report=report.markdown_report,
            created_at=report.created_at,
        )

    def _finalize_execution(
        self,
        *,
        incident_id: uuid.UUID,
        workflow_id: uuid.UUID,
        started_at: datetime,
        timer_start: float,
        result: ExecutiveReportResult,
    ) -> ExecutiveReportResponse:
        self._persist_report(incident_id, result)

        duration_ms = int((time.perf_counter() - timer_start) * 1000)
        completed_at = datetime.now(UTC)
        execution = AgentExecution(
            incident_id=incident_id,
            workflow_id=workflow_id,
            agent_name=EXECUTIVE_REPORT_AGENT_NAME,
            status=AgentExecutionStatus.COMPLETED,
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=duration_ms,
            message=(
                f"Executive report generated via {result.source.value}: "
                f"{len(result.key_findings)} key findings"
            ),
        )
        self.execution_repository.create(execution)
        self.db.commit()

        logger.info(
            "Executive Report Agent execution recorded: workflow_id=%s duration_ms=%s source=%s",
            workflow_id,
            duration_ms,
            result.source.value,
        )
        return ExecutiveReportResponse.model_validate(result.model_dump())

    def _persist_report(
        self,
        incident_id: uuid.UUID,
        result: ExecutiveReportResult,
    ) -> None:
        self.report_repository.delete_by_incident_id(incident_id)
        report = ExecutiveReport(
            incident_id=incident_id,
            source=result.source.value,
            title=result.title,
            executive_summary=result.executive_summary,
            business_impact=result.business_impact,
            markdown_report=result.markdown,
        )
        self.report_repository.create(report)
