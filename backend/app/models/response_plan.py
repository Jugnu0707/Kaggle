"""Response plan ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.incident import Incident


class ResponsePlan(Base):
    """Persisted incident response plan for an incident."""

    __tablename__ = "response_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    incident_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
    )
    source: Mapped[str] = mapped_column(String(16), nullable=False)
    priority: Mapped[str] = mapped_column(String(8), nullable=False)
    containment: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    eradication: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    recovery: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    monitoring: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    executive_summary: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    incident: Mapped[Incident] = relationship(back_populates="response_plans")
