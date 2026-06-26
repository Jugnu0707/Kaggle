"""Incident management API routes."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.enums import IncidentStatus, Severity
from app.schemas.incident import (
    IncidentCreate,
    IncidentDetailResponse,
    IncidentListResponse,
    IncidentResponse,
    IncidentUpdate,
)
from app.schemas.mitre_agent import MitreFindingListResponse
from app.schemas.response import APIResponse
from app.services.incident_service import IncidentService
from app.services.mitre_agent_service import MitreAgentService

router = APIRouter(prefix="/incidents", tags=["incidents"])


def get_incident_service(db: Session = Depends(get_db)) -> IncidentService:
    """Provide an incident service bound to the request database session."""
    return IncidentService(db)


def get_mitre_agent_service(db: Session = Depends(get_db)) -> MitreAgentService:
    """Provide a MITRE Mapping Agent service bound to the request database session."""
    return MitreAgentService(db)


@router.post(
    "",
    response_model=APIResponse[IncidentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create incident",
    description="Create a new security incident record.",
    responses={
        201: {"description": "Incident created successfully"},
        422: {"description": "Validation error"},
    },
)
def create_incident(
    payload: IncidentCreate,
    service: IncidentService = Depends(get_incident_service),
) -> APIResponse[IncidentResponse]:
    """Create a new incident."""
    incident = service.create_incident(payload)
    return APIResponse(
        success=True,
        message="Incident created successfully",
        data=incident,
    )


@router.get(
    "",
    response_model=APIResponse[IncidentListResponse],
    summary="List incidents",
    description=(
        "Return a paginated list of incidents with optional severity, status, "
        "and search filters. Results are sorted by created_at descending."
    ),
    responses={
        200: {"description": "Incidents retrieved successfully"},
        400: {"description": "Invalid pagination parameters"},
        422: {"description": "Validation error"},
    },
)
def list_incidents(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    severity: Severity | None = Query(default=None, description="Filter by severity"),
    status: IncidentStatus | None = Query(default=None, description="Filter by status"),
    search: str | None = Query(
        default=None, description="Search title and description"
    ),
    service: IncidentService = Depends(get_incident_service),
) -> APIResponse[IncidentListResponse]:
    """List incidents with pagination and filters."""
    incidents = service.list_incidents(
        page=page,
        page_size=page_size,
        severity=severity,
        status=status,
        search=search,
    )
    return APIResponse(
        success=True,
        message="Incidents retrieved successfully",
        data=incidents,
    )


@router.get(
    "/{incident_id}",
    response_model=APIResponse[IncidentDetailResponse],
    summary="Get incident",
    description="Return a single incident with investigation details and evidence count.",
    responses={
        200: {"description": "Incident retrieved successfully"},
        404: {"description": "Incident not found"},
        422: {"description": "Invalid incident ID format"},
    },
)
def get_incident(
    incident_id: uuid.UUID,
    service: IncidentService = Depends(get_incident_service),
) -> APIResponse[IncidentDetailResponse]:
    """Return one incident by ID."""
    incident = service.get_incident(incident_id)
    return APIResponse(
        success=True,
        message="Incident retrieved successfully",
        data=incident,
    )


@router.get(
    "/{incident_id}/mitre",
    response_model=APIResponse[MitreFindingListResponse],
    summary="Get MITRE ATT&CK mapping",
    description="Return persisted MITRE ATT&CK technique mappings for an incident.",
    responses={
        200: {"description": "MITRE mappings retrieved successfully"},
        404: {"description": "Incident not found"},
        422: {"description": "Invalid incident ID format"},
    },
)
def get_incident_mitre_mappings(
    incident_id: uuid.UUID,
    service: MitreAgentService = Depends(get_mitre_agent_service),
) -> APIResponse[MitreFindingListResponse]:
    """Return MITRE ATT&CK findings for an incident."""
    findings = service.list_findings(incident_id)
    return APIResponse(
        success=True,
        message="MITRE mappings retrieved successfully",
        data=findings,
    )


@router.put(
    "/{incident_id}",
    response_model=APIResponse[IncidentResponse],
    summary="Update incident",
    description="Update mutable incident fields: title, description, severity, and status.",
    responses={
        200: {"description": "Incident updated successfully"},
        400: {"description": "Invalid update payload"},
        404: {"description": "Incident not found"},
        422: {"description": "Validation error"},
    },
)
def update_incident(
    incident_id: uuid.UUID,
    payload: IncidentUpdate,
    service: IncidentService = Depends(get_incident_service),
) -> APIResponse[IncidentResponse]:
    """Update an existing incident."""
    incident = service.update_incident(incident_id, payload)
    return APIResponse(
        success=True,
        message="Incident updated successfully",
        data=incident,
    )


@router.delete(
    "/{incident_id}",
    response_model=APIResponse[IncidentResponse],
    summary="Delete incident",
    description="Soft delete an incident by setting deleted_at without removing the record.",
    responses={
        200: {"description": "Incident deleted successfully"},
        404: {"description": "Incident not found"},
        422: {"description": "Invalid incident ID format"},
    },
)
def delete_incident(
    incident_id: uuid.UUID,
    service: IncidentService = Depends(get_incident_service),
) -> APIResponse[IncidentResponse]:
    """Soft delete an incident."""
    incident = service.delete_incident(incident_id)
    return APIResponse(
        success=True,
        message="Incident deleted successfully",
        data=incident,
    )
