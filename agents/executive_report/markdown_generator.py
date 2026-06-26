"""Markdown report generator for executive incident reports."""

from __future__ import annotations

from agents.executive_report.schemas import ReportSections


def _bullet_list(items: list[str]) -> str:
    if not items:
        return "- No items recorded.\n"
    return "".join(f"- {item}\n" for item in items)


def generate_markdown_report(sections: ReportSections) -> str:
    """Generate a complete Markdown executive incident report."""
    return (
        f"# {sections.title}\n\n"
        "> This report omits sensitive technical details and raw log data.\n\n"
        "## Executive Summary\n\n"
        f"{sections.executive_summary.strip()}\n\n"
        "## Business Impact\n\n"
        f"{sections.business_impact.strip()}\n\n"
        "## Incident Timeline Summary\n\n"
        f"{sections.incident_timeline_summary.strip()}\n\n"
        "## Key Findings\n\n"
        f"{_bullet_list(sections.key_findings)}"
        "\n"
        "## MITRE Summary\n\n"
        f"{sections.mitre_summary.strip()}\n\n"
        "## Risk Summary\n\n"
        f"{sections.risk_summary.strip()}\n\n"
        "## Recommended Actions\n\n"
        f"{_bullet_list(sections.recommended_actions)}"
        "\n"
        "## Lessons Learned\n\n"
        f"{_bullet_list(sections.lessons_learned)}"
    )


def _extract_section_body(markdown: str, heading: str) -> str:
    marker = f"## {heading}\n\n"
    start = markdown.find(marker)
    if start == -1:
        return ""
    start += len(marker)
    end = markdown.find("\n## ", start)
    if end == -1:
        return markdown[start:].strip()
    return markdown[start:end].strip()


def _extract_bullet_items(section_body: str) -> list[str]:
    items: list[str] = []
    for line in section_body.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
    return items


def parse_markdown_report(markdown: str) -> dict[str, str | list[str]]:
    """Extract structured sections from a generated executive report."""
    return {
        "key_findings": _extract_bullet_items(_extract_section_body(markdown, "Key Findings")),
        "recommended_actions": _extract_bullet_items(
            _extract_section_body(markdown, "Recommended Actions")
        ),
        "lessons_learned": _extract_bullet_items(_extract_section_body(markdown, "Lessons Learned")),
        "incident_timeline_summary": _extract_section_body(markdown, "Incident Timeline Summary"),
        "mitre_summary": _extract_section_body(markdown, "MITRE Summary"),
        "risk_summary": _extract_section_body(markdown, "Risk Summary"),
    }
