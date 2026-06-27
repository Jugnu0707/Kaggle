"""Investigation run ORM model for end-to-end workflow tracking."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import InvestigationRunStatus

if TYPE_CHECKING:
    from app.models.incident import Incident


class InvestigationRun(Base):
    """Records a complete Coordinator-driven investigation execution."""

    __tablename__ = "investigation_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    incident_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
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
    status: Mapped[InvestigationRunStatus] = mapped_column(
        Enum(InvestigationRunStatus, name="investigation_run_status"),
        nullable=False,
        default=InvestigationRunStatus.RUNNING,
    )
    agents_completed: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    agents_failed: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    overall_result: Mapped[str | None] = mapped_column(Text, nullable=True)

    incident: Mapped[Incident] = relationship(back_populates="investigation_runs")
