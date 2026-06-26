"""Dashboard metrics API routes."""

from fastapi import APIRouter, Depends, status

from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.dashboard import DashboardStats
from app.schemas.response import APIResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    """Provide a dashboard service bound to the request database session."""
    return DashboardService(db)


@router.get(
    "/stats",
    response_model=APIResponse[DashboardStats],
    summary="Get dashboard statistics",
    description=(
        "Return aggregate metrics used by the operations dashboard including "
        "incident counts by severity and uploaded log totals."
    ),
    responses={
        status.HTTP_200_OK: {"description": "Dashboard statistics retrieved successfully"},
    },
)
def get_dashboard_stats(
    service: DashboardService = Depends(get_dashboard_service),
) -> APIResponse[DashboardStats]:
    """Return dashboard summary statistics."""
    stats = service.get_stats()
    return APIResponse(
        success=True,
        message="Dashboard statistics retrieved successfully",
        data=stats,
    )
