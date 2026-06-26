"""Pydantic schemas for Incident."""

import uuid
from datetime import datetime
from math import ceil

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import IncidentStatus, Severity
from app.schemas.investigation import InvestigationResponse

_INCIDENT_EXAMPLE = {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "title": "Suspicious outbound traffic detected",
    "description": "Multiple connections to an unknown external IP from finance workstation.",
    "severity": "High",
    "status": "Investigating",
    "source": "SIEM Alert",
    "confidence_score": 0.82,
    "created_at": "2026-06-26T10:15:00Z",
    "updated_at": "2026-06-26T10:20:00Z",
    "deleted_at": None,
}


class IncidentCreate(BaseModel):
    """Schema for creating an incident."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Suspicious outbound traffic detected",
                "description": "Multiple connections to an unknown external IP from finance workstation.",
                "severity": "High",
                "source": "SIEM Alert",
                "status": "New",
                "confidence_score": 0.82,
            }
        }
    )

    title: str = Field(min_length=1, max_length=255, description="Short incident title")
    description: str = Field(min_length=1, description="Detailed incident description")
    severity: Severity = Field(description="Incident severity level")
    source: str = Field(min_length=1, max_length=255, description="Alert or data source")
    status: IncidentStatus = Field(default=IncidentStatus.NEW, description="Workflow status")
    confidence_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0 and 1",
    )


class IncidentUpdate(BaseModel):
    """Schema for updating an incident."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Suspicious outbound traffic — under review",
                "severity": "Critical",
                "status": "Investigating",
            }
        }
    )

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1)
    severity: Severity | None = None
    status: IncidentStatus | None = None


class IncidentResponse(BaseModel):
    """Schema for incident API responses."""

    model_config = ConfigDict(from_attributes=True, json_schema_extra={"example": _INCIDENT_EXAMPLE})

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

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                **_INCIDENT_EXAMPLE,
                "investigation": None,
                "evidence_count": 3,
            }
        }
    )

    investigation: InvestigationResponse | None = None
    evidence_count: int


class IncidentListResponse(BaseModel):
    """Paginated incident list response."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [_INCIDENT_EXAMPLE],
                "total": 1,
                "page": 1,
                "page_size": 10,
                "total_pages": 1,
            }
        }
    )

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
