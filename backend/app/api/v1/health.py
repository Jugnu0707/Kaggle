"""Health check endpoint."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.state import get_uptime_seconds
from app.db.database import check_database_connection, get_db
from app.schemas.response import APIResponse

router = APIRouter()


class HealthData(BaseModel):
    """Health check payload fields."""

    application_name: str
    version: str
    uptime_seconds: float
    database_connected: bool
    timestamp: str


@router.get("/health", response_model=APIResponse[HealthData])
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
