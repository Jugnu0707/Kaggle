"""Data access repositories."""

from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.incident_repository import IncidentRepository

__all__ = ["AuditLogRepository", "IncidentRepository"]
