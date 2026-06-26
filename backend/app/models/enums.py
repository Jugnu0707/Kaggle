"""Shared enumeration types for ORM models."""

from enum import Enum


class Severity(str, Enum):
    """Incident severity levels."""

    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class IncidentStatus(str, Enum):
    """Incident lifecycle status values."""

    NEW = "New"
    INVESTIGATING = "Investigating"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


class InvestigationStatus(str, Enum):
    """Investigation pipeline status values."""

    PENDING = "Pending"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"


class UploadStatus(str, Enum):
    """Log file upload lifecycle status."""

    COMPLETED = "Completed"
    DELETED = "Deleted"
    FAILED = "Failed"


class AgentExecutionStatus(str, Enum):
    """Agent execution lifecycle status."""

    ACCEPTED = "accepted"
    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
