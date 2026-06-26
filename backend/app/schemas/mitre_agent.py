"""Pydantic schemas for the MITRE Mapping Agent API."""

from __future__ import annotations

import uuid
from datetime import datetime

from agents.mitre.models import MappedTechnique
from pydantic import BaseModel, ConfigDict, Field


class MitreMappingRequest(BaseModel):
    """Request body for POST /api/v1/agents/mitre."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            }
        },
    )

    incident_id: uuid.UUID = Field(description="Incident to map against MITRE ATT&CK")


class MitreMappingResponse(BaseModel):
    """MITRE mapping response returned by the API."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "completed",
                "techniques": [
                    {
                        "technique_id": "T1059.001",
                        "technique_name": "PowerShell",
                        "tactic": "Execution",
                        "confidence": 96,
                        "matched_evidence": ["powershell.exe"],
                    }
                ],
                "message": None,
            }
        }
    )

    status: str
    techniques: list[MappedTechnique]
    message: str | None = None


class MitreFindingResponse(BaseModel):
    """Persisted MITRE finding returned by incident detail endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    incident_id: uuid.UUID
    technique_id: str
    technique_name: str
    tactic: str
    confidence: int
    evidence: list[str]
    created_at: datetime


class MitreFindingListResponse(BaseModel):
    """List of MITRE findings for an incident."""

    items: list[MitreFindingResponse]
    total: int
