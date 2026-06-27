"""Oz AI evaluation engine — orchestrates benchmarks, scoring, and reporting."""

from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from evaluation.benchmark import run_all_benchmarks
from evaluation.metrics import AgentMetrics, EvaluationSummary, ExecutionMetric
from evaluation.report_generator import generate_json_report, generate_markdown_report
from evaluation.scorer import calculate_health_score


class EvaluationEngine:
    """Runs offline benchmarks and aggregates agent health metrics."""

    def run_benchmarks(self, db: Session) -> list[ExecutionMetric]:
        """Execute all agent benchmarks without requiring AI availability."""
        return run_all_benchmarks(db)

    def aggregate_metrics(self, metrics: list[ExecutionMetric]) -> list[AgentMetrics]:
        """Group execution metrics by agent name."""
        grouped: dict[str, list[ExecutionMetric]] = defaultdict(list)
        for metric in metrics:
            grouped[metric.agent_name].append(metric)
        return [
            AgentMetrics(agent_name=agent_name, executions=executions)
            for agent_name, executions in sorted(grouped.items())
        ]

    def build_summary(self, metrics: list[ExecutionMetric]) -> EvaluationSummary:
        """Calculate overall and per-agent health scores."""
        agents = self.aggregate_metrics(metrics)
        if not agents:
            return EvaluationSummary(
                overall_score=0, agents=[], generated_at=datetime.now(UTC)
            )

        agent_scores = [calculate_health_score(agent) for agent in agents]
        overall_score = int(round(sum(agent_scores) / len(agent_scores)))
        return EvaluationSummary(
            overall_score=overall_score,
            agents=agents,
            generated_at=datetime.now(UTC),
        )

    def evaluate(self, db: Session) -> EvaluationSummary:
        """Run benchmarks, generate reports, and return the evaluation summary."""
        metrics = self.run_benchmarks(db)
        summary = self.build_summary(metrics)
        generate_json_report(summary)
        generate_markdown_report(summary)
        return summary
