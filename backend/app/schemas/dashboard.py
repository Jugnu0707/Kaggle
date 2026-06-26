"""Pydantic schemas for dashboard metrics."""

from pydantic import BaseModel


class DashboardStats(BaseModel):
    """Aggregate dashboard statistics."""

    total_incidents: int
    critical_incidents: int
    high_incidents: int
    uploaded_logs: int
