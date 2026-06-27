"""Minimal Gemini API connectivity verification."""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError
from dataclasses import dataclass
from datetime import UTC, datetime

from google import genai
from google.genai import errors as genai_errors

from app.core.ai_config import ai_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

AI_TEST_TIMEOUT_SECONDS = 30
AI_TEST_PROMPT = (
    "Reply with exactly one word.\n\n"
    "READY\n\n"
    "Do not add punctuation.\n"
    "Do not explain.\n"
    "Do not use Markdown.\n\n"
    "This minimizes token usage."
)
PROVIDER_NAME = "Google Gemini"


@dataclass(frozen=True)
class AITestResult:
    """Outcome of a single Gemini connectivity probe."""

    connected: bool
    provider: str | None = None
    model: str | None = None
    response: str | None = None
    latency_ms: int | None = None
    reason: str | None = None


class AITestService:
    """Verifies Google Gemini connectivity with a one-token probe."""

    def test_connectivity(self) -> AITestResult:
        """Send one minimal prompt and report connectivity status."""
        api_key = ai_settings.google_api_key.strip()
        model = ai_settings.google_model.strip() or "gemini-2.5-pro"

        if not api_key:
            logger.warning(
                "AI connectivity test failed: model=%s status=invalid_api_key",
                model,
            )
            return AITestResult(connected=False, reason="Invalid API key")

        start_dt = datetime.now(UTC)
        start_perf = time.perf_counter()
        logger.info(
            "AI connectivity test started: model=%s start_time=%s",
            model,
            start_dt.isoformat(),
        )

        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self._generate, api_key, model)
                response_text = future.result(timeout=AI_TEST_TIMEOUT_SECONDS)
        except FuturesTimeoutError:
            end_dt = datetime.now(UTC)
            latency_ms = int((time.perf_counter() - start_perf) * 1000)
            logger.warning(
                "AI connectivity test failed: model=%s start_time=%s end_time=%s "
                "latency_ms=%s status=timeout",
                model,
                start_dt.isoformat(),
                end_dt.isoformat(),
                latency_ms,
            )
            return AITestResult(connected=False, reason="Timeout")
        except genai_errors.ClientError as exc:
            end_dt = datetime.now(UTC)
            latency_ms = int((time.perf_counter() - start_perf) * 1000)
            reason = self._client_error_reason(exc)
            logger.warning(
                "AI connectivity test failed: model=%s start_time=%s end_time=%s "
                "latency_ms=%s status=%s",
                model,
                start_dt.isoformat(),
                end_dt.isoformat(),
                latency_ms,
                reason,
            )
            return AITestResult(connected=False, reason=reason)
        except (genai_errors.ServerError, Exception) as exc:
            end_dt = datetime.now(UTC)
            latency_ms = int((time.perf_counter() - start_perf) * 1000)
            reason = self._generic_error_reason(exc)
            logger.warning(
                "AI connectivity test failed: model=%s start_time=%s end_time=%s "
                "latency_ms=%s status=%s error=%s",
                model,
                start_dt.isoformat(),
                end_dt.isoformat(),
                latency_ms,
                reason,
                exc,
            )
            return AITestResult(connected=False, reason=reason)

        end_dt = datetime.now(UTC)
        latency_ms = int((time.perf_counter() - start_perf) * 1000)
        logger.info(
            "AI connectivity test completed: model=%s start_time=%s end_time=%s "
            "latency_ms=%s status=connected response=%s",
            model,
            start_dt.isoformat(),
            end_dt.isoformat(),
            latency_ms,
            response_text,
        )
        return AITestResult(
            connected=True,
            provider=PROVIDER_NAME,
            model=model,
            response=response_text,
            latency_ms=latency_ms,
        )

    def _generate(self, api_key: str, model: str) -> str:
        client = genai.Client(api_key=api_key)
        generation = client.models.generate_content(
            model=model,
            contents=AI_TEST_PROMPT,
        )
        return (generation.text or "").strip()

    def _client_error_reason(self, exc: genai_errors.ClientError) -> str:
        code = getattr(exc, "code", None)
        message = str(exc).lower()
        if code == 429 or "quota" in message:
            return "Quota exceeded"
        if code in (401, 403) or "api key" in message or "invalid" in message:
            return "Invalid API key"
        return "Invalid API key"

    def _generic_error_reason(self, exc: Exception) -> str:
        message = str(exc).lower()
        if "timeout" in message or "timed out" in message:
            return "Timeout"
        if "quota" in message or "429" in message:
            return "Quota exceeded"
        if "api key" in message or "401" in message or "403" in message:
            return "Invalid API key"
        return "Invalid API key"
