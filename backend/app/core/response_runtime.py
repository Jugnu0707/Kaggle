"""Response Planning Agent runtime initialization and status tracking."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.core.logging import get_logger

if TYPE_CHECKING:
    from agents.response.agent import ResponsePlanningAgent

logger = get_logger(__name__)

_response_loaded = False
_response_agent: ResponsePlanningAgent | None = None


def initialize_response_runtime() -> None:
    """Initialize the Response Planning Agent at application startup."""
    global _response_loaded, _response_agent

    from agents.response.agent import ResponsePlanningAgent

    agent = ResponsePlanningAgent()
    agent.initialize()
    _response_agent = agent
    _response_loaded = agent.is_loaded
    logger.info("Response Planning Agent initialized: loaded=%s", _response_loaded)


def get_response_agent() -> ResponsePlanningAgent:
    """Return the initialized Response Planning Agent instance."""
    if _response_agent is None or not _response_loaded:
        raise RuntimeError("Response Planning Agent is not initialized")
    return _response_agent
