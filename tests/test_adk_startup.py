"""ADK runtime and startup tests."""

from fastapi.testclient import TestClient

from app.core.adk_runtime import get_adk_status, get_coordinator, verify_adk_installed


def test_adk_import_verifies_successfully() -> None:
    """Google ADK package imports without error."""
    assert verify_adk_installed() is True


def test_application_starts_without_ai_execution(client: TestClient) -> None:
    """Application startup initializes ADK and Coordinator without LLM calls."""
    adk_status = get_adk_status()
    assert adk_status["adk"] is True
    assert adk_status["coordinator"] is True

    coordinator = get_coordinator()
    response = coordinator.handle_request()
    assert response["status"] == "Coordinator initialized"

    root_response = client.get("/")
    assert root_response.status_code == 200
