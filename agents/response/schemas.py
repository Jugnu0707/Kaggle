"""Pydantic schemas for the Response Planning Agent."""

from __future__ import annotations

import uuid
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

from agents.evidence.models import EvidenceSummary
from agents.mitre.models import MappedTechnique
from agents.threat_intelligence.models import ThreatIntelligenceReport


class ResponsePlanSource(str, Enum):
    """Response plan origin."""

    AI = "AI"
    FALLBACK = "FALLBACK"


class IncidentContext(BaseModel):
    """Incident metadata used for response planning."""

    id: uuid.UUID
    title: str
    description: str
    severity: str
    status: str
    source: str
    confidence_score: float = Field(ge=0.0, le=1.0)


class RiskAssessmentContext(BaseModel):
    """Risk assessment inputs consumed by response planning."""

    overall_risk: str
    risk_score: int = Field(ge=0, le=100)
    priority: str
    summary: str
    reasoning: str


class ResponsePlanningContext(BaseModel):
    """Inputs gathered for AI and fallback response planning."""

    incident: IncidentContext
    evidence_summaries: list[EvidenceSummary] = Field(default_factory=list)
    mitre_techniques: list[MappedTechnique] = Field(default_factory=list)
    threat_intelligence_reports: list[ThreatIntelligenceReport] = Field(
        default_factory=list
    )
    risk_assessment: RiskAssessmentContext | None = None
    total_iocs: int = 0
    suspicious_indicators: list[str] = Field(default_factory=list)


class AIResponsePlanResponse(BaseModel):
    """Validated JSON response expected from Gemini."""

    priority: Literal["P1", "P2", "P3", "P4"]
    containment: list[str] = Field(min_length=1)
    eradication: list[str] = Field(min_length=1)
    recovery: list[str] = Field(min_length=1)
    monitoring: list[str] = Field(min_length=1)
    executive_summary: str
