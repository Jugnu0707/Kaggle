"""Health check endpoint."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.state import get_uptime_seconds
from app.db.database import check_database_connection, get_db
from app.schemas.response import APIResponse

router = APIRouter(tags=["health"])


class HealthData(BaseModel):
    """Health check payload fields."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "application_name": "Oz AI",
                "version": "0.1.0",
                "uptime_seconds": 42.5,
                "database_connected": True,
                "timestamp": "2026-06-26T10:00:00+00:00",
            }
        }
    )

    application_name: str
    version: str
    uptime_seconds: float
    database_connected: bool
    timestamp: str = Field(description="ISO-8601 timestamp for the health check")


@router.get(
    "/health",
    response_model=APIResponse[HealthData],
    summary="Health check",
    description="Return service health, uptime, database connectivity, and timestamp.",
    responses={
        status.HTTP_200_OK: {"description": "Service is healthy"},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Service is degraded"},
    },
)
def health_check(db: Session = Depends(get_db)) -> APIResponse[HealthData]:
    """Return application health, uptime, and database connectivity."""
    return APIResponse(
        success=True,
        message="Healthy",
        data=HealthData(
            application_name=settings.app_name,
            version=settings.app_version,
            uptime_seconds=get_uptime_seconds(),
            database_connected=check_database_connection(db),
            timestamp=datetime.now(UTC).isoformat(),
        ),
    )
