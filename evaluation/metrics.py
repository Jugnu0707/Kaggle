"""Metric collection and aggregation for Oz AI agent evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ExecutionMetric:
    """Single agent execution measurement."""

    agent_name: str
    execution_time_ms: int
    success: bool
    ai_used: bool = False
    fallback_used: bool = False
    retry_count: int = 0
    confidence: float | None = None
    output_size: int = 0

    @property
    def failure(self) -> bool:
        return not self.success


@dataclass
class AgentMetrics:
    """Aggregated metrics for one agent."""

    agent_name: str
    executions: list[ExecutionMetric] = field(default_factory=list)

    @property
    def total_executions(self) -> int:
        return len(self.executions)

    @property
    def success_count(self) -> int:
        return sum(1 for item in self.executions if item.success)

    @property
    def failure_count(self) -> int:
        return sum(1 for item in self.executions if not item.success)

    @property
    def success_rate(self) -> float:
        if not self.executions:
            return 0.0
        return self.success_count / len(self.executions)

    @property
    def mean_execution_time_ms(self) -> float:
        if not self.executions:
            return 0.0
        return sum(item.execution_time_ms for item in self.executions) / len(
            self.executions
        )

    @property
    def ai_used_count(self) -> int:
        return sum(1 for item in self.executions if item.ai_used)

    @property
    def fallback_used_count(self) -> int:
        return sum(1 for item in self.executions if item.fallback_used)

    @property
    def mean_confidence(self) -> float | None:
        values = [
            item.confidence for item in self.executions if item.confidence is not None
        ]
        if not values:
            return None
        return sum(values) / len(values)

    @property
    def mean_retry_count(self) -> float:
        if not self.executions:
            return 0.0
        return sum(item.retry_count for item in self.executions) / len(self.executions)

    @property
    def mean_output_size(self) -> float:
        if not self.executions:
            return 0.0
        return sum(item.output_size for item in self.executions) / len(self.executions)


@dataclass
class EvaluationSummary:
    """Platform-wide evaluation rollup."""

    overall_score: int
    agents: list[AgentMetrics]
    generated_at: datetime = field(default_factory=lambda: datetime.now())

    @property
    def total_executions(self) -> int:
        return sum(agent.total_executions for agent in self.agents)

    @property
    def overall_success_rate(self) -> float:
        total = self.total_executions
        if total == 0:
            return 0.0
        successes = sum(agent.success_count for agent in self.agents)
        return successes / total
