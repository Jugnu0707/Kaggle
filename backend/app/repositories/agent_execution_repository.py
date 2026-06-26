"""Repository for agent execution persistence."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.agent_execution import AgentExecution


class AgentExecutionRepository:
    """Handles database operations for agent execution records."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, execution: AgentExecution) -> AgentExecution:
        """Persist a new agent execution record."""
        self.db.add(execution)
        self.db.flush()
        return execution

    def get_by_workflow_id(self, workflow_id: uuid.UUID) -> list[AgentExecution]:
        """Return all execution records for a workflow."""
        stmt = (
            select(AgentExecution)
            .where(AgentExecution.workflow_id == workflow_id)
            .order_by(AgentExecution.started_at.asc())
        )
        return list(self.db.scalars(stmt).all())
