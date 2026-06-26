"""Pydantic schemas for the Risk Assessment Agent API."""

from __future__ import annotations

import uuid
from datetime import datetime

from agents.risk.models import RiskAssessmentResult
from pydantic import BaseModel, ConfigDict, Field


class RiskAssessmentRequest(BaseModel):
    """Request body for POST /api/v1/agents/risk."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            }
        },
    )

    incident_id: uuid.UUID = Field(description="Incident to assess")


class RiskAssessmentResponse(RiskAssessmentResult):
    """Risk assessment response returned by the API."""


class RiskAssessmentRecordResponse(BaseModel):
    """Persisted risk assessment returned by incident detail endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    incident_id: uuid.UUID
    source: str
    overall_risk: str
    risk_score: int
    likelihood: str
    business_impact: str
    confidence: int
    priority: str
    summary: str
    reasoning: str
    created_at: datetime
