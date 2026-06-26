"""Guardian Agent runtime initialization and status tracking."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.core.logging import get_logger

if TYPE_CHECKING:
    from agents.guardian.agent import GuardianAgent

logger = get_logger(__name__)

_guardian_loaded = False
_guardian_agent: GuardianAgent | None = None


def initialize_guardian_runtime() -> None:
    """Initialize the Guardian Agent at application startup."""
    global _guardian_loaded, _guardian_agent

    from agents.guardian.agent import GuardianAgent

    agent = GuardianAgent()
    agent.initialize()
    _guardian_agent = agent
    _guardian_loaded = agent.is_loaded
    logger.info("Guardian Agent initialized: loaded=%s", _guardian_loaded)


def get_guardian_agent() -> GuardianAgent:
    """Return the initialized Guardian Agent instance."""
    if _guardian_agent is None or not _guardian_loaded:
        raise RuntimeError("Guardian Agent is not initialized")
    return _guardian_agent
