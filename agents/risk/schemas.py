"""Pydantic schemas for the Risk Assessment Agent."""

from __future__ import annotations

import uuid
from enum import Enum
from typing import Literal

from agents.evidence.models import EvidenceSummary
from agents.mitre.models import MappedTechnique
from agents.threat_intelligence.models import ThreatIntelligenceReport
from pydantic import BaseModel, ConfigDict, Field


class RiskAssessmentSource(str, Enum):
    """Assessment origin."""

    AI = "AI"
    FALLBACK = "FALLBACK"


class RiskLevel(str, Enum):
    """Enterprise risk level."""

    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class IncidentContext(BaseModel):
    """Incident metadata used for risk assessment."""

    id: uuid.UUID
    title: str
    description: str
    severity: str
    status: str
    source: str
    confidence_score: float = Field(ge=0.0, le=1.0)


class RiskAssessmentContext(BaseModel):
    """Inputs gathered for AI and fallback risk assessment."""

    incident: IncidentContext
    evidence_summaries: list[EvidenceSummary] = Field(default_factory=list)
    mitre_techniques: list[MappedTechnique] = Field(default_factory=list)
    threat_intelligence_reports: list[ThreatIntelligenceReport] = Field(default_factory=list)
    total_iocs: int = 0
    suspicious_indicators: list[str] = Field(default_factory=list)


class AIRiskAssessmentResponse(BaseModel):
    """Validated JSON response expected from Gemini."""

    overall_risk: RiskLevel
    risk_score: int = Field(ge=0, le=100)
    likelihood: str
    business_impact: str
    confidence: int = Field(ge=0, le=100)
    priority: Literal["P1", "P2", "P3", "P4"]
    summary: str
    reasoning: str

    @classmethod
    def priority_for_risk(cls, overall_risk: RiskLevel) -> str:
        """Map risk level to enterprise priority."""
        mapping = {
            RiskLevel.CRITICAL: "P1",
            RiskLevel.HIGH: "P2",
            RiskLevel.MEDIUM: "P3",
            RiskLevel.LOW: "P4",
        }
        return mapping[overall_risk]
