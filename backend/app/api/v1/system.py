"""System information endpoints."""

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.db.database import get_db, get_table_names
from app.schemas.response import APIResponse

router = APIRouter(prefix="/system", tags=["system"])


class TablesData(BaseModel):
    """Database table listing payload."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tables": ["audit_logs", "evidence", "incidents", "investigations", "log_files"],
            }
        }
    )

    tables: list[str] = Field(description="Sorted list of database table names")


@router.get(
    "/tables",
    response_model=APIResponse[TablesData],
    summary="List database tables",
    description="Return all tables detected in the connected SQLite database.",
    responses={
        status.HTTP_200_OK: {"description": "Tables retrieved successfully"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Database introspection failed"},
    },
)
def list_database_tables(db: Session = Depends(get_db)) -> APIResponse[TablesData]:
    """Return all tables detected in the connected database."""
    return APIResponse(
        success=True,
        message="Tables retrieved",
        data=TablesData(tables=get_table_names(db)),
    )
