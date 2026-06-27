"""Repository for investigation replay persistence."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.investigation_replay import InvestigationReplay


class InvestigationReplayRepository:
    """Handles database operations for investigation replay steps."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, step: InvestigationReplay) -> InvestigationReplay:
        """Persist a replay step."""
        self.db.add(step)
        self.db.flush()
        return step

    def create_many(
        self, steps: list[InvestigationReplay]
    ) -> list[InvestigationReplay]:
        """Persist multiple replay steps."""
        for step in steps:
            self.db.add(step)
        self.db.flush()
        return steps

    def list_by_run_id(self, run_id: uuid.UUID) -> list[InvestigationReplay]:
        """Return replay steps ordered by step number."""
        stmt = (
            select(InvestigationReplay)
            .where(InvestigationReplay.investigation_run_id == run_id)
            .order_by(InvestigationReplay.step_number)
        )
        return list(self.db.scalars(stmt).all())

    def delete_by_run_id(self, run_id: uuid.UUID) -> None:
        """Remove all replay steps for a run."""
        steps = self.list_by_run_id(run_id)
        for step in steps:
            self.db.delete(step)
