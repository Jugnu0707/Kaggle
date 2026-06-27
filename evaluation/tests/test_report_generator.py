"""Unit tests for evaluation report generation."""

from datetime import UTC, datetime

from evaluation.metrics import AgentMetrics, EvaluationSummary, ExecutionMetric
from evaluation.report_generator import (
    build_report_payload,
    generate_json_report,
    generate_markdown_report,
)


def test_build_report_payload_structure() -> None:
    """Report payload includes overall score and agent summaries."""
    summary = EvaluationSummary(
        overall_score=92,
        agents=[
            AgentMetrics(
                agent_name="Evidence Agent",
                executions=[
                    ExecutionMetric(
                        agent_name="Evidence Agent",
                        execution_time_ms=100,
                        success=True,
                        confidence=90.0,
                    )
                ],
            )
        ],
        generated_at=datetime(2026, 6, 27, 12, 0, 0, tzinfo=UTC),
    )
    payload = build_report_payload(summary)

    assert payload["overall_score"] == 92
    assert len(payload["agents"]) == 1
    assert payload["agents"][0]["agent_name"] == "Evidence Agent"


def test_generate_reports_write_files(tmp_path, monkeypatch) -> None:
    """JSON and Markdown reports are written to the results directory."""
    monkeypatch.setattr(
        "evaluation.report_generator.RESULTS_DIR",
        tmp_path,
    )
    summary = EvaluationSummary(
        overall_score=88,
        agents=[
            AgentMetrics(
                agent_name="Coordinator Agent",
                executions=[
                    ExecutionMetric(
                        agent_name="Coordinator Agent",
                        execution_time_ms=50,
                        success=True,
                    )
                ],
            )
        ],
    )

    json_path = generate_json_report(summary)
    markdown_path = generate_markdown_report(summary)

    assert json_path.exists()
    assert markdown_path.exists()
    assert "overall_score" in json_path.read_text(encoding="utf-8")
    assert "# Oz AI Evaluation Report" in markdown_path.read_text(encoding="utf-8")
