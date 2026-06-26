"""Pydantic schemas for Incident."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import IncidentStatus, Severity


class IncidentCreate(BaseModel):
    """Schema for creating an incident."""

    title: str = Field(min_length=1, max_length=255)
    description: str
    severity: Severity
    status: IncidentStatus = IncidentStatus.NEW
    source: str = Field(min_length=1, max_length=255)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)


class IncidentUpdate(BaseModel):
    """Schema for updating an incident."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    severity: Severity | None = None
    status: IncidentStatus | None = None
    source: str | None = Field(default=None, min_length=1, max_length=255)
    confidence_score: float | None = Field(default=None, ge=0.0, le=1.0)


class IncidentResponse(BaseModel):
    """Schema for incident API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str
    severity: Severity
    status: IncidentStatus
    source: str
    confidence_score: float
    created_at: datetime
    updated_at: datetime
