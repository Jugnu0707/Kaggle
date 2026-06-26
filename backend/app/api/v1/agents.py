"""Agent orchestration API routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.evidence_agent import EvidenceCollectRequest, EvidenceCollectResponse
from app.schemas.orchestration import OrchestrateRequest, OrchestrateResponse
from app.schemas.response import APIResponse
from app.services.evidence_agent_service import EvidenceAgentService
from app.services.orchestration_service import OrchestrationService

router = APIRouter(prefix="/agents", tags=["agents"])


def get_orchestration_service(db: Session = Depends(get_db)) -> OrchestrationService:
    """Provide an orchestration service bound to the request database session."""
    return OrchestrationService(db)


def get_evidence_agent_service(db: Session = Depends(get_db)) -> EvidenceAgentService:
    """Provide an Evidence Agent service bound to the request database session."""
    return EvidenceAgentService(db)


@router.post(
    "/evidence",
    response_model=APIResponse[EvidenceCollectResponse],
    status_code=status.HTTP_200_OK,
    summary="Collect incident evidence",
    description=(
        "Collect, validate, normalize, and summarize evidence from an uploaded "
        "log file for an incident. No threat analysis or LLM reasoning is performed."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Evidence collected successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Evidence collected",
                        "data": {
                            "status": "completed",
                            "evidence_summary": {
                                "file_type": "application_log",
                                "total_entries": 3,
                                "time_range": "2026-06-26T10:00:00 to 2026-06-26T11:00:00",
                                "possible_log_source": "Generic application log",
                                "data_quality_observations": [
                                    "Sample entries are available for review",
                                    "Timestamps detected in log entries",
                                ],
                            },
                            "evidence_package": {
                                "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                "uploaded_file_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                                "file_size": 256,
                                "number_of_lines": 3,
                                "detected_log_type": "application_log",
                                "sample_entries": [
                                    "2026-06-26T10:00:00 ERROR process started"
                                ],
                                "collection_timestamp": "2026-06-26T12:00:00Z",
                            },
                        },
                    }
                }
            },
        },
        status.HTTP_404_NOT_FOUND: {"description": "Incident or log file not found"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error"},
    },
)
def collect_evidence(
    payload: EvidenceCollectRequest,
    service: EvidenceAgentService = Depends(get_evidence_agent_service),
) -> APIResponse[EvidenceCollectResponse]:
    """Collect and summarize evidence from an uploaded log file."""
    result = service.collect(payload)
    return APIResponse(
        success=True,
        message="Evidence collected",
        data=result,
    )


@router.post(
    "/orchestrate",
    response_model=APIResponse[OrchestrateResponse],
    status_code=status.HTTP_200_OK,
    summary="Generate orchestration plan",
    description=(
        "Accept an incident ID or uploaded log ID, validate the request, invoke "
        "the Evidence Agent when a log file is present, and return a structured "
        "orchestration plan. Remaining specialist agents are placeholders."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Orchestration plan generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Orchestration plan generated",
                        "data": {
                            "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            "log_id": None,
                            "workflow_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
                            "status": "accepted",
                            "workflow": [
                                "Evidence Agent",
                                "Threat Intelligence Agent",
                                "MITRE Mapping Agent",
                                "Risk Assessment Agent",
                                "Response Planning Agent",
                                "Executive Report Agent",
                                "Guardian Agent",
                            ],
                        },
                    }
                }
            },
        },
        status.HTTP_404_NOT_FOUND: {"description": "Incident or log file not found"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error"},
    },
)
def orchestrate_agents(
    payload: OrchestrateRequest,
    service: OrchestrationService = Depends(get_orchestration_service),
) -> APIResponse[OrchestrateResponse]:
    """Generate a Coordinator orchestration plan for an incident or log."""
    plan = service.orchestrate(payload)
    return APIResponse(
        success=True,
        message="Orchestration plan generated",
        data=plan,
    )
