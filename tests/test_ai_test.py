"""AI connectivity test endpoint tests."""

from concurrent.futures import TimeoutError as FuturesTimeoutError
from unittest.mock import MagicMock, patch

from google.genai import errors as genai_errors
from fastapi.testclient import TestClient

from app.services.ai_test_service import AITestService


def test_ai_test_missing_api_key(client: TestClient) -> None:
    """Missing GOOGLE_API_KEY returns connected=false with Invalid API key."""
    with patch("app.services.ai_test_service.ai_settings") as mock_settings:
        mock_settings.google_api_key = ""
        mock_settings.google_model = "gemini-2.5-pro"
        response = client.get("/api/v1/ai/test")

    assert response.status_code == 200
    body = response.json()
    assert body == {"connected": False, "reason": "Invalid API key"}


def test_ai_test_success(client: TestClient) -> None:
    """Successful Gemini response returns connected=true with latency."""
    with patch("app.services.ai_test_service.ai_settings") as mock_settings:
        mock_settings.google_api_key = "test-key"
        mock_settings.google_model = "gemini-2.5-pro"
        with patch.object(AITestService, "_generate", return_value="READY") as mock_generate:
            response = client.get("/api/v1/ai/test")

    assert response.status_code == 200
    body = response.json()
    assert body["connected"] is True
    assert body["provider"] == "Google Gemini"
    assert body["model"] == "gemini-2.5-pro"
    assert body["response"] == "READY"
    assert isinstance(body["latency_ms"], int)
    assert body["latency_ms"] >= 0
    mock_generate.assert_called_once_with("test-key", "gemini-2.5-pro")


def test_ai_test_quota_exceeded(client: TestClient) -> None:
    """429 Gemini errors return connected=false with Quota exceeded."""
    with patch("app.services.ai_test_service.ai_settings") as mock_settings:
        mock_settings.google_api_key = "test-key"
        mock_settings.google_model = "gemini-2.5-pro"
        with patch.object(
            AITestService,
            "_generate",
            side_effect=genai_errors.ClientError(
                429,
                {"error": {"message": "Quota exceeded"}},
                None,
            ),
        ):
            response = client.get("/api/v1/ai/test")

    assert response.status_code == 200
    assert response.json() == {"connected": False, "reason": "Quota exceeded"}


def test_ai_test_invalid_api_key(client: TestClient) -> None:
    """401 Gemini errors return connected=false with Invalid API key."""
    with patch("app.services.ai_test_service.ai_settings") as mock_settings:
        mock_settings.google_api_key = "bad-key"
        mock_settings.google_model = "gemini-2.5-pro"
        with patch.object(
            AITestService,
            "_generate",
            side_effect=genai_errors.ClientError(
                401,
                {"error": {"message": "API key not valid"}},
                None,
            ),
        ):
            response = client.get("/api/v1/ai/test")

    assert response.status_code == 200
    assert response.json() == {"connected": False, "reason": "Invalid API key"}


def test_ai_test_timeout(client: TestClient) -> None:
    """Slow Gemini responses return connected=false with Timeout."""
    with patch("app.services.ai_test_service.ai_settings") as mock_settings:
        mock_settings.google_api_key = "test-key"
        mock_settings.google_model = "gemini-2.5-pro"
        with patch(
            "app.services.ai_test_service.ThreadPoolExecutor",
        ) as mock_executor_cls:
            mock_future = MagicMock()
            mock_future.result.side_effect = FuturesTimeoutError()
            mock_executor = MagicMock()
            mock_executor.submit.return_value = mock_future
            mock_executor_cls.return_value.__enter__.return_value = mock_executor
            response = client.get("/api/v1/ai/test")

    assert response.status_code == 200
    assert response.json() == {"connected": False, "reason": "Timeout"}
