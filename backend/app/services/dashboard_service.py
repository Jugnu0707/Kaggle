"""Business logic for dashboard metrics."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.enums import Severity, UploadStatus
from app.models.incident import Incident
from app.models.log_file import LogFile
from app.schemas.dashboard import DashboardStats


class DashboardService:
    """Provides aggregate metrics for the dashboard."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_stats(self) -> DashboardStats:
        """Return dashboard summary statistics."""
        active_incidents = Incident.deleted_at.is_(None)
        active_logs = LogFile.deleted_at.is_(None)

        total_incidents = self.db.scalar(
            select(func.count()).select_from(Incident).where(active_incidents)
        ) or 0
        critical_incidents = self.db.scalar(
            select(func.count())
            .select_from(Incident)
            .where(active_incidents, Incident.severity == Severity.CRITICAL)
        ) or 0
        high_incidents = self.db.scalar(
            select(func.count())
            .select_from(Incident)
            .where(active_incidents, Incident.severity == Severity.HIGH)
        ) or 0
        uploaded_logs = self.db.scalar(
            select(func.count())
            .select_from(LogFile)
            .where(active_logs, LogFile.upload_status != UploadStatus.DELETED)
        ) or 0

        return DashboardStats(
            total_incidents=total_incidents,
            critical_incidents=critical_incidents,
            high_incidents=high_incidents,
            uploaded_logs=uploaded_logs,
        )
