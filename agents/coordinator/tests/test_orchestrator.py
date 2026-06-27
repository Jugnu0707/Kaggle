"""Coordinator orchestrator unit tests."""

import uuid
from unittest.mock import patch

import pytest
from agents.conftest import build_mock_ai_runtime
from agents.coordinator.models import CoordinatorInput
from agents.coordinator.orchestrator import DEFAULT_WORKFLOW, CoordinatorOrchestrator
from mcp.registry import ToolResult
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.models.enums import IncidentStatus, Severity
from app.models.incident import Incident


@pytest.fixture
def mock_ai_runtime():
    mock_runtime = build_mock_ai_runtime()
    with patch(
        "agents.coordinator.orchestrator.get_ai_runtime", return_value=mock_runtime
    ):
        yield mock_runtime


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


def test_orchestrator_generates_default_workflow(
    db_session: Session, mock_ai_runtime
) -> None:
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


def test_orchestrator_rejects_missing_incident(
    db_session: Session, mock_ai_runtime
) -> None:
    """Invalid incident IDs raise a not-found error."""
    mock_ai_runtime.invoke_tool.return_value = ToolResult(
        success=False, error="Incident not found"
    )
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
