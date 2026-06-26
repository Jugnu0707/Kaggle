"""Pydantic schemas for the Threat Intelligence Agent API."""

from __future__ import annotations

import uuid
from datetime import datetime

from agents.threat_intelligence.models import ThreatIntelligenceFinding
from pydantic import BaseModel, ConfigDict, Field


class ThreatIntelligenceRequest(BaseModel):
    """Request body for POST /api/v1/agents/threat-intelligence."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            }
        },
    )

    incident_id: uuid.UUID = Field(description="Incident to enrich with threat intelligence")


class ThreatIntelligenceResponse(BaseModel):
    """Threat intelligence response returned by the API."""

    status: str
    ioc_count: int = Field(ge=0)
    findings: list[ThreatIntelligenceFinding]


class ThreatIntelligenceFindingRecordResponse(BaseModel):
    """Persisted threat intelligence finding for incident detail endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    incident_id: uuid.UUID
    indicator: str
    indicator_type: str
    reputation: str
    confidence: int
    source: str
    description: str
    analyst_notes: str
    created_at: datetime


class ThreatIntelligenceFindingListResponse(BaseModel):
    """List of persisted threat intelligence findings."""

    items: list[ThreatIntelligenceFindingRecordResponse]
    total: int
