"""Pydantic schemas for the Guardian Agent API."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from agents.guardian.schemas import GuardianAgentName, ValidationStatus
from pydantic import BaseModel, ConfigDict, Field

AGENT_DISPLAY_NAMES: dict[GuardianAgentName, str] = {
    GuardianAgentName.EVIDENCE: "Evidence Agent",
    GuardianAgentName.THREAT_INTELLIGENCE: "Threat Intelligence Agent",
    GuardianAgentName.MITRE: "MITRE Mapping Agent",
    GuardianAgentName.RISK: "Risk Assessment Agent",
    GuardianAgentName.RESPONSE: "Response Planning Agent",
    GuardianAgentName.EXECUTIVE_REPORT: "Executive Report Agent",
}


class GuardianValidateRequest(BaseModel):
    """Request body for POST /api/v1/agents/guardian/validate."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "agent": "risk",
                "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "response": {
                    "source": "AI",
                    "overall_risk": "High",
                    "risk_score": 80,
                    "likelihood": "Likely",
                    "business_impact": "Significant disruption",
                    "confidence": 85,
                    "priority": "P2",
                    "summary": "High-risk incident",
                    "reasoning": "Multiple indicators observed",
                },
            }
        },
    )

    agent: GuardianAgentName
    response: dict[str, Any]
    incident_id: uuid.UUID | None = None
    retry_attempt: int = Field(default=0, ge=0, le=1)


class GuardianValidateResponse(BaseModel):
    """Guardian validation response returned by the API."""

    status: ValidationStatus
    issues: list[str] = Field(default_factory=list)
    masked_response: dict[str, Any] | None = None
    fallback_triggered: bool = False
    retry_recommended: bool = False


class GuardianAuditRecordResponse(BaseModel):
    """Persisted Guardian audit record."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    incident_id: uuid.UUID | None
    agent_name: str
    validation_status: str
    issues_found: list[str]
    action_taken: str
    created_at: datetime


class GuardianAuditListResponse(BaseModel):
    """List of Guardian audit records for an incident."""

    items: list[GuardianAuditRecordResponse]
    total: int
