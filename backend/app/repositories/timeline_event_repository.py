"""Repository for timeline event persistence."""

import uuid

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.timeline_event import TimelineEvent


class TimelineEventRepository:
    """Handles database operations for investigation timeline events."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, event: TimelineEvent) -> TimelineEvent:
        """Persist a new timeline event."""
        self.db.add(event)
        self.db.flush()
        return event

    def delete_by_incident_id(self, incident_id: uuid.UUID) -> None:
        """Remove existing timeline events for an incident."""
        stmt = delete(TimelineEvent).where(TimelineEvent.incident_id == incident_id)
        self.db.execute(stmt)

    def list_by_incident_id(self, incident_id: uuid.UUID) -> list[TimelineEvent]:
        """Return timeline events for an incident ordered by sequence."""
        stmt = (
            select(TimelineEvent)
            .where(TimelineEvent.incident_id == incident_id)
            .order_by(TimelineEvent.sequence.asc())
        )
        return list(self.db.scalars(stmt).all())
