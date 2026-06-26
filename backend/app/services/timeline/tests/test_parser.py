"""Unit tests for timeline parser utilities."""

from datetime import UTC, datetime

from app.services.timeline.models import RawTimelineEvent, TimelineEventType
from app.services.timeline.parser import (
    deduplicate_key,
    extract_timestamp,
    infer_event_type,
    normalize_timestamp_string,
    parse_log_line,
)


def test_normalize_timestamp_iso_with_z() -> None:
  """ISO timestamps with Z suffix normalize to UTC."""
  parsed = normalize_timestamp_string("2026-06-24T08:15:01Z")
  assert parsed == datetime(2026, 6, 24, 8, 15, 1, tzinfo=UTC)


def test_normalize_timestamp_space_separated() -> None:
  """Space-separated timestamps are normalized."""
  parsed = normalize_timestamp_string("2026/06/24 08:15:01")
  assert parsed == datetime(2026, 6, 24, 8, 15, 1, tzinfo=UTC)


def test_infer_event_type_powershell() -> None:
  """PowerShell content maps to the PowerShell event type."""
  assert infer_event_type("EVENT=ScriptBlock TEXT=Invoke-Expression") == TimelineEventType.POWERSHELL


def test_infer_event_type_network() -> None:
  """Network connections map to the Network event type."""
  assert infer_event_type("EVENT=NetworkConnect DEST=10.0.0.1:443") == TimelineEventType.NETWORK


def test_parse_log_line_with_timestamp() -> None:
  """Log lines with timestamps use parsed values and high confidence."""
  fallback = datetime(2026, 1, 1, tzinfo=UTC)
  event = parse_log_line(
    "2026-06-24T08:15:03Z HOST=WS EVENT=NetworkConnect DEST=1.2.3.4:443",
    source="Evidence Agent",
    evidence_reference="events.log",
    fallback_timestamp=fallback,
  )
  assert event is not None
  assert event.confidence == 85
  assert event.timestamp_uncertain is False
  assert event.event_type == TimelineEventType.NETWORK


def test_parse_log_line_missing_timestamp() -> None:
  """Log lines without timestamps use fallback values and lower confidence."""
  fallback = datetime(2026, 1, 1, tzinfo=UTC)
  event = parse_log_line(
    "HOST=WS EVENT=ProcessCreate PROCESS=cmd.exe",
    source="Evidence Agent",
    evidence_reference="events.log",
    fallback_timestamp=fallback,
  )
  assert event is not None
  assert event.timestamp == fallback
  assert event.confidence == 40
  assert event.timestamp_uncertain is True


def test_deduplicate_key_is_stable() -> None:
  """Duplicate keys remain stable for equivalent events."""
  event = RawTimelineEvent(
    timestamp=datetime(2026, 6, 24, 8, 15, 1, tzinfo=UTC),
    source="Evidence Agent",
    event_type=TimelineEventType.ALERT,
    severity="High",
    description="Duplicate   test",
    confidence=80,
  )
  assert deduplicate_key(event) == deduplicate_key(event)


def test_extract_timestamp_from_mixed_log_format() -> None:
  """Mixed log formats still expose a parseable timestamp."""
  parsed = extract_timestamp("2026-06-25 02:41:01 EVENT=4625 RESULT=Failure")
  assert parsed == datetime(2026, 6, 25, 2, 41, 1, tzinfo=UTC)
