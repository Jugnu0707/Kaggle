"""Pydantic schemas for the Executive Report Agent."""

from __future__ import annotations

import uuid
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from agents.evidence.models import EvidenceSummary
from agents.mitre.models import MappedTechnique
from agents.threat_intelligence.models import ThreatIntelligenceReport


class ExecutiveReportSource(str, Enum):
    """Executive report origin."""

    AI = "AI"
    FALLBACK = "FALLBACK"


class IncidentContext(BaseModel):
    """Incident metadata used for executive reporting."""

    id: uuid.UUID
    title: str
    description: str
    severity: str
    status: str
    source: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    created_at: str | None = None


class RiskAssessmentContext(BaseModel):
    """Risk assessment inputs consumed by executive reporting."""

    overall_risk: str
    risk_score: int = Field(ge=0, le=100)
    priority: str
    likelihood: str
    business_impact: str
    summary: str
    reasoning: str


class ResponsePlanContext(BaseModel):
    """Response plan inputs consumed by executive reporting."""

    priority: str
    containment: list[str] = Field(default_factory=list)
    eradication: list[str] = Field(default_factory=list)
    recovery: list[str] = Field(default_factory=list)
    monitoring: list[str] = Field(default_factory=list)
    executive_summary: str


class ExecutiveReportContext(BaseModel):
    """Inputs gathered for AI and fallback executive reporting."""

    incident: IncidentContext
    evidence_summaries: list[EvidenceSummary] = Field(default_factory=list)
    mitre_techniques: list[MappedTechnique] = Field(default_factory=list)
    threat_intelligence_reports: list[ThreatIntelligenceReport] = Field(
        default_factory=list
    )
    risk_assessment: RiskAssessmentContext | None = None
    response_plan: ResponsePlanContext | None = None
    total_iocs: int = 0
    suspicious_indicator_count: int = 0


class AIExecutiveReportResponse(BaseModel):
    """Validated JSON response expected from Gemini."""

    title: str = "Executive Incident Report"
    executive_summary: str
    business_impact: str
    incident_timeline_summary: str
    key_findings: list[str] = Field(min_length=1)
    mitre_summary: str
    risk_summary: str
    recommended_actions: list[str] = Field(min_length=1)
    lessons_learned: list[str] = Field(min_length=1)


class ReportSections(BaseModel):
    """Structured report sections used for Markdown generation."""

    model_config = ConfigDict(extra="forbid")

    title: str
    executive_summary: str
    business_impact: str
    incident_timeline_summary: str
    key_findings: list[str]
    mitre_summary: str
    risk_summary: str
    recommended_actions: list[str]
    lessons_learned: list[str]
