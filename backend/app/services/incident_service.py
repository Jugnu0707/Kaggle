"""Business logic for incident management."""

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models.audit_log import AuditLog
from app.models.enums import IncidentStatus, Severity
from app.models.incident import Incident
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.incident_repository import IncidentRepository
from app.schemas.incident import (
    IncidentCreate,
    IncidentDetailResponse,
    IncidentListResponse,
    IncidentResponse,
    IncidentUpdate,
)
from app.schemas.investigation import InvestigationResponse

SYSTEM_ACTOR = "system"


class IncidentService:
    """Orchestrates incident CRUD operations and audit logging."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.incident_repository = IncidentRepository(db)
        self.audit_log_repository = AuditLogRepository(db)

    def create_incident(self, payload: IncidentCreate) -> IncidentResponse:
        """Create a new incident and record an audit log entry."""
        incident = Incident(
            title=payload.title,
            description=payload.description,
            severity=payload.severity,
            status=payload.status,
            source=payload.source,
            confidence_score=payload.confidence_score,
        )
        self.incident_repository.create(incident)
        self._record_audit(
            action="CREATE",
            entity_id=incident.id,
            details={
                "title": incident.title,
                "severity": incident.severity.value,
                "status": incident.status.value,
            },
        )
        self.db.commit()
        self.db.refresh(incident)
        return IncidentResponse.model_validate(incident)

    def list_incidents(
        self,
        *,
        page: int = 1,
        page_size: int = 10,
        severity: Severity | None = None,
        status: IncidentStatus | None = None,
        search: str | None = None,
    ) -> IncidentListResponse:
        """Return a paginated list of active incidents."""
        if page < 1:
            raise AppException("Page must be greater than or equal to 1", status_code=400)
        if page_size < 1 or page_size > 100:
            raise AppException("Page size must be between 1 and 100", status_code=400)

        incidents, total = self.incident_repository.list_incidents(
            page=page,
            page_size=page_size,
            severity=severity,
            status=status,
            search=search,
        )
        items = [IncidentResponse.model_validate(incident) for incident in incidents]
        return IncidentListResponse.from_results(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_incident(self, incident_id: uuid.UUID) -> IncidentDetailResponse:
        """Return a single incident with investigation and evidence count."""
        incident = self.incident_repository.get_by_id(incident_id)
        if incident is None:
            raise AppException("Incident not found", status_code=404)

        investigation = (
            InvestigationResponse.model_validate(incident.investigation)
            if incident.investigation is not None
            else None
        )
        evidence_count = len(incident.evidence)

        return IncidentDetailResponse(
            **IncidentResponse.model_validate(incident).model_dump(),
            investigation=investigation,
            evidence_count=evidence_count,
        )

    def update_incident(
        self,
        incident_id: uuid.UUID,
        payload: IncidentUpdate,
    ) -> IncidentResponse:
        """Update mutable incident fields and record an audit log entry."""
        incident = self.incident_repository.get_by_id(incident_id)
        if incident is None:
            raise AppException("Incident not found", status_code=404)

        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            raise AppException("No fields provided for update", status_code=400)

        for field, value in update_data.items():
            setattr(incident, field, value)

        incident.updated_at = datetime.now(UTC)
        self.incident_repository.update(incident)
        self._record_audit(
            action="UPDATE",
            entity_id=incident.id,
            details=update_data,
        )
        self.db.commit()
        self.db.refresh(incident)
        return IncidentResponse.model_validate(incident)

    def delete_incident(self, incident_id: uuid.UUID) -> IncidentResponse:
        """Soft delete an incident and record an audit log entry."""
        incident = self.incident_repository.get_by_id(incident_id)
        if incident is None:
            raise AppException("Incident not found", status_code=404)

        now = datetime.now(UTC)
        incident.deleted_at = now
        incident.updated_at = now
        self.incident_repository.update(incident)
        self._record_audit(
            action="DELETE",
            entity_id=incident.id,
            details={"deleted_at": now.isoformat()},
        )
        self.db.commit()
        self.db.refresh(incident)
        return IncidentResponse.model_validate(incident)

    def _record_audit(
        self,
        *,
        action: str,
        entity_id: uuid.UUID,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Insert an audit log entry for an incident mutation."""
        audit_log = AuditLog(
            action=action,
            performed_by=SYSTEM_ACTOR,
            entity_type="incident",
            entity_id=entity_id,
            details=details,
        )
        self.audit_log_repository.create(audit_log)
