"""Repository for investigation run persistence."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.investigation_run import InvestigationRun


class InvestigationRunRepository:
    """Handles database operations for investigation runs."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, run: InvestigationRun) -> InvestigationRun:
        """Persist a new investigation run."""
        self.db.add(run)
        self.db.flush()
        return run

    def get_by_id(self, run_id: uuid.UUID) -> InvestigationRun | None:
        """Return an investigation run by ID."""
        stmt = select(InvestigationRun).where(InvestigationRun.id == run_id)
        return self.db.scalar(stmt)

    def list_by_incident_id(self, incident_id: uuid.UUID) -> list[InvestigationRun]:
        """Return investigation runs for an incident ordered by start time."""
        stmt = (
            select(InvestigationRun)
            .where(InvestigationRun.incident_id == incident_id)
            .order_by(InvestigationRun.started_at.desc())
        )
        return list(self.db.scalars(stmt).all())
