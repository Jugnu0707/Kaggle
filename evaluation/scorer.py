"""Health score calculation for Oz AI agents."""

from __future__ import annotations

from evaluation.metrics import AgentMetrics

HEALTH_WEIGHTS = {
    "availability": 0.30,
    "reliability": 0.30,
    "performance": 0.20,
    "accuracy": 0.20,
}

PERFORMANCE_TARGET_MS = 5000
PERFORMANCE_MAX_MS = 15000


def _clamp_score(value: float) -> int:
    return max(0, min(100, int(round(value))))


def score_availability(metrics: AgentMetrics) -> int:
    """Availability reflects whether the agent responds without hard failures."""
    if not metrics.executions:
        return 0
    availability_rate = metrics.success_count / len(metrics.executions)
    return _clamp_score(availability_rate * 100)


def score_reliability(metrics: AgentMetrics) -> int:
    """Reliability rewards consistent success and low retry pressure."""
    if not metrics.executions:
        return 0
    success_component = metrics.success_rate * 80
    retry_penalty = min(metrics.mean_retry_count * 20, 20)
    return _clamp_score(success_component + (20 - retry_penalty))


def score_performance(metrics: AgentMetrics) -> int:
    """Performance degrades as mean latency exceeds the target threshold."""
    if not metrics.executions:
        return 0
    mean_ms = metrics.mean_execution_time_ms
    if mean_ms <= PERFORMANCE_TARGET_MS:
        return 100
    if mean_ms >= PERFORMANCE_MAX_MS:
        return 0
    ratio = (PERFORMANCE_MAX_MS - mean_ms) / (
        PERFORMANCE_MAX_MS - PERFORMANCE_TARGET_MS
    )
    return _clamp_score(ratio * 100)


def score_accuracy(metrics: AgentMetrics) -> int:
    """Accuracy uses benchmark confidence when available, otherwise success rate."""
    if metrics.mean_confidence is not None:
        return _clamp_score(metrics.mean_confidence)
    return _clamp_score(metrics.success_rate * 100)


def calculate_health_score(metrics: AgentMetrics) -> int:
    """Calculate weighted overall health score for one agent."""
    components = {
        "availability": score_availability(metrics),
        "reliability": score_reliability(metrics),
        "performance": score_performance(metrics),
        "accuracy": score_accuracy(metrics),
    }
    weighted = sum(components[key] * HEALTH_WEIGHTS[key] for key in HEALTH_WEIGHTS)
    return _clamp_score(weighted)


def calculate_health_breakdown(metrics: AgentMetrics) -> dict[str, int]:
    """Return component scores used by dashboards and reports."""
    return {
        "availability": score_availability(metrics),
        "reliability": score_reliability(metrics),
        "performance": score_performance(metrics),
        "accuracy": score_accuracy(metrics),
        "health_score": calculate_health_score(metrics),
    }
