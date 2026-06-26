"""Response Planning Agent — ADK configuration and planning entry point."""

from __future__ import annotations

from pathlib import Path

from google.adk.agents import Agent
from sqlalchemy.orm import Session

from agents.response.models import ResponsePlanInput, ResponsePlanResult
from agents.response.service import ResponsePlanningService
from app.core.logging import get_logger

logger = get_logger(__name__)

RESPONSE_AGENT_NAME = "response_planning"
RESPONSE_AGENT_DESCRIPTION = (
    "Produces structured incident response plans from incident, evidence, MITRE, "
    "threat intelligence, and risk assessment inputs. Recommendations only — "
    "never executes remediation. AI-first with automatic rule-based fallback."
)
PROMPT_PATH = Path(__file__).with_name("prompt.md")


def load_response_prompt() -> str:
    """Load the versioned Response Planning Agent system prompt from disk."""
    return PROMPT_PATH.read_text(encoding="utf-8")


class ResponsePlanningAgent:
    """Google ADK Response Planning Agent — AI-first with automatic fallback."""

    def __init__(self) -> None:
        self._loaded = False
        self._adk_agent = Agent(
            name=RESPONSE_AGENT_NAME,
            description=RESPONSE_AGENT_DESCRIPTION,
            instruction=load_response_prompt(),
            input_schema=ResponsePlanInput,
            output_schema=ResponsePlanResult,
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
            "Response Planning Agent configured: name=%s description=%s",
            self.name,
            self.description,
        )

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def plan(self, request: ResponsePlanInput, db: Session) -> ResponsePlanResult:
        return ResponsePlanningService(db).plan(request)
