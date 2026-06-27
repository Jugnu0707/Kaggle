"""Coordinator orchestration logic — plan generation without agent execution."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from agents.coordinator.models import CoordinatorInput, OrchestrationPlan
from app.ai.runtime import get_ai_runtime
from app.core.exceptions import NotFoundException
from app.core.logging import get_logger
from app.repositories.log_repository import LogRepository

logger = get_logger(__name__)

DEFAULT_WORKFLOW: list[str] = [
    "Evidence Agent",
    "Threat Intelligence Agent",
    "MITRE Mapping Agent",
    "Risk Assessment Agent",
    "Response Planning Agent",
    "Executive Report Agent",
    "Guardian Agent",
]


@dataclass(frozen=True)
class ValidatedOrchestrationRequest:
    """Normalized identifiers after validation."""

    incident_id: uuid.UUID | None
    log_id: uuid.UUID | None


class CoordinatorOrchestrator:
    """Validates requests and generates deterministic orchestration plans."""

    def validate_request(
        self, request: CoordinatorInput, db: Session
    ) -> ValidatedOrchestrationRequest:
        """Validate that referenced incidents or logs exist via MCP and repositories."""
        runtime = get_ai_runtime()
        log_repo = LogRepository(db)

        incident_id = request.incident_id
        log_id = request.log_id

        if incident_id is not None:
            incident_result = runtime.invoke_tool(
                "incident_details",
                {"incident_id": str(incident_id)},
                db,
            )
            if not incident_result.success:
                raise NotFoundException("Incident not found")

        log_file = None
        if log_id is not None:
            log_file = log_repo.get_by_id(log_id)
            if log_file is None:
                raise NotFoundException("Log file not found")

        resolved_incident_id = incident_id
        if resolved_incident_id is None and log_file is not None:
            resolved_incident_id = log_file.incident_id

        if incident_id is not None and log_file is not None and log_file.incident_id is not None:
            if log_file.incident_id != incident_id:
                raise NotFoundException("Log file is not linked to the specified incident")

        logger.info(
            "Orchestration validation passed: incident_id=%s log_id=%s",
            resolved_incident_id,
            log_id,
        )
        return ValidatedOrchestrationRequest(
            incident_id=resolved_incident_id,
            log_id=log_id,
        )

    def route_agents(
        self,
        validated: ValidatedOrchestrationRequest,
    ) -> list[str]:
        """Return the placeholder agent execution order (no execution)."""
        _ = validated
        workflow = list(DEFAULT_WORKFLOW)
        logger.info("Generated workflow: %s", workflow)
        return workflow

    def build_plan(
        self,
        request: CoordinatorInput,
        db: Session,
    ) -> tuple[OrchestrationPlan, int]:
        """Validate the request and build an orchestration plan through the AI runtime."""
        runtime = get_ai_runtime()
        session = runtime.create_agent_session("Coordinator Agent")
        started = time.perf_counter()
        logger.info(
            "Orchestration request received: incident_id=%s log_id=%s tools=%d",
            request.incident_id,
            request.log_id,
            len(runtime.discover_tools()),
        )

        try:
            validated = self.validate_request(request, db)
            workflow = self.route_agents(validated)
            workflow_id = uuid.uuid4()

            plan = OrchestrationPlan(
                incident_id=validated.incident_id,
                log_id=validated.log_id,
                workflow_id=workflow_id,
                status="accepted",
                workflow=workflow,
            )
        finally:
            runtime.close_agent_session(session.session_id)

        duration_ms = int((time.perf_counter() - started) * 1000)
        logger.info("Orchestration completed in %dms", duration_ms)
        return plan, duration_ms
