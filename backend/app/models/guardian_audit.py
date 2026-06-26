"""Guardian audit ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.incident import Incident


class GuardianAudit(Base):
    """Persisted Guardian validation audit record."""

    __tablename__ = "guardian_audits"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    incident_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=True,
    )
    agent_name: Mapped[str] = mapped_column(String(64), nullable=False)
    validation_status: Mapped[str] = mapped_column(String(16), nullable=False)
    issues_found: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    action_taken: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    incident: Mapped[Incident | None] = relationship(back_populates="guardian_audits")
