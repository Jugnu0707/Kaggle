"""Pydantic schemas for Google AI health verification."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AIHealthData(BaseModel):
    """Google AI Studio connectivity check result."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "connected": True,
                    "model": "gemini-2.5-pro",
                    "response": "Oz AI Ready",
                },
                {
                    "connected": False,
                    "error": "GOOGLE_API_KEY is not configured",
                },
            ]
        }
    )

    connected: bool
    model: str | None = Field(default=None, description="Configured Gemini model name")
    response: str | None = Field(
        default=None,
        description="Model response to the verification prompt",
    )
    error: str | None = Field(
        default=None,
        description="Error message when connectivity check fails",
    )
