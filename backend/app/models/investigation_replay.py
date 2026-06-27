"""Investigation replay step ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import ReplayStepStatus

if TYPE_CHECKING:
    from app.models.investigation_run import InvestigationRun


class InvestigationReplay(Base):
    """Persisted step record for investigation replay and explainability."""

    __tablename__ = "investigation_replays"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    investigation_run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("investigation_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    agent_name: Mapped[str] = mapped_column(String(128), nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    input_summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    output_summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    ai_used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    fallback_used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[ReplayStepStatus] = mapped_column(
        Enum(ReplayStepStatus, name="replay_step_status"),
        nullable=False,
    )

    investigation_run: Mapped[InvestigationRun] = relationship(
        back_populates="replay_steps"
    )
