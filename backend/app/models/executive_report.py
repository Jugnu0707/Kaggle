"""Executive report ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.incident import Incident


class ExecutiveReport(Base):
    """Persisted executive incident report for an incident."""

    __tablename__ = "executive_reports"

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
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    executive_summary: Mapped[str] = mapped_column(Text, nullable=False)
    business_impact: Mapped[str] = mapped_column(Text, nullable=False)
    markdown_report: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    incident: Mapped[Incident] = relationship(back_populates="executive_reports")
