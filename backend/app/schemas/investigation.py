"""Pydantic schemas for Investigation."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import InvestigationRunStatus, InvestigationStatus


class InvestigationCreate(BaseModel):
    """Schema for creating an investigation."""

    incident_id: uuid.UUID
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_seconds: int | None = Field(default=None, ge=0)
    investigation_status: InvestigationStatus = InvestigationStatus.PENDING


class InvestigationUpdate(BaseModel):
    """Schema for updating an investigation."""

    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_seconds: int | None = Field(default=None, ge=0)
    investigation_status: InvestigationStatus | None = None


class InvestigationResponse(BaseModel):
    """Schema for investigation API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    incident_id: uuid.UUID
    started_at: datetime
    completed_at: datetime | None
    duration_seconds: int | None
    investigation_status: InvestigationStatus


class RunInvestigationRequest(BaseModel):
    """Request body for POST /api/v1/investigations/run."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {"incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"}
        },
    )

    incident_id: uuid.UUID = Field(description="Incident to investigate end-to-end")


class InvestigationStageResult(BaseModel):
    """Execution result for a single pipeline stage."""

    agent: str
    success: bool
    duration_ms: int
    fallback_used: bool = False
    error: str | None = None


class InvestigationPackageResponse(BaseModel):
    """Consolidated end-to-end investigation result."""

    execution_id: uuid.UUID
    incident_id: uuid.UUID
    status: InvestigationRunStatus
    duration_ms: int
    overall_risk: str
    agents_executed: list[str]
    agents_completed: list[str]
    agents_failed: list[str]
    stages: list[InvestigationStageResult] = Field(default_factory=list)
    report_id: uuid.UUID | None = None
    timeline_id: uuid.UUID | None = None
    evaluation_score: int | None = Field(default=None, ge=0, le=100)
    started_at: datetime
    completed_at: datetime | None = None
