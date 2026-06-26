"""Deterministic Investigation Timeline Engine."""

from __future__ import annotations

import time
import uuid
from collections import Counter
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import NotFoundException
from app.core.logging import get_logger
from app.models.incident import Incident
from app.services.timeline.models import ProcessedTimelineEvent
from app.repositories.incident_repository import IncidentRepository
from app.services.timeline.models import (
    ProcessedTimelineEvent,
    RawTimelineEvent,
    TimelineBuildResult,
    TimelineEventType,
)
from app.services.timeline.parser import deduplicate_key, parse_log_line

logger = get_logger(__name__)


class TimelineEngine:
    """Builds a chronological investigation timeline from incident artifacts."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.incident_repository = IncidentRepository(db)

    def build(self, incident_id: uuid.UUID) -> TimelineBuildResult:
        """Collect, normalize, deduplicate, and sequence timeline events."""
        timer_start = time.perf_counter()
        incident = self._load_incident(incident_id)
        if incident is None:
            raise NotFoundException("Incident not found")

        raw_events = self._collect_events(incident)
        logger.info(
            "Timeline collection complete: incident_id=%s events_collected=%s",
            incident_id,
            len(raw_events),
        )

        normalized = self._normalize_timestamps(raw_events)
        deduplicated, duplicates_removed = self._remove_duplicates(normalized)
        sorted_events = self._sort_chronologically(deduplicated)
        sequenced = self._assign_sequence(sorted_events)
        summary = self._generate_investigation_summary(incident, sequenced)

        duration_ms = int((time.perf_counter() - timer_start) * 1000)
        logger.info(
            "Timeline generated: incident_id=%s events_processed=%s duplicates_removed=%s duration_ms=%s",
            incident_id,
            len(sequenced),
            duplicates_removed,
            duration_ms,
        )

        return TimelineBuildResult(
            incident_id=incident_id,
            total_events=len(sequenced),
            timeline=sequenced,
            investigation_summary=summary,
            duplicates_removed=duplicates_removed,
            processing_duration_ms=duration_ms,
        )

    def _load_incident(self, incident_id: uuid.UUID) -> Incident | None:
        stmt = (
            select(Incident)
            .options(
                selectinload(Incident.evidence),
                selectinload(Incident.log_files),
                selectinload(Incident.mitre_findings),
                selectinload(Incident.threat_intelligence_findings),
                selectinload(Incident.risk_assessments),
                selectinload(Incident.response_plans),
            )
            .where(Incident.id == incident_id, Incident.deleted_at.is_(None))
        )
        return self.db.scalar(stmt)

    def _collect_events(self, incident: Incident) -> list[RawTimelineEvent]:
        events: list[RawTimelineEvent] = []
        events.extend(self._collect_incident_events(incident))
        events.extend(self._collect_log_upload_events(incident))
        events.extend(self._collect_evidence_events(incident))
        events.extend(self._collect_threat_intelligence_events(incident))
        events.extend(self._collect_mitre_events(incident))
        events.extend(self._collect_risk_events(incident))
        events.extend(self._collect_response_events(incident))
        return events

    def _collect_incident_events(self, incident: Incident) -> list[RawTimelineEvent]:
        confidence = min(100, max(0, int(round(incident.confidence_score * 100))))
        return [
            RawTimelineEvent(
                timestamp=incident.created_at,
                source=incident.source,
                event_type=TimelineEventType.ALERT,
                severity=incident.severity.value,
                description=f"Incident reported: {incident.title}",
                evidence_reference=str(incident.id),
                confidence=confidence,
            ),
            RawTimelineEvent(
                timestamp=incident.created_at,
                source="Incident Management",
                event_type=TimelineEventType.USER_ACTION,
                severity=incident.severity.value,
                description=incident.description,
                evidence_reference=str(incident.id),
                confidence=confidence,
            ),
        ]

    def _collect_log_upload_events(self, incident: Incident) -> list[RawTimelineEvent]:
        events: list[RawTimelineEvent] = []
        for log_file in incident.log_files:
            if log_file.deleted_at is not None:
                continue
            events.append(
                RawTimelineEvent(
                    timestamp=log_file.uploaded_at,
                    source="Log Upload",
                    event_type=TimelineEventType.USER_ACTION,
                    severity="Low",
                    description=f"Log file uploaded: {log_file.original_filename}",
                    evidence_reference=str(log_file.id),
                    confidence=100,
                )
            )
        return events

    def _collect_evidence_events(self, incident: Incident) -> list[RawTimelineEvent]:
        events: list[RawTimelineEvent] = []
        for evidence in incident.evidence:
            events.append(
                RawTimelineEvent(
                    timestamp=evidence.created_at,
                    source="Evidence Agent",
                    event_type=TimelineEventType.USER_ACTION,
                    severity=incident.severity.value,
                    description=(
                        f"Evidence collected ({evidence.evidence_type}): {evidence.filename}"
                    ),
                    evidence_reference=str(evidence.id),
                    confidence=95,
                )
            )

            for line in evidence.raw_data.splitlines():
                parsed = parse_log_line(
                    line,
                    source="Evidence Agent",
                    evidence_reference=evidence.filename,
                    fallback_timestamp=evidence.created_at,
                    default_severity=incident.severity.value,
                )
                if parsed is not None:
                    events.append(parsed)
        return events

    def _collect_threat_intelligence_events(
        self,
        incident: Incident,
    ) -> list[RawTimelineEvent]:
        events: list[RawTimelineEvent] = []
        for finding in incident.threat_intelligence_findings:
            event_type = (
                TimelineEventType.NETWORK
                if finding.indicator_type.lower() in {"ip", "domain", "url"}
                else TimelineEventType.ALERT
            )
            severity = self._reputation_to_severity(finding.reputation)
            events.append(
                RawTimelineEvent(
                    timestamp=finding.created_at,
                    source="Threat Intelligence",
                    event_type=event_type,
                    severity=severity,
                    description=(
                        f"IOC enrichment: {finding.indicator} "
                        f"({finding.indicator_type}) — {finding.reputation}"
                    ),
                    evidence_reference=finding.indicator,
                    confidence=finding.confidence,
                )
            )
        return events

    def _collect_mitre_events(self, incident: Incident) -> list[RawTimelineEvent]:
        events: list[RawTimelineEvent] = []
        for finding in incident.mitre_findings:
            events.append(
                RawTimelineEvent(
                    timestamp=finding.created_at,
                    source="MITRE Mapping",
                    event_type=TimelineEventType.AI_ASSESSMENT,
                    severity=self._confidence_to_severity(finding.confidence),
                    description=(
                        f"MITRE mapping: {finding.technique_id} "
                        f"{finding.technique_name} ({finding.tactic})"
                    ),
                    evidence_reference=finding.technique_id,
                    confidence=finding.confidence,
                )
            )
        return events

    def _collect_risk_events(self, incident: Incident) -> list[RawTimelineEvent]:
        if not incident.risk_assessments:
            return []

        assessment = max(incident.risk_assessments, key=lambda item: item.created_at)
        return [
            RawTimelineEvent(
                timestamp=assessment.created_at,
                source="Risk Assessment",
                event_type=TimelineEventType.AI_ASSESSMENT,
                severity=assessment.overall_risk,
                description=f"Risk assessment: {assessment.summary}",
                evidence_reference=str(assessment.id),
                confidence=assessment.confidence,
            )
        ]

    def _collect_response_events(self, incident: Incident) -> list[RawTimelineEvent]:
        if not incident.response_plans:
            return []

        plan = max(incident.response_plans, key=lambda item: item.created_at)
        events: list[RawTimelineEvent] = [
            RawTimelineEvent(
                timestamp=plan.created_at,
                source="Response Planning",
                event_type=TimelineEventType.AI_ASSESSMENT,
                severity=incident.severity.value,
                description=f"Response plan generated: {plan.executive_summary}",
                evidence_reference=str(plan.id),
                confidence=90,
            )
        ]

        for phase, actions in (
            ("Containment", plan.containment),
            ("Eradication", plan.eradication),
            ("Recovery", plan.recovery),
            ("Monitoring", plan.monitoring),
        ):
            for action in actions:
                events.append(
                    RawTimelineEvent(
                        timestamp=plan.created_at,
                        source="Response Planning",
                        event_type=TimelineEventType.USER_ACTION,
                        severity=incident.severity.value,
                        description=f"{phase} action: {action}",
                        evidence_reference=str(plan.id),
                        confidence=85,
                    )
                )
        return events

    def _normalize_timestamps(self, events: list[RawTimelineEvent]) -> list[RawTimelineEvent]:
        normalized: list[RawTimelineEvent] = []
        for event in events:
            timestamp = event.timestamp
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=UTC)
            else:
                timestamp = timestamp.astimezone(UTC)
            normalized.append(event.model_copy(update={"timestamp": timestamp}))
        return normalized

    def _remove_duplicates(
        self,
        events: list[RawTimelineEvent],
    ) -> tuple[list[RawTimelineEvent], int]:
        seen: set[tuple[str, str, str, str]] = set()
        unique: list[RawTimelineEvent] = []
        duplicates_removed = 0

        for event in events:
            key = deduplicate_key(event)
            if key in seen:
                duplicates_removed += 1
                continue
            seen.add(key)
            unique.append(event)

        return unique, duplicates_removed

    def _sort_chronologically(self, events: list[RawTimelineEvent]) -> list[RawTimelineEvent]:
        return sorted(
            events,
            key=lambda event: (
                event.timestamp,
                event.source.lower(),
                event.description.lower(),
            ),
        )

    def _assign_sequence(self, events: list[RawTimelineEvent]) -> list[ProcessedTimelineEvent]:
        processed: list[ProcessedTimelineEvent] = []
        for index, event in enumerate(events, start=1):
            processed.append(
                ProcessedTimelineEvent(
                    sequence=index,
                    timestamp=event.timestamp,
                    source=event.source,
                    event_type=event.event_type,
                    severity=event.severity,
                    description=event.description,
                    evidence_reference=event.evidence_reference,
                    confidence=event.confidence,
                    timestamp_uncertain=event.timestamp_uncertain,
                )
            )
        return processed

    def _generate_investigation_summary(
        self,
        incident: Incident,
        events: list[ProcessedTimelineEvent],
    ) -> str:
        if not events:
            return (
                f"No timeline events were reconstructed for incident '{incident.title}'. "
                "Upload logs and run agent analysis to populate the investigation timeline."
            )

        type_counts = Counter(event.event_type.value for event in events)
        type_summary = ", ".join(
            f"{event_type} ({count})" for event_type, count in sorted(type_counts.items())
        )
        severities = [event.severity for event in events]
        highest_severity = self._highest_severity(severities)
        start = events[0].timestamp.isoformat()
        end = events[-1].timestamp.isoformat()

        return (
            f"Investigation timeline for '{incident.title}' contains {len(events)} events "
            f"spanning {start} to {end}. Event types: {type_summary}. "
            f"Highest observed severity: {highest_severity}."
        )

    def _reputation_to_severity(self, reputation: str) -> str:
        mapping = {
            "Malicious": "Critical",
            "Suspicious": "High",
            "Unknown": "Medium",
            "Safe": "Low",
            "Informational": "Low",
        }
        return mapping.get(reputation, "Medium")

    def _confidence_to_severity(self, confidence: int) -> str:
        if confidence >= 90:
            return "High"
        if confidence >= 75:
            return "Medium"
        return "Low"

    def _highest_severity(self, severities: list[str]) -> str:
        order = ["Critical", "High", "Medium", "Low"]
        for severity in order:
            if severity in severities:
                return severity
        return severities[0]
