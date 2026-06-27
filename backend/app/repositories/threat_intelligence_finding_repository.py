"""Repository for threat intelligence finding persistence."""

import uuid

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.threat_intelligence_finding import ThreatIntelligenceFinding


class ThreatIntelligenceFindingRepository:
    """Handles database operations for threat intelligence findings."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, finding: ThreatIntelligenceFinding) -> ThreatIntelligenceFinding:
        """Persist a new threat intelligence finding."""
        self.db.add(finding)
        self.db.flush()
        return finding

    def delete_by_incident_id(self, incident_id: uuid.UUID) -> None:
        """Remove existing findings for an incident."""
        stmt = delete(ThreatIntelligenceFinding).where(
            ThreatIntelligenceFinding.incident_id == incident_id
        )
        self.db.execute(stmt)

    def list_by_incident_id(
        self, incident_id: uuid.UUID
    ) -> list[ThreatIntelligenceFinding]:
        """Return findings for an incident ordered by indicator."""
        stmt = (
            select(ThreatIntelligenceFinding)
            .where(ThreatIntelligenceFinding.incident_id == incident_id)
            .order_by(
                ThreatIntelligenceFinding.indicator_type.asc(),
                ThreatIntelligenceFinding.indicator.asc(),
            )
        )
        return list(self.db.scalars(stmt).all())
