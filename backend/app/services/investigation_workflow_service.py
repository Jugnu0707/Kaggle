"""End-to-end investigation workflow orchestrated by the Coordinator."""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from agents.coordinator.models import CoordinatorInput
from agents.guardian.schemas import GuardianAgentName, ValidationStatus
from sqlalchemy.orm import Session

from app.core.adk_runtime import get_coordinator
from app.core.exceptions import NotFoundException
from app.core.logging import get_logger
from app.models.agent_execution import AgentExecution
from app.models.enums import AgentExecutionStatus, IncidentStatus, InvestigationRunStatus, InvestigationStatus
from app.models.investigation import Investigation
from app.models.investigation_run import InvestigationRun
from app.repositories.agent_execution_repository import AgentExecutionRepository
from app.repositories.executive_report_repository import ExecutiveReportRepository
from app.repositories.incident_repository import IncidentRepository
from app.repositories.investigation_run_repository import InvestigationRunRepository
from app.repositories.log_repository import LogRepository
from app.repositories.timeline_event_repository import TimelineEventRepository
from app.schemas.executive_report_agent import ExecutiveReportRequest
from app.schemas.evidence_agent import EvidenceCollectRequest
from app.schemas.guardian_agent import GuardianValidateResponse
from app.schemas.investigation import InvestigationPackageResponse, InvestigationStageResult
from app.schemas.risk_agent import RiskAssessmentRequest
from app.schemas.response_agent import ResponsePlanRequest
from app.services.evaluation_service import EvaluationService
from app.services.evidence_agent_service import EvidenceAgentService
from app.services.executive_report_agent_service import ExecutiveReportAgentService
from app.services.mitre_agent_service import MitreAgentService
from app.services.orchestration_guardian import run_stage_with_guardian
from app.services.response_agent_service import ResponseAgentService
from app.services.risk_agent_service import RiskAgentService
from app.services.threat_intelligence_agent_service import ThreatIntelligenceAgentService
from app.services.timeline_service import TimelineService

logger = get_logger(__name__)

COORDINATOR_AGENT_NAME = "Coordinator Agent"
GUARDIAN_STAGE_NAME = "Guardian"
TIMELINE_STAGE_NAME = "Timeline"
EVALUATION_STAGE_NAME = "Evaluation"

STAGE_DISPLAY_NAMES: dict[GuardianAgentName, str] = {
    GuardianAgentName.EVIDENCE: "Evidence",
    GuardianAgentName.THREAT_INTELLIGENCE: "Threat Intelligence",
    GuardianAgentName.MITRE: "MITRE",
    GuardianAgentName.RISK: "Risk",
    GuardianAgentName.RESPONSE: "Response",
    GuardianAgentName.EXECUTIVE_REPORT: "Executive Report",
}


@dataclass
class _WorkflowState:
    """Mutable state accumulated during an investigation run."""

    agents_completed: list[str] = field(default_factory=list)
    agents_failed: list[str] = field(default_factory=list)
    stages: list[InvestigationStageResult] = field(default_factory=list)
    guardian_validations: int = 0
    guardian_failures: int = 0
    overall_risk: str = "Medium"
    report_id: uuid.UUID | None = None
    timeline_id: uuid.UUID | None = None
    evaluation_score: int | None = None
    evidence_result: Any = None


class InvestigationWorkflowService:
    """Runs the full Coordinator investigation pipeline."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.incident_repository = IncidentRepository(db)
        self.log_repository = LogRepository(db)
        self.run_repository = InvestigationRunRepository(db)
        self.execution_repository = AgentExecutionRepository(db)
        self.report_repository = ExecutiveReportRepository(db)
        self.timeline_repository = TimelineEventRepository(db)
        self.evaluation_service = EvaluationService(db)
        self.timeline_service = TimelineService(db)

    def run(self, incident_id: uuid.UUID) -> InvestigationPackageResponse:
        """Execute the end-to-end investigation workflow for an incident."""
        incident = self.incident_repository.get_by_id(incident_id)
        if incident is None:
            raise NotFoundException("Incident not found")

        execution_id = uuid.uuid4()
        started_at = datetime.now(UTC)
        timer_start = time.perf_counter()

        logger.info(
            "Investigation started: execution_id=%s incident_id=%s",
            execution_id,
            incident_id,
        )

        run = InvestigationRun(
            id=execution_id,
            incident_id=incident_id,
            started_at=started_at,
            status=InvestigationRunStatus.RUNNING,
        )
        self.run_repository.create(run)

        incident.status = IncidentStatus.INVESTIGATING
        self._ensure_investigation_record(incident_id, started_at)

        state = _WorkflowState(overall_risk=incident.severity.value)
        log_file = self.log_repository.get_latest_for_incident(incident_id)
        log_id = log_file.id if log_file is not None else None

        self._run_coordinator_stage(
            incident_id=incident_id,
            log_id=log_id,
            workflow_id=execution_id,
            state=state,
        )

        if log_id is not None:
            state.evidence_result = self._run_guarded_stage(
                display_name="Evidence",
                guardian_agent=GuardianAgentName.EVIDENCE,
                incident_id=incident_id,
                workflow_id=execution_id,
                state=state,
                run_callable=lambda: EvidenceAgentService(self.db).collect(
                    EvidenceCollectRequest(
                        incident_id=incident_id,
                        log_file_id=log_id,
                    ),
                    workflow_id=execution_id,
                ),
            )

            if state.evidence_result is not None:
                self._run_guarded_stage(
                    display_name="Threat Intelligence",
                    guardian_agent=GuardianAgentName.THREAT_INTELLIGENCE,
                    incident_id=incident_id,
                    workflow_id=execution_id,
                    state=state,
                    run_callable=lambda: ThreatIntelligenceAgentService(self.db).enrich_from_package(
                        state.evidence_result.evidence_package,
                        workflow_id=execution_id,
                    ),
                )
                self._run_guarded_stage(
                    display_name="MITRE",
                    guardian_agent=GuardianAgentName.MITRE,
                    incident_id=incident_id,
                    workflow_id=execution_id,
                    state=state,
                    run_callable=lambda: MitreAgentService(self.db).map_from_package(
                        state.evidence_result.evidence_package,
                        workflow_id=execution_id,
                    ),
                )
        else:
            logger.warning(
                "No log file for incident_id=%s — skipping evidence-dependent stages",
                incident_id,
            )
            self._record_skipped_stage(
                state,
                "Evidence",
                "No uploaded log file linked to incident",
            )
            self._record_skipped_stage(
                state,
                "Threat Intelligence",
                "Requires evidence collection",
            )
            self._record_skipped_stage(state, "MITRE", "Requires evidence collection")

        risk_result = self._run_guarded_stage(
            display_name="Risk",
            guardian_agent=GuardianAgentName.RISK,
            incident_id=incident_id,
            workflow_id=execution_id,
            state=state,
            run_callable=lambda: RiskAgentService(self.db).assess(
                RiskAssessmentRequest(incident_id=incident_id),
                workflow_id=execution_id,
            ),
        )
        if risk_result is not None:
            state.overall_risk = str(risk_result.overall_risk)

        self._run_guarded_stage(
            display_name="Response",
            guardian_agent=GuardianAgentName.RESPONSE,
            incident_id=incident_id,
            workflow_id=execution_id,
            state=state,
            run_callable=lambda: ResponseAgentService(self.db).plan(
                ResponsePlanRequest(incident_id=incident_id),
                workflow_id=execution_id,
            ),
        )
        self._run_guarded_stage(
            display_name="Executive Report",
            guardian_agent=GuardianAgentName.EXECUTIVE_REPORT,
            incident_id=incident_id,
            workflow_id=execution_id,
            state=state,
            run_callable=lambda: ExecutiveReportAgentService(self.db).generate(
                ExecutiveReportRequest(incident_id=incident_id),
                workflow_id=execution_id,
            ),
        )

        report = self.report_repository.get_latest_by_incident_id(incident_id)
        if report is not None:
            state.report_id = report.id

        if state.guardian_validations > 0 and state.guardian_failures == 0:
            state.agents_completed.append(GUARDIAN_STAGE_NAME)
        elif state.guardian_failures > 0:
            state.agents_failed.append(GUARDIAN_STAGE_NAME)

        self._run_timeline_stage(incident_id, execution_id, state)
        self._run_evaluation_stage(state)

        duration_ms = int((time.perf_counter() - timer_start) * 1000)
        completed_at = datetime.now(UTC)

        if state.agents_failed and state.agents_completed:
            run_status = InvestigationRunStatus.PARTIAL
        elif state.agents_failed and not state.agents_completed:
            run_status = InvestigationRunStatus.FAILED
        else:
            run_status = InvestigationRunStatus.COMPLETED

        agents_executed = self._build_agents_executed(state)

        overall_result = {
            "execution_id": str(execution_id),
            "overall_risk": state.overall_risk,
            "evaluation_score": state.evaluation_score,
            "report_id": str(state.report_id) if state.report_id else None,
            "timeline_id": str(state.timeline_id) if state.timeline_id else None,
            "agents_executed": agents_executed,
        }

        run.completed_at = completed_at
        run.duration_ms = duration_ms
        run.status = run_status
        run.agents_completed = json.dumps(state.agents_completed)
        run.agents_failed = json.dumps(state.agents_failed)
        run.overall_result = json.dumps(overall_result)

        investigation = incident.investigation
        if investigation is not None:
            investigation.investigation_status = (
                InvestigationStatus.COMPLETED
                if run_status == InvestigationRunStatus.COMPLETED
                else InvestigationStatus.FAILED
                if run_status == InvestigationRunStatus.FAILED
                else InvestigationStatus.RUNNING
            )
            investigation.completed_at = completed_at
            investigation.duration_seconds = duration_ms // 1000

        self.db.commit()

        logger.info(
            "Investigation completed: execution_id=%s status=%s duration_ms=%s "
            "completed=%s failed=%s",
            execution_id,
            run_status.value,
            duration_ms,
            state.agents_completed,
            state.agents_failed,
        )

        return InvestigationPackageResponse(
            execution_id=execution_id,
            incident_id=incident_id,
            status=run_status,
            duration_ms=duration_ms,
            overall_risk=state.overall_risk,
            agents_executed=agents_executed,
            agents_completed=state.agents_completed,
            agents_failed=state.agents_failed,
            stages=state.stages,
            report_id=state.report_id,
            timeline_id=state.timeline_id,
            evaluation_score=state.evaluation_score,
            started_at=started_at,
            completed_at=completed_at,
        )

    def get_run(self, run_id: uuid.UUID) -> InvestigationPackageResponse:
        """Return a persisted investigation run as a response package."""
        run = self.run_repository.get_by_id(run_id)
        if run is None:
            raise NotFoundException("Investigation run not found")

        overall = json.loads(run.overall_result or "{}")
        agents_completed = json.loads(run.agents_completed or "[]")
        agents_failed = json.loads(run.agents_failed or "[]")

        return InvestigationPackageResponse(
            execution_id=run.id,
            incident_id=run.incident_id,
            status=run.status,
            duration_ms=run.duration_ms or 0,
            overall_risk=str(overall.get("overall_risk", "Medium")),
            agents_executed=list(overall.get("agents_executed", [])),
            agents_completed=agents_completed,
            agents_failed=agents_failed,
            report_id=uuid.UUID(overall["report_id"]) if overall.get("report_id") else None,
            timeline_id=uuid.UUID(overall["timeline_id"]) if overall.get("timeline_id") else None,
            evaluation_score=overall.get("evaluation_score"),
            started_at=run.started_at,
            completed_at=run.completed_at,
        )

    def _run_coordinator_stage(
        self,
        *,
        incident_id: uuid.UUID,
        log_id: uuid.UUID | None,
        workflow_id: uuid.UUID,
        state: _WorkflowState,
    ) -> None:
        stage_start = time.perf_counter()
        try:
            coordinator = get_coordinator()
            plan = coordinator.orchestrate(
                CoordinatorInput(incident_id=incident_id, log_id=log_id),
                self.db,
            )
            duration_ms = int((time.perf_counter() - stage_start) * 1000)
            self.execution_repository.create(
                AgentExecution(
                    incident_id=incident_id,
                    workflow_id=workflow_id,
                    agent_name=COORDINATOR_AGENT_NAME,
                    status=AgentExecutionStatus.COMPLETED,
                    started_at=datetime.now(UTC),
                    completed_at=datetime.now(UTC),
                    duration_ms=duration_ms,
                    message=f"Coordinator plan accepted with {len(plan.workflow)} stages",
                )
            )
            state.stages.append(
                InvestigationStageResult(
                    agent=COORDINATOR_AGENT_NAME,
                    success=True,
                    duration_ms=duration_ms,
                )
            )
            logger.info(
                "Coordinator stage completed: execution_id=%s duration_ms=%s",
                workflow_id,
                duration_ms,
            )
        except Exception as exc:
            duration_ms = int((time.perf_counter() - stage_start) * 1000)
            state.stages.append(
                InvestigationStageResult(
                    agent=COORDINATOR_AGENT_NAME,
                    success=False,
                    duration_ms=duration_ms,
                    error=str(exc),
                )
            )
            logger.exception("Coordinator stage failed: execution_id=%s", workflow_id)

    def _run_guarded_stage(
        self,
        *,
        display_name: str,
        guardian_agent: GuardianAgentName,
        incident_id: uuid.UUID,
        workflow_id: uuid.UUID,
        state: _WorkflowState,
        run_callable,
    ) -> Any | None:
        stage_start = time.perf_counter()
        try:
            result, validation = run_stage_with_guardian(
                self.db,
                incident_id=incident_id,
                workflow_id=workflow_id,
                agent=guardian_agent,
                run_callable=run_callable,
            )
            duration_ms = int((time.perf_counter() - stage_start) * 1000)
            fallback_used = self._detect_fallback(result, validation)
            guardian_ok = self._record_guardian_validation(validation, state)

            success = guardian_ok and validation.status != ValidationStatus.REJECTED
            state.stages.append(
                InvestigationStageResult(
                    agent=display_name,
                    success=success,
                    duration_ms=duration_ms,
                    fallback_used=fallback_used,
                    error=None if success else "Guardian validation did not approve output",
                )
            )
            if success:
                state.agents_completed.append(display_name)
                logger.info(
                    "Stage completed: execution_id=%s agent=%s duration_ms=%s fallback=%s",
                    workflow_id,
                    display_name,
                    duration_ms,
                    fallback_used,
                )
                return result

            state.agents_failed.append(display_name)
            logger.warning(
                "Stage failed guardian validation: execution_id=%s agent=%s",
                workflow_id,
                display_name,
            )
            return None
        except Exception as exc:
            duration_ms = int((time.perf_counter() - stage_start) * 1000)
            state.agents_failed.append(display_name)
            state.stages.append(
                InvestigationStageResult(
                    agent=display_name,
                    success=False,
                    duration_ms=duration_ms,
                    error=str(exc),
                )
            )
            logger.exception(
                "Stage failed: execution_id=%s agent=%s",
                workflow_id,
                display_name,
            )
            return None

    def _run_timeline_stage(
        self,
        incident_id: uuid.UUID,
        workflow_id: uuid.UUID,
        state: _WorkflowState,
    ) -> None:
        stage_start = time.perf_counter()
        try:
            timeline = self.timeline_service.get_timeline(incident_id)
            events = self.timeline_repository.list_by_incident_id(incident_id)
            state.timeline_id = events[0].id if events else workflow_id
            duration_ms = int((time.perf_counter() - stage_start) * 1000)
            state.agents_completed.append(TIMELINE_STAGE_NAME)
            state.stages.append(
                InvestigationStageResult(
                    agent=TIMELINE_STAGE_NAME,
                    success=True,
                    duration_ms=duration_ms,
                )
            )
            logger.info(
                "Timeline stage completed: execution_id=%s events=%s duration_ms=%s",
                workflow_id,
                timeline.total_events,
                duration_ms,
            )
        except Exception as exc:
            duration_ms = int((time.perf_counter() - stage_start) * 1000)
            state.agents_failed.append(TIMELINE_STAGE_NAME)
            state.stages.append(
                InvestigationStageResult(
                    agent=TIMELINE_STAGE_NAME,
                    success=False,
                    duration_ms=duration_ms,
                    error=str(exc),
                )
            )
            logger.exception("Timeline stage failed: execution_id=%s", workflow_id)

    def _run_evaluation_stage(self, state: _WorkflowState) -> None:
        stage_start = time.perf_counter()
        try:
            overview = self.evaluation_service.get_overview()
            state.evaluation_score = overview.overall_score
            duration_ms = int((time.perf_counter() - stage_start) * 1000)
            state.agents_completed.append(EVALUATION_STAGE_NAME)
            state.stages.append(
                InvestigationStageResult(
                    agent=EVALUATION_STAGE_NAME,
                    success=True,
                    duration_ms=duration_ms,
                )
            )
            logger.info(
                "Evaluation stage completed: score=%s duration_ms=%s",
                state.evaluation_score,
                duration_ms,
            )
        except Exception as exc:
            duration_ms = int((time.perf_counter() - stage_start) * 1000)
            state.agents_failed.append(EVALUATION_STAGE_NAME)
            state.stages.append(
                InvestigationStageResult(
                    agent=EVALUATION_STAGE_NAME,
                    success=False,
                    duration_ms=duration_ms,
                    error=str(exc),
                )
            )
            logger.exception("Evaluation stage failed")

    def _record_guardian_validation(
        self,
        validation: GuardianValidateResponse,
        state: _WorkflowState,
    ) -> bool:
        state.guardian_validations += 1
        if validation.status == ValidationStatus.REJECTED:
            state.guardian_failures += 1
            return False
        return True

    def _detect_fallback(self, result: Any, validation: GuardianValidateResponse) -> bool:
        if validation.fallback_triggered:
            return True
        if hasattr(result, "source"):
            source = getattr(result, "source", None)
            if source is not None and "FALLBACK" in str(source).upper():
                return True
        if hasattr(result, "model_dump"):
            payload = result.model_dump(mode="json")
            if self._contains_fallback_source(payload):
                return True
        return False

    def _contains_fallback_source(self, value: Any) -> bool:
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "source" and "FALLBACK" in str(item).upper():
                    return True
                if self._contains_fallback_source(item):
                    return True
        elif isinstance(value, list):
            for item in value:
                if self._contains_fallback_source(item):
                    return True
        return False

    def _record_skipped_stage(
        self,
        state: _WorkflowState,
        display_name: str,
        reason: str,
    ) -> None:
        state.agents_failed.append(display_name)
        state.stages.append(
            InvestigationStageResult(
                agent=display_name,
                success=False,
                duration_ms=0,
                error=reason,
            )
        )

    def _ensure_investigation_record(
        self,
        incident_id: uuid.UUID,
        started_at: datetime,
    ) -> None:
        incident = self.incident_repository.get_by_id(incident_id)
        if incident is None:
            return
        if incident.investigation is None:
            incident.investigation = Investigation(
                incident_id=incident_id,
                started_at=started_at,
                investigation_status=InvestigationStatus.RUNNING,
            )
        else:
            incident.investigation.investigation_status = InvestigationStatus.RUNNING
            incident.investigation.started_at = started_at
            incident.investigation.completed_at = None

    def _build_agents_executed(self, state: _WorkflowState) -> list[str]:
        ordered = [
            "Evidence",
            "Threat Intelligence",
            "MITRE",
            "Risk",
            "Response",
            "Executive Report",
            GUARDIAN_STAGE_NAME,
            TIMELINE_STAGE_NAME,
            EVALUATION_STAGE_NAME,
        ]
        executed = [
            name
            for name in ordered
            if name in state.agents_completed or name in state.agents_failed
        ]
        return executed
