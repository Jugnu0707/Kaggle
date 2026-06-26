"""Pydantic schemas for the Evidence Agent."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EvidenceInput(BaseModel):
    """Input schema for Evidence Agent collection requests."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "log_file_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
            }
        },
    )

    incident_id: uuid.UUID = Field(description="Incident associated with the evidence")
    log_file_id: uuid.UUID = Field(description="Uploaded log file to collect evidence from")


class FileMetadata(BaseModel):
    """Metadata for an uploaded log file."""

    original_filename: str
    stored_filename: str
    file_extension: str
    mime_type: str
    upload_status: str
    uploaded_at: datetime
    checksum_sha256: str


class TimestampRange(BaseModel):
    """Detected timestamp range within the log file."""

    start: str | None = Field(default=None, description="Earliest detected timestamp")
    end: str | None = Field(default=None, description="Latest detected timestamp")


class EvidencePackage(BaseModel):
    """Normalized evidence package produced by the Evidence Agent."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "uploaded_file_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                "file_metadata": {
                    "original_filename": "events.log",
                    "stored_filename": "7c9e6679-7425-40de-944b-e07fc1f90ae7.log",
                    "file_extension": ".log",
                    "mime_type": "text/plain",
                    "upload_status": "Completed",
                    "uploaded_at": "2026-06-26T11:00:00Z",
                    "checksum_sha256": "abc123",
                },
                "file_size": 2048,
                "number_of_lines": 42,
                "detected_log_type": "application_log",
                "timestamp_range": {"start": "2026-06-26T10:00:00", "end": "2026-06-26T11:00:00"},
                "sample_entries": ["2026-06-26 ERROR suspicious process started"],
                "collection_timestamp": "2026-06-26T12:00:00Z",
                "parse_notes": None,
            }
        }
    )

    incident_id: uuid.UUID
    uploaded_file_id: uuid.UUID
    file_metadata: FileMetadata
    file_size: int = Field(ge=0)
    number_of_lines: int = Field(ge=0)
    detected_log_type: str
    timestamp_range: TimestampRange
    sample_entries: list[str] = Field(max_length=20)
    collection_timestamp: datetime
    parse_notes: str | None = Field(
        default=None,
        description="Non-fatal parsing notes such as unsupported binary formats",
    )


class EvidenceSummary(BaseModel):
    """Concise deterministic summary of collected evidence."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "file_type": "application_log",
                "total_entries": 42,
                "time_range": "2026-06-26T10:00:00 to 2026-06-26T11:00:00",
                "possible_log_source": "Generic application log",
                "data_quality_observations": [
                    "Timestamps detected in log entries",
                    "All sample lines are non-empty",
                ],
            }
        }
    )

    file_type: str
    total_entries: int = Field(ge=0)
    time_range: str
    possible_log_source: str
    data_quality_observations: list[str]


class EvidenceResult(BaseModel):
    """Evidence Agent output returned to callers."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "completed",
                "evidence_summary": {
                    "file_type": "application_log",
                    "total_entries": 42,
                    "time_range": "2026-06-26T10:00:00 to 2026-06-26T11:00:00",
                    "possible_log_source": "Generic application log",
                    "data_quality_observations": ["Timestamps detected in log entries"],
                },
                "evidence_package": {
                    "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "uploaded_file_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                    "file_metadata": {
                        "original_filename": "events.log",
                        "stored_filename": "events.log",
                        "file_extension": ".log",
                        "mime_type": "text/plain",
                        "upload_status": "Completed",
                        "uploaded_at": "2026-06-26T11:00:00Z",
                        "checksum_sha256": "abc123",
                    },
                    "file_size": 2048,
                    "number_of_lines": 42,
                    "detected_log_type": "application_log",
                    "timestamp_range": {
                        "start": "2026-06-26T10:00:00",
                        "end": "2026-06-26T11:00:00",
                    },
                    "sample_entries": ["2026-06-26 ERROR suspicious process started"],
                    "collection_timestamp": "2026-06-26T12:00:00Z",
                    "parse_notes": None,
                },
            }
        }
    )

    status: str = Field(description="Evidence collection status")
    evidence_summary: EvidenceSummary
    evidence_package: EvidencePackage
