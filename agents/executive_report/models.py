"""Pydantic schemas for the Executive Report Agent API surface."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field

from agents.executive_report.schemas import ExecutiveReportSource


class ExecutiveReportInput(BaseModel):
    """Input schema for Executive Report Agent requests."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            }
        },
    )

    incident_id: uuid.UUID = Field(description="Incident to generate an executive report for")


class ExecutiveReportResult(BaseModel):
    """Structured executive report returned to callers."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "source": "AI",
                    "title": "Executive Incident Report",
                    "executive_summary": "A high-severity security incident requires executive attention.",
                    "business_impact": "Potential disruption to finance operations and customer data exposure.",
                    "key_findings": [
                        "Suspicious activity detected on a critical endpoint",
                        "Attack techniques align with known ransomware patterns",
                    ],
                    "recommended_actions": [
                        "Approve containment actions for affected systems",
                        "Brief leadership on recovery timeline and customer impact",
                    ],
                    "lessons_learned": [
                        "Improve monitoring for early-stage encryption activity",
                    ],
                    "markdown": "# Executive Incident Report\n\n## Executive Summary\n...",
                }
            ]
        }
    )

    source: ExecutiveReportSource
    title: str
    executive_summary: str
    business_impact: str
    key_findings: list[str]
    recommended_actions: list[str]
    lessons_learned: list[str]
    markdown: str
