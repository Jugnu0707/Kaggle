"""Pydantic schemas for log file uploads."""

import uuid
from datetime import datetime
from math import ceil

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import UploadStatus

_LOG_METADATA_EXAMPLE = {
    "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "original_filename": "firewall.log",
    "stored_filename": "7c9e6679-7425-40de-944b-e07fc1f90ae7.log",
    "file_extension": ".log",
    "mime_type": "text/plain",
    "file_size_bytes": 2048,
    "upload_status": "Completed",
    "uploaded_at": "2026-06-26T11:00:00Z",
    "storage_path": "storage/uploads/7c9e6679-7425-40de-944b-e07fc1f90ae7.log",
    "checksum_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "deleted_at": None,
}


class LogFileUploadResponse(BaseModel):
    """Response returned after a successful upload."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "file_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                "filename": "firewall.log",
                "size": 2048,
                "upload_timestamp": "2026-06-26T11:00:00Z",
            }
        }
    )

    file_id: uuid.UUID = Field(description="Unique identifier for the uploaded file")
    filename: str = Field(description="Original filename provided by the client")
    size: int = Field(ge=0, description="File size in bytes")
    upload_timestamp: datetime = Field(
        description="UTC timestamp when the upload completed"
    )


class LogFileMetadataResponse(BaseModel):
    """Metadata response for a stored log file."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"example": _LOG_METADATA_EXAMPLE},
    )

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

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [_LOG_METADATA_EXAMPLE],
                "total": 1,
                "page": 1,
                "page_size": 10,
                "total_pages": 1,
            }
        }
    )

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
