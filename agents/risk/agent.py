"""Risk Assessment Agent — ADK configuration and assessment entry point."""

from __future__ import annotations

from pathlib import Path

from google.adk.agents import Agent
from sqlalchemy.orm import Session

from agents.risk.models import RiskAssessmentInput, RiskAssessmentResult
from agents.risk.service import RiskAssessmentService
from app.core.logging import get_logger

logger = get_logger(__name__)

RISK_AGENT_NAME = "risk_assessment"
RISK_AGENT_DESCRIPTION = (
    "Produces structured enterprise risk assessments from incident, evidence, "
    "MITRE, and threat intelligence inputs with AI-first execution and automatic "
    "rule-based fallback when Gemini is unavailable."
)
PROMPT_PATH = Path(__file__).with_name("prompt.md")


def load_risk_prompt() -> str:
    """Load the versioned Risk Assessment Agent system prompt from disk."""
    return PROMPT_PATH.read_text(encoding="utf-8")


class RiskAssessmentAgent:
    """Google ADK Risk Assessment Agent — AI-first with automatic fallback."""

    def __init__(self) -> None:
        self._loaded = False
        self._adk_agent = Agent(
            name=RISK_AGENT_NAME,
            description=RISK_AGENT_DESCRIPTION,
            instruction=load_risk_prompt(),
            input_schema=RiskAssessmentInput,
            output_schema=RiskAssessmentResult,
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
            "Risk Assessment Agent configured: name=%s description=%s",
            self.name,
            self.description,
        )

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def assess(self, request: RiskAssessmentInput, db: Session) -> RiskAssessmentResult:
        return RiskAssessmentService(db).assess(request)
