"""Uploaded file validation helpers."""

from pathlib import Path, PurePath

from app.core.exceptions import AppException

ALLOWED_EXTENSIONS: dict[str, set[str]] = {
    ".log": {"text/plain", "application/octet-stream"},
    ".txt": {"text/plain", "application/octet-stream"},
    ".json": {"application/json", "text/plain", "application/octet-stream"},
    ".csv": {"text/csv", "application/csv", "text/plain", "application/octet-stream"},
    ".evtx": {"application/octet-stream", "application/vnd.ms-evtx"},
}


def sanitize_original_filename(filename: str | None) -> str:
    """Return a safe basename without directory traversal components."""
    if not filename:
        raise AppException("Filename is required", status_code=400)

    sanitized = PurePath(filename).name.strip()
    if not sanitized or sanitized in {".", ".."}:
        raise AppException("Invalid filename", status_code=400)

    return sanitized


def validate_extension(filename: str) -> str:
    """Validate and return the lowercase file extension."""
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise AppException(
            "Unsupported file extension. Allowed: .log, .txt, .json, .csv, .evtx",
            status_code=400,
        )
    return extension


def validate_mime_type(extension: str, mime_type: str | None) -> str:
    """Validate MIME type against the allowed set for an extension."""
    normalized_mime = (mime_type or "application/octet-stream").split(";")[0].strip().lower()
    allowed_mimes = ALLOWED_EXTENSIONS[extension]

    if normalized_mime not in allowed_mimes:
        raise AppException(
            f"Unsupported MIME type '{normalized_mime}' for extension '{extension}'",
            status_code=400,
        )

    return normalized_mime


def build_stored_filename(file_id: str, extension: str) -> str:
    """Generate a UUID-based stored filename with a validated extension."""
    return f"{file_id}{extension}"
