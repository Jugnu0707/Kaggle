"""Guardian Agent API service."""

from __future__ import annotations

import uuid

from agents.guardian.schemas import GuardianValidateInput, ValidationStatus
from agents.guardian.service import GuardianService
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.core.guardian_runtime import get_guardian_agent
from app.core.logging import get_logger
from app.models.guardian_audit import GuardianAudit
from app.repositories.guardian_audit_repository import GuardianAuditRepository
from app.repositories.incident_repository import IncidentRepository
from app.schemas.guardian_agent import (
    AGENT_DISPLAY_NAMES,
    GuardianAuditListResponse,
    GuardianAuditRecordResponse,
    GuardianValidateRequest,
    GuardianValidateResponse,
)

logger = get_logger(__name__)

GUARDIAN_AGENT_NAME = "Guardian Agent"


class GuardianAgentService:
    """Runs Guardian validation and persists audit records."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.audit_repository = GuardianAuditRepository(db)
        self.incident_repository = IncidentRepository(db)

    def validate(
        self,
        request: GuardianValidateRequest,
        *,
        workflow_id: uuid.UUID | None = None,
    ) -> GuardianValidateResponse:
        """Validate an agent response and persist a Guardian audit record."""
        get_guardian_agent()
        if request.incident_id is not None:
            incident = self.incident_repository.get_by_id(request.incident_id)
            if incident is None:
                raise NotFoundException("Incident not found")

        result = GuardianService().validate(
            GuardianValidateInput(
                agent=request.agent,
                response=request.response,
                incident_id=request.incident_id,
                retry_attempt=request.retry_attempt,
            )
        )
        action_taken = ", ".join(result.actions_taken) if result.actions_taken else "none"
        audit = GuardianAudit(
            incident_id=request.incident_id,
            agent_name=AGENT_DISPLAY_NAMES[request.agent],
            validation_status=result.status.value,
            issues_found=result.issues,
            action_taken=action_taken,
        )
        self.audit_repository.create(audit)
        self.db.commit()

        logger.info(
            "Guardian validation recorded: agent=%s status=%s workflow_id=%s",
            request.agent.value,
            result.status.value,
            workflow_id,
        )
        return GuardianValidateResponse(
            status=result.status,
            issues=result.issues,
            masked_response=result.masked_response,
            fallback_triggered=result.fallback_triggered,
            retry_recommended=result.retry_recommended,
        )

    def list_audits(self, incident_id: uuid.UUID) -> GuardianAuditListResponse:
        """Return Guardian audit records for an incident."""
        incident = self.incident_repository.get_by_id(incident_id)
        if incident is None:
            raise NotFoundException("Incident not found")

        records = self.audit_repository.list_by_incident_id(incident_id)
        items = [GuardianAuditRecordResponse.model_validate(record) for record in records]
        return GuardianAuditListResponse(items=items, total=len(items))
