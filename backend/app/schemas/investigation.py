"""Pydantic schemas for Investigation."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import InvestigationStatus


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
