"""Repository for risk assessment persistence."""

import uuid

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.risk_assessment import RiskAssessment


class RiskAssessmentRepository:
    """Handles database operations for risk assessments."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, assessment: RiskAssessment) -> RiskAssessment:
        """Persist a new risk assessment."""
        self.db.add(assessment)
        self.db.flush()
        return assessment

    def delete_by_incident_id(self, incident_id: uuid.UUID) -> None:
        """Remove existing risk assessments for an incident."""
        stmt = delete(RiskAssessment).where(RiskAssessment.incident_id == incident_id)
        self.db.execute(stmt)

    def get_latest_by_incident_id(self, incident_id: uuid.UUID) -> RiskAssessment | None:
        """Return the most recent risk assessment for an incident."""
        stmt = (
            select(RiskAssessment)
            .where(RiskAssessment.incident_id == incident_id)
            .order_by(RiskAssessment.created_at.desc())
            .limit(1)
        )
        return self.db.scalar(stmt)
