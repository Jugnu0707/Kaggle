"""Pydantic schemas for the Guardian Agent."""

from __future__ import annotations

import uuid
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class GuardianAgentName(str, Enum):
    """Supported agent identifiers for Guardian validation."""

    EVIDENCE = "evidence"
    THREAT_INTELLIGENCE = "threat_intelligence"
    MITRE = "mitre"
    RISK = "risk"
    RESPONSE = "response"
    EXECUTIVE_REPORT = "executive_report"


class ValidationStatus(str, Enum):
    """Guardian validation outcome."""

    APPROVED = "approved"
    WARNING = "warning"
    REJECTED = "rejected"


class GuardianValidateInput(BaseModel):
    """Input schema for Guardian validation requests."""

    model_config = ConfigDict(extra="forbid")

    agent: GuardianAgentName
    response: dict[str, Any]
    incident_id: uuid.UUID | None = None
    retry_attempt: int = Field(default=0, ge=0, le=1)


class GuardianValidationResult(BaseModel):
    """Structured Guardian validation outcome."""

    status: ValidationStatus
    issues: list[str] = Field(default_factory=list)
    masked_response: dict[str, Any] | None = None
    fallback_triggered: bool = False
    retry_recommended: bool = False
    actions_taken: list[str] = Field(default_factory=list)
