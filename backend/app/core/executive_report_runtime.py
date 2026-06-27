"""Executive Report Agent runtime initialization and status tracking."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.core.logging import get_logger

if TYPE_CHECKING:
    from agents.executive_report.agent import ExecutiveReportAgent

logger = get_logger(__name__)

_executive_report_loaded = False
_executive_report_agent: ExecutiveReportAgent | None = None


def initialize_executive_report_runtime() -> None:
    """Initialize the Executive Report Agent at application startup."""
    global _executive_report_loaded, _executive_report_agent

    from agents.executive_report.agent import ExecutiveReportAgent

    agent = ExecutiveReportAgent()
    agent.initialize()
    _executive_report_agent = agent
    _executive_report_loaded = agent.is_loaded
    logger.info(
        "Executive Report Agent initialized: loaded=%s", _executive_report_loaded
    )


def get_executive_report_agent() -> ExecutiveReportAgent:
    """Return the initialized Executive Report Agent instance."""
    if _executive_report_agent is None or not _executive_report_loaded:
        raise RuntimeError("Executive Report Agent is not initialized")
    return _executive_report_agent
