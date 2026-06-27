"""Timestamp normalization and log-line parsing for the timeline engine."""

from __future__ import annotations

import re
from datetime import UTC, datetime

from app.services.timeline.models import RawTimelineEvent, TimelineEventType

TIMESTAMP_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"(?P<value>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)"
    ),
    re.compile(r"(?P<value>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})"),
    re.compile(r"(?P<value>\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})"),
)

EVENT_TYPE_RULES: tuple[tuple[re.Pattern[str], TimelineEventType], ...] = (
    (
        re.compile(r"powershell|scriptblock|encodedcommand", re.I),
        TimelineEventType.POWERSHELL,
    ),
    (
        re.compile(r"processcreate|processterminate|process=", re.I),
        TimelineEventType.PROCESS_EXECUTION,
    ),
    (re.compile(r"networkconnect|dest=|protocol=", re.I), TimelineEventType.NETWORK),
    (
        re.compile(r"logon|4625|4624|4771|4723|4740", re.I),
        TimelineEventType.AUTHENTICATION,
    ),
    (
        re.compile(
            r"filecreate|filemodify|filedelete|fim|massrename|massencrypt", re.I
        ),
        TimelineEventType.FILE,
    ),
    (re.compile(r"registryset|registry", re.I), TimelineEventType.REGISTRY),
    (
        re.compile(r"edralert|defenderalert|defenderquarantine|amsi_scan", re.I),
        TimelineEventType.EDR,
    ),
    (
        re.compile(r"firewall|5152|5157|block|drop|denied", re.I),
        TimelineEventType.FIREWALL,
    ),
    (
        re.compile(r"alert|defenderalert|incidentescalation", re.I),
        TimelineEventType.ALERT,
    ),
    (re.compile(r"upload|user action|analyst=", re.I), TimelineEventType.USER_ACTION),
)

SEVERITY_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"severity=critical|critical", re.I), "Critical"),
    (re.compile(r"severity=high|ransomware|malicious", re.I), "High"),
    (re.compile(r"severity=medium|suspicious", re.I), "Medium"),
    (re.compile(r"severity=low", re.I), "Low"),
)


def extract_timestamp(text: str) -> datetime | None:
    """Extract and normalize the first timestamp found in a log line."""
    for pattern in TIMESTAMP_PATTERNS:
        match = pattern.search(text)
        if match is None:
            continue
        normalized = normalize_timestamp_string(match.group("value"))
        if normalized is not None:
            return normalized
    return None


def normalize_timestamp_string(value: str) -> datetime | None:
    """Normalize supported timestamp strings to UTC-aware datetimes."""
    candidate = value.strip()
    if candidate.endswith("Z"):
        candidate = candidate[:-1] + "+00:00"

    iso_candidate = candidate
    if " " in iso_candidate and "T" not in iso_candidate:
        iso_candidate = iso_candidate.replace(" ", "T", 1)

    for candidate_value in (candidate, iso_candidate):
        for fmt in (
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%f%z",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y/%m/%d %H:%M:%S",
            "%m/%d/%Y %H:%M:%S",
        ):
            try:
                parsed = datetime.strptime(candidate_value, fmt)
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=UTC)
                return parsed.astimezone(UTC)
            except ValueError:
                continue

    try:
        parsed = datetime.fromisoformat(
            candidate.replace(" ", "T", 1) if " " in candidate else candidate
        )
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)
    except ValueError:
        return None


def infer_event_type(text: str) -> TimelineEventType:
    """Infer a timeline event type from log content."""
    for pattern, event_type in EVENT_TYPE_RULES:
        if pattern.search(text):
            return event_type
    return TimelineEventType.ALERT


def infer_severity(text: str, default: str = "Medium") -> str:
    """Infer event severity from log content."""
    for pattern, severity in SEVERITY_RULES:
        if pattern.search(text):
            return severity
    return default


def parse_log_line(
    line: str,
    *,
    source: str,
    evidence_reference: str | None,
    fallback_timestamp: datetime,
    default_severity: str = "Medium",
) -> RawTimelineEvent | None:
    """Parse a single log line into a raw timeline event."""
    stripped = line.strip()
    if not stripped:
        return None

    parsed_timestamp = extract_timestamp(stripped)
    timestamp_uncertain = parsed_timestamp is None
    timestamp = parsed_timestamp or fallback_timestamp
    confidence = 85 if parsed_timestamp else 40

    event_type = infer_event_type(stripped)
    severity = infer_severity(stripped, default=default_severity)

    return RawTimelineEvent(
        timestamp=timestamp,
        source=source,
        event_type=event_type,
        severity=severity,
        description=stripped,
        evidence_reference=evidence_reference,
        confidence=confidence,
        timestamp_uncertain=timestamp_uncertain,
    )


def deduplicate_key(event: RawTimelineEvent) -> tuple[str, str, str, str]:
    """Build a deterministic key for duplicate detection."""
    normalized_description = " ".join(event.description.lower().split())
    normalized_timestamp = event.timestamp.astimezone(UTC).isoformat()
    return (
        normalized_timestamp,
        event.source.lower(),
        event.event_type.value,
        normalized_description,
    )
