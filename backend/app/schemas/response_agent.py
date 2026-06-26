"""Pydantic schemas for the Response Planning Agent API."""

from __future__ import annotations

import uuid
from datetime import datetime

from agents.response.models import ResponsePlanResult
from pydantic import BaseModel, ConfigDict, Field


class ResponsePlanRequest(BaseModel):
    """Request body for POST /api/v1/agents/response."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            }
        },
    )

    incident_id: uuid.UUID = Field(description="Incident to plan response for")


class ResponsePlanResponse(ResponsePlanResult):
    """Response plan returned by the API."""


class ResponsePlanRecordResponse(BaseModel):
    """Persisted response plan returned by incident detail endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    incident_id: uuid.UUID
    source: str
    priority: str
    containment: list[str]
    eradication: list[str]
    recovery: list[str]
    monitoring: list[str]
    executive_summary: str
    created_at: datetime
