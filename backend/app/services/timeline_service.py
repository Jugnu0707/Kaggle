"""Investigation timeline API service."""

from __future__ import annotations

import json
import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.core.logging import get_logger
from app.models.timeline_event import TimelineEvent
from app.repositories.incident_repository import IncidentRepository
from app.repositories.timeline_event_repository import TimelineEventRepository
from app.services.timeline.engine import TimelineEngine
from app.services.timeline.models import ProcessedTimelineEvent
from app.services.timeline.schemas import TimelineEventResponse, TimelineResponse, timeline_to_markdown

logger = get_logger(__name__)


class TimelineService:
    """Generates, persists, and returns investigation timelines."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.incident_repository = IncidentRepository(db)
        self.timeline_repository = TimelineEventRepository(db)
        self.engine = TimelineEngine(db)

    def get_timeline(self, incident_id: uuid.UUID) -> TimelineResponse:
        """Build, persist, and return the investigation timeline for an incident."""
        incident = self.incident_repository.get_by_id(incident_id)
        if incident is None:
            raise NotFoundException("Incident not found")

        result = self.engine.build(incident_id)
        self._persist_timeline(incident_id, result.timeline)
        self.db.commit()

        persisted = self.timeline_repository.list_by_incident_id(incident_id)
        return TimelineResponse(
            incident_id=incident_id,
            total_events=result.total_events,
            timeline=[self._to_response(event) for event in persisted],
            investigation_summary=result.investigation_summary,
        )

    def export_timeline(self, incident_id: uuid.UUID, export_format: str) -> tuple[str, str, str]:
        """Return export payload, media type, and filename suffix."""
        timeline = self.get_timeline(incident_id)
        normalized_format = export_format.lower().strip()

        if normalized_format == "markdown":
            return (
                timeline_to_markdown(timeline),
                "text/markdown; charset=utf-8",
                "md",
            )

        if normalized_format == "json":
            payload = timeline.model_dump(mode="json")
            return (
                json.dumps(payload, indent=2),
                "application/json; charset=utf-8",
                "json",
            )

        raise NotFoundException("Unsupported export format")

    def _persist_timeline(
        self,
        incident_id: uuid.UUID,
        events: list[ProcessedTimelineEvent],
    ) -> None:
        self.timeline_repository.delete_by_incident_id(incident_id)
        for event in events:
            self.timeline_repository.create(
                TimelineEvent(
                    incident_id=incident_id,
                    timestamp=event.timestamp,
                    sequence=event.sequence,
                    source=event.source,
                    event_type=event.event_type.value,
                    severity=event.severity,
                    description=event.description,
                    evidence_reference=event.evidence_reference,
                    confidence=event.confidence,
                )
            )

    def _to_response(self, event: TimelineEvent) -> TimelineEventResponse:
        uncertain = event.confidence <= 40
        return TimelineEventResponse(
            id=event.id,
            sequence=event.sequence,
            timestamp=event.timestamp,
            source=event.source,
            event_type=event.event_type,
            severity=event.severity,
            description=event.description,
            evidence_reference=event.evidence_reference,
            confidence=event.confidence,
            timestamp_uncertain=uncertain,
        )
