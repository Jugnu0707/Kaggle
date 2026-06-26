"""Repository for response plan persistence."""

import uuid

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.response_plan import ResponsePlan


class ResponsePlanRepository:
    """Handles database operations for response plans."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, plan: ResponsePlan) -> ResponsePlan:
        """Persist a new response plan."""
        self.db.add(plan)
        self.db.flush()
        return plan

    def delete_by_incident_id(self, incident_id: uuid.UUID) -> None:
        """Remove existing response plans for an incident."""
        stmt = delete(ResponsePlan).where(ResponsePlan.incident_id == incident_id)
        self.db.execute(stmt)

    def get_latest_by_incident_id(self, incident_id: uuid.UUID) -> ResponsePlan | None:
        """Return the most recent response plan for an incident."""
        stmt = (
            select(ResponsePlan)
            .where(ResponsePlan.incident_id == incident_id)
            .order_by(ResponsePlan.created_at.desc())
            .limit(1)
        )
        return self.db.scalar(stmt)
