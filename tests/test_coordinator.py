"""Coordinator Agent tests."""

from agents.coordinator.agent import CoordinatorAgent


def test_coordinator_initializes() -> None:
    """Coordinator Agent initializes and reports loaded status."""
    coordinator = CoordinatorAgent()
    assert coordinator.is_loaded is False

    coordinator.initialize()

    assert coordinator.is_loaded is True


def test_coordinator_returns_placeholder_response() -> None:
    """Coordinator returns the static placeholder without LLM execution."""
    coordinator = CoordinatorAgent()
    coordinator.initialize()

    response = coordinator.handle_request({"incident_id": "test-123"})

    assert response == {
        "status": "Coordinator initialized",
        "message": "Ready for agent orchestration.",
    }
