"""Investigation workflow API routes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.investigation import InvestigationPackageResponse, RunInvestigationRequest
from app.schemas.response import APIResponse
from app.services.investigation_workflow_service import InvestigationWorkflowService

router = APIRouter(prefix="/investigations", tags=["investigations"])


def get_investigation_workflow_service(
    db: Session = Depends(get_db),
) -> InvestigationWorkflowService:
    """Provide an investigation workflow service bound to the request database session."""
    return InvestigationWorkflowService(db)


@router.post(
    "/run",
    response_model=APIResponse[InvestigationPackageResponse],
    status_code=status.HTTP_200_OK,
    summary="Run end-to-end investigation",
    description=(
        "Execute the full Coordinator investigation pipeline: Evidence, Guardian validation, "
        "Threat Intelligence, MITRE, Risk, Response, Executive Report, Timeline Engine, and "
        "Evaluation Engine. Returns a consolidated investigation package."
    ),
    responses={
        status.HTTP_200_OK: {"description": "Investigation completed or partially completed"},
        status.HTTP_404_NOT_FOUND: {"description": "Incident not found"},
    },
)
def run_investigation(
    payload: RunInvestigationRequest,
    service: InvestigationWorkflowService = Depends(get_investigation_workflow_service),
) -> APIResponse[InvestigationPackageResponse]:
    """Run the complete investigation workflow for an incident."""
    result = service.run(payload.incident_id)
    return APIResponse(
        success=True,
        message="Investigation workflow completed",
        data=result,
    )


@router.get(
    "/runs/{run_id}",
    response_model=APIResponse[InvestigationPackageResponse],
    summary="Get investigation run",
    description="Return a persisted investigation run package by execution ID.",
    responses={
        status.HTTP_200_OK: {"description": "Investigation run retrieved successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "Investigation run not found"},
    },
)
def get_investigation_run(
    run_id: uuid.UUID,
    service: InvestigationWorkflowService = Depends(get_investigation_workflow_service),
) -> APIResponse[InvestigationPackageResponse]:
    """Return details for a prior investigation run."""
    result = service.get_run(run_id)
    return APIResponse(
        success=True,
        message="Investigation run retrieved successfully",
        data=result,
    )
