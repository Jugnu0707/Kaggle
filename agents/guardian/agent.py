"""Guardian Agent — ADK configuration and validation entry point."""

from __future__ import annotations

from google.adk.agents import Agent

from agents.guardian.schemas import GuardianValidateInput, GuardianValidationResult
from agents.guardian.service import GuardianService
from app.core.logging import get_logger

logger = get_logger(__name__)

GUARDIAN_AGENT_NAME = "guardian"
GUARDIAN_AGENT_DESCRIPTION = (
    "Validates AI agent outputs for security, governance, schema compliance, "
    "prompt injection, secret exposure, PII leakage, confidence thresholds, "
    "and mandatory field completeness before responses reach users."
)


class GuardianAgent:
    """Google ADK Guardian Agent — AI output validation and governance."""

    def __init__(self) -> None:
        self._loaded = False
        self._service = GuardianService()
        self._adk_agent = Agent(
            name=GUARDIAN_AGENT_NAME,
            description=GUARDIAN_AGENT_DESCRIPTION,
            instruction=(
                "Validate specialist agent outputs for security and governance. "
                "Never modify approved architecture. Mask secrets and PII before approval."
            ),
            input_schema=GuardianValidateInput,
            output_schema=GuardianValidationResult,
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
            "Guardian Agent configured: name=%s description=%s",
            self.name,
            self.description,
        )

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def validate(self, request: GuardianValidateInput) -> GuardianValidationResult:
        return self._service.validate(request)
