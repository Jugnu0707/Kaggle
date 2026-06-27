"""Executive Report Agent — ADK configuration and generation entry point."""

from __future__ import annotations

from pathlib import Path

from google.adk.agents import Agent
from sqlalchemy.orm import Session

from agents.executive_report.models import ExecutiveReportInput, ExecutiveReportResult
from agents.executive_report.service import ExecutiveReportService
from app.core.logging import get_logger

logger = get_logger(__name__)

EXECUTIVE_REPORT_AGENT_NAME = "executive_report"
EXECUTIVE_REPORT_AGENT_DESCRIPTION = (
    "Transforms incident analysis into executive-friendly reports for CISOs, managers, "
    "and business leaders. AI-first with automatic template fallback. Generates structured "
    "JSON and Markdown — no PDF generation."
)
PROMPT_PATH = Path(__file__).with_name("prompt.md")


def load_executive_report_prompt() -> str:
    """Load the versioned Executive Report Agent system prompt from disk."""
    return PROMPT_PATH.read_text(encoding="utf-8")


class ExecutiveReportAgent:
    """Google ADK Executive Report Agent — AI-first with automatic fallback."""

    def __init__(self) -> None:
        self._loaded = False
        self._adk_agent = Agent(
            name=EXECUTIVE_REPORT_AGENT_NAME,
            description=EXECUTIVE_REPORT_AGENT_DESCRIPTION,
            instruction=load_executive_report_prompt(),
            input_schema=ExecutiveReportInput,
            output_schema=ExecutiveReportResult,
        )

    @property
    def name(self) -> str:
        return self._adk_agent.name

    @property
    def description(self) -> str:
        return self._adk_agent.description

    @property
    def adk_agent(self) -> Agent:
        return self._adk_agent

    def initialize(self) -> None:
        self._loaded = True
        logger.info(
            "Executive Report Agent configured: name=%s description=%s",
            self.name,
            self.description,
        )

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def generate(
        self, request: ExecutiveReportInput, db: Session
    ) -> ExecutiveReportResult:
        return ExecutiveReportService(db).generate(request)
