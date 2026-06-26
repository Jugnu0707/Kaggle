"""Log upload and metadata API routes."""

import uuid

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.log_file import (
    LogFileListResponse,
    LogFileMetadataResponse,
    LogFileUploadResponse,
)
from app.schemas.response import APIResponse
from app.services.log_service import LogService

router = APIRouter(prefix="/logs", tags=["logs"])


def get_log_service(db: Session = Depends(get_db)) -> LogService:
    """Provide a log service bound to the request database session."""
    return LogService(db)


@router.post(
    "/upload",
    response_model=APIResponse[LogFileUploadResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload log file",
    description=(
        "Upload a log file using multipart/form-data. Allowed extensions: "
        ".log, .txt, .json, .csv, .evtx. Maximum file size is 50 MB."
    ),
    responses={
        201: {"description": "Log file uploaded successfully"},
        400: {"description": "Invalid file type, size, or filename"},
        422: {"description": "Validation error"},
    },
)
async def upload_log_file(
    file: UploadFile = File(..., description="Log file to upload"),
    incident_id: uuid.UUID | None = Form(
        default=None,
        description="Optional incident ID to associate with the upload",
    ),
    service: LogService = Depends(get_log_service),
) -> APIResponse[LogFileUploadResponse]:
    """Store an uploaded log file and persist its metadata."""
    uploaded = await service.upload_log_file(file, incident_id=incident_id)
    return APIResponse(
        success=True,
        message="Log file uploaded successfully",
        data=uploaded,
    )


@router.get(
    "",
    response_model=APIResponse[LogFileListResponse],
    summary="List log files",
    description="Return a paginated list of uploaded log file metadata records.",
    responses={
        200: {"description": "Log files retrieved successfully"},
        400: {"description": "Invalid pagination parameters"},
    },
)
def list_log_files(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    service: LogService = Depends(get_log_service),
) -> APIResponse[LogFileListResponse]:
    """List uploaded log files with pagination."""
    log_files = service.list_log_files(page=page, page_size=page_size)
    return APIResponse(
        success=True,
        message="Log files retrieved successfully",
        data=log_files,
    )


@router.get(
    "/{log_id}",
    response_model=APIResponse[LogFileMetadataResponse],
    summary="Get log file metadata",
    description="Return metadata for an uploaded log file without returning file content.",
    responses={
        200: {"description": "Log file metadata retrieved successfully"},
        404: {"description": "Log file not found"},
        422: {"description": "Invalid log file ID format"},
    },
)
def get_log_file(
    log_id: uuid.UUID,
    service: LogService = Depends(get_log_service),
) -> APIResponse[LogFileMetadataResponse]:
    """Return metadata for a single log file."""
    log_file = service.get_log_file(log_id)
    return APIResponse(
        success=True,
        message="Log file metadata retrieved successfully",
        data=log_file,
    )


@router.delete(
    "/{log_id}",
    response_model=APIResponse[LogFileMetadataResponse],
    summary="Delete log file",
    description="Soft delete a log file record without removing the physical file.",
    responses={
        200: {"description": "Log file deleted successfully"},
        404: {"description": "Log file not found"},
        422: {"description": "Invalid log file ID format"},
    },
)
def delete_log_file(
    log_id: uuid.UUID,
    service: LogService = Depends(get_log_service),
) -> APIResponse[LogFileMetadataResponse]:
    """Soft delete an uploaded log file."""
    log_file = service.delete_log_file(log_id)
    return APIResponse(
        success=True,
        message="Log file deleted successfully",
        data=log_file,
    )
