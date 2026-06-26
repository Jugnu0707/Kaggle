"""Repository for Guardian audit persistence."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.guardian_audit import GuardianAudit


class GuardianAuditRepository:
    """Handles database operations for Guardian audit records."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, audit: GuardianAudit) -> GuardianAudit:
        """Persist a new Guardian audit record."""
        self.db.add(audit)
        self.db.flush()
        return audit

    def list_by_incident_id(self, incident_id: uuid.UUID) -> list[GuardianAudit]:
        """Return Guardian audit records for an incident ordered by newest first."""
        stmt = (
            select(GuardianAudit)
            .where(GuardianAudit.incident_id == incident_id)
            .order_by(GuardianAudit.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())
