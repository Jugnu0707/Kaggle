"""Evaluation report generation for Oz AI."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from evaluation.metrics import AgentMetrics, EvaluationSummary
from evaluation.scorer import calculate_health_breakdown

RESULTS_DIR = Path(__file__).resolve().parent / "results"


def _ensure_results_dir() -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    return RESULTS_DIR


def _serialize_agent(agent: AgentMetrics) -> dict[str, object]:
    breakdown = calculate_health_breakdown(agent)
    return {
        "agent_name": agent.agent_name,
        "health_score": breakdown["health_score"],
        "availability": breakdown["availability"],
        "reliability": breakdown["reliability"],
        "performance": breakdown["performance"],
        "accuracy": breakdown["accuracy"],
        "total_executions": agent.total_executions,
        "success_count": agent.success_count,
        "failure_count": agent.failure_count,
        "success_rate": round(agent.success_rate * 100, 2),
        "mean_execution_time_ms": round(agent.mean_execution_time_ms, 2),
        "ai_used_count": agent.ai_used_count,
        "fallback_used_count": agent.fallback_used_count,
        "mean_confidence": (
            round(agent.mean_confidence, 2)
            if agent.mean_confidence is not None
            else None
        ),
        "mean_retry_count": round(agent.mean_retry_count, 2),
        "mean_output_size": round(agent.mean_output_size, 2),
    }


def build_report_payload(summary: EvaluationSummary) -> dict[str, object]:
    """Build a JSON-serializable evaluation report."""
    return {
        "overall_score": summary.overall_score,
        "overall_success_rate": round(summary.overall_success_rate * 100, 2),
        "total_executions": summary.total_executions,
        "generated_at": summary.generated_at.isoformat(),
        "agents": [_serialize_agent(agent) for agent in summary.agents],
    }


def generate_json_report(summary: EvaluationSummary) -> Path:
    """Write evaluation results as JSON for later PDF export."""
    results_dir = _ensure_results_dir()
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    output_path = results_dir / f"evaluation_report_{timestamp}.json"
    payload = build_report_payload(summary)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path


def generate_markdown_report(summary: EvaluationSummary) -> Path:
    """Write evaluation results as Markdown for later PDF export."""
    results_dir = _ensure_results_dir()
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    output_path = results_dir / f"evaluation_report_{timestamp}.md"

    lines = [
        "# Oz AI Evaluation Report",
        "",
        f"**Generated:** {summary.generated_at.isoformat()}",
        f"**Overall Health Score:** {summary.overall_score}",
        f"**Overall Success Rate:** {round(summary.overall_success_rate * 100, 2)}%",
        f"**Total Executions:** {summary.total_executions}",
        "",
        "## Agent Summary",
        "",
        "| Agent | Health | Availability | Reliability | Performance | Accuracy | Success Rate | Mean Latency (ms) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for agent in summary.agents:
        breakdown = calculate_health_breakdown(agent)
        lines.append(
            f"| {agent.agent_name} | {breakdown['health_score']} | "
            f"{breakdown['availability']} | {breakdown['reliability']} | "
            f"{breakdown['performance']} | {breakdown['accuracy']} | "
            f"{round(agent.success_rate * 100, 2)}% | "
            f"{round(agent.mean_execution_time_ms, 2)} |"
        )

    lines.extend(
        [
            "",
            "## AI vs Fallback Usage",
            "",
            "| Agent | AI Used | Fallback Used |",
            "|---|---:|---:|",
        ]
    )
    for agent in summary.agents:
        lines.append(
            f"| {agent.agent_name} | {agent.ai_used_count} | {agent.fallback_used_count} |"
        )

    lines.extend(
        [
            "",
            "## Health Score Weights",
            "",
            "- Availability: 30%",
            "- Reliability: 30%",
            "- Performance: 20%",
            "- Accuracy: 20%",
            "",
        ]
    )
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path
