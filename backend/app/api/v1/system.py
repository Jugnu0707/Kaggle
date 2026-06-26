"""System information endpoints."""

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.core.mcp_runtime import get_mcp_status
from app.db.database import get_db, get_table_names
from app.schemas.response import APIResponse

router = APIRouter(prefix="/system", tags=["system"])


class TablesData(BaseModel):
    """Database table listing payload."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tables": [
                    "audit_logs",
                    "evidence",
                    "incidents",
                    "investigations",
                    "log_files",
                ],
            }
        }
    )

    tables: list[str] = Field(description="Sorted list of database table names")


class MCPStatusData(BaseModel):
    """MCP server status payload."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "mcp": True,
                "tool_count": 5,
                "tools": [
                    "health",
                    "incident_details",
                    "list_incidents",
                    "list_logs",
                    "system_info",
                ],
            }
        }
    )

    mcp: bool = Field(description="Whether the MCP server is running")
    tool_count: int = Field(description="Number of registered MCP tools")
    tools: list[str] = Field(description="Sorted list of registered MCP tool names")


@router.get(
    "/tables",
    response_model=APIResponse[TablesData],
    summary="List database tables",
    description="Return all tables detected in the connected SQLite database.",
    responses={
        status.HTTP_200_OK: {"description": "Tables retrieved successfully"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Database introspection failed"
        },
    },
)
def list_database_tables(db: Session = Depends(get_db)) -> APIResponse[TablesData]:
    """Return all tables detected in the connected database."""
    return APIResponse(
        success=True,
        message="Tables retrieved",
        data=TablesData(tables=get_table_names(db)),
    )


@router.get(
    "/mcp",
    response_model=APIResponse[MCPStatusData],
    summary="MCP server status",
    description="Return MCP server status and the list of registered tools.",
    responses={status.HTTP_200_OK: {"description": "MCP status retrieved successfully"}},
)
def get_mcp_server_status() -> APIResponse[MCPStatusData]:
    """Return MCP server status and registered tool inventory."""
    status_data = get_mcp_status()
    return APIResponse(
        success=True,
        message="MCP status retrieved",
        data=MCPStatusData(
            mcp=bool(status_data["mcp"]),
            tool_count=int(status_data["tool_count"]),
            tools=list(status_data["tools"]),
        ),
    )
