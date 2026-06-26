"""Repository for executive report persistence."""

import uuid

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.executive_report import ExecutiveReport


class ExecutiveReportRepository:
    """Handles database operations for executive reports."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, report: ExecutiveReport) -> ExecutiveReport:
        """Persist a new executive report."""
        self.db.add(report)
        self.db.flush()
        return report

    def delete_by_incident_id(self, incident_id: uuid.UUID) -> None:
        """Remove existing executive reports for an incident."""
        stmt = delete(ExecutiveReport).where(ExecutiveReport.incident_id == incident_id)
        self.db.execute(stmt)

    def get_latest_by_incident_id(self, incident_id: uuid.UUID) -> ExecutiveReport | None:
        """Return the most recent executive report for an incident."""
        stmt = (
            select(ExecutiveReport)
            .where(ExecutiveReport.incident_id == incident_id)
            .order_by(ExecutiveReport.created_at.desc())
            .limit(1)
        )
        return self.db.scalar(stmt)
