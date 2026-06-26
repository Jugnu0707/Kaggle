"""Pydantic schemas for the Coordinator Agent."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CoordinatorInput(BaseModel):
    """Input schema for Coordinator orchestration requests."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            }
        },
    )

    incident_id: uuid.UUID | None = Field(
        default=None,
        description="Incident to orchestrate",
    )
    log_id: uuid.UUID | None = Field(
        default=None,
        description="Uploaded log file to orchestrate",
    )

    @model_validator(mode="after")
    def require_incident_or_log(self) -> CoordinatorInput:
        """Ensure at least one identifier is provided."""
        if self.incident_id is None and self.log_id is None:
            raise ValueError("Either incident_id or log_id is required")
        return self


class OrchestrationPlan(BaseModel):
    """Structured orchestration plan returned by the Coordinator."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
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
            }
        }
    )

    incident_id: uuid.UUID | None = Field(
        default=None,
        description="Resolved incident identifier for the workflow",
    )
    log_id: uuid.UUID | None = Field(
        default=None,
        description="Resolved log file identifier when supplied",
    )
    workflow_id: uuid.UUID = Field(description="Unique workflow run identifier")
    status: str = Field(description="Orchestration acceptance status")
    workflow: list[str] = Field(description="Ordered list of agents to execute")
