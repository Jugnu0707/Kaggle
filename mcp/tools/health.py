"""MCP health tool."""

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.state import get_uptime_seconds
from app.db.database import check_database_connection
from mcp.registry import register_tool


class HealthInput(BaseModel):
    """Input schema for the health MCP tool."""

    model_config = ConfigDict(extra="forbid")


class HealthOutput(BaseModel):
    """Output schema for the health MCP tool."""

    status: str = Field(description="Overall application health status")
    application_name: str
    version: str
    database_connected: bool
    uptime_seconds: float
    timestamp: str = Field(description="ISO-8601 timestamp for the health check")


@register_tool(
    name="health",
    description="Return application health status.",
    input_model=HealthInput,
    output_model=HealthOutput,
)
def health_tool(_input: HealthInput, db: Session) -> HealthOutput:
    """Return application health information."""
    return HealthOutput(
        status="healthy",
        application_name=settings.app_name,
        version=settings.app_version,
        database_connected=check_database_connection(db),
        uptime_seconds=get_uptime_seconds(),
        timestamp=datetime.now(UTC).isoformat(),
    )
