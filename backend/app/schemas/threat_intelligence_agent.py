"""Pydantic schemas for the Threat Intelligence Agent API."""

from __future__ import annotations

import uuid

from agents.threat_intelligence.models import IOC, ThreatIntelligenceReport
from pydantic import BaseModel, ConfigDict, Field


class ThreatIntelligenceRequest(BaseModel):
    """Request body for POST /api/v1/agents/threat-intelligence."""

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


class ThreatIntelligenceResponse(BaseModel):
    """Threat intelligence response returned by the API."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "completed",
                "ioc_count": 4,
                "report": {
                    "total_iocs": 4,
                    "ioc_breakdown": {
                        "ipv4": 2,
                        "url": 1,
                        "sha256": 1,
                        "windows_username": 1,
                    },
                    "suspicious_indicators": [
                        "External IPv4 address observed in evidence entries"
                    ],
                    "interesting_findings": [
                        "4 unique IOCs extracted from evidence sample"
                    ],
                    "data_quality_notes": [
                        "Sample entries were used for IOC extraction"
                    ],
                },
                "iocs": [
                    {
                        "type": "IPv4",
                        "value": "185.234.72.19",
                        "confidence": 90,
                        "source": "Application Log",
                    }
                ],
            }
        }
    )

    status: str
    ioc_count: int = Field(ge=0)
    report: ThreatIntelligenceReport
    iocs: list[IOC]
