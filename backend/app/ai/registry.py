"""Registered AI agent metadata for the ADK runtime."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger(__name__)

REGISTERED_AGENT_NAMES: tuple[str, ...] = (
    "Coordinator Agent",
    "Evidence Agent",
    "Threat Intelligence Agent",
    "MITRE Mapping Agent",
    "Risk Assessment Agent",
    "Response Planning Agent",
    "Executive Report Agent",
    "Guardian Agent",
)


class AgentDefinition(BaseModel):
    """Metadata for one registered ADK agent."""

    name: str
    description: str
    version: str = Field(default="1.0.0")


class AgentRegistry:
    """Registry of agents available through the AI runtime."""

    def __init__(self) -> None:
        self._agents: dict[str, AgentDefinition] = {}

    def register(self, definition: AgentDefinition) -> None:
        """Register an agent by name."""
        if definition.name in self._agents:
            raise ValueError(f"Agent already registered: {definition.name}")
        self._agents[definition.name] = definition
        logger.info("Registered ADK agent: %s v%s", definition.name, definition.version)

    def list_agents(self) -> list[AgentDefinition]:
        """Return all registered agents sorted by name."""
        return sorted(self._agents.values(), key=lambda item: item.name)

    def agent_count(self) -> int:
        """Return the number of registered agents."""
        return len(self._agents)

    def get(self, name: str) -> AgentDefinition | None:
        """Return one agent definition."""
        return self._agents.get(name)


def build_default_agent_registry() -> AgentRegistry:
    """Populate the default eight-agent registry."""
    registry = AgentRegistry()
    descriptions = {
        "Coordinator Agent": "Orchestrates investigation workflows and agent sequencing.",
        "Evidence Agent": "Collects and normalizes log evidence.",
        "Threat Intelligence Agent": "Enriches IOCs with threat intelligence.",
        "MITRE Mapping Agent": "Maps evidence to MITRE ATT&CK techniques.",
        "Risk Assessment Agent": "Assesses incident severity and business impact.",
        "Response Planning Agent": "Generates containment and remediation plans.",
        "Executive Report Agent": "Produces technical and executive summaries.",
        "Guardian Agent": "Validates outputs for safety, PII, and injection.",
    }
    for name in REGISTERED_AGENT_NAMES:
        registry.register(
            AgentDefinition(
                name=name,
                description=descriptions[name],
                version="1.0.0",
            )
        )
    return registry
