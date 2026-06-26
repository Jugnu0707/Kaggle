"""Pydantic schemas for AuditLog."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AuditLogCreate(BaseModel):
    """Schema for creating an audit log entry."""

    action: str = Field(min_length=1, max_length=255)
    performed_by: str = Field(min_length=1, max_length=255)
    entity_type: str = Field(min_length=1, max_length=100)
    entity_id: uuid.UUID
    details: dict[str, Any] | None = None


class AuditLogUpdate(BaseModel):
    """Schema for updating an audit log entry."""

    action: str | None = Field(default=None, min_length=1, max_length=255)
    performed_by: str | None = Field(default=None, min_length=1, max_length=255)
    entity_type: str | None = Field(default=None, min_length=1, max_length=100)
    entity_id: uuid.UUID | None = None
    details: dict[str, Any] | None = None


class AuditLogResponse(BaseModel):
    """Schema for audit log API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    action: str
    performed_by: str
    entity_type: str
    entity_id: uuid.UUID
    timestamp: datetime
    details: dict[str, Any] | None = None
