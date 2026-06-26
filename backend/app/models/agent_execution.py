"""Agent execution ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base
from app.models.enums import AgentExecutionStatus


class AgentExecution(Base):
    """Records agent workflow execution metadata."""

    __tablename__ = "agent_executions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    incident_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("incidents.id", ondelete="SET NULL"),
        nullable=True,
    )
    workflow_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    agent_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[AgentExecutionStatus] = mapped_column(
        Enum(AgentExecutionStatus, name="agent_execution_status"),
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
