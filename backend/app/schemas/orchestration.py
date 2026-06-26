"""Pydantic schemas for agent orchestration API."""

from __future__ import annotations

import uuid

from agents.coordinator.models import OrchestrationPlan
from agents.evidence.models import EvidenceResult
from agents.mitre.models import MitreMappingResult
from agents.risk.models import RiskAssessmentResult
from agents.response.models import ResponsePlanResult
from agents.threat_intelligence.models import ThreatIntelligenceResult
from pydantic import BaseModel, ConfigDict, Field, model_validator


class OrchestrateRequest(BaseModel):
    """Request body for POST /api/v1/agents/orchestrate."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            }
        },
    )

    incident_id: uuid.UUID | None = Field(
        default=None,
        description="Incident to orchestrate",
    )
    log_id: uuid.UUID | None = Field(
        default=None,
        description="Uploaded log file to orchestrate",
    )

    @model_validator(mode="after")
    def require_incident_or_log(self) -> OrchestrateRequest:
        """Ensure at least one identifier is provided."""
        if self.incident_id is None and self.log_id is None:
            raise ValueError("Either incident_id or log_id is required")
        return self


class OrchestrateResponse(OrchestrationPlan):
    """Orchestration plan returned by the Coordinator Agent."""

    evidence_result: EvidenceResult | None = Field(
        default=None,
        description="Evidence Agent output when a log file is orchestrated",
    )
    mitre_result: MitreMappingResult | None = Field(
        default=None,
        description="MITRE Mapping Agent output when evidence is orchestrated",
    )
    threat_intelligence_result: ThreatIntelligenceResult | None = Field(
        default=None,
        description="Threat Intelligence Agent output when evidence is orchestrated",
    )
    risk_result: RiskAssessmentResult | None = Field(
        default=None,
        description="Risk Assessment Agent output when upstream agents are orchestrated",
    )
    response_result: ResponsePlanResult | None = Field(
        default=None,
        description="Response Planning Agent output when upstream agents are orchestrated",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "log_id": None,
                "workflow_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
                "status": "accepted",
                "workflow": [
                    "Evidence Agent",
                    "Threat Intelligence Agent",
                    "MITRE Mapping Agent",
                    "Risk Assessment Agent",
                    "Response Planning Agent",
                    "Executive Report Agent",
                    "Guardian Agent",
                ],
            }
        }
    )
