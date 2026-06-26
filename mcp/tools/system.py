"""MCP system information tool."""

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.core.adk_runtime import get_adk_status
from app.core.config import settings
from mcp.registry import register_tool
from mcp.server import get_mcp_server


class SystemInfoInput(BaseModel):
    """Input schema for the system information MCP tool."""

    model_config = ConfigDict(extra="forbid")


class ADKStatus(BaseModel):
    """ADK runtime status fields."""

    adk: bool
    coordinator: bool


class MCPStatus(BaseModel):
    """MCP server status fields."""

    mcp: bool
    tool_count: int
    tools: list[str]


class SystemInfoOutput(BaseModel):
    """Output schema for the system information MCP tool."""

    version: str = Field(description="Application version")
    database: str = Field(description="Configured database connection string")
    adk_status: ADKStatus
    mcp_status: MCPStatus


@register_tool(
    name="system_info",
    description="Return application version, database, ADK status, and MCP status.",
    input_model=SystemInfoInput,
    output_model=SystemInfoOutput,
)
def system_info_tool(_input: SystemInfoInput, _db: Session) -> SystemInfoOutput:
    """Return system information for agents and operators."""
    adk_status = get_adk_status()
    server = get_mcp_server()
    return SystemInfoOutput(
        version=settings.app_version,
        database=settings.database_url,
        adk_status=ADKStatus(
            adk=adk_status["adk"],
            coordinator=adk_status["coordinator"],
        ),
        mcp_status=MCPStatus(
            mcp=server.is_running(),
            tool_count=server.registry.tool_count(),
            tools=server.registry.list_tools(),
        ),
    )
