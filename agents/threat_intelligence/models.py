"""Pydantic schemas for the Threat Intelligence Agent API surface."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field

from agents.evidence.models import EvidencePackage
from agents.threat_intelligence.schemas import IOCType, ThreatIntelligenceSource


class ThreatIntelligenceInput(BaseModel):
    """Input schema for Threat Intelligence Agent enrichment requests."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            }
        },
    )

    incident_id: uuid.UUID = Field(
        description="Incident to enrich with threat intelligence"
    )


class IOC(BaseModel):
    """Extracted indicator of compromise."""

    type: IOCType
    value: str
    confidence: int = Field(ge=0, le=100)
    source: str


class ThreatIntelligenceFinding(BaseModel):
    """Enriched threat intelligence finding for a single IOC."""

    indicator: str
    indicator_type: IOCType
    reputation: str
    confidence: int = Field(ge=0, le=100)
    source: ThreatIntelligenceSource
    description: str
    analyst_notes: str


class IOCBreakdown(BaseModel):
    """Count of IOCs grouped by type."""

    ipv4: int = 0
    ipv6: int = 0
    domain: int = 0
    url: int = 0
    email: int = 0
    sha1: int = 0
    sha256: int = 0
    md5: int = 0
    hostname: int = 0
    windows_username: int = 0


class ThreatIntelligenceReport(BaseModel):
    """Structured threat intelligence summary for downstream agents."""

    total_iocs: int = Field(ge=0)
    ioc_breakdown: IOCBreakdown
    suspicious_indicators: list[str]
    interesting_findings: list[str]
    data_quality_notes: list[str]


class ThreatIntelligenceResult(BaseModel):
    """Threat Intelligence Agent output returned to callers."""

    status: str = Field(description="Threat intelligence enrichment status")
    ioc_count: int = Field(ge=0)
    findings: list[ThreatIntelligenceFinding]
    report: ThreatIntelligenceReport
    iocs: list[IOC] = Field(default_factory=list)
    evidence_package: EvidencePackage | None = Field(
        default=None,
        description="Primary evidence package when enrichment used a single package",
    )
