"""MITRE Mapping Agent runtime initialization and status tracking."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.core.logging import get_logger

if TYPE_CHECKING:
    from agents.mitre.agent import MitreMappingAgent

logger = get_logger(__name__)

_mitre_loaded = False
_mitre_agent: MitreMappingAgent | None = None


def initialize_mitre_runtime() -> None:
    """Initialize the MITRE Mapping Agent at application startup."""
    global _mitre_loaded, _mitre_agent

    from agents.mitre.agent import MitreMappingAgent

    agent = MitreMappingAgent()
    agent.initialize()
    _mitre_agent = agent
    _mitre_loaded = agent.is_loaded
    logger.info("MITRE Mapping Agent initialized: loaded=%s", _mitre_loaded)


def get_mitre_agent() -> MitreMappingAgent:
    """Return the initialized MITRE Mapping Agent instance."""
    if _mitre_agent is None or not _mitre_loaded:
        raise RuntimeError("MITRE Mapping Agent is not initialized")
    return _mitre_agent
