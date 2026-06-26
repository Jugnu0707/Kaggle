"""Risk Assessment Agent runtime initialization and status tracking."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.core.logging import get_logger

if TYPE_CHECKING:
    from agents.risk.agent import RiskAssessmentAgent

logger = get_logger(__name__)

_risk_loaded = False
_risk_agent: RiskAssessmentAgent | None = None


def initialize_risk_runtime() -> None:
    """Initialize the Risk Assessment Agent at application startup."""
    global _risk_loaded, _risk_agent

    from agents.risk.agent import RiskAssessmentAgent

    agent = RiskAssessmentAgent()
    agent.initialize()
    _risk_agent = agent
    _risk_loaded = agent.is_loaded
    logger.info("Risk Assessment Agent initialized: loaded=%s", _risk_loaded)


def get_risk_agent() -> RiskAssessmentAgent:
    """Return the initialized Risk Assessment Agent instance."""
    if _risk_agent is None or not _risk_loaded:
        raise RuntimeError("Risk Assessment Agent is not initialized")
    return _risk_agent
