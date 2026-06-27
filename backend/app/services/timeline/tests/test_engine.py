"""Unit tests for the timeline engine."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from app.models.enums import IncidentStatus, Severity
from app.models.evidence import Evidence
from app.models.incident import Incident
from app.models.mitre_finding import MitreFinding
from app.models.risk_assessment import RiskAssessment
from app.models.threat_intelligence_finding import ThreatIntelligenceFinding
from app.services.timeline.engine import TimelineEngine
from app.services.timeline.models import TimelineEventType


def _create_incident(db_session: Session) -> Incident:
    incident = Incident(
        title="Suspicious PowerShell Execution",
        description="PowerShell launched from Word process.",
        severity=Severity.HIGH,
        status=IncidentStatus.INVESTIGATING,
        source="Microsoft Defender",
        confidence_score=0.92,
    )
    db_session.add(incident)
    db_session.flush()
    return incident


def test_timeline_orders_events_chronologically(db_session: Session) -> None:
    """Timeline events are sorted by timestamp."""
    incident = _create_incident(db_session)
    base = datetime(2026, 6, 24, 8, 15, 0, tzinfo=UTC)

    db_session.add(
        Evidence(
            incident_id=incident.id,
            evidence_type="PowerShell Transcript",
            filename="powershell.log",
            raw_data=(
                "2026-06-24T08:15:10Z EVENT=NetworkConnect DEST=1.2.3.4:443\n"
                "2026-06-24T08:15:02Z EVENT=ProcessCreate PROCESS=powershell.exe\n"
            ),
        )
    )
    db_session.commit()

    result = TimelineEngine(db_session).build(incident.id)
    timestamps = [event.timestamp for event in result.timeline]
    assert timestamps == sorted(timestamps)


def test_timeline_removes_duplicate_events(db_session: Session) -> None:
    """Identical events are deduplicated during processing."""
    incident = _create_incident(db_session)
    duplicate_line = "2026-06-24T08:15:03Z EVENT=ProcessCreate PROCESS=powershell.exe"

    db_session.add(
        Evidence(
            incident_id=incident.id,
            evidence_type="PowerShell Transcript",
            filename="powershell.log",
            raw_data=f"{duplicate_line}\n{duplicate_line}\n",
        )
    )
    db_session.commit()

    result = TimelineEngine(db_session).build(incident.id)
    assert result.duplicates_removed >= 1
    descriptions = [event.description for event in result.timeline]
    assert descriptions.count(duplicate_line) == 1


def test_timeline_includes_agent_assessments(db_session: Session) -> None:
    """MITRE, threat intelligence, and risk outputs appear as timeline events."""
    incident = _create_incident(db_session)
    created_at = datetime(2026, 6, 24, 9, 0, 0, tzinfo=UTC)

    db_session.add(
        MitreFinding(
            incident_id=incident.id,
            technique_id="T1059.001",
            technique_name="PowerShell",
            tactic="Execution",
            confidence=88,
            evidence=["powershell.exe"],
            created_at=created_at,
        )
    )
    db_session.add(
        ThreatIntelligenceFinding(
            incident_id=incident.id,
            indicator="185.234.72.19",
            indicator_type="ip",
            reputation="Malicious",
            confidence=91,
            source="FALLBACK",
            description="Known malicious host",
            analyst_notes="Seen in prior campaigns",
            created_at=created_at + timedelta(minutes=1),
        )
    )
    db_session.add(
        RiskAssessment(
            incident_id=incident.id,
            source="FALLBACK",
            overall_risk="High",
            risk_score=82,
            likelihood="Likely",
            business_impact="Finance workstation compromise",
            confidence=87,
            priority="P1",
            summary="Elevated risk due to credential exposure.",
            reasoning="PowerShell execution from Office process.",
            created_at=created_at + timedelta(minutes=2),
        )
    )
    db_session.commit()

    result = TimelineEngine(db_session).build(incident.id)
    event_types = {event.event_type for event in result.timeline}
    sources = {event.source for event in result.timeline}

    assert TimelineEventType.AI_ASSESSMENT in event_types
    assert "MITRE Mapping" in sources
    assert "Threat Intelligence" in sources
    assert "Risk Assessment" in sources
    assert "5 events" in result.investigation_summary
    assert "AI Assessment (2)" in result.investigation_summary


def test_timeline_handles_missing_timestamps(db_session: Session) -> None:
    """Events without timestamps are retained with uncertain markers."""
    incident = _create_incident(db_session)
    db_session.add(
        Evidence(
            incident_id=incident.id,
            evidence_type="Application Log",
            filename="partial.log",
            raw_data="EVENT=ProcessCreate PROCESS=cmd.exe PID=1234\n",
        )
    )
    db_session.commit()

    result = TimelineEngine(db_session).build(incident.id)
    uncertain_events = [event for event in result.timeline if event.timestamp_uncertain]
    assert uncertain_events
    assert uncertain_events[0].confidence == 40


def test_timeline_build_requires_existing_incident(db_session: Session) -> None:
    """Building a timeline for a missing incident raises NotFoundException."""
    from app.core.exceptions import NotFoundException

    with pytest.raises(NotFoundException):
        TimelineEngine(db_session).build(uuid.uuid4())
