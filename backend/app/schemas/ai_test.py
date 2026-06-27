"""Pydantic schemas for AI connectivity test."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AITestResponse(BaseModel):
    """Result of a minimal Gemini connectivity probe."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "connected": True,
                    "provider": "Google Gemini",
                    "model": "gemini-2.5-pro",
                    "response": "READY",
                    "latency_ms": 123,
                },
                {
                    "connected": False,
                    "reason": "Invalid API key",
                },
            ]
        }
    )

    connected: bool = Field(description="Whether the Gemini API accepted the request")
    provider: str | None = Field(
        default=None,
        description="AI provider name when connectivity succeeds",
    )
    model: str | None = Field(
        default=None,
        description="Configured Gemini model used for the probe",
    )
    response: str | None = Field(
        default=None,
        description="One-word model response to the connectivity prompt",
    )
    latency_ms: int | None = Field(
        default=None,
        description="Round-trip latency of the probe in milliseconds",
    )
    reason: str | None = Field(
        default=None,
        description="Failure reason when connected is false",
    )
