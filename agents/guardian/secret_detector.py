"""Sensitive secret detection and masking for Guardian validation."""

from __future__ import annotations

import re
from typing import Any

MASK = "[REDACTED_SECRET]"

SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("AWS Access Key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Google API Key", re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b")),
    ("Bearer Token", re.compile(r"\bBearer\s+[A-Za-z0-9\-._~+/]+=*\b", re.IGNORECASE)),
    ("JWT Token", re.compile(r"\beyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\b")),
    ("Azure Secret", re.compile(r"\b[a-zA-Z0-9+/]{86}==\b")),
    (
        "Private Key",
        re.compile(
            r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[\s\S]+?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
        ),
    ),
    (
        "Database Credential",
        re.compile(
            r"(?i)(?:password|passwd|pwd|db_password|database_url)\s*[:=]\s*[^\s,;\"']+"
        ),
    ),
    (
        "API Key Assignment",
        re.compile(
            r"(?i)(?:api[_-]?key|secret[_-]?key|access[_-]?token)\s*[:=]\s*[^\s,;\"']+"
        ),
    ),
    ("Generic Password", re.compile(r"(?i)password\s*[:=]\s*\S+")),
)


def detect_secrets(text: str) -> list[str]:
    """Return labels for secret patterns detected in text."""
    if not text:
        return []

    findings: list[str] = []
    for label, pattern in SECRET_PATTERNS:
        if pattern.search(text):
            findings.append(label)
    return findings


def mask_secrets_in_text(text: str) -> tuple[str, list[str]]:
    """Mask secret patterns in text and return findings."""
    if not text:
        return text, []

    findings: list[str] = []
    masked = text
    for label, pattern in SECRET_PATTERNS:
        if pattern.search(masked):
            findings.append(label)
            masked = pattern.sub(MASK, masked)
    return masked, findings


def mask_secrets_in_response(response: Any) -> tuple[Any, list[str]]:
    """Recursively mask secrets in a response payload."""
    if isinstance(response, str):
        return mask_secrets_in_text(response)
    if isinstance(response, dict):
        masked_dict: dict[Any, Any] = {}
        findings: list[str] = []
        for key, value in response.items():
            masked_value, value_findings = mask_secrets_in_response(value)
            masked_dict[key] = masked_value
            findings.extend(value_findings)
        return masked_dict, _dedupe(findings)
    if isinstance(response, list):
        masked_list: list[Any] = []
        findings = []
        for item in response:
            masked_item, item_findings = mask_secrets_in_response(item)
            masked_list.append(masked_item)
            findings.extend(item_findings)
        return masked_list, _dedupe(findings)
    return response, []


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered
