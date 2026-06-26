"""Pydantic schemas for Evidence."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EvidenceCreate(BaseModel):
    """Schema for creating evidence."""

    incident_id: uuid.UUID
    evidence_type: str = Field(min_length=1, max_length=100)
    filename: str = Field(min_length=1, max_length=512)
    raw_data: str
    metadata: dict[str, Any] | None = None


class EvidenceUpdate(BaseModel):
    """Schema for updating evidence."""

    evidence_type: str | None = Field(default=None, min_length=1, max_length=100)
    filename: str | None = Field(default=None, min_length=1, max_length=512)
    raw_data: str | None = None
    metadata: dict[str, Any] | None = None


class EvidenceResponse(BaseModel):
    """Schema for evidence API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    incident_id: uuid.UUID
    evidence_type: str
    filename: str
    raw_data: str
    metadata: dict[str, Any] | None = Field(
        default=None,
        validation_alias="metadata_",
    )
    created_at: datetime
