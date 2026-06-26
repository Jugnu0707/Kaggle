"""Pydantic schemas for Incident."""

import uuid
from datetime import datetime
from math import ceil

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import IncidentStatus, Severity
from app.schemas.investigation import InvestigationResponse


class IncidentCreate(BaseModel):
    """Schema for creating an incident."""

    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    severity: Severity
    source: str = Field(min_length=1, max_length=255)
    status: IncidentStatus = IncidentStatus.NEW
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)


class IncidentUpdate(BaseModel):
    """Schema for updating an incident."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1)
    severity: Severity | None = None
    status: IncidentStatus | None = None


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
    deleted_at: datetime | None = None


class IncidentDetailResponse(IncidentResponse):
    """Schema for a single incident with related data."""

    investigation: InvestigationResponse | None = None
    evidence_count: int


class IncidentListResponse(BaseModel):
    """Paginated incident list response."""

    items: list[IncidentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def from_results(
        cls,
        items: list[IncidentResponse],
        total: int,
        page: int,
        page_size: int,
    ) -> "IncidentListResponse":
        """Build a paginated list response from query results."""
        total_pages = ceil(total / page_size) if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
