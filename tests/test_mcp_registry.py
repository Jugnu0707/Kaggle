"""MCP registry tests."""

import pytest
from mcp.registry import ToolDefinition, ToolRegistry
from pydantic import BaseModel
from sqlalchemy.orm import Session


class SampleInput(BaseModel):
    value: str


class SampleOutput(BaseModel):
    result: str


def _sample_handler(_input: SampleInput, _db: Session) -> SampleOutput:
    return SampleOutput(result=_input.value)


def test_registry_rejects_duplicate_tool_registration() -> None:
    """Registering the same tool name twice raises an error."""
    registry = ToolRegistry()
    tool = ToolDefinition(
        name="duplicate_tool",
        description="First registration",
        input_schema=SampleInput.model_json_schema(),
        output_schema=SampleOutput.model_json_schema(),
        input_model=SampleInput,
        output_model=SampleOutput,
        handler=_sample_handler,
    )
    registry.register(tool)

    duplicate = tool.model_copy(update={"description": "Second registration"})
    with pytest.raises(ValueError, match="already registered"):
        registry.register(duplicate)


def test_registry_lists_tools_in_sorted_order() -> None:
    """Registered tool names are returned in sorted order."""
    registry = ToolRegistry()
    for name in ("zebra", "alpha", "middle"):
        registry.register(
            ToolDefinition(
                name=name,
                description=f"{name} tool",
                input_schema=SampleInput.model_json_schema(),
                output_schema=SampleOutput.model_json_schema(),
                input_model=SampleInput,
                output_model=SampleOutput,
                handler=_sample_handler,
            )
        )

    assert registry.list_tools() == ["alpha", "middle", "zebra"]
