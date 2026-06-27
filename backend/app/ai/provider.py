"""Centralized Google Gemini client provider."""

from __future__ import annotations

from google import genai
from google.genai import errors as genai_errors
from google.genai import types as genai_types

from app.core.ai_config import ai_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class GeminiProvider:
    """Single source for Gemini API configuration and client access."""

    def __init__(self) -> None:
        self._api_key = ai_settings.google_api_key.strip()
        self._default_model = ai_settings.google_model.strip() or "gemini-2.5-pro"
        self._client: genai.Client | None = None

    @property
    def default_model(self) -> str:
        """Return the configured default Gemini model."""
        return self._default_model

    def has_api_key(self) -> bool:
        """Return whether a Gemini API key is configured."""
        return bool(self._api_key)

    def get_api_key(self) -> str:
        """Return the configured API key (may be empty)."""
        return self._api_key

    def get_model(self, model: str | None = None) -> str:
        """Resolve the model name, falling back to the configured default."""
        candidate = (model or "").strip()
        return candidate or self._default_model

    def get_client(self) -> genai.Client | None:
        """Return a shared Gemini client, or None when no API key is configured."""
        if not self._api_key:
            return None
        if self._client is None:
            self._client = genai.Client(api_key=self._api_key)
            logger.info("Gemini client initialized via AI runtime provider")
        return self._client

    def generate_text(self, prompt: str, model: str | None = None) -> str | None:
        """Send a plain-text prompt and return the model response."""
        client = self.get_client()
        if client is None:
            return None
        resolved_model = self.get_model(model)
        try:
            generation = client.models.generate_content(
                model=resolved_model,
                contents=prompt,
            )
            return (generation.text or "").strip() or None
        except (genai_errors.ClientError, genai_errors.ServerError) as exc:
            logger.warning("Gemini text generation failed: %s", exc)
            return None

    def generate_json(self, prompt: str, model: str | None = None) -> str | None:
        """Send a prompt and return JSON text from the model."""
        client = self.get_client()
        if client is None:
            return None
        resolved_model = self.get_model(model)
        try:
            generation = client.models.generate_content(
                model=resolved_model,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            return (generation.text or "").strip() or None
        except (genai_errors.ClientError, genai_errors.ServerError) as exc:
            logger.warning("Gemini JSON generation failed: %s", exc)
            return None
