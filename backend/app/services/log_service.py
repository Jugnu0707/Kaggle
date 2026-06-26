"""Business logic for log file uploads and metadata management."""

import hashlib
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_upload_path, settings
from app.core.exceptions import AppException
from app.models.audit_log import AuditLog
from app.models.enums import UploadStatus
from app.models.log_file import LogFile
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.log_repository import LogRepository
from app.schemas.log_file import (
    LogFileListResponse,
    LogFileMetadataResponse,
    LogFileUploadResponse,
)
from app.utils.file_validation import (
    build_stored_filename,
    sanitize_original_filename,
    validate_extension,
    validate_mime_type,
)

SYSTEM_ACTOR = "system"


class LogService:
    """Orchestrates secure log upload and metadata operations."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.log_repository = LogRepository(db)
        self.audit_log_repository = AuditLogRepository(db)
        self.upload_dir = get_upload_path()

    async def upload_log_file(
        self,
        upload_file: UploadFile,
        incident_id: uuid.UUID | None = None,
    ) -> LogFileUploadResponse:
        """Validate, store, and persist metadata for an uploaded log file."""
        original_filename = sanitize_original_filename(upload_file.filename)
        extension = validate_extension(original_filename)
        mime_type = validate_mime_type(extension, upload_file.content_type)

        file_id = uuid.uuid4()
        stored_filename = build_stored_filename(str(file_id), extension)
        destination = (self.upload_dir / stored_filename).resolve()
        upload_root = self.upload_dir.resolve()
        if destination.parent != upload_root:
            raise AppException("Invalid storage path", status_code=400)

        content = await self._read_upload_with_limit(upload_file)
        checksum = hashlib.sha256(content).hexdigest()
        destination.write_bytes(content)

        relative_storage_path = str(Path(settings.upload_dir) / stored_filename)
        log_file = LogFile(
            id=file_id,
            incident_id=incident_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_extension=extension,
            mime_type=mime_type,
            file_size_bytes=len(content),
            upload_status=UploadStatus.COMPLETED,
            storage_path=relative_storage_path,
            checksum_sha256=checksum,
        )
        self.log_repository.create(log_file)
        self._record_audit(
            action="UPLOAD",
            entity_id=log_file.id,
            details={
                "original_filename": original_filename,
                "stored_filename": stored_filename,
                "file_size_bytes": log_file.file_size_bytes,
                "checksum_sha256": checksum,
            },
        )
        if incident_id is not None:
            self._record_audit(
                action="METADATA_UPDATE",
                entity_id=log_file.id,
                details={"incident_id": str(incident_id)},
            )
        self.db.commit()
        self.db.refresh(log_file)

        return LogFileUploadResponse(
            file_id=log_file.id,
            filename=log_file.original_filename,
            size=log_file.file_size_bytes,
            upload_timestamp=log_file.uploaded_at,
        )

    def list_log_files(self, *, page: int = 1, page_size: int = 10) -> LogFileListResponse:
        """Return a paginated list of uploaded log files."""
        if page < 1:
            raise AppException("Page must be greater than or equal to 1", status_code=400)
        if page_size < 1 or page_size > 100:
            raise AppException("Page size must be between 1 and 100", status_code=400)

        log_files, total = self.log_repository.list_log_files(page=page, page_size=page_size)
        items = [LogFileMetadataResponse.model_validate(log_file) for log_file in log_files]
        return LogFileListResponse.from_results(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_log_file(self, log_id: uuid.UUID) -> LogFileMetadataResponse:
        """Return metadata for a single log file."""
        log_file = self.log_repository.get_by_id(log_id)
        if log_file is None:
            raise AppException("Log file not found", status_code=404)
        return LogFileMetadataResponse.model_validate(log_file)

    def delete_log_file(self, log_id: uuid.UUID) -> LogFileMetadataResponse:
        """Soft delete a log file without removing the physical file."""
        log_file = self.log_repository.get_by_id(log_id)
        if log_file is None:
            raise AppException("Log file not found", status_code=404)

        now = datetime.now(UTC)
        log_file.deleted_at = now
        log_file.upload_status = UploadStatus.DELETED
        self.log_repository.update(log_file)
        self._record_audit(
            action="DELETE",
            entity_id=log_file.id,
            details={
                "original_filename": log_file.original_filename,
                "deleted_at": now.isoformat(),
            },
        )
        self.db.commit()
        self.db.refresh(log_file)
        return LogFileMetadataResponse.model_validate(log_file)

    async def _read_upload_with_limit(self, upload_file: UploadFile) -> bytes:
        """Read upload content and enforce the configured maximum size."""
        chunks: list[bytes] = []
        total_size = 0
        max_size = settings.max_upload_size_bytes

        while True:
            chunk = await upload_file.read(1024 * 1024)
            if not chunk:
                break
            total_size += len(chunk)
            if total_size > max_size:
                raise AppException(
                    f"File exceeds maximum allowed size of {max_size} bytes",
                    status_code=400,
                )
            chunks.append(chunk)

        if total_size == 0:
            raise AppException("Uploaded file is empty", status_code=400)

        return b"".join(chunks)

    def _record_audit(
        self,
        *,
        action: str,
        entity_id: uuid.UUID,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Insert an audit log entry for a log file mutation."""
        audit_log = AuditLog(
            action=action,
            performed_by=SYSTEM_ACTOR,
            entity_type="log_file",
            entity_id=entity_id,
            details=details,
        )
        self.audit_log_repository.create(audit_log)
