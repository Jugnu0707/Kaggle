"""MCP log file tools."""

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.schemas.log_file import LogFileListResponse
from app.services.log_service import LogService
from mcp.registry import register_tool


class ListLogsInput(BaseModel):
    """Input schema for listing uploaded log metadata."""

    model_config = ConfigDict(extra="forbid")

    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=10, ge=1, le=100, description="Items per page")


class ListLogsOutput(BaseModel):
    """Output schema for listing uploaded log metadata."""

    logs: LogFileListResponse


@register_tool(
    name="list_logs",
    description="Return uploaded log file metadata.",
    input_model=ListLogsInput,
    output_model=ListLogsOutput,
)
def list_logs_tool(input_data: ListLogsInput, db: Session) -> ListLogsOutput:
    """Return uploaded log metadata using the log service layer."""
    logs = LogService(db).list_log_files(
        page=input_data.page,
        page_size=input_data.page_size,
    )
    return ListLogsOutput(logs=logs)
