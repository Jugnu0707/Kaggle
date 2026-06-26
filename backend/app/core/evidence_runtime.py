"""Evidence Agent runtime initialization and status tracking."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.core.logging import get_logger

if TYPE_CHECKING:
    from agents.evidence.agent import EvidenceAgent

logger = get_logger(__name__)

_evidence_loaded = False
_evidence_agent: EvidenceAgent | None = None


def initialize_evidence_runtime() -> None:
    """Initialize the Evidence Agent at application startup."""
    global _evidence_loaded, _evidence_agent

    from agents.evidence.agent import EvidenceAgent

    agent = EvidenceAgent()
    agent.initialize()
    _evidence_agent = agent
    _evidence_loaded = agent.is_loaded
    logger.info("Evidence Agent initialized: loaded=%s", _evidence_loaded)


def get_evidence_agent() -> EvidenceAgent:
    """Return the initialized Evidence Agent instance."""
    if _evidence_agent is None or not _evidence_loaded:
        raise RuntimeError("Evidence Agent is not initialized")
    return _evidence_agent
