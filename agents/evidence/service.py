"""Evidence collection, validation, normalization, and summarization."""

from __future__ import annotations

import csv
import json
import re
from datetime import UTC, datetime
from io import StringIO
from pathlib import Path

from sqlalchemy.orm import Session

from agents.evidence.models import (
    EvidenceInput,
    EvidencePackage,
    EvidenceResult,
    EvidenceSummary,
    FileMetadata,
    TimestampRange,
)
from app.core.config import get_upload_path
from app.core.exceptions import AppException, NotFoundException
from app.core.logging import get_logger
from app.models.log_file import LogFile
from app.repositories.incident_repository import IncidentRepository
from app.repositories.log_repository import LogRepository

logger = get_logger(__name__)

READABLE_EXTENSIONS = {".log", ".txt", ".json", ".csv"}
EVTX_EXTENSION = ".evtx"
MAX_SAMPLE_ENTRIES = 20
EVTX_MESSAGE = "EVTX parsing not implemented in Sprint 2."

TIMESTAMP_PATTERNS = (
    re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}"),
    re.compile(r"\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}"),
    re.compile(r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}"),
)


class EvidenceCollectionService:
    """Collects and normalizes evidence from uploaded log files."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.incident_repository = IncidentRepository(db)
        self.log_repository = LogRepository(db)

    def collect(self, request: EvidenceInput) -> EvidenceResult:
        """Validate inputs, read the log file, and produce an evidence package."""
        incident = self.incident_repository.get_by_id(request.incident_id)
        if incident is None:
            raise NotFoundException("Incident not found")

        log_file = self.log_repository.get_by_id(request.log_file_id)
        if log_file is None:
            raise NotFoundException("Log file not found")

        if log_file.incident_id is not None and log_file.incident_id != request.incident_id:
            raise AppException(
                "Log file is not linked to the specified incident",
                status_code=400,
            )

        file_path = self._resolve_file_path(log_file)
        if not file_path.exists():
            raise NotFoundException("Log file not found on disk")

        logger.info("Evidence file loaded: %s", file_path.name)

        extension = log_file.file_extension.lower()
        if extension == EVTX_EXTENSION:
            package = self._build_evtx_package(request, log_file)
        elif extension in READABLE_EXTENSIONS:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            self._validate_readable_content(content, extension)
            logger.info("Evidence validation complete: extension=%s", extension)
            package = self._build_readable_package(request, log_file, content, extension)
        else:
            raise AppException(
                f"Unsupported file extension for evidence collection: {extension}",
                status_code=400,
            )

        summary = self._build_summary(package)
        logger.info("Evidence package generated for log_file_id=%s", request.log_file_id)
        logger.info("Evidence summary generated: file_type=%s", summary.file_type)

        return EvidenceResult(
            status="completed",
            evidence_summary=summary,
            evidence_package=package,
        )

    def _resolve_file_path(self, log_file: LogFile) -> Path:
        """Resolve the on-disk path for an uploaded log file."""
        return get_upload_path() / log_file.stored_filename

    def _validate_readable_content(self, content: str, extension: str) -> None:
        """Validate readable file content without threat analysis."""
        if not content.strip():
            logger.info("Evidence validation complete: empty file detected")
            return

        if extension == ".json":
            try:
                json.loads(content)
            except json.JSONDecodeError as exc:
                raise AppException(
                    f"Invalid JSON log file: {exc.msg}",
                    status_code=400,
                ) from exc

    def _build_evtx_package(
        self,
        request: EvidenceInput,
        log_file: LogFile,
    ) -> EvidencePackage:
        """Build a non-fatal evidence package for EVTX uploads."""
        logger.info("Evidence validation complete: EVTX file accepted without parsing")
        return EvidencePackage(
            incident_id=request.incident_id,
            uploaded_file_id=request.log_file_id,
            file_metadata=self._build_file_metadata(log_file),
            file_size=log_file.file_size_bytes,
            number_of_lines=0,
            detected_log_type="evtx",
            timestamp_range=TimestampRange(),
            sample_entries=[],
            collection_timestamp=datetime.now(UTC),
            parse_notes=EVTX_MESSAGE,
        )

    def _build_readable_package(
        self,
        request: EvidenceInput,
        log_file: LogFile,
        content: str,
        extension: str,
    ) -> EvidencePackage:
        """Parse readable log content into a normalized evidence package."""
        entries, detected_log_type = self._parse_content(content, extension)
        timestamps = self._extract_timestamps(entries)
        timestamp_range = TimestampRange(
            start=timestamps[0] if timestamps else None,
            end=timestamps[-1] if timestamps else None,
        )
        sample_entries = entries[:MAX_SAMPLE_ENTRIES]

        return EvidencePackage(
            incident_id=request.incident_id,
            uploaded_file_id=request.log_file_id,
            file_metadata=self._build_file_metadata(log_file),
            file_size=log_file.file_size_bytes,
            number_of_lines=len(entries),
            detected_log_type=detected_log_type,
            timestamp_range=timestamp_range,
            sample_entries=sample_entries,
            collection_timestamp=datetime.now(UTC),
            parse_notes=None,
        )

    def _parse_content(self, content: str, extension: str) -> tuple[list[str], str]:
        """Parse file content into normalized entry strings."""
        if not content.strip():
            return [], self._detect_empty_log_type(extension)

        if extension == ".json":
            return self._parse_json(content)
        if extension == ".csv":
            return self._parse_csv(content)
        return self._parse_text_lines(content, extension)

    def _parse_json(self, content: str) -> tuple[list[str], str]:
        """Parse JSON content into string entries."""
        payload = json.loads(content)
        if isinstance(payload, list):
            entries = [json.dumps(item, ensure_ascii=True) for item in payload]
            return entries, "json"
        if isinstance(payload, dict):
            return [json.dumps(payload, ensure_ascii=True)], "json"
        return [json.dumps(payload, ensure_ascii=True)], "json"

    def _parse_csv(self, content: str) -> tuple[list[str], str]:
        """Parse CSV content into row entries."""
        reader = csv.reader(StringIO(content))
        entries = [",".join(row) for row in reader if any(cell.strip() for cell in row)]
        return entries, "csv"

    def _parse_text_lines(self, content: str, extension: str) -> tuple[list[str], str]:
        """Parse line-based text or log files."""
        entries = [line for line in content.splitlines() if line.strip()]
        detected_type = "text" if extension == ".txt" else self._detect_log_type(entries)
        return entries, detected_type

    def _detect_log_type(self, entries: list[str]) -> str:
        """Infer a generic log type from sample content."""
        sample = " ".join(entries[:10]).lower()
        if "syslog" in sample or "rsyslog" in sample:
            return "syslog"
        if "apache" in sample or "nginx" in sample or "http/" in sample:
            return "web_server_log"
        return "application_log"

    def _detect_empty_log_type(self, extension: str) -> str:
        """Return a log type label for empty readable files."""
        mapping = {
            ".json": "json",
            ".csv": "csv",
            ".txt": "text",
            ".log": "application_log",
        }
        return mapping.get(extension, "unknown")

    def _extract_timestamps(self, entries: list[str]) -> list[str]:
        """Extract sortable timestamp strings from log entries."""
        timestamps: list[str] = []
        for entry in entries:
            for pattern in TIMESTAMP_PATTERNS:
                match = pattern.search(entry)
                if match:
                    timestamps.append(match.group(0))
                    break
        return sorted(timestamps)

    def _build_file_metadata(self, log_file: LogFile) -> FileMetadata:
        """Build file metadata from the ORM model."""
        return FileMetadata(
            original_filename=log_file.original_filename,
            stored_filename=log_file.stored_filename,
            file_extension=log_file.file_extension,
            mime_type=log_file.mime_type,
            upload_status=log_file.upload_status.value,
            uploaded_at=log_file.uploaded_at,
            checksum_sha256=log_file.checksum_sha256,
        )

    def _build_summary(self, package: EvidencePackage) -> EvidenceSummary:
        """Generate a deterministic evidence summary without AI reasoning."""
        observations: list[str] = []

        if package.number_of_lines == 0:
            observations.append("File contains no parseable entries")
        else:
            observations.append("Sample entries are available for review")

        if package.timestamp_range.start and package.timestamp_range.end:
            observations.append("Timestamps detected in log entries")
        else:
            observations.append("No consistent timestamps detected")

        if package.parse_notes:
            observations.append(package.parse_notes)

        if package.file_size == 0:
            observations.append("File size is zero bytes")

        time_range = self._format_time_range(package.timestamp_range)
        return EvidenceSummary(
            file_type=package.detected_log_type,
            total_entries=package.number_of_lines,
            time_range=time_range,
            possible_log_source=self._infer_log_source(package),
            data_quality_observations=observations,
        )

    def _format_time_range(self, timestamp_range: TimestampRange) -> str:
        """Format the timestamp range for summary output."""
        if timestamp_range.start and timestamp_range.end:
            return f"{timestamp_range.start} to {timestamp_range.end}"
        if timestamp_range.start:
            return f"{timestamp_range.start} to unknown"
        return "unknown"

    def _infer_log_source(self, package: EvidencePackage) -> str:
        """Infer a generic log source label from detected log type."""
        mapping = {
            "json": "Structured JSON log export",
            "csv": "Tabular CSV log export",
            "text": "Plain text log file",
            "application_log": "Generic application log",
            "syslog": "Syslog-formatted log",
            "web_server_log": "Web server access or error log",
            "evtx": "Windows Event Trace log (EVTX)",
        }
        return mapping.get(package.detected_log_type, "Unknown log source")
