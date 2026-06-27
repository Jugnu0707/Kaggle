"""Confidence validation for AI-generated Guardian outputs."""

from __future__ import annotations

from typing import Any


def extract_confidence_values(response: dict[str, Any]) -> list[int]:
    """Collect confidence scores from a response payload."""
    values: list[int] = []

    def _walk(node: Any) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "confidence" and isinstance(value, int | float):
                    values.append(int(value))
                else:
                    _walk(value)
        elif isinstance(node, list):
            for item in node:
                _walk(item)

    _walk(response)
    return values


def validate_confidence(
    response: dict[str, Any],
    *,
    min_confidence: int,
    source: str | None = None,
) -> list[str]:
    """Return issues when AI confidence is below the configured threshold."""
    if source and source.upper() != "AI":
        return []

    if "source" in response and str(response["source"]).upper() != "AI":
        return []

    confidence_values: list[int] = []
    findings = response.get("findings")
    if isinstance(findings, list):
        for finding in findings:
            if not isinstance(finding, dict):
                continue
            finding_source = str(finding.get("source", "")).upper()
            if finding_source and finding_source != "AI":
                continue
            confidence = finding.get("confidence")
            if isinstance(confidence, int | float):
                confidence_values.append(int(confidence))
    else:
        confidence_values = extract_confidence_values(response)

    if not confidence_values and "confidence" in response:
        try:
            confidence_values = [int(response["confidence"])]
        except (TypeError, ValueError):
            return ["Invalid confidence value"]

    if not confidence_values:
        return []

    issues: list[str] = []
    for value in confidence_values:
        if value < min_confidence:
            issues.append(
                f"AI confidence {value}% is below the minimum threshold of {min_confidence}%"
            )
    return issues
