"""Seed Oz AI with demo cybersecurity incidents, evidence, logs, and investigations.

Run manually from the repository root:

    python scripts/reset_demo.py

Or seed only (idempotent, no wipe):

    python backend/scripts/seed_demo_data.py
"""

from __future__ import annotations

import hashlib
import os
import sys
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlalchemy import func, select

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

os.chdir(BACKEND_ROOT)

import app.models  # noqa: E402, F401

from app.core.config import get_database_path, get_upload_path, settings  # noqa: E402
from app.db.database import SessionLocal, init_db  # noqa: E402
from app.models.audit_log import AuditLog  # noqa: E402
from app.models.evidence import Evidence  # noqa: E402
from app.models.incident import Incident  # noqa: E402
from app.models.investigation import Investigation  # noqa: E402
from app.models.log_file import LogFile  # noqa: E402
from app.models.enums import UploadStatus  # noqa: E402
from app.models.executive_report import ExecutiveReport  # noqa: E402
from app.models.guardian_audit import GuardianAudit  # noqa: E402
from app.models.mitre_finding import MitreFinding  # noqa: E402
from app.models.response_plan import ResponsePlan  # noqa: E402
from app.models.risk_assessment import RiskAssessment  # noqa: E402
from app.models.threat_intelligence_finding import ThreatIntelligenceFinding  # noqa: E402
from app.repositories.audit_log_repository import AuditLogRepository  # noqa: E402
from app.repositories.incident_repository import IncidentRepository  # noqa: E402
from app.repositories.log_repository import LogRepository  # noqa: E402
from app.schemas.incident import IncidentCreate  # noqa: E402
from app.services.incident_service import IncidentService  # noqa: E402
from app.utils.file_validation import build_stored_filename  # noqa: E402
from scripts.demo_agent_outputs import DEMO_AGENT_OUTPUTS, GUARDIAN_AGENTS  # noqa: E402
from scripts.demo_catalog import DEMO_INCIDENTS, LOG_GENERATORS  # noqa: E402

SEED_ACTOR = "seed_script"


@dataclass
class SeedStats:
    """Counts of records created during a seed run."""

    incidents: int = 0
    investigations: int = 0
    evidence: int = 0
    log_files: int = 0
    audit_logs: int = 0
    investigation_runs: int = 0
    skipped: list[str] = field(default_factory=list)


def _now() -> datetime:
    return datetime.now(UTC)


def clear_demo_storage() -> None:
    """Remove uploaded log files from the configured upload directory."""
    upload_dir = get_upload_path()
    for path in upload_dir.iterdir():
        if path.name == ".gitkeep":
            continue
        if path.is_file():
            path.unlink()


def reset_database_file() -> None:
    """Delete the SQLite database file if it exists."""
    db_path = get_database_path()
    if db_path.exists():
        db_path.unlink()


def initialize_demo_runtimes() -> None:
    """Initialize agent, MCP, and AI runtimes required for investigation runs."""
    from app.core.adk_runtime import initialize_adk_runtime
    from app.ai.runtime import initialize_ai_runtime
    from app.core.evidence_runtime import initialize_evidence_runtime
    from app.core.executive_report_runtime import initialize_executive_report_runtime
    from app.core.guardian_runtime import initialize_guardian_runtime
    from app.core.mcp_runtime import initialize_mcp_runtime
    from app.core.mitre_runtime import initialize_mitre_runtime
    from app.core.response_runtime import initialize_response_runtime
    from app.core.risk_runtime import initialize_risk_runtime
    from app.core.threat_intelligence_runtime import initialize_threat_intelligence_runtime

    initialize_adk_runtime()
    initialize_evidence_runtime()
    initialize_threat_intelligence_runtime()
    initialize_mitre_runtime()
    initialize_risk_runtime()
    initialize_response_runtime()
    initialize_executive_report_runtime()
    initialize_guardian_runtime()
    initialize_mcp_runtime()
    initialize_ai_runtime()


def _find_incident_by_title(db, title: str) -> Incident | None:
    stmt = select(Incident).where(
        func.lower(Incident.title) == title.lower(),
        Incident.deleted_at.is_(None),
    )
    return db.scalar(stmt)


def _audit_exists(
    db,
    *,
    action: str,
    entity_type: str,
    entity_id: uuid.UUID,
) -> bool:
    stmt = select(AuditLog.id).where(
        AuditLog.action == action,
        AuditLog.entity_type == entity_type,
        AuditLog.entity_id == entity_id,
    )
    return db.scalar(stmt) is not None


def _record_audit(
    audit_repo: AuditLogRepository,
    *,
    action: str,
    entity_type: str,
    entity_id: uuid.UUID,
    timestamp: datetime,
    details: dict | None = None,
    stats: SeedStats,
) -> None:
    audit_repo.create(
        AuditLog(
            action=action,
            performed_by=SEED_ACTOR,
            entity_type=entity_type,
            entity_id=entity_id,
            timestamp=timestamp,
            details=details,
        )
    )
    stats.audit_logs += 1


def _evidence_raw_sample(evidence_type: str, incident_title: str) -> str:
    return (
        f"Sample {evidence_type} excerpt collected for incident '{incident_title}'. "
        "Contains normalized timestamps, source host identifiers, and analyst notes."
    )


def _ensure_incident(
    db,
    incident_service: IncidentService,
    incident_repo: IncidentRepository,
    audit_repo: AuditLogRepository,
    spec: dict,
    stats: SeedStats,
) -> Incident:
    existing = _find_incident_by_title(db, spec["title"])
    if existing is not None:
        stats.skipped.append(f"incident:{spec['title']}")
        return existing

    created_at = _now() - timedelta(hours=spec["created_offset_hours"])
    payload = IncidentCreate(
        title=spec["title"],
        description=spec["description"],
        severity=spec["severity"],
        status=spec["status"],
        source=spec["source"],
        confidence_score=spec["confidence_score"],
    )
    incident_response = incident_service.create_incident(payload)
    incident = incident_repo.get_by_id(incident_response.id)
    if incident is None:
        raise RuntimeError(f"Failed to load incident after creation: {spec['title']}")

    incident.created_at = created_at
    incident.updated_at = created_at + timedelta(minutes=15)
    incident_repo.update(incident)

    if not _audit_exists(
        db,
        action="Incident Created",
        entity_type="incident",
        entity_id=incident.id,
    ):
        _record_audit(
            audit_repo,
            action="Incident Created",
            entity_type="incident",
            entity_id=incident.id,
            timestamp=created_at,
            details={
                "title": incident.title,
                "severity": incident.severity.value,
                "source": incident.source,
            },
            stats=stats,
        )

    stats.incidents += 1
    return incident


def _ensure_investigation(
    db,
    incident_repo: IncidentRepository,
    audit_repo: AuditLogRepository,
    incident: Incident,
    spec: dict,
    stats: SeedStats,
) -> Investigation:
    incident = incident_repo.get_by_id(incident.id)
    if incident is None:
        raise RuntimeError("Incident disappeared during seeding")

    if incident.investigation is not None:
        stats.skipped.append(f"investigation:{incident.title}")
        return incident.investigation

    started_at = _now() - timedelta(hours=spec["investigation_started_offset_hours"])
    investigation = Investigation(
        incident_id=incident.id,
        started_at=started_at,
        completed_at=None,
        duration_seconds=None,
        investigation_status=spec["investigation_status"],
    )
    db.add(investigation)
    db.flush()

    if not _audit_exists(
        db,
        action="Investigation Started",
        entity_type="investigation",
        entity_id=investigation.id,
    ):
        _record_audit(
            audit_repo,
            action="Investigation Started",
            entity_type="investigation",
            entity_id=investigation.id,
            timestamp=started_at,
            details={
                "incident_id": str(incident.id),
                "status": investigation.investigation_status.value,
            },
            stats=stats,
        )

    stats.investigations += 1
    return investigation


def _ensure_evidence(
    db,
    audit_repo: AuditLogRepository,
    incident: Incident,
    spec: dict,
    stats: SeedStats,
) -> None:
    for item in spec["evidence"]:
        stmt = select(Evidence).where(
            Evidence.incident_id == incident.id,
            Evidence.evidence_type == item["evidence_type"],
            Evidence.filename == item["filename"],
        )
        if db.scalar(stmt) is not None:
            stats.skipped.append(f"evidence:{item['filename']}")
            continue

        created_at = incident.created_at + timedelta(minutes=20)
        evidence = Evidence(
            incident_id=incident.id,
            evidence_type=item["evidence_type"],
            filename=item["filename"],
            raw_data=_evidence_raw_sample(item["evidence_type"], incident.title),
            metadata_={
                "source": incident.source,
                "collector": SEED_ACTOR,
            },
            created_at=created_at,
        )
        db.add(evidence)
        db.flush()

        if not _audit_exists(
            db,
            action="Evidence Added",
            entity_type="evidence",
            entity_id=evidence.id,
        ):
            _record_audit(
                audit_repo,
                action="Evidence Added",
                entity_type="evidence",
                entity_id=evidence.id,
                timestamp=created_at,
                details={
                    "incident_id": str(incident.id),
                    "evidence_type": evidence.evidence_type,
                    "filename": evidence.filename,
                },
                stats=stats,
            )

        stats.evidence += 1


def _ensure_log_file(
    db,
    log_repo: LogRepository,
    audit_repo: AuditLogRepository,
    incident: Incident,
    original_filename: str,
    upload_dir: Path,
    offset_minutes: int,
    stats: SeedStats,
) -> None:
    stmt = select(LogFile).where(
        LogFile.original_filename == original_filename,
        LogFile.incident_id == incident.id,
        LogFile.deleted_at.is_(None),
    )
    if db.scalar(stmt) is not None:
        stats.skipped.append(f"log:{original_filename}")
        return

    generator = LOG_GENERATORS.get(original_filename)
    if generator is None:
        raise KeyError(f"No log generator for {original_filename}")

    content = generator().encode("utf-8")
    file_id = uuid.uuid4()
    extension = Path(original_filename).suffix or ".log"
    stored_filename = build_stored_filename(str(file_id), extension)
    destination = upload_dir / stored_filename
    destination.write_bytes(content)

    uploaded_at = incident.created_at + timedelta(minutes=offset_minutes)
    checksum = hashlib.sha256(content).hexdigest()
    relative_storage_path = str(Path(settings.upload_dir) / stored_filename)

    log_file = LogFile(
        id=file_id,
        incident_id=incident.id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_extension=extension,
        mime_type="text/plain",
        file_size_bytes=len(content),
        upload_status=UploadStatus.COMPLETED,
        uploaded_at=uploaded_at,
        storage_path=relative_storage_path,
        checksum_sha256=checksum,
    )
    log_repo.create(log_file)

    if not _audit_exists(
        db,
        action="Log Uploaded",
        entity_type="log_file",
        entity_id=log_file.id,
    ):
        _record_audit(
            audit_repo,
            action="Log Uploaded",
            entity_type="log_file",
            entity_id=log_file.id,
            timestamp=uploaded_at,
            details={
                "incident_id": str(incident.id),
                "original_filename": original_filename,
                "file_size_bytes": log_file.file_size_bytes,
                "checksum_sha256": checksum,
            },
            stats=stats,
        )

    stats.log_files += 1


def _count_for_incident(db, model, incident_id: uuid.UUID) -> int:
    stmt = select(func.count()).select_from(model).where(model.incident_id == incident_id)
    return int(db.scalar(stmt) or 0)


def seed_agent_outputs(
    db,
    incident: Incident,
    stats: SeedStats,
) -> None:
    """Insert curated agent outputs so every incident detail tab has data."""
    outputs = DEMO_AGENT_OUTPUTS.get(incident.title)
    if outputs is None:
        return

    created_at = incident.created_at + timedelta(hours=1)

    if _count_for_incident(db, ThreatIntelligenceFinding, incident.id) == 0:
        for item in outputs.get("threat_intel", []):
            db.add(
                ThreatIntelligenceFinding(
                    incident_id=incident.id,
                    indicator=item["indicator"],
                    indicator_type=item["indicator_type"],
                    reputation=item["reputation"],
                    confidence=item["confidence"],
                    source=item["source"],
                    description=item["description"],
                    analyst_notes=item["analyst_notes"],
                    created_at=created_at,
                )
            )
        stats.audit_logs += 0

    if _count_for_incident(db, MitreFinding, incident.id) == 0:
        for item in outputs.get("mitre", []):
            db.add(
                MitreFinding(
                    incident_id=incident.id,
                    technique_id=item["technique_id"],
                    technique_name=item["technique_name"],
                    tactic=item["tactic"],
                    confidence=item["confidence"],
                    evidence=item["evidence"],
                    created_at=created_at,
                )
            )

    if _count_for_incident(db, RiskAssessment, incident.id) == 0 and "risk" in outputs:
        risk = outputs["risk"]
        db.add(
            RiskAssessment(
                incident_id=incident.id,
                source="FALLBACK",
                overall_risk=risk["overall_risk"],
                risk_score=risk["risk_score"],
                likelihood=risk["likelihood"],
                business_impact=risk["business_impact"],
                confidence=risk["confidence"],
                priority=risk["priority"],
                summary=risk["summary"],
                reasoning=risk["reasoning"],
                created_at=created_at,
            )
        )

    if _count_for_incident(db, ResponsePlan, incident.id) == 0 and "response" in outputs:
        resp = outputs["response"]
        db.add(
            ResponsePlan(
                incident_id=incident.id,
                source="FALLBACK",
                priority=resp["priority"],
                containment=resp["containment"],
                eradication=resp["eradication"],
                recovery=resp["recovery"],
                monitoring=resp["monitoring"],
                executive_summary=resp["executive_summary"],
                created_at=created_at,
            )
        )

    if _count_for_incident(db, ExecutiveReport, incident.id) == 0 and "executive_report" in outputs:
        report = outputs["executive_report"]
        db.add(
            ExecutiveReport(
                incident_id=incident.id,
                source="FALLBACK",
                title=report["title"],
                executive_summary=report["executive_summary"],
                business_impact=report["business_impact"],
                markdown_report=report["markdown_report"],
                created_at=created_at,
            )
        )

    if _count_for_incident(db, GuardianAudit, incident.id) == 0:
        for agent_name in GUARDIAN_AGENTS:
            db.add(
                GuardianAudit(
                    incident_id=incident.id,
                    agent_name=agent_name,
                    validation_status="approved",
                    issues_found=[],
                    action_taken="approved",
                    created_at=created_at + timedelta(minutes=5),
                )
            )

    db.flush()


def seed_timelines(db, incident: Incident) -> None:
    """Build timeline events from evidence and logs when none exist."""
    from app.models.timeline_event import TimelineEvent
    from app.services.timeline_service import TimelineService

    existing = _count_for_incident(db, TimelineEvent, incident.id)
    if existing > 0:
        return

    TimelineService(db).get_timeline(incident.id)


def run_demo_investigations(db, stats: SeedStats) -> None:
    """Run the full investigation workflow for flagged demo incidents."""
    from app.services.investigation_workflow_service import InvestigationWorkflowService

    workflow = InvestigationWorkflowService(db)
    incident_repo = IncidentRepository(db)

    for spec in DEMO_INCIDENTS:
        if not spec.get("run_investigation"):
            continue

        incident = _find_incident_by_title(db, spec["title"])
        if incident is None:
            continue

        try:
            result = workflow.run(incident.id)
            stats.investigation_runs += 1
            incident = incident_repo.get_by_id(incident.id)
            if incident and incident.investigation:
                incident.investigation.investigation_status = spec["investigation_status"]
            print(
                f"  Investigation run completed: {spec['title']} "
                f"(status={result.status}, score={result.evaluation_score})"
            )
        except Exception as exc:
            print(f"  Investigation run failed: {spec['title']}: {exc}")
            raise


def seed_demo_data(run_investigations: bool = False) -> SeedStats:
    """Populate the database with demo records and return creation counts."""
    init_db()
    upload_dir = get_upload_path()
    stats = SeedStats()

    db = SessionLocal()
    try:
        incident_service = IncidentService(db)
        incident_repo = IncidentRepository(db)
        log_repo = LogRepository(db)
        audit_repo = AuditLogRepository(db)

        for spec in DEMO_INCIDENTS:
            incident = _ensure_incident(
                db,
                incident_service,
                incident_repo,
                audit_repo,
                spec,
                stats,
            )
            _ensure_investigation(db, incident_repo, audit_repo, incident, spec, stats)
            _ensure_evidence(db, audit_repo, incident, spec, stats)

            offset = 35
            for log_filename in spec["log_filenames"]:
                _ensure_log_file(
                    db,
                    log_repo,
                    audit_repo,
                    incident,
                    log_filename,
                    upload_dir,
                    offset,
                    stats,
                )
                offset += 5

        db.commit()

        if run_investigations:
            initialize_demo_runtimes()
            run_demo_investigations(db, stats)

        for spec in DEMO_INCIDENTS:
            incident = _find_incident_by_title(db, spec["title"])
            if incident is not None:
                seed_agent_outputs(db, incident, stats)
                seed_timelines(db, incident)

        db.commit()

        return stats
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def reset_and_seed_demo(run_investigations: bool = True) -> SeedStats:
    """Wipe storage and database, then seed a fresh deterministic demo state."""
    clear_demo_storage()
    reset_database_file()
    return seed_demo_data(run_investigations=run_investigations)


def main() -> None:
    stats = seed_demo_data(run_investigations=False)
    print("Oz AI demo data seed complete.")
    print(f"  Database path:          {get_database_path()}")
    print(f"  Incidents created:      {stats.incidents}")
    print(f"  Investigations created: {stats.investigations}")
    print(f"  Evidence records:       {stats.evidence}")
    print(f"  Uploaded logs:          {stats.log_files}")
    print(f"  Audit records:          {stats.audit_logs}")
    if stats.skipped:
        print(f"  Skipped (already exist): {len(stats.skipped)}")


if __name__ == "__main__":
    main()
