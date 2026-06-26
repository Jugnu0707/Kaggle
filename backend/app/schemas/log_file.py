"""Pydantic schemas for log file uploads."""

import uuid
from datetime import datetime
from math import ceil

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import UploadStatus


class LogFileUploadResponse(BaseModel):
    """Response returned after a successful upload."""

    file_id: uuid.UUID
    filename: str
    size: int
    upload_timestamp: datetime


class LogFileMetadataResponse(BaseModel):
    """Metadata response for a stored log file."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    incident_id: uuid.UUID | None
    original_filename: str
    stored_filename: str
    file_extension: str
    mime_type: str
    file_size_bytes: int
    upload_status: UploadStatus
    uploaded_at: datetime
    storage_path: str
    checksum_sha256: str
    deleted_at: datetime | None = None


class LogFileListResponse(BaseModel):
    """Paginated log file list response."""

    items: list[LogFileMetadataResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def from_results(
        cls,
        items: list[LogFileMetadataResponse],
        total: int,
        page: int,
        page_size: int,
    ) -> "LogFileListResponse":
        """Build a paginated list response from query results."""
        total_pages = ceil(total / page_size) if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
