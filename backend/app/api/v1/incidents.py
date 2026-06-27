"""Incident management API routes."""

import uuid

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.enums import IncidentStatus, Severity
from app.schemas.executive_report_agent import ExecutiveReportRecordResponse
from app.schemas.guardian_agent import GuardianAuditListResponse
from app.schemas.incident import (
    IncidentCreate,
    IncidentDetailResponse,
    IncidentListResponse,
    IncidentResponse,
    IncidentUpdate,
)
from app.schemas.mitre_agent import MitreFindingListResponse
from app.schemas.response import APIResponse
from app.schemas.response_agent import ResponsePlanRecordResponse
from app.schemas.risk_agent import RiskAssessmentRecordResponse
from app.schemas.threat_intelligence_agent import ThreatIntelligenceFindingListResponse
from app.services.executive_report_agent_service import ExecutiveReportAgentService
from app.services.guardian_agent_service import GuardianAgentService
from app.services.incident_service import IncidentService
from app.services.mitre_agent_service import MitreAgentService
from app.services.response_agent_service import ResponseAgentService
from app.services.risk_agent_service import RiskAgentService
from app.services.threat_intelligence_agent_service import (
    ThreatIntelligenceAgentService,
)
from app.services.timeline.schemas import TimelineResponse
from app.services.timeline_service import TimelineService

router = APIRouter(prefix="/incidents", tags=["incidents"])


def get_incident_service(db: Session = Depends(get_db)) -> IncidentService:
    """Provide an incident service bound to the request database session."""
    return IncidentService(db)


def get_mitre_agent_service(db: Session = Depends(get_db)) -> MitreAgentService:
    """Provide a MITRE Mapping Agent service bound to the request database session."""
    return MitreAgentService(db)


def get_risk_agent_service(db: Session = Depends(get_db)) -> RiskAgentService:
    """Provide a Risk Assessment Agent service bound to the request database session."""
    return RiskAgentService(db)


def get_response_agent_service(db: Session = Depends(get_db)) -> ResponseAgentService:
    """Provide a Response Planning Agent service bound to the request database session."""
    return ResponseAgentService(db)


def get_threat_intelligence_agent_service(
    db: Session = Depends(get_db),
) -> ThreatIntelligenceAgentService:
    """Provide a Threat Intelligence Agent service bound to the request database session."""
    return ThreatIntelligenceAgentService(db)


def get_executive_report_agent_service(
    db: Session = Depends(get_db),
) -> ExecutiveReportAgentService:
    """Provide an Executive Report Agent service bound to the request database session."""
    return ExecutiveReportAgentService(db)


def get_guardian_agent_service(
    db: Session = Depends(get_db),
) -> GuardianAgentService:
    """Provide a Guardian Agent service bound to the request database session."""
    return GuardianAgentService(db)


def get_timeline_service(db: Session = Depends(get_db)) -> TimelineService:
    """Provide a timeline service bound to the request database session."""
    return TimelineService(db)


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


@router.get(
    "/{incident_id}/threat-intelligence",
    response_model=APIResponse[ThreatIntelligenceFindingListResponse],
    summary="Get threat intelligence findings",
    description="Return persisted threat intelligence findings for an incident.",
    responses={
        200: {"description": "Threat intelligence findings retrieved successfully"},
        404: {"description": "Incident not found"},
        422: {"description": "Invalid incident ID format"},
    },
)
def get_incident_threat_intelligence(
    incident_id: uuid.UUID,
    service: ThreatIntelligenceAgentService = Depends(
        get_threat_intelligence_agent_service
    ),
) -> APIResponse[ThreatIntelligenceFindingListResponse]:
    """Return threat intelligence findings for an incident."""
    findings = service.list_findings(incident_id)
    return APIResponse(
        success=True,
        message="Threat intelligence findings retrieved successfully",
        data=findings,
    )


@router.get(
    "/{incident_id}/risk",
    response_model=APIResponse[RiskAssessmentRecordResponse],
    summary="Get risk assessment",
    description="Return the latest persisted risk assessment for an incident.",
    responses={
        200: {"description": "Risk assessment retrieved successfully"},
        404: {"description": "Incident or risk assessment not found"},
        422: {"description": "Invalid incident ID format"},
    },
)
def get_incident_risk_assessment(
    incident_id: uuid.UUID,
    service: RiskAgentService = Depends(get_risk_agent_service),
) -> APIResponse[RiskAssessmentRecordResponse]:
    """Return the latest risk assessment for an incident."""
    assessment = service.get_latest_assessment(incident_id)
    return APIResponse(
        success=True,
        message="Risk assessment retrieved successfully",
        data=assessment,
    )


@router.get(
    "/{incident_id}/response",
    response_model=APIResponse[ResponsePlanRecordResponse],
    summary="Get response plan",
    description="Return the latest persisted response plan for an incident.",
    responses={
        200: {"description": "Response plan retrieved successfully"},
        404: {"description": "Incident or response plan not found"},
        422: {"description": "Invalid incident ID format"},
    },
)
def get_incident_response_plan(
    incident_id: uuid.UUID,
    service: ResponseAgentService = Depends(get_response_agent_service),
) -> APIResponse[ResponsePlanRecordResponse]:
    """Return the latest response plan for an incident."""
    plan = service.get_latest_plan(incident_id)
    return APIResponse(
        success=True,
        message="Response plan retrieved successfully",
        data=plan,
    )


@router.get(
    "/{incident_id}/executive-report",
    response_model=APIResponse[ExecutiveReportRecordResponse],
    summary="Get executive report",
    description="Return the latest persisted executive report for an incident.",
    responses={
        200: {"description": "Executive report retrieved successfully"},
        404: {"description": "Incident or executive report not found"},
        422: {"description": "Invalid incident ID format"},
    },
)
def get_incident_executive_report(
    incident_id: uuid.UUID,
    service: ExecutiveReportAgentService = Depends(get_executive_report_agent_service),
) -> APIResponse[ExecutiveReportRecordResponse]:
    """Return the latest executive report for an incident."""
    report = service.get_latest_report(incident_id)
    return APIResponse(
        success=True,
        message="Executive report retrieved successfully",
        data=report,
    )


@router.get(
    "/{incident_id}/timeline",
    response_model=APIResponse[TimelineResponse],
    summary="Get investigation timeline",
    description="Return a chronologically ordered investigation timeline reconstructed from incident artifacts.",
    responses={
        200: {"description": "Timeline retrieved successfully"},
        404: {"description": "Incident not found"},
        422: {"description": "Invalid incident ID format"},
    },
)
def get_incident_timeline(
    incident_id: uuid.UUID,
    service: TimelineService = Depends(get_timeline_service),
) -> APIResponse[TimelineResponse]:
    """Return the investigation timeline for an incident."""
    timeline = service.get_timeline(incident_id)
    return APIResponse(
        success=True,
        message="Timeline retrieved successfully",
        data=timeline,
    )


@router.get(
    "/{incident_id}/timeline/export",
    summary="Export investigation timeline",
    description="Export the investigation timeline as JSON or Markdown.",
    responses={
        200: {"description": "Timeline exported successfully"},
        404: {"description": "Incident not found or unsupported format"},
        422: {"description": "Invalid incident ID or format"},
    },
)
def export_incident_timeline(
    incident_id: uuid.UUID,
    format: str = Query(
        default="json",
        alias="format",
        description="Export format: json or markdown",
    ),
    service: TimelineService = Depends(get_timeline_service),
) -> Response:
    """Export the investigation timeline in the requested format."""
    content, media_type, suffix = service.export_timeline(incident_id, format)
    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename=timeline-{incident_id}.{suffix}",
        },
    )


@router.get(
    "/{incident_id}/guardian-audits",
    response_model=APIResponse[GuardianAuditListResponse],
    summary="Get Guardian audit records",
    description="Return Guardian validation audit records for an incident.",
    responses={
        200: {"description": "Guardian audit records retrieved successfully"},
        404: {"description": "Incident not found"},
        422: {"description": "Invalid incident ID format"},
    },
)
def get_incident_guardian_audits(
    incident_id: uuid.UUID,
    service: GuardianAgentService = Depends(get_guardian_agent_service),
) -> APIResponse[GuardianAuditListResponse]:
    """Return Guardian audit records for an incident."""
    audits = service.list_audits(incident_id)
    return APIResponse(
        success=True,
        message="Guardian audit records retrieved successfully",
        data=audits,
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
