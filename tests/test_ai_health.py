"""Google AI health verification endpoint tests."""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


def test_ai_health_missing_api_key(client: TestClient) -> None:
    """Missing GOOGLE_API_KEY returns connected=false with an error message."""
    with patch("app.services.gemini_service.ai_settings") as mock_settings:
        mock_settings.google_api_key = ""
        mock_settings.google_model = "gemini-2.5-pro"

        response = client.get("/api/v1/ai/health")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert body["data"]["connected"] is False
    assert body["data"]["error"] == "GOOGLE_API_KEY is not configured"


def test_ai_health_success(client: TestClient) -> None:
    """Successful Gemini response returns connected=true with model and response."""
    mock_generation = MagicMock()
    mock_generation.text = "Oz AI Ready"
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_generation

    with patch("app.services.gemini_service.ai_settings") as mock_settings:
        mock_settings.google_api_key = "test-key"
        mock_settings.google_model = "gemini-2.5-pro"
        with patch("app.services.gemini_service.genai.Client", return_value=mock_client):
            response = client.get("/api/v1/ai/health")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Google AI connectivity verified"
    assert body["data"]["connected"] is True
    assert body["data"]["model"] == "gemini-2.5-pro"
    assert body["data"]["response"] == "Oz AI Ready"

    mock_client.models.generate_content.assert_called_once_with(
        model="gemini-2.5-pro",
        contents="Reply with exactly: Oz AI Ready",
    )


def test_ai_health_api_error(client: TestClient) -> None:
    """Gemini API errors return connected=false with error details."""
    from google.genai import errors as genai_errors

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = genai_errors.ClientError(
        401,
        {"error": {"message": "API key not valid"}},
        None,
    )

    with patch("app.services.gemini_service.ai_settings") as mock_settings:
        mock_settings.google_api_key = "invalid-key"
        mock_settings.google_model = "gemini-2.5-pro"
        with patch("app.services.gemini_service.genai.Client", return_value=mock_client):
            response = client.get("/api/v1/ai/health")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert body["data"]["connected"] is False
    assert body["data"]["error"] is not None
