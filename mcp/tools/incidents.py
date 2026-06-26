"""MCP incident tools."""

import uuid

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.schemas.enums import IncidentStatus, Severity
from app.schemas.incident import IncidentDetailResponse, IncidentListResponse
from app.services.incident_service import IncidentService
from mcp.registry import register_tool


class ListIncidentsInput(BaseModel):
    """Input schema for listing incidents."""

    model_config = ConfigDict(extra="forbid")

    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=10, ge=1, le=100, description="Items per page")
    severity: Severity | None = Field(default=None, description="Optional severity filter")
    status: IncidentStatus | None = Field(default=None, description="Optional status filter")
    search: str | None = Field(default=None, description="Optional title search term")


class ListIncidentsOutput(BaseModel):
    """Output schema for listing incidents."""

    incidents: IncidentListResponse


class IncidentDetailsInput(BaseModel):
    """Input schema for retrieving one incident."""

    model_config = ConfigDict(extra="forbid")

    incident_id: uuid.UUID = Field(description="Unique incident identifier")


class IncidentDetailsOutput(BaseModel):
    """Output schema for retrieving one incident."""

    incident: IncidentDetailResponse


@register_tool(
    name="list_incidents",
    description="Return a paginated list of incidents.",
    input_model=ListIncidentsInput,
    output_model=ListIncidentsOutput,
)
def list_incidents_tool(input_data: ListIncidentsInput, db: Session) -> ListIncidentsOutput:
    """Return all incidents using the incident service layer."""
    incidents = IncidentService(db).list_incidents(
        page=input_data.page,
        page_size=input_data.page_size,
        severity=input_data.severity,
        status=input_data.status,
        search=input_data.search,
    )
    return ListIncidentsOutput(incidents=incidents)


@register_tool(
    name="incident_details",
    description="Return details for a single incident.",
    input_model=IncidentDetailsInput,
    output_model=IncidentDetailsOutput,
)
def incident_details_tool(
    input_data: IncidentDetailsInput, db: Session
) -> IncidentDetailsOutput:
    """Return one incident by ID using the incident service layer."""
    incident = IncidentService(db).get_incident(input_data.incident_id)
    return IncidentDetailsOutput(incident=incident)
