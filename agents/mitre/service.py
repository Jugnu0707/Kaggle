"""MITRE ATT&CK mapping from normalized evidence."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from agents.evidence.models import EvidenceInput, EvidencePackage
from agents.evidence.service import EvidenceCollectionService
from agents.mitre.mappings import map_evidence_text
from agents.mitre.models import MitreMappingInput, MitreMappingResult
from app.core.exceptions import NotFoundException
from app.core.logging import get_logger
from app.models.log_file import LogFile
from app.repositories.incident_repository import IncidentRepository

logger = get_logger(__name__)

NO_MAPPING_MESSAGE = "No mapping found."


class MitreMappingService:
    """Maps evidence from an incident to local MITRE ATT&CK techniques."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.incident_repository = IncidentRepository(db)
        self.evidence_service = EvidenceCollectionService(db)

    def map_incident(self, request: MitreMappingInput) -> MitreMappingResult:
        """Collect incident evidence and apply rule-based MITRE mappings."""
        incident = self.incident_repository.get_by_id(request.incident_id)
        if incident is None:
            raise NotFoundException("Incident not found")

        logger.info("Evidence received for MITRE mapping: incident_id=%s", request.incident_id)
        packages = self._collect_incident_evidence(request.incident_id)
        combined_text = self._build_mapping_text(packages)

        logger.info("MITRE mapping started: incident_id=%s", request.incident_id)
        techniques = map_evidence_text(combined_text)
        logger.info("MITRE mapping completed: techniques=%s", len(techniques))

        message = NO_MAPPING_MESSAGE if not techniques else None
        return MitreMappingResult(
            status="completed",
            techniques=techniques,
            message=message,
            evidence_packages=packages,
        )

    def map_from_package(self, package: EvidencePackage) -> MitreMappingResult:
        """Map MITRE techniques from a pre-collected evidence package."""
        logger.info(
            "Evidence received for MITRE mapping: incident_id=%s evidence_id=%s",
            package.incident_id,
            package.uploaded_file_id,
        )
        combined_text = self._build_mapping_text([package])
        logger.info("MITRE mapping started: incident_id=%s", package.incident_id)
        techniques = map_evidence_text(combined_text)
        logger.info("MITRE mapping completed: techniques=%s", len(techniques))
        message = NO_MAPPING_MESSAGE if not techniques else None
        return MitreMappingResult(
            status="completed",
            techniques=techniques,
            message=message,
            evidence_packages=[package],
        )

    def _collect_incident_evidence(self, incident_id: uuid.UUID) -> list[EvidencePackage]:
        stmt = select(LogFile).where(
            LogFile.incident_id == incident_id,
            LogFile.deleted_at.is_(None),
        )
        log_files = list(self.db.scalars(stmt).all())
        packages: list[EvidencePackage] = []
        for log_file in log_files:
            result = self.evidence_service.collect(
                EvidenceInput(incident_id=incident_id, log_file_id=log_file.id)
            )
            packages.append(result.evidence_package)
        return packages

    def _build_mapping_text(self, packages: list[EvidencePackage]) -> str:
        parts: list[str] = []
        for package in packages:
            parts.append(package.file_metadata.original_filename)
            parts.extend(package.sample_entries)
        return "\n".join(part for part in parts if part)
