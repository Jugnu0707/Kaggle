"""Pydantic schemas for the Evidence Agent API."""

from __future__ import annotations

import uuid

from agents.evidence.models import EvidenceResult
from pydantic import BaseModel, ConfigDict, Field


class EvidenceCollectRequest(BaseModel):
    """Request body for POST /api/v1/agents/evidence."""

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
    log_file_id: uuid.UUID = Field(description="Uploaded log file ID")


class EvidenceCollectResponse(EvidenceResult):
    """Evidence collection response returned by the API."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "completed",
                "evidence_summary": {
                    "file_type": "application_log",
                    "total_entries": 3,
                    "time_range": "2026-06-26T10:00:00 to 2026-06-26T11:00:00",
                    "possible_log_source": "Generic application log",
                    "data_quality_observations": [
                        "Sample entries are available for review",
                        "Timestamps detected in log entries",
                    ],
                },
                "evidence_package": {
                    "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "uploaded_file_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                    "file_size": 256,
                    "number_of_lines": 3,
                    "detected_log_type": "application_log",
                    "timestamp_range": {
                        "start": "2026-06-26T10:00:00",
                        "end": "2026-06-26T11:00:00",
                    },
                    "sample_entries": [
                        "2026-06-26T10:00:00 ERROR process started",
                        "2026-06-26T10:30:00 WARN retry attempt",
                        "2026-06-26T11:00:00 INFO process ended",
                    ],
                    "collection_timestamp": "2026-06-26T12:00:00Z",
                    "parse_notes": None,
                },
            }
        }
    )
