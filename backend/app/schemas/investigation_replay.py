"""Pydantic schemas for investigation replay and explainability."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.enums import InvestigationRunStatus


class ReplayStepExplainability(BaseModel):
    """Detailed explainability metadata for a single replay step."""

    decision: str
    reason: str
    confidence: int | None = Field(default=None, ge=0, le=100)
    evidence_used: list[str] = Field(default_factory=list)
    inputs: dict[str, object] = Field(default_factory=dict)
    outputs: dict[str, object] = Field(default_factory=dict)
    execution_time_ms: int = Field(ge=0)
    source: Literal["AI", "FALLBACK", "SYSTEM"]


class InvestigationReplayStepResponse(BaseModel):
    """Single step in an investigation replay."""

    step: int
    agent: str
    duration_ms: int
    source: Literal["AI", "FALLBACK", "SYSTEM"]
    summary: str
    confidence: int | None = Field(default=None, ge=0, le=100)
    status: str
    fallback_used: bool = False
    started_at: datetime | None = None
    completed_at: datetime | None = None
    explainability: ReplayStepExplainability | None = None


class InvestigationReplayResponse(BaseModel):
    """Full investigation replay payload."""

    run_id: uuid.UUID
    incident_id: uuid.UUID
    status: InvestigationRunStatus
    duration_ms: int
    steps: list[InvestigationReplayStepResponse] = Field(default_factory=list)


class DecisionChainItem(BaseModel):
    """One decision in the investigation decision chain."""

    step: int
    agent: str
    decision: str
    reason: str
    confidence: int | None = Field(default=None, ge=0, le=100)
    source: Literal["AI", "FALLBACK", "SYSTEM"]


class ConfidenceDistribution(BaseModel):
    """Distribution of confidence scores across replay steps."""

    min_confidence: int | None = None
    max_confidence: int | None = None
    average_confidence: float | None = None
    steps_with_confidence: int = 0


class InvestigationExplainResponse(BaseModel):
    """Explainability summary for an investigation run."""

    run_id: uuid.UUID
    incident_id: uuid.UUID
    status: InvestigationRunStatus
    overall_investigation_summary: str
    overall_risk: str
    ai_usage_count: int = Field(ge=0)
    fallback_usage_count: int = Field(ge=0)
    system_steps_count: int = Field(ge=0)
    decision_chain: list[DecisionChainItem] = Field(default_factory=list)
    agent_reasoning: list[ReplayStepExplainability] = Field(default_factory=list)
    confidence_distribution: ConfidenceDistribution
    evaluation_score: int | None = Field(default=None, ge=0, le=100)
    duration_ms: int = Field(ge=0)


class InvestigationReplayExportResponse(BaseModel):
    """Exported replay document."""

    format: Literal["json", "markdown"]
    content: str
    run_id: uuid.UUID
