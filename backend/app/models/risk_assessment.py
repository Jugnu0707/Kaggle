"""Risk assessment ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.incident import Incident


class RiskAssessment(Base):
    """Persisted enterprise risk assessment for an incident."""

    __tablename__ = "risk_assessments"

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
    overall_risk: Mapped[str] = mapped_column(String(32), nullable=False)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False)
    likelihood: Mapped[str] = mapped_column(String(128), nullable=False)
    business_impact: Mapped[str] = mapped_column(String(255), nullable=False)
    confidence: Mapped[int] = mapped_column(Integer, nullable=False)
    priority: Mapped[str] = mapped_column(String(8), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    incident: Mapped[Incident] = relationship(back_populates="risk_assessments")
