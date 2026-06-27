"""Evaluation metrics API routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.evaluation import AgentEvaluationDetail, EvaluationOverview
from app.schemas.response import APIResponse
from app.services.evaluation_service import EvaluationService

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


def get_evaluation_service(db: Session = Depends(get_db)) -> EvaluationService:
    """Provide an evaluation service bound to the request database session."""
    return EvaluationService(db)


@router.get(
    "",
    response_model=APIResponse[EvaluationOverview],
    summary="Get evaluation overview",
    description=(
        "Return overall health score and per-agent evaluation summaries. "
        "Runs offline benchmarks automatically when no metrics are stored."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Evaluation overview retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Evaluation overview retrieved successfully",
                        "data": {
                            "overall_score": 95,
                            "agents": [],
                            "total_executions": 0,
                            "overall_success_rate": 0,
                        },
                    }
                }
            },
        },
    },
)
def get_evaluation_overview(
    service: EvaluationService = Depends(get_evaluation_service),
) -> APIResponse[EvaluationOverview]:
    """Return platform-wide evaluation metrics."""
    overview = service.get_overview()
    return APIResponse(
        success=True,
        message="Evaluation overview retrieved successfully",
        data=overview,
    )


@router.get(
    "/{agent_name}",
    response_model=APIResponse[AgentEvaluationDetail],
    summary="Get agent evaluation detail",
    description="Return detailed evaluation statistics for a single agent.",
    responses={
        status.HTTP_200_OK: {"description": "Agent evaluation detail retrieved successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "Agent evaluation metrics not found"},
    },
)
def get_agent_evaluation(
    agent_name: str,
    service: EvaluationService = Depends(get_evaluation_service),
) -> APIResponse[AgentEvaluationDetail]:
    """Return detailed evaluation statistics for one agent."""
    detail = service.get_agent_detail(agent_name)
    return APIResponse(
        success=True,
        message="Agent evaluation detail retrieved successfully",
        data=detail,
    )
