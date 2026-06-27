"""Google AI health verification endpoint tests."""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


def test_ai_health_missing_api_key(client: TestClient) -> None:
    """Missing GOOGLE_API_KEY returns connected=false with an error message."""
    mock_provider = MagicMock()
    mock_provider.has_api_key.return_value = False
    mock_provider.get_model.return_value = "gemini-2.5-pro"

    with patch("app.services.gemini_service.get_ai_runtime") as mock_runtime:
        mock_runtime.return_value.provider = mock_provider
        response = client.get("/api/v1/ai/health")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert body["data"]["connected"] is False
    assert body["data"]["error"] == "GOOGLE_API_KEY is not configured"


def test_ai_health_success(client: TestClient) -> None:
    """Successful Gemini response returns connected=true with model and response."""
    mock_provider = MagicMock()
    mock_provider.has_api_key.return_value = True
    mock_provider.get_model.return_value = "gemini-2.5-pro"
    mock_provider.generate_text.return_value = "Oz AI Ready"

    with patch("app.services.gemini_service.get_ai_runtime") as mock_runtime:
        mock_runtime.return_value.provider = mock_provider
        response = client.get("/api/v1/ai/health")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Google AI connectivity verified"
    assert body["data"]["connected"] is True
    assert body["data"]["model"] == "gemini-2.5-pro"
    assert body["data"]["response"] == "Oz AI Ready"

    mock_provider.generate_text.assert_called_once_with(
        "Reply with exactly: Oz AI Ready",
        model="gemini-2.5-pro",
    )


def test_ai_health_api_error(client: TestClient) -> None:
    """Empty Gemini responses return connected=false with error details."""
    mock_provider = MagicMock()
    mock_provider.has_api_key.return_value = True
    mock_provider.get_model.return_value = "gemini-2.5-pro"
    mock_provider.generate_text.return_value = None

    with patch("app.services.gemini_service.get_ai_runtime") as mock_runtime:
        mock_runtime.return_value.provider = mock_provider
        response = client.get("/api/v1/ai/health")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert body["data"]["connected"] is False
    assert body["data"]["error"] is not None
