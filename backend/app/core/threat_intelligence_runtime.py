"""Threat Intelligence Agent runtime initialization and status tracking."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.core.logging import get_logger

if TYPE_CHECKING:
    from agents.threat_intelligence.agent import ThreatIntelligenceAgent

logger = get_logger(__name__)

_threat_intelligence_loaded = False
_threat_intelligence_agent: ThreatIntelligenceAgent | None = None


def initialize_threat_intelligence_runtime() -> None:
    """Initialize the Threat Intelligence Agent at application startup."""
    global _threat_intelligence_loaded, _threat_intelligence_agent

    from agents.threat_intelligence.agent import ThreatIntelligenceAgent

    agent = ThreatIntelligenceAgent()
    agent.initialize()
    _threat_intelligence_agent = agent
    _threat_intelligence_loaded = agent.is_loaded
    logger.info(
        "Threat Intelligence Agent initialized: loaded=%s",
        _threat_intelligence_loaded,
    )


def get_threat_intelligence_agent() -> ThreatIntelligenceAgent:
    """Return the initialized Threat Intelligence Agent instance."""
    if _threat_intelligence_agent is None or not _threat_intelligence_loaded:
        raise RuntimeError("Threat Intelligence Agent is not initialized")
    return _threat_intelligence_agent
