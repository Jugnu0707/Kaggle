"""Investigation ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import InvestigationStatus

if TYPE_CHECKING:
    from app.models.incident import Incident


class Investigation(Base):
    """Investigation record linked one-to-one with an incident."""

    __tablename__ = "investigations"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    incident_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
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
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    investigation_status: Mapped[InvestigationStatus] = mapped_column(
        Enum(InvestigationStatus, name="investigation_status"),
        nullable=False,
        default=InvestigationStatus.PENDING,
    )

    incident: Mapped["Incident"] = relationship(back_populates="investigation")
