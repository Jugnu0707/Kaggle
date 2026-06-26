"""Threat intelligence finding ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.incident import Incident


class ThreatIntelligenceFinding(Base):
    """Persisted threat intelligence enrichment for a single IOC."""

    __tablename__ = "threat_intelligence_findings"

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
    indicator: Mapped[str] = mapped_column(String(512), nullable=False)
    indicator_type: Mapped[str] = mapped_column(String(32), nullable=False)
    reputation: Mapped[str] = mapped_column(String(32), nullable=False)
    confidence: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[str] = mapped_column(String(16), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    analyst_notes: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    incident: Mapped[Incident] = relationship(back_populates="threat_intelligence_findings")
