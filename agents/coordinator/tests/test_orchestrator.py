"""Coordinator orchestrator unit tests."""

import uuid

import pytest
from agents.coordinator.models import CoordinatorInput
from agents.coordinator.orchestrator import DEFAULT_WORKFLOW, CoordinatorOrchestrator
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.models.enums import IncidentStatus, Severity
from app.models.incident import Incident


def _create_incident(db_session: Session) -> uuid.UUID:
    incident = Incident(
        title="Test incident",
        description="Orchestration test incident",
        severity=Severity.HIGH,
        status=IncidentStatus.NEW,
        source="Unit Test",
        confidence_score=0.5,
    )
    db_session.add(incident)
    db_session.commit()
    db_session.refresh(incident)
    return incident.id


def test_orchestrator_generates_default_workflow(db_session: Session) -> None:
    """Coordinator generates the expected placeholder workflow."""
    incident_id = _create_incident(db_session)
    orchestrator = CoordinatorOrchestrator()

    plan, duration_ms = orchestrator.build_plan(
        CoordinatorInput(incident_id=incident_id),
        db_session,
    )

    assert plan.status == "accepted"
    assert plan.incident_id == incident_id
    assert plan.workflow == DEFAULT_WORKFLOW
    assert duration_ms >= 0


def test_orchestrator_rejects_missing_incident(db_session: Session) -> None:
    """Invalid incident IDs raise a not-found error."""
    orchestrator = CoordinatorOrchestrator()

    with pytest.raises(NotFoundException, match="Incident not found"):
        orchestrator.build_plan(
            CoordinatorInput(incident_id=uuid.uuid4()),
            db_session,
        )


def test_coordinator_input_requires_identifier() -> None:
    """Coordinator input validation requires incident_id or log_id."""
    with pytest.raises(ValueError, match="Either incident_id or log_id is required"):
        CoordinatorInput()
