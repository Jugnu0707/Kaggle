"""Repository for MITRE finding persistence."""

import uuid

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.mitre_finding import MitreFinding


class MitreFindingRepository:
    """Handles database operations for MITRE ATT&CK findings."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, finding: MitreFinding) -> MitreFinding:
        """Persist a new MITRE finding."""
        self.db.add(finding)
        self.db.flush()
        return finding

    def delete_by_incident_id(self, incident_id: uuid.UUID) -> None:
        """Remove existing MITRE findings for an incident."""
        stmt = delete(MitreFinding).where(MitreFinding.incident_id == incident_id)
        self.db.execute(stmt)

    def list_by_incident_id(self, incident_id: uuid.UUID) -> list[MitreFinding]:
        """Return MITRE findings for an incident ordered by technique ID."""
        stmt = (
            select(MitreFinding)
            .where(MitreFinding.incident_id == incident_id)
            .order_by(MitreFinding.technique_id.asc())
        )
        return list(self.db.scalars(stmt).all())
