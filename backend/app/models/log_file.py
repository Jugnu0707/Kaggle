"""Log file ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import UploadStatus

if TYPE_CHECKING:
    from app.models.incident import Incident


class LogFile(Base):
    """Uploaded log file metadata."""

    __tablename__ = "log_files"

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
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    file_extension: Mapped[str] = mapped_column(String(20), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    upload_status: Mapped[UploadStatus] = mapped_column(
        Enum(UploadStatus, name="upload_status"),
        nullable=False,
        default=UploadStatus.COMPLETED,
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    incident: Mapped[Incident | None] = relationship(back_populates="log_files")
