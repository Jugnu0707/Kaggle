"""Repository for audit log persistence."""

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditLogRepository:
    """Handles database operations for audit log entries."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, audit_log: AuditLog) -> AuditLog:
        """Persist a new audit log entry."""
        self.db.add(audit_log)
        self.db.flush()
        return audit_log
