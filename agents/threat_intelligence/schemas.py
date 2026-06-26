"""Internal schemas for the Threat Intelligence Agent pipeline."""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

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


class ThreatIntelligenceSource(str, Enum):
    """Enrichment origin."""

    AI = "AI"
    FALLBACK = "FALLBACK"


class Reputation(str, Enum):
    """Offline reputation classification."""

    MALICIOUS = "Malicious"
    SUSPICIOUS = "Suspicious"
    UNKNOWN = "Unknown"
    SAFE = "Safe"
    INFORMATIONAL = "Informational"


class ReputationAssessment(BaseModel):
    """Offline reputation and baseline confidence for an IOC."""

    reputation: Reputation
    confidence: int = Field(ge=0, le=100)
    description: str


class AIEnrichedFinding(BaseModel):
    """Single IOC enrichment returned by Gemini."""

    indicator: str
    indicator_type: IOCType
    description: str
    analyst_notes: str
    confidence: int = Field(ge=0, le=100)


class AIThreatIntelligenceResponse(BaseModel):
    """Validated JSON response expected from Gemini."""

    findings: list[AIEnrichedFinding] = Field(min_length=0)
