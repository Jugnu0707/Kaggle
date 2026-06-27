"""Unit tests for evaluation metrics and scoring."""

from evaluation.metrics import AgentMetrics, ExecutionMetric
from evaluation.scorer import calculate_health_breakdown, calculate_health_score


def test_execution_metric_failure_property() -> None:
    """Failed executions expose the failure property."""
    metric = ExecutionMetric(
        agent_name="Evidence Agent",
        execution_time_ms=100,
        success=False,
    )
    assert metric.failure is True


def test_agent_metrics_aggregation() -> None:
    """AgentMetrics aggregates success, latency, and usage counters."""
    metrics = AgentMetrics(
        agent_name="MITRE Mapping Agent",
        executions=[
            ExecutionMetric(
                agent_name="MITRE Mapping Agent",
                execution_time_ms=120,
                success=True,
                fallback_used=True,
                confidence=95.0,
                output_size=256,
            ),
            ExecutionMetric(
                agent_name="MITRE Mapping Agent",
                execution_time_ms=180,
                success=True,
                ai_used=True,
                confidence=90.0,
                output_size=300,
            ),
        ],
    )

    assert metrics.total_executions == 2
    assert metrics.success_count == 2
    assert metrics.failure_count == 0
    assert metrics.success_rate == 1.0
    assert metrics.mean_execution_time_ms == 150.0
    assert metrics.ai_used_count == 1
    assert metrics.fallback_used_count == 1
    assert metrics.mean_confidence == 92.5


def test_health_score_weighted_calculation() -> None:
    """Health score applies the approved weight distribution."""
    metrics = AgentMetrics(
        agent_name="Guardian Agent",
        executions=[
            ExecutionMetric(
                agent_name="Guardian Agent",
                execution_time_ms=250,
                success=True,
                confidence=95.0,
            )
        ],
    )
    breakdown = calculate_health_breakdown(metrics)

    assert breakdown["availability"] == 100
    assert breakdown["reliability"] == 100
    assert breakdown["performance"] == 100
    assert breakdown["accuracy"] == 95
    assert calculate_health_score(metrics) == 99
