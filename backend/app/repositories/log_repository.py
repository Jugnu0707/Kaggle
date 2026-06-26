"""Repository for log file persistence and queries."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.log_file import LogFile


class LogRepository:
    """Handles database operations for uploaded log files."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, log_file: LogFile) -> LogFile:
        """Persist a new log file record."""
        self.db.add(log_file)
        self.db.flush()
        return log_file

    def get_by_id(self, log_id: uuid.UUID) -> LogFile | None:
        """Return an active log file by ID."""
        stmt = select(LogFile).where(LogFile.id == log_id, LogFile.deleted_at.is_(None))
        return self.db.scalar(stmt)

    def list_log_files(
        self,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[LogFile], int]:
        """Return paginated active log files sorted by uploaded_at descending."""
        filters = [LogFile.deleted_at.is_(None)]

        count_stmt = select(func.count()).select_from(LogFile).where(*filters)
        total = self.db.scalar(count_stmt) or 0

        offset = (page - 1) * page_size
        stmt = (
            select(LogFile)
            .where(*filters)
            .order_by(LogFile.uploaded_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        log_files = list(self.db.scalars(stmt).all())
        return log_files, total

    def update(self, log_file: LogFile) -> LogFile:
        """Persist log file updates."""
        self.db.add(log_file)
        self.db.flush()
        return log_file
