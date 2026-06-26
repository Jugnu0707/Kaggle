"""System information endpoints."""

from pydantic import BaseModel
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends

from app.db.database import get_db, get_table_names
from app.schemas.response import APIResponse

router = APIRouter(prefix="/system", tags=["system"])


class TablesData(BaseModel):
    """Database table listing payload."""

    tables: list[str]


@router.get("/tables", response_model=APIResponse[TablesData])
def list_database_tables(db: Session = Depends(get_db)) -> APIResponse[TablesData]:
    """Return all tables detected in the connected database."""
    return APIResponse(
        success=True,
        message="Tables retrieved",
        data=TablesData(tables=get_table_names(db)),
    )
