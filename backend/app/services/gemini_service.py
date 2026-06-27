"""Google Gemini API connectivity verification service."""

from __future__ import annotations

from dataclasses import dataclass

from app.ai.runtime import get_ai_runtime
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

    def health_check(self) -> GeminiHealthResult:
        """Send a minimal prompt to verify the configured Gemini API key and model."""
        provider = get_ai_runtime().provider
        model = provider.get_model()

        if not provider.has_api_key():
            logger.warning("Gemini health check skipped: GOOGLE_API_KEY is not configured")
            return GeminiHealthResult(
                connected=False,
                error="GOOGLE_API_KEY is not configured",
            )

        logger.info("Gemini health check started: model=%s", model)
        response_text = provider.generate_text(HEALTH_CHECK_PROMPT, model=model)

        if not response_text:
            logger.error("Gemini health check failed: empty response from model")
            return GeminiHealthResult(
                connected=False,
                model=model,
                error="Gemini API returned an empty response",
            )

        logger.info(
            "Gemini health check completed: model=%s response=%s",
            model,
            response_text,
        )
        return GeminiHealthResult(
            connected=True,
            model=model,
            response=response_text,
        )
