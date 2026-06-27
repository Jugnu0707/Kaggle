"""PII detection and masking for Guardian validation."""

from __future__ import annotations

import re
from typing import Any

EMAIL_MASK = "[REDACTED_EMAIL]"
PHONE_MASK = "[REDACTED_PHONE]"
AADHAAR_MASK = "[REDACTED_AADHAAR]"
PAN_MASK = "[REDACTED_PAN]"
CARD_MASK = "[REDACTED_CARD]"

PII_PATTERNS: tuple[tuple[str, re.Pattern[str], str, bool], ...] = (
    (
        "Email Address",
        re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        EMAIL_MASK,
        False,
    ),
    (
        "Phone Number",
        re.compile(
            r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(\d{2,4}\)[-.\s]?)?\d{3,4}[-.\s]?\d{4}\b"
        ),
        PHONE_MASK,
        False,
    ),
    (
        "Aadhaar Number",
        re.compile(r"\b[2-9]\d{3}\s?\d{4}\s?\d{4}\b"),
        AADHAAR_MASK,
        False,
    ),
    (
        "PAN Number",
        re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"),
        PAN_MASK,
        False,
    ),
    (
        "Credit Card Number",
        re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
        CARD_MASK,
        False,
    ),
    (
        "IP Address",
        re.compile(
            r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\b"
        ),
        "[REDACTED_IP]",
        True,
    ),
)


def detect_pii(text: str) -> tuple[list[str], list[str]]:
    """Return blocking and warning PII findings in text."""
    if not text:
        return [], []

    blocking: list[str] = []
    warnings: list[str] = []
    for label, pattern, _, warning_only in PII_PATTERNS:
        if pattern.search(text):
            if warning_only:
                warnings.append(label)
            else:
                blocking.append(label)
    return _dedupe(blocking), _dedupe(warnings)


def mask_pii_in_text(text: str) -> tuple[str, list[str], list[str]]:
    """Mask PII in text and return blocking and warning findings."""
    if not text:
        return text, [], []

    blocking: list[str] = []
    warnings: list[str] = []
    masked = text
    for label, pattern, replacement, warning_only in PII_PATTERNS:
        if pattern.search(masked):
            if warning_only:
                warnings.append(label)
            else:
                blocking.append(label)
            masked = pattern.sub(replacement, masked)
    return masked, _dedupe(blocking), _dedupe(warnings)


def mask_pii_in_response(response: Any) -> tuple[Any, list[str], list[str]]:
    """Recursively mask PII in a response payload."""
    if isinstance(response, str):
        masked, blocking, warnings = mask_pii_in_text(response)
        return masked, blocking, warnings
    if isinstance(response, dict):
        masked_dict: dict[Any, Any] = {}
        blocking: list[str] = []
        warnings: list[str] = []
        for key, value in response.items():
            masked_value, value_blocking, value_warnings = mask_pii_in_response(value)
            masked_dict[key] = masked_value
            blocking.extend(value_blocking)
            warnings.extend(value_warnings)
        return masked_dict, _dedupe(blocking), _dedupe(warnings)
    if isinstance(response, list):
        masked_list: list[Any] = []
        blocking = []
        warnings = []
        for item in response:
            masked_item, item_blocking, item_warnings = mask_pii_in_response(item)
            masked_list.append(masked_item)
            blocking.extend(item_blocking)
            warnings.extend(item_warnings)
        return masked_list, _dedupe(blocking), _dedupe(warnings)
    return response, [], []


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered
