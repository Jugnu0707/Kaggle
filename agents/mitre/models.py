"""Pydantic schemas for the MITRE Mapping Agent."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field

from agents.evidence.models import EvidencePackage


class MitreMappingInput(BaseModel):
    """Input schema for MITRE mapping requests."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            }
        },
    )

    incident_id: uuid.UUID = Field(description="Incident to map against MITRE ATT&CK")


class MappedTechnique(BaseModel):
    """Single ATT&CK technique mapped from observed evidence."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "technique_id": "T1059.001",
                "technique_name": "PowerShell",
                "tactic": "Execution",
                "confidence": 96,
                "matched_evidence": ["powershell.exe", "-encodedcommand"],
            }
        }
    )

    technique_id: str
    technique_name: str
    tactic: str
    confidence: int = Field(ge=0, le=100)
    matched_evidence: list[str]


class MitreMappingResult(BaseModel):
    """MITRE Mapping Agent output returned to callers."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "completed",
                "techniques": [
                    {
                        "technique_id": "T1059.001",
                        "technique_name": "PowerShell",
                        "tactic": "Execution",
                        "confidence": 96,
                        "matched_evidence": ["powershell.exe"],
                    }
                ],
                "message": None,
            }
        }
    )

    status: str
    techniques: list[MappedTechnique]
    message: str | None = Field(
        default=None,
        description="Informational message such as when no mapping is found",
    )
    evidence_packages: list[EvidencePackage] = Field(default_factory=list)
