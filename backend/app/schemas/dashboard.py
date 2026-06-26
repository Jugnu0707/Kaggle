"""Pydantic schemas for dashboard metrics."""

from pydantic import BaseModel, ConfigDict, Field


class DashboardStats(BaseModel):
    """Aggregate dashboard statistics."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_incidents": 12,
                "critical_incidents": 2,
                "high_incidents": 4,
                "uploaded_logs": 8,
            }
        }
    )

    total_incidents: int = Field(ge=0)
    critical_incidents: int = Field(ge=0)
    high_incidents: int = Field(ge=0)
    uploaded_logs: int = Field(ge=0)
