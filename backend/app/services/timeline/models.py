"""Internal models for the Investigation Timeline Engine."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TimelineEventType(str, Enum):
    """Supported investigation timeline event categories."""

    ALERT = "Alert"
    PROCESS_EXECUTION = "Process Execution"
    AUTHENTICATION = "Authentication"
    NETWORK = "Network"
    FILE = "File"
    REGISTRY = "Registry"
    POWERSHELL = "PowerShell"
    EDR = "EDR"
    FIREWALL = "Firewall"
    USER_ACTION = "User Action"
    AI_ASSESSMENT = "AI Assessment"


class RawTimelineEvent(BaseModel):
    """Unprocessed timeline event collected from incident data sources."""

    model_config = ConfigDict(extra="forbid")

    timestamp: datetime
    source: str
    event_type: TimelineEventType
    severity: str
    description: str
    evidence_reference: str | None = None
    confidence: int = Field(ge=0, le=100)
    timestamp_uncertain: bool = False


class ProcessedTimelineEvent(BaseModel):
    """Timeline event after normalization, deduplication, and sequencing."""

    model_config = ConfigDict(extra="forbid")

    sequence: int = Field(ge=1)
    timestamp: datetime
    source: str
    event_type: TimelineEventType
    severity: str
    description: str
    evidence_reference: str | None = None
    confidence: int = Field(ge=0, le=100)
    timestamp_uncertain: bool = False


class TimelineBuildResult(BaseModel):
    """Complete output from the timeline engine."""

    model_config = ConfigDict(extra="forbid")

    incident_id: uuid.UUID
    total_events: int = Field(ge=0)
    timeline: list[ProcessedTimelineEvent]
    investigation_summary: str
    duplicates_removed: int = Field(ge=0)
    processing_duration_ms: int = Field(ge=0)
