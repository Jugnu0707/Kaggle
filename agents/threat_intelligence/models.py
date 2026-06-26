"""Pydantic schemas for the Threat Intelligence Agent."""

from __future__ import annotations

import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from agents.evidence.models import EvidencePackage

IOCType = Literal[
    "IPv4",
    "IPv6",
    "Domain",
    "URL",
    "Email",
    "SHA1",
    "SHA256",
    "MD5",
    "Hostname",
    "WindowsUsername",
]


class ThreatIntelligenceInput(BaseModel):
    """Input schema for Threat Intelligence Agent enrichment requests."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "evidence_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
            }
        },
    )

    incident_id: uuid.UUID = Field(description="Incident associated with the evidence")
    evidence_id: uuid.UUID = Field(
        description="Evidence package identifier (uploaded log file ID)",
    )


class IOC(BaseModel):
    """Extracted indicator of compromise with rule-based classification."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "IPv4",
                "value": "192.168.10.25",
                "confidence": 100,
                "source": "PowerShell Log",
            }
        }
    )

    type: IOCType
    value: str
    confidence: int = Field(ge=0, le=100)
    source: str


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
    """Structured threat intelligence report without external enrichment."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_iocs": 12,
                "ioc_breakdown": {
                    "ipv4": 3,
                    "ipv6": 0,
                    "domain": 1,
                    "url": 2,
                    "email": 1,
                    "sha1": 0,
                    "sha256": 1,
                    "md5": 0,
                    "hostname": 2,
                    "windows_username": 2,
                },
                "suspicious_indicators": [
                    "Encoded PowerShell command pattern detected",
                    "External IPv4 address observed in log entries",
                ],
                "interesting_findings": [
                    "12 unique IOCs extracted from evidence sample",
                    "Evidence spans 2026-06-24T08:15:01Z to 2026-06-24T08:15:42Z",
                ],
                "data_quality_notes": [
                    "Sample entries are available for review",
                    "Timestamps detected in log entries",
                ],
            }
        }
    )

    total_iocs: int = Field(ge=0)
    ioc_breakdown: IOCBreakdown
    suspicious_indicators: list[str]
    interesting_findings: list[str]
    data_quality_notes: list[str]


class ThreatIntelligenceResult(BaseModel):
    """Threat Intelligence Agent output returned to callers."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "completed",
                "ioc_count": 12,
                "report": {
                    "total_iocs": 12,
                    "ioc_breakdown": {"ipv4": 3, "domain": 1, "url": 2},
                    "suspicious_indicators": ["External IPv4 address observed"],
                    "interesting_findings": ["12 unique IOCs extracted"],
                    "data_quality_notes": ["Sample entries are available for review"],
                },
                "iocs": [
                    {
                        "type": "IPv4",
                        "value": "192.168.10.25",
                        "confidence": 100,
                        "source": "PowerShell Log",
                    }
                ],
            }
        }
    )

    status: str = Field(description="Threat intelligence enrichment status")
    ioc_count: int = Field(ge=0)
    report: ThreatIntelligenceReport
    iocs: list[IOC]
    evidence_package: EvidencePackage | None = Field(
        default=None,
        description="Evidence package used for enrichment when available",
    )
