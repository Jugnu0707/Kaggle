"""API schemas for investigation timeline responses."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TimelineEventResponse(BaseModel):
    """Single timeline event returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID | None = None
    sequence: int = Field(ge=1)
    timestamp: datetime
    source: str
    event_type: str
    severity: str
    description: str
    evidence_reference: str | None = None
    confidence: int = Field(ge=0, le=100)
    timestamp_uncertain: bool = False


class TimelineResponse(BaseModel):
    """Investigation timeline payload."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "total_events": 24,
                "timeline": [],
                "investigation_summary": "Investigation timeline contains 24 events.",
            }
        }
    )

    incident_id: uuid.UUID
    total_events: int = Field(ge=0)
    timeline: list[TimelineEventResponse]
    investigation_summary: str


def timeline_to_markdown(response: TimelineResponse) -> str:
    """Render a timeline response as Markdown for export."""
    lines = [
        "# Investigation Timeline",
        "",
        f"**Incident ID:** `{response.incident_id}`",
        f"**Total Events:** {response.total_events}",
        "",
        "## Investigation Summary",
        "",
        response.investigation_summary,
        "",
        "## Events",
        "",
    ]

    if not response.timeline:
        lines.append("No timeline events available.")
        return "\n".join(lines) + "\n"

    for event in response.timeline:
        lines.extend(
            [
                f"### {event.sequence}. {event.timestamp.isoformat()} — {event.event_type}",
                "",
                f"- **Severity:** {event.severity}",
                f"- **Source:** {event.source}",
                f"- **Confidence:** {event.confidence}%",
                f"- **Description:** {event.description}",
            ]
        )
        if event.evidence_reference:
            lines.append(f"- **Evidence Reference:** {event.evidence_reference}")
        if event.timestamp_uncertain:
            lines.append("- **Timestamp:** uncertain (estimated)")
        lines.append("")

    return "\n".join(lines).strip() + "\n"
