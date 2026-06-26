"""Coordinator Agent — ADK configuration and orchestration entry point."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from google.adk.agents import Agent
from sqlalchemy.orm import Session

from agents.coordinator.models import CoordinatorInput, OrchestrationPlan
from agents.coordinator.orchestrator import CoordinatorOrchestrator
from app.core.logging import get_logger

logger = get_logger(__name__)

COORDINATOR_NAME = "coordinator"
COORDINATOR_DESCRIPTION = (
    "Orchestrates the Oz AI incident response pipeline by validating requests "
    "and generating structured execution plans."
)
PROMPT_PATH = Path(__file__).with_name("prompt.md")


def load_coordinator_prompt() -> str:
    """Load the versioned Coordinator system prompt from disk."""
    return PROMPT_PATH.read_text(encoding="utf-8")


class CoordinatorAgent:
    """Google ADK Coordinator Agent — plan generation only, no LLM execution."""

    PLACEHOLDER_RESPONSE: dict[str, str] = {
        "status": "Coordinator initialized",
        "message": "Ready for agent orchestration.",
    }

    def __init__(self) -> None:
        self._loaded = False
        self._orchestrator = CoordinatorOrchestrator()
        self._adk_agent = Agent(
            name=COORDINATOR_NAME,
            description=COORDINATOR_DESCRIPTION,
            instruction=load_coordinator_prompt(),
            input_schema=CoordinatorInput,
            output_schema=OrchestrationPlan,
        )

    @property
    def name(self) -> str:
        """Return the ADK agent name."""
        return self._adk_agent.name

    @property
    def description(self) -> str:
        """Return the ADK agent description."""
        return self._adk_agent.description

    @property
    def adk_agent(self) -> Agent:
        """Return the underlying Google ADK agent configuration."""
        return self._adk_agent

    def initialize(self) -> None:
        """Initialize the coordinator without invoking the LLM."""
        self._loaded = True
        logger.info(
            "Coordinator Agent configured: name=%s description=%s",
            self.name,
            self.description,
        )

    @property
    def is_loaded(self) -> bool:
        """Return whether the coordinator finished initialization."""
        return self._loaded

    def handle_request(self, request: dict[str, Any] | None = None) -> dict[str, str]:
        """Return startup health information without orchestration."""
        _ = request
        return dict(self.PLACEHOLDER_RESPONSE)

    def orchestrate(self, request: CoordinatorInput, db: Session) -> OrchestrationPlan:
        """Validate the request and return an orchestration plan."""
        plan, _duration_ms = self._orchestrator.build_plan(request, db)
        return plan
