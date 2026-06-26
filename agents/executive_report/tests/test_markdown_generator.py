"""Unit tests for executive report Markdown generation."""

from agents.executive_report.markdown_generator import (
    generate_markdown_report,
    parse_markdown_report,
)
from agents.executive_report.schemas import ReportSections


def test_generate_markdown_includes_all_sections() -> None:
    """Markdown report includes every required executive section."""
    sections = ReportSections(
        title="Executive Incident Report",
        executive_summary="A critical incident requires leadership attention.",
        business_impact="Finance operations may experience disruption.",
        incident_timeline_summary="Activity was observed during the morning window.",
        key_findings=["Suspicious endpoint activity detected"],
        mitre_summary="Attack patterns align with ransomware techniques.",
        risk_summary="Enterprise risk is assessed as High.",
        recommended_actions=["Approve containment for affected systems"],
        lessons_learned=["Improve monitoring for early encryption signals"],
    )

    markdown = generate_markdown_report(sections)

    assert "# Executive Incident Report" in markdown
    assert "## Executive Summary" in markdown
    assert "## Business Impact" in markdown
    assert "## Incident Timeline Summary" in markdown
    assert "## Key Findings" in markdown
    assert "## MITRE Summary" in markdown
    assert "## Risk Summary" in markdown
    assert "## Recommended Actions" in markdown
    assert "## Lessons Learned" in markdown
    assert "Suspicious endpoint activity detected" in markdown


def test_parse_markdown_report_extracts_lists() -> None:
    """Markdown parser returns structured list sections."""
    sections = ReportSections(
        title="Executive Incident Report",
        executive_summary="Summary text.",
        business_impact="Impact text.",
        incident_timeline_summary="Timeline text.",
        key_findings=["Finding one", "Finding two"],
        mitre_summary="MITRE text.",
        risk_summary="Risk text.",
        recommended_actions=["Action one"],
        lessons_learned=["Lesson one"],
    )
    markdown = generate_markdown_report(sections)

    parsed = parse_markdown_report(markdown)

    assert parsed["key_findings"] == ["Finding one", "Finding two"]
    assert parsed["recommended_actions"] == ["Action one"]
    assert parsed["lessons_learned"] == ["Lesson one"]
    assert parsed["incident_timeline_summary"] == "Timeline text."
