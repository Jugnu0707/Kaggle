"""Orchestration service — Coordinator plan generation and execution logging."""

from __future__ import annotations

import time
from datetime import UTC, datetime

from agents.coordinator.models import CoordinatorInput
from agents.guardian.schemas import GuardianAgentName
from sqlalchemy.orm import Session

from app.core.adk_runtime import get_coordinator
from app.core.logging import get_logger
from app.models.agent_execution import AgentExecution
from app.models.enums import AgentExecutionStatus
from app.repositories.agent_execution_repository import AgentExecutionRepository
from app.schemas.evidence_agent import EvidenceCollectRequest
from app.schemas.executive_report_agent import ExecutiveReportRequest
from app.schemas.orchestration import OrchestrateRequest, OrchestrateResponse
from app.schemas.response_agent import ResponsePlanRequest
from app.schemas.risk_agent import RiskAssessmentRequest
from app.services.evidence_agent_service import EvidenceAgentService
from app.services.executive_report_agent_service import ExecutiveReportAgentService
from app.services.mitre_agent_service import MitreAgentService
from app.services.orchestration_guardian import run_stage_with_guardian
from app.services.response_agent_service import ResponseAgentService
from app.services.risk_agent_service import RiskAgentService
from app.services.threat_intelligence_agent_service import (
    ThreatIntelligenceAgentService,
)

logger = get_logger(__name__)

COORDINATOR_AGENT_NAME = "Coordinator Agent"


class OrchestrationService:
    """Generates orchestration plans and persists Coordinator execution records."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.execution_repository = AgentExecutionRepository(db)

    def orchestrate(self, request: OrchestrateRequest) -> OrchestrateResponse:
        """Run Coordinator orchestration and record the execution."""
        coordinator = get_coordinator()
        coordinator_input = CoordinatorInput(
            incident_id=request.incident_id,
            log_id=request.log_id,
        )

        started_at = datetime.now(UTC)
        timer_start = time.perf_counter()
        plan = coordinator.orchestrate(coordinator_input, self.db)

        evidence_result = None
        mitre_result = None
        threat_intelligence_result = None
        risk_result = None
        response_result = None
        executive_report_result = None
        if plan.incident_id is not None and plan.log_id is not None:
            evidence_result, _ = run_stage_with_guardian(
                self.db,
                incident_id=plan.incident_id,
                workflow_id=plan.workflow_id,
                agent=GuardianAgentName.EVIDENCE,
                run_callable=lambda: EvidenceAgentService(self.db).collect(
                    EvidenceCollectRequest(
                        incident_id=plan.incident_id,
                        log_file_id=plan.log_id,
                    ),
                    workflow_id=plan.workflow_id,
                ),
            )
            threat_intelligence_result, _ = run_stage_with_guardian(
                self.db,
                incident_id=plan.incident_id,
                workflow_id=plan.workflow_id,
                agent=GuardianAgentName.THREAT_INTELLIGENCE,
                run_callable=lambda: ThreatIntelligenceAgentService(
                    self.db
                ).enrich_from_package(
                    evidence_result.evidence_package,
                    workflow_id=plan.workflow_id,
                ),
            )
            mitre_result, _ = run_stage_with_guardian(
                self.db,
                incident_id=plan.incident_id,
                workflow_id=plan.workflow_id,
                agent=GuardianAgentName.MITRE,
                run_callable=lambda: MitreAgentService(self.db).map_from_package(
                    evidence_result.evidence_package,
                    workflow_id=plan.workflow_id,
                ),
            )
            risk_result, _ = run_stage_with_guardian(
                self.db,
                incident_id=plan.incident_id,
                workflow_id=plan.workflow_id,
                agent=GuardianAgentName.RISK,
                run_callable=lambda: RiskAgentService(self.db).assess(
                    RiskAssessmentRequest(incident_id=plan.incident_id),
                    workflow_id=plan.workflow_id,
                ),
            )
            response_result, _ = run_stage_with_guardian(
                self.db,
                incident_id=plan.incident_id,
                workflow_id=plan.workflow_id,
                agent=GuardianAgentName.RESPONSE,
                run_callable=lambda: ResponseAgentService(self.db).plan(
                    ResponsePlanRequest(incident_id=plan.incident_id),
                    workflow_id=plan.workflow_id,
                ),
            )
            executive_report_result, _ = run_stage_with_guardian(
                self.db,
                incident_id=plan.incident_id,
                workflow_id=plan.workflow_id,
                agent=GuardianAgentName.EXECUTIVE_REPORT,
                run_callable=lambda: ExecutiveReportAgentService(self.db).generate(
                    ExecutiveReportRequest(incident_id=plan.incident_id),
                    workflow_id=plan.workflow_id,
                ),
            )

        duration_ms = int((time.perf_counter() - timer_start) * 1000)
        completed_at = datetime.now(UTC)

        message = (
            f"Orchestration plan generated with {len(plan.workflow)} workflow stages"
        )
        execution = AgentExecution(
            incident_id=plan.incident_id,
            workflow_id=plan.workflow_id,
            agent_name=COORDINATOR_AGENT_NAME,
            status=AgentExecutionStatus.ACCEPTED,
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=duration_ms,
            message=message,
        )
        self.execution_repository.create(execution)
        self.db.commit()

        logger.info(
            "Coordinator execution recorded: workflow_id=%s duration_ms=%s",
            plan.workflow_id,
            duration_ms,
        )
        return OrchestrateResponse.model_validate(
            {
                **plan.model_dump(),
                "evidence_result": evidence_result,
                "mitre_result": (
                    {
                        "status": mitre_result.status,
                        "techniques": mitre_result.techniques,
                        "message": mitre_result.message,
                    }
                    if mitre_result is not None
                    else None
                ),
                "threat_intelligence_result": (
                    threat_intelligence_result.model_dump()
                    if threat_intelligence_result is not None
                    else None
                ),
                "risk_result": (
                    risk_result.model_dump() if risk_result is not None else None
                ),
                "response_result": (
                    response_result.model_dump()
                    if response_result is not None
                    else None
                ),
                "executive_report_result": (
                    executive_report_result.model_dump()
                    if executive_report_result is not None
                    else None
                ),
            }
        )
