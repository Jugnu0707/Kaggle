"""Prompt injection detection for Guardian validation."""

from __future__ import annotations

import re

DEFAULT_INJECTION_BLOCKLIST: tuple[str, ...] = (
    "ignore previous instructions",
    "reveal system prompt",
    "show hidden prompt",
    "execute shell command",
    "override safety",
    "forget previous instructions",
    "disregard prior instructions",
    "ignore all previous",
    "you are now",
    "jailbreak",
)


def detect_prompt_injection(
    text: str,
    *,
    blocklist: tuple[str, ...] | None = None,
) -> list[str]:
    """Return matched prompt injection phrases found in text."""
    if not text.strip():
        return []

    patterns = blocklist or DEFAULT_INJECTION_BLOCKLIST
    lowered = text.lower()
    matches: list[str] = []
    for phrase in patterns:
        if phrase.lower() in lowered:
            matches.append(phrase)
    return matches


def scan_response_for_injection(response: object) -> list[str]:
    """Recursively scan a response payload for prompt injection patterns."""
    findings: list[str] = []

    if isinstance(response, str):
        findings.extend(detect_prompt_injection(response))
    elif isinstance(response, dict):
        for value in response.values():
            findings.extend(scan_response_for_injection(value))
    elif isinstance(response, list):
        for item in response:
            findings.extend(scan_response_for_injection(item))

    return _dedupe(findings)


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            ordered.append(item)
    return ordered
