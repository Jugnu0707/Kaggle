"""Pydantic schemas for the Executive Report Agent API."""

from __future__ import annotations

import uuid
from datetime import datetime

from agents.executive_report.models import ExecutiveReportResult
from pydantic import BaseModel, ConfigDict, Field


class ExecutiveReportRequest(BaseModel):
    """Request body for POST /api/v1/agents/executive-report."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            }
        },
    )

    incident_id: uuid.UUID = Field(description="Incident to generate an executive report for")


class ExecutiveReportResponse(ExecutiveReportResult):
    """Executive report returned by the API."""


class ExecutiveReportRecordResponse(BaseModel):
    """Persisted executive report returned by incident detail endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    incident_id: uuid.UUID
    source: str
    title: str
    executive_summary: str
    business_impact: str
    key_findings: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    lessons_learned: list[str] = Field(default_factory=list)
    markdown_report: str
    created_at: datetime
