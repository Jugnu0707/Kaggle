"""Coordinator Agent tests."""

from agents.coordinator.agent import CoordinatorAgent


def test_coordinator_initializes() -> None:
    """Coordinator Agent initializes and reports loaded status."""
    coordinator = CoordinatorAgent()
    assert coordinator.is_loaded is False

    coordinator.initialize()

    assert coordinator.is_loaded is True
    assert coordinator.name == "coordinator"
    assert coordinator.adk_agent is not None


def test_coordinator_returns_startup_response() -> None:
    """Coordinator returns startup health information without orchestration."""
    coordinator = CoordinatorAgent()
    coordinator.initialize()

    response = coordinator.handle_request()

    assert response == {
        "status": "Coordinator initialized",
        "message": "Ready for agent orchestration.",
    }
