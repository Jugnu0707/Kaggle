"""Minimal Coordinator Agent placeholder for ADK framework integration."""

from typing import Any


class CoordinatorAgent:
    """Coordinator Agent placeholder — no LLM calls or tools in Sprint 2 Task 1."""

    PLACEHOLDER_RESPONSE: dict[str, str] = {
        "status": "Coordinator initialized",
        "message": "Ready for agent orchestration.",
    }

    def __init__(self) -> None:
        self._loaded = False

    def initialize(self) -> None:
        """Initialize the coordinator without invoking the LLM."""
        self._loaded = True

    @property
    def is_loaded(self) -> bool:
        """Return whether the coordinator finished initialization."""
        return self._loaded

    def handle_request(self, request: dict[str, Any] | None = None) -> dict[str, str]:
        """Accept a request and return a static placeholder response."""
        _ = request
        return dict(self.PLACEHOLDER_RESPONSE)
