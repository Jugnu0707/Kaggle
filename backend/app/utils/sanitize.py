"""Sanitize agent outputs for explainability and replay (no secrets or prompts)."""

from __future__ import annotations

import json
import re
from typing import Any

SECRET_PATTERNS = [
    re.compile(r"AIza[0-9A-Za-z\-_]{35}", re.IGNORECASE),
    re.compile(r"sk-[0-9A-Za-z]{20,}", re.IGNORECASE),
    re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*[^\s,}]+"),
]

PROMPT_MARKERS = (
    "system prompt",
    "you are a",
    "your task is",
    "follow these instructions",
)


def _redact_string(value: str) -> str:
    redacted = value
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    lowered = redacted.lower()
    for marker in PROMPT_MARKERS:
        if marker in lowered:
            return "Sanitized agent reasoning (system prompts are not exposed)."
    if len(redacted) > 2000:
        return redacted[:2000] + "…"
    return redacted


def sanitize_value(value: Any) -> Any:
    """Recursively sanitize a value for safe external exposure."""
    if value is None:
        return None
    if isinstance(value, str):
        return _redact_string(value)
    if isinstance(value, int | float | bool):
        return value
    if isinstance(value, dict):
        blocked_keys = {
            "prompt",
            "system_prompt",
            "api_key",
            "google_api_key",
            "raw_prompt",
        }
        return {
            key: sanitize_value(item)
            for key, item in value.items()
            if key.lower() not in blocked_keys
        }
    if isinstance(value, list):
        return [sanitize_value(item) for item in value[:50]]
    return _redact_string(str(value))


def sanitize_text(text: str) -> str:
    """Sanitize a plain-text summary."""
    return _redact_string(text)


def summarize_json(payload: dict[str, Any], *, max_keys: int = 12) -> str:
    """Produce a compact JSON summary for storage."""
    sanitized = sanitize_value(payload)
    if isinstance(sanitized, dict):
        trimmed = dict(list(sanitized.items())[:max_keys])
        return json.dumps(trimmed, default=str)
    return json.dumps(sanitized, default=str)
