"""MCP tool registry with automatic registration support."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Session

T = TypeVar("T")


class ToolResult(BaseModel, Generic[T]):
    """Standard MCP tool response contract."""

    success: bool
    data: T | None = None
    error: str | None = None


class ToolDefinition(BaseModel):
    """Registered MCP tool metadata and handler."""

    model_config = {"arbitrary_types_allowed": True}

    name: str
    description: str
    version: str = "1.0.0"
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    input_model: type[BaseModel]
    output_model: type[BaseModel]
    handler: Callable[[BaseModel, Session], BaseModel]


class ToolRegistry:
    """Registry that stores MCP tools and prevents duplicate registration."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        """Register a tool by name."""
        if tool.name in self._tools:
            raise ValueError(f"MCP tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> ToolDefinition | None:
        """Return a registered tool definition."""
        return self._tools.get(name)

    def list_tools(self) -> list[str]:
        """Return sorted registered tool names."""
        return sorted(self._tools.keys())

    def tool_count(self) -> int:
        """Return the number of registered tools."""
        return len(self._tools)

    def list_tool_definitions(self) -> list[ToolDefinition]:
        """Return all registered tool definitions sorted by name."""
        return [self._tools[name] for name in self.list_tools()]

    def invoke(
        self, name: str, payload: dict[str, Any], db: Session
    ) -> ToolResult[Any]:
        """Validate input, execute a tool handler, and return a structured result."""
        tool = self.get_tool(name)
        if tool is None:
            return ToolResult(success=False, error=f"Unknown MCP tool: {name}")

        try:
            validated_input = tool.input_model.model_validate(payload)
            result = tool.handler(validated_input, db)
            validated_output = tool.output_model.model_validate(result.model_dump())
            return ToolResult(success=True, data=validated_output)
        except Exception as exc:  # noqa: BLE001 - tool boundary captures all failures
            return ToolResult(success=False, error=str(exc))


_registry = ToolRegistry()


def get_registry() -> ToolRegistry:
    """Return the process-wide MCP tool registry."""
    return _registry


def register_tool(
    *,
    name: str,
    description: str,
    input_model: type[BaseModel],
    output_model: type[BaseModel],
    version: str = "1.0.0",
) -> Callable[[Callable[[BaseModel, Session], BaseModel]], Callable[..., BaseModel]]:
    """Decorator that registers an MCP tool with input and output schemas."""

    def decorator(
        handler: Callable[[BaseModel, Session], BaseModel],
    ) -> Callable[[BaseModel, Session], BaseModel]:
        get_registry().register(
            ToolDefinition(
                name=name,
                description=description,
                version=version,
                input_schema=input_model.model_json_schema(),
                output_schema=output_model.model_json_schema(),
                input_model=input_model,
                output_model=output_model,
                handler=handler,
            )
        )
        return handler

    return decorator
