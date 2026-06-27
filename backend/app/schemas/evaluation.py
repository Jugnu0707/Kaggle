"""Pydantic schemas for evaluation API responses."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AgentEvaluationSummary(BaseModel):
    """Per-agent rollup for the evaluation dashboard."""

    model_config = ConfigDict(from_attributes=True)

    agent_name: str
    health_score: int = Field(ge=0, le=100)
    availability: int = Field(ge=0, le=100)
    reliability: int = Field(ge=0, le=100)
    performance: int = Field(ge=0, le=100)
    accuracy: int = Field(ge=0, le=100)
    total_executions: int = Field(ge=0)
    success_count: int = Field(ge=0)
    failure_count: int = Field(ge=0)
    success_rate: float = Field(ge=0, le=100)
    mean_execution_time_ms: float = Field(ge=0)
    ai_used_count: int = Field(ge=0)
    fallback_used_count: int = Field(ge=0)
    mean_confidence: float | None = None
    mean_retry_count: float = Field(ge=0, default=0)
    mean_output_size: float = Field(ge=0, default=0)


class EvaluationOverview(BaseModel):
    """Platform-wide evaluation summary."""

    overall_score: int = Field(ge=0, le=100)
    agents: list[AgentEvaluationSummary]
    total_executions: int = Field(ge=0, default=0)
    overall_success_rate: float = Field(ge=0, le=100, default=0)
    generated_at: datetime | None = None
    tool_execution_count: int = Field(ge=0, default=0)
    tool_failure_count: int = Field(ge=0, default=0)
    mean_adk_session_duration_ms: float = Field(ge=0, default=0)
    mean_investigation_duration_ms: float = Field(ge=0, default=0)
    mean_agent_execution_time_ms: float = Field(ge=0, default=0)
    mean_mcp_latency_ms: float = Field(ge=0, default=0)


class AgentEvaluationDetail(AgentEvaluationSummary):
    """Detailed per-agent evaluation statistics."""

    recent_executions: list[dict[str, object]] = Field(default_factory=list)
