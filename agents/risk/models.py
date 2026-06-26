"""Pydantic schemas for the Risk Assessment Agent API surface."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field

from agents.risk.schemas import RiskAssessmentSource


class RiskAssessmentInput(BaseModel):
    """Input schema for Risk Assessment Agent requests."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            }
        },
    )

    incident_id: uuid.UUID = Field(description="Incident to assess")


class RiskAssessmentResult(BaseModel):
    """Structured enterprise risk assessment returned to callers."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "source": "AI",
                    "overall_risk": "Critical",
                    "risk_score": 95,
                    "likelihood": "High",
                    "business_impact": "Severe operational disruption",
                    "confidence": 92,
                    "priority": "P1",
                    "summary": "Ransomware activity with high-confidence MITRE mappings.",
                    "reasoning": "Critical severity combined with T1486 and multiple IOCs.",
                },
                {
                    "source": "FALLBACK",
                    "overall_risk": "High",
                    "risk_score": 80,
                    "likelihood": "Likely",
                    "business_impact": "Elevated",
                    "confidence": 85,
                    "priority": "P2",
                    "summary": "Rule-based assessment triggered after AI unavailability.",
                    "reasoning": "High severity incident with more than three MITRE techniques.",
                },
            ]
        }
    )

    source: RiskAssessmentSource
    overall_risk: str
    risk_score: int = Field(ge=0, le=100)
    likelihood: str
    business_impact: str
    confidence: int = Field(ge=0, le=100)
    priority: str
    summary: str
    reasoning: str
