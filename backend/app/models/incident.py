"""Incident ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Float, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import IncidentStatus, Severity

if TYPE_CHECKING:
    from app.models.evidence import Evidence
    from app.models.investigation import Investigation
    from app.models.log_file import LogFile
    from app.models.mitre_finding import MitreFinding
    from app.models.risk_assessment import RiskAssessment
    from app.models.response_plan import ResponsePlan
    from app.models.threat_intelligence_finding import ThreatIntelligenceFinding


class Incident(Base):
    """Primary incident record."""

    __tablename__ = "incidents"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[Severity] = mapped_column(
        Enum(Severity, name="severity"),
        nullable=False,
    )
    status: Mapped[IncidentStatus] = mapped_column(
        Enum(IncidentStatus, name="incident_status"),
        nullable=False,
        default=IncidentStatus.NEW,
    )
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    evidence: Mapped[list[Evidence]] = relationship(
        back_populates="incident",
        cascade="all, delete-orphan",
    )
    investigation: Mapped[Investigation | None] = relationship(
        back_populates="incident",
        uselist=False,
        cascade="all, delete-orphan",
    )
    log_files: Mapped[list[LogFile]] = relationship(
        back_populates="incident",
    )
    mitre_findings: Mapped[list[MitreFinding]] = relationship(
        back_populates="incident",
        cascade="all, delete-orphan",
    )
    risk_assessments: Mapped[list[RiskAssessment]] = relationship(
        back_populates="incident",
        cascade="all, delete-orphan",
    )
    response_plans: Mapped[list[ResponsePlan]] = relationship(
        back_populates="incident",
        cascade="all, delete-orphan",
    )
    threat_intelligence_findings: Mapped[list[ThreatIntelligenceFinding]] = relationship(
        back_populates="incident",
        cascade="all, delete-orphan",
    )
