"""Pydantic schemas for the Response Planning Agent API surface."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field

from agents.response.schemas import ResponsePlanSource


class ResponsePlanInput(BaseModel):
    """Input schema for Response Planning Agent requests."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            }
        },
    )

    incident_id: uuid.UUID = Field(description="Incident to plan response for")


class ResponsePlanResult(BaseModel):
    """Structured incident response plan returned to callers."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "source": "AI",
                    "priority": "P1",
                    "containment": ["Isolate affected host from the network"],
                    "eradication": ["Remove ransomware binaries and persistence"],
                    "recovery": ["Restore encrypted files from verified backups"],
                    "monitoring": ["Monitor for re-encryption activity"],
                    "executive_summary": "Critical ransomware response plan prioritizing containment.",
                },
                {
                    "source": "FALLBACK",
                    "priority": "P2",
                    "containment": ["Isolate endpoint"],
                    "eradication": ["Block PowerShell execution"],
                    "recovery": ["Validate endpoint integrity before reconnection"],
                    "monitoring": ["Review parent process activity"],
                    "executive_summary": "Rule-based response plan for suspicious PowerShell execution.",
                },
            ]
        }
    )

    source: ResponsePlanSource
    priority: str
    containment: list[str]
    eradication: list[str]
    recovery: list[str]
    monitoring: list[str]
    executive_summary: str
