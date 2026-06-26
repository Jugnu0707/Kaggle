"""Google Gemini API connectivity verification service."""

from __future__ import annotations

from dataclasses import dataclass

from google import genai
from google.genai import errors as genai_errors

from app.core.ai_config import ai_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

HEALTH_CHECK_PROMPT = "Reply with exactly: Oz AI Ready"
EXPECTED_RESPONSE = "Oz AI Ready"


@dataclass(frozen=True)
class GeminiHealthResult:
    """Result of a Gemini API connectivity check."""

    connected: bool
    model: str | None = None
    response: str | None = None
    error: str | None = None


class GeminiService:
    """Verifies connectivity to Google AI Studio via the Gemini API."""

    def __init__(self) -> None:
        self._api_key = ai_settings.google_api_key.strip()
        self._model = ai_settings.google_model.strip() or "gemini-2.5-pro"

    def health_check(self) -> GeminiHealthResult:
        """Send a minimal prompt to verify the configured Gemini API key and model."""
        if not self._api_key:
            logger.warning("Gemini health check skipped: GOOGLE_API_KEY is not configured")
            return GeminiHealthResult(
                connected=False,
                error="GOOGLE_API_KEY is not configured",
            )

        logger.info("Gemini health check started: model=%s", self._model)

        try:
            client = genai.Client(api_key=self._api_key)
            generation = client.models.generate_content(
                model=self._model,
                contents=HEALTH_CHECK_PROMPT,
            )
            response_text = (generation.text or "").strip()

            if not response_text:
                logger.error("Gemini health check failed: empty response from model")
                return GeminiHealthResult(
                    connected=False,
                    model=self._model,
                    error="Gemini API returned an empty response",
                )

            logger.info(
                "Gemini health check completed: model=%s response=%s",
                self._model,
                response_text,
            )
            return GeminiHealthResult(
                connected=True,
                model=self._model,
                response=response_text,
            )
        except genai_errors.ClientError as exc:
            logger.error("Gemini health check failed: %s", exc)
            return GeminiHealthResult(
                connected=False,
                model=self._model,
                error=str(exc),
            )
        except genai_errors.ServerError as exc:
            logger.error("Gemini health check failed: %s", exc)
            return GeminiHealthResult(
                connected=False,
                model=self._model,
                error=str(exc),
            )
        except Exception as exc:
            logger.exception("Gemini health check failed with unexpected error")
            return GeminiHealthResult(
                connected=False,
                model=self._model,
                error=str(exc),
            )
