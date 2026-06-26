"""Repository for incident persistence and queries."""

import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.enums import IncidentStatus, Severity
from app.models.evidence import Evidence
from app.models.incident import Incident


class IncidentRepository:
    """Handles database operations for incidents."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, incident: Incident) -> Incident:
        """Persist a new incident."""
        self.db.add(incident)
        self.db.flush()
        return incident

    def get_by_id(self, incident_id: uuid.UUID) -> Incident | None:
        """Return an active incident by ID, excluding soft-deleted records."""
        stmt = (
            select(Incident)
            .options(
                selectinload(Incident.investigation),
                selectinload(Incident.evidence),
            )
            .where(Incident.id == incident_id, Incident.deleted_at.is_(None))
        )
        return self.db.scalar(stmt)

    def get_by_id_including_deleted(self, incident_id: uuid.UUID) -> Incident | None:
        """Return an incident by ID, including soft-deleted records."""
        stmt = select(Incident).where(Incident.id == incident_id)
        return self.db.scalar(stmt)

    def list_incidents(
        self,
        *,
        page: int,
        page_size: int,
        severity: Severity | None = None,
        status: IncidentStatus | None = None,
        search: str | None = None,
    ) -> tuple[list[Incident], int]:
        """Return paginated active incidents sorted by created_at descending."""
        filters = [Incident.deleted_at.is_(None)]

        if severity is not None:
            filters.append(Incident.severity == severity)
        if status is not None:
            filters.append(Incident.status == status)
        if search:
            search_term = f"%{search.lower()}%"
            filters.append(
                or_(
                    func.lower(Incident.title).like(search_term),
                    func.lower(Incident.description).like(search_term),
                )
            )

        count_stmt = select(func.count()).select_from(Incident).where(*filters)
        total = self.db.scalar(count_stmt) or 0

        offset = (page - 1) * page_size
        stmt = (
            select(Incident)
            .where(*filters)
            .order_by(Incident.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        incidents = list(self.db.scalars(stmt).all())
        return incidents, total

    def update(self, incident: Incident) -> Incident:
        """Persist incident updates."""
        self.db.add(incident)
        self.db.flush()
        return incident

    def count_evidence(self, incident_id: uuid.UUID) -> int:
        """Return the number of evidence records for an incident."""
        stmt = select(func.count()).select_from(Evidence).where(Evidence.incident_id == incident_id)
        return self.db.scalar(stmt) or 0
