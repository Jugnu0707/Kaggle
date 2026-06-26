"""Seed Oz AI with demo cybersecurity incidents, evidence, logs, and audit records.

Run manually from the repository root:

    python backend/scripts/seed_demo_data.py

The script is idempotent — re-running it will not create duplicates.
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

from app.core.config import get_upload_path, settings  # noqa: E402
from app.db.database import Base, SessionLocal, engine, init_db  # noqa: E402
from app.models.audit_log import AuditLog  # noqa: E402
from app.models.enums import (  # noqa: E402
    IncidentStatus,
    InvestigationStatus,
    Severity,
    UploadStatus,
)
from app.models.evidence import Evidence  # noqa: E402
from app.models.incident import Incident  # noqa: E402
from app.models.investigation import Investigation  # noqa: E402
from app.models.log_file import LogFile  # noqa: E402
from app.repositories.audit_log_repository import AuditLogRepository  # noqa: E402
from app.repositories.incident_repository import IncidentRepository  # noqa: E402
from app.repositories.log_repository import LogRepository  # noqa: E402
from app.schemas.incident import IncidentCreate  # noqa: E402
from app.services.incident_service import IncidentService  # noqa: E402
from app.utils.file_validation import build_stored_filename  # noqa: E402

SEED_ACTOR = "seed_script"

DEMO_INCIDENTS: tuple[dict, ...] = (
    {
        "title": "Suspicious PowerShell Execution",
        "description": (
            "PowerShell was launched by WINWORD.EXE on an employee workstation."
        ),
        "severity": Severity.HIGH,
        "status": IncidentStatus.INVESTIGATING,
        "source": "Microsoft Defender",
        "confidence_score": 0.92,
        "created_offset_hours": 48,
        "investigation_status": InvestigationStatus.RUNNING,
        "investigation_started_offset_hours": 47,
        "evidence": (
            {
                "evidence_type": "Windows Event Log",
                "filename": "security_events_1042.evtx",
            },
            {
                "evidence_type": "PowerShell Transcript",
                "filename": "powershell_transcript_1042.txt",
            },
        ),
        "log_filename": "powershell_execution.log",
    },
    {
        "title": "Multiple Failed Login Attempts",
        "description": (
            "More than 150 failed logon attempts detected from a single IP "
            "within five minutes."
        ),
        "severity": Severity.MEDIUM,
        "status": IncidentStatus.NEW,
        "source": "Windows Security Logs",
        "confidence_score": 0.88,
        "created_offset_hours": 26,
        "investigation_status": InvestigationStatus.PENDING,
        "investigation_started_offset_hours": 25,
        "evidence": (
            {
                "evidence_type": "Authentication Log",
                "filename": "auth_failures_dc01.log",
            },
            {
                "evidence_type": "Firewall Event",
                "filename": "firewall_blocked_185.log",
            },
        ),
        "log_filename": "failed_login_attempts.log",
    },
    {
        "title": "Possible Ransomware Activity",
        "description": (
            "Rapid file encryption activity detected across multiple directories."
        ),
        "severity": Severity.CRITICAL,
        "status": IncidentStatus.INVESTIGATING,
        "source": "CrowdStrike Falcon",
        "confidence_score": 0.98,
        "created_offset_hours": 8,
        "investigation_status": InvestigationStatus.RUNNING,
        "investigation_started_offset_hours": 7,
        "evidence": (
            {
                "evidence_type": "EDR Alert",
                "filename": "falcon_ransomware_alert.json",
            },
            {
                "evidence_type": "File Integrity Alert",
                "filename": "fim_encryption_burst.csv",
            },
        ),
        "log_filename": "ransomware_activity.log",
    },
)


@dataclass
class SeedStats:
    """Counts of records created during a seed run."""

    incidents: int = 0
    investigations: int = 0
    evidence: int = 0
    log_files: int = 0
    audit_logs: int = 0
    skipped: list[str] = field(default_factory=list)


def _ensure_current_schema() -> None:
    """Fail fast when the local SQLite schema is older than the application models."""
    from sqlalchemy import inspect

    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    if "incidents" not in table_names:
        Base.metadata.create_all(bind=engine)
        return

    incident_columns = {column["name"] for column in inspector.get_columns("incidents")}
    required_columns = {"deleted_at", "confidence_score"}
    if not required_columns.issubset(incident_columns):
        raise SystemExit(
            "Database schema is outdated. Stop the backend, delete backend/oz_ai.db, "
            "restart the backend, and run this script again."
        )


def _now() -> datetime:
    return datetime.now(UTC)


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


def _generate_powershell_log() -> str:
    lines = [
        "2026-06-24T08:15:01Z HOST=WS-FIN-042 EVENT=ProcessCreate PROCESS=WINWORD.EXE PID=4892 USER=DOMAIN\\jsmith",
        "2026-06-24T08:15:03Z HOST=WS-FIN-042 EVENT=ProcessCreate PARENT=WINWORD.EXE PROCESS=powershell.exe PID=5120",
        "2026-06-24T08:15:03Z HOST=WS-FIN-042 EVENT=CommandLine CMD=powershell.exe -NoProfile -WindowStyle Hidden -EncodedCommand ...",
        "2026-06-24T08:15:04Z HOST=WS-FIN-042 EVENT=NetworkConnect PROCESS=powershell.exe DEST=185.234.72.19:443",
        "2026-06-24T08:15:05Z HOST=WS-FIN-042 EVENT=FileCreate PATH=C:\\Users\\jsmith\\AppData\\Local\\Temp\\stage.ps1",
        "2026-06-24T08:15:06Z HOST=WS-FIN-042 EVENT=RegistrySet KEY=HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run VALUE=Updater",
        "2026-06-24T08:15:08Z HOST=WS-FIN-042 EVENT=ScriptBlock ID=1 TEXT=IEX (New-Object Net.WebClient).DownloadString(...)",
        "2026-06-24T08:15:10Z HOST=WS-FIN-042 EVENT=AMSI_SCAN RESULT=Suspicious SCRIPT=Invoke-Expression detected",
        "2026-06-24T08:15:11Z HOST=WS-FIN-042 EVENT=DefenderAlert SEVERITY=High TECHNIQUE=T1059.001",
        "2026-06-24T08:15:12Z HOST=WS-FIN-042 EVENT=ProcessTerminate PROCESS=powershell.exe PID=5120 EXIT=1",
        "2026-06-24T08:15:14Z HOST=WS-FIN-042 EVENT=ProcessCreate PROCESS=cmd.exe PID=5201 PARENT=WINWORD.EXE",
        "2026-06-24T08:15:16Z HOST=WS-FIN-042 EVENT=FileDelete PATH=C:\\Users\\jsmith\\AppData\\Local\\Temp\\stage.ps1",
        "2026-06-24T08:15:18Z HOST=WS-FIN-042 EVENT=NetworkConnect PROCESS=WINWORD.EXE DEST=185.234.72.19:8080",
        "2026-06-24T08:15:20Z HOST=WS-FIN-042 EVENT=TokenElevation PROCESS=powershell.exe RESULT=Denied",
        "2026-06-24T08:15:22Z HOST=WS-FIN-042 EVENT=LogonType=2 USER=DOMAIN\\jsmith SOURCE=Console",
        "2026-06-24T08:15:24Z HOST=WS-FIN-042 EVENT=ServiceCreate NAME=UpdateHelper DISPLAY=Windows Update Helper",
        "2026-06-24T08:15:26Z HOST=WS-FIN-042 EVENT=FileCreate PATH=C:\\ProgramData\\Updater\\config.json",
        "2026-06-24T08:15:28Z HOST=WS-FIN-042 EVENT=PowerShellModule LOAD=Microsoft.PowerShell.Utility",
        "2026-06-24T08:15:30Z HOST=WS-FIN-042 EVENT=DefenderQuarantine FILE=C:\\Users\\jsmith\\AppData\\Local\\Temp\\stage.ps1",
        "2026-06-24T08:15:32Z HOST=WS-FIN-042 EVENT=ProcessCreate PROCESS=MsMpEng.exe PID=1044",
        "2026-06-24T08:15:34Z HOST=WS-FIN-042 EVENT=AuditPolicyChange CATEGORY=Process Creation",
        "2026-06-24T08:15:36Z HOST=WS-FIN-042 EVENT=NetworkConnect PROCESS=WINWORD.EXE DEST=10.20.30.5:445",
        "2026-06-24T08:15:38Z HOST=WS-FIN-042 EVENT=ScriptBlock ID=2 TEXT=Start-Sleep -Seconds 2; Remove-Item -Force stage.ps1",
        "2026-06-24T08:15:40Z HOST=WS-FIN-042 EVENT=IncidentEscalation SEVERITY=High ANALYST=auto-triage",
        "2026-06-24T08:15:42Z HOST=WS-FIN-042 EVENT=CollectionComplete ARTIFACTS=4 STATUS=Investigating",
    ]
    return "\n".join(lines) + "\n"


def _generate_failed_login_log() -> str:
    lines = [
        "2026-06-25T02:41:01Z EVENT=4625 RESULT=Failure LOGON_TYPE=3 USER=administrator SOURCE=203.0.113.44 WORKSTATION=KALI-01",
        "2026-06-25T02:41:02Z EVENT=4625 RESULT=Failure LOGON_TYPE=3 USER=administrator SOURCE=203.0.113.44 WORKSTATION=KALI-01",
        "2026-06-25T02:41:03Z EVENT=4625 RESULT=Failure LOGON_TYPE=3 USER=svc_backup SOURCE=203.0.113.44 WORKSTATION=KALI-01",
        "2026-06-25T02:41:04Z EVENT=4625 RESULT=Failure LOGON_TYPE=3 USER=jsmith SOURCE=203.0.113.44 WORKSTATION=KALI-01",
        "2026-06-25T02:41:05Z EVENT=4625 RESULT=Failure LOGON_TYPE=3 USER=administrator SOURCE=203.0.113.44 WORKSTATION=KALI-01",
        "2026-06-25T02:41:06Z EVENT=4771 RESULT=Failure SERVICE=krbtgt USER=administrator SOURCE=203.0.113.44",
        "2026-06-25T02:41:07Z EVENT=4625 RESULT=Failure LOGON_TYPE=3 USER=guest SOURCE=203.0.113.44 WORKSTATION=KALI-01",
        "2026-06-25T02:41:08Z EVENT=4625 RESULT=Failure LOGON_TYPE=3 USER=administrator SOURCE=203.0.113.44 WORKSTATION=KALI-01",
        "2026-06-25T02:41:09Z EVENT=5140 RESULT=Denied USER=anonymous SOURCE=203.0.113.44 SHARE=\\\\DC01\\SYSVOL",
        "2026-06-25T02:41:10Z EVENT=4625 RESULT=Failure LOGON_TYPE=3 USER=helpdesk SOURCE=203.0.113.44 WORKSTATION=KALI-01",
        "2026-06-25T02:41:11Z EVENT=4625 RESULT=Failure LOGON_TYPE=3 USER=administrator SOURCE=203.0.113.44 WORKSTATION=KALI-01",
        "2026-06-25T02:41:12Z EVENT=4740 RESULT=Lockout USER=administrator SOURCE=203.0.113.44",
        "2026-06-25T02:41:13Z EVENT=4625 RESULT=Failure LOGON_TYPE=3 USER=administrator SOURCE=203.0.113.44 WORKSTATION=KALI-01",
        "2026-06-25T02:41:14Z EVENT=5152 RESULT=Drop PROTO=TCP SOURCE=203.0.113.44:55221 DEST=10.10.0.10:3389",
        "2026-06-25T02:41:15Z EVENT=4625 RESULT=Failure LOGON_TYPE=3 USER=administrator SOURCE=203.0.113.44 WORKSTATION=KALI-01",
        "2026-06-25T02:41:16Z EVENT=4625 RESULT=Failure LOGON_TYPE=3 USER=administrator SOURCE=203.0.113.44 WORKSTATION=KALI-01",
        "2026-06-25T02:41:17Z EVENT=4625 RESULT=Failure LOGON_TYPE=3 USER=administrator SOURCE=203.0.113.44 WORKSTATION=KALI-01",
        "2026-06-25T02:41:18Z EVENT=5157 RESULT=Block PROTO=TCP SOURCE=203.0.113.44 DEST=10.10.0.10:445 RULE=Block-External-SMB",
        "2026-06-25T02:41:19Z EVENT=4625 RESULT=Failure LOGON_TYPE=3 USER=administrator SOURCE=203.0.113.44 WORKSTATION=KALI-01",
        "2026-06-25T02:41:20Z EVENT=4625 RESULT=Failure LOGON_TYPE=3 USER=administrator SOURCE=203.0.113.44 WORKSTATION=KALI-01",
        "2026-06-25T02:41:21Z EVENT=4625 RESULT=Failure LOGON_TYPE=3 USER=administrator SOURCE=203.0.113.44 WORKSTATION=KALI-01",
        "2026-06-25T02:41:22Z EVENT=4723 RESULT=Failure USER=administrator SOURCE=203.0.113.44 REASON=Bad password",
        "2026-06-25T02:41:23Z EVENT=4625 RESULT=Failure LOGON_TYPE=3 USER=administrator SOURCE=203.0.113.44 WORKSTATION=KALI-01",
        "2026-06-25T02:41:24Z EVENT=4625 RESULT=Failure LOGON_TYPE=3 USER=administrator SOURCE=203.0.113.44 WORKSTATION=KALI-01",
        "2026-06-25T02:41:25Z EVENT=Alert THRESHOLD=150/5min SOURCE=203.0.113.44 ACTION=Account lockout triggered",
    ]
    return "\n".join(lines) + "\n"


def _generate_ransomware_log() -> str:
    lines = [
        "2026-06-26T05:12:01Z HOST=FS-PROD-01 EVENT=EDRAlert SEVERITY=Critical DETECTION=Ransomware.Behavior.A",
        "2026-06-26T05:12:03Z HOST=FS-PROD-01 EVENT=FileModify PATH=\\\\FS-PROD-01\\Finance\\Q2\\report.xlsx EXT=.locked",
        "2026-06-26T05:12:04Z HOST=FS-PROD-01 EVENT=FileModify PATH=\\\\FS-PROD-01\\Finance\\Q2\\ledger.csv EXT=.locked",
        "2026-06-26T05:12:05Z HOST=WS-HR-017 EVENT=ProcessCreate PROCESS=encrypt.exe PID=8844 PARENT=explorer.exe",
        "2026-06-26T05:12:06Z HOST=WS-HR-017 EVENT=FileModify PATH=C:\\Users\\hradmin\\Documents\\policy.docx EXT=.locked",
        "2026-06-26T05:12:07Z HOST=FS-PROD-01 EVENT=FileModify PATH=\\\\FS-PROD-01\\Shared\\Projects\\alpha.pptx EXT=.locked",
        "2026-06-26T05:12:08Z HOST=WS-HR-017 EVENT=NetworkConnect PROCESS=encrypt.exe DEST=198.51.100.77:443",
        "2026-06-26T05:12:09Z HOST=FS-PROD-01 EVENT=FileCreate PATH=\\\\FS-PROD-01\\Finance\\Q2\\README_RESTORE.txt",
        "2026-06-26T05:12:10Z HOST=WS-HR-017 EVENT=FileModify PATH=C:\\Users\\hradmin\\Desktop\\contacts.xlsx EXT=.locked",
        "2026-06-26T05:12:11Z HOST=FS-PROD-01 EVENT=FIM ALERT CHANGE=MassRename COUNT=42 DIRECTORY=\\\\FS-PROD-01\\Finance",
        "2026-06-26T05:12:12Z HOST=WS-HR-017 EVENT=RegistrySet KEY=HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run VALUE=CryptSvc",
        "2026-06-26T05:12:13Z HOST=FS-PROD-01 EVENT=FileModify PATH=\\\\FS-PROD-01\\Legal\\contracts.zip EXT=.locked",
        "2026-06-26T05:12:14Z HOST=WS-HR-017 EVENT=DefenderAlert SEVERITY=Critical BEHAVIOR=CredentialAccess",
        "2026-06-26T05:12:15Z HOST=FS-PROD-01 EVENT=VolumeShadowCopy DELETE RESULT=Success HOST=FS-PROD-01",
        "2026-06-26T05:12:16Z HOST=WS-HR-017 EVENT=FileModify PATH=C:\\Users\\hradmin\\Pictures\\archive.zip EXT=.locked",
        "2026-06-26T05:12:17Z HOST=FS-PROD-01 EVENT=FileModify PATH=\\\\FS-PROD-01\\Engineering\\build.ps1 EXT=.locked",
        "2026-06-26T05:12:18Z HOST=WS-HR-017 EVENT=ProcessCreate PROCESS=vssadmin.exe PID=9011 CMD=delete shadows /all /quiet",
        "2026-06-26T05:12:19Z HOST=FS-PROD-01 EVENT=EDRAlert SEVERITY=Critical DETECTION=ShadowCopyDeletion",
        "2026-06-26T05:12:20Z HOST=WS-HR-017 EVENT=FileCreate PATH=C:\\Users\\Public\\DECRYPT_INSTRUCTIONS.txt",
        "2026-06-26T05:12:21Z HOST=FS-PROD-01 EVENT=FileModify PATH=\\\\FS-PROD-01\\Finance\\Q2\\budget.pdf EXT=.locked",
        "2026-06-26T05:12:22Z HOST=WS-HR-017 EVENT=NetworkConnect PROCESS=encrypt.exe DEST=198.51.100.77:8080",
        "2026-06-26T05:12:23Z HOST=FS-PROD-01 EVENT=FIM ALERT CHANGE=MassEncrypt COUNT=128 DIRECTORY=\\\\FS-PROD-01\\Shared",
        "2026-06-26T05:12:24Z HOST=WS-HR-017 EVENT=ProcessTerminate PROCESS=encrypt.exe PID=8844",
        "2026-06-26T05:12:25Z HOST=FS-PROD-01 EVENT=IncidentEscalation SEVERITY=Critical ACTION=Isolate host FS-PROD-01",
        "2026-06-26T05:12:26Z HOST=WS-HR-017 EVENT=HostContainment STATUS=Initiated ANALYST=auto-response",
    ]
    return "\n".join(lines) + "\n"


LOG_GENERATORS = {
    "powershell_execution.log": _generate_powershell_log,
    "failed_login_attempts.log": _generate_failed_login_log,
    "ransomware_activity.log": _generate_ransomware_log,
}


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
    spec: dict,
    upload_dir: Path,
    stats: SeedStats,
) -> None:
    original_filename = spec["log_filename"]
    stmt = select(LogFile).where(
        LogFile.original_filename == original_filename,
        LogFile.deleted_at.is_(None),
    )
    existing = db.scalar(stmt)
    if existing is not None:
        stats.skipped.append(f"log:{original_filename}")
        return

    generator = LOG_GENERATORS[original_filename]
    content = generator().encode("utf-8")
    file_id = uuid.uuid4()
    extension = ".log"
    stored_filename = build_stored_filename(str(file_id), extension)
    destination = upload_dir / stored_filename
    destination.write_bytes(content)

    uploaded_at = incident.created_at + timedelta(minutes=35)
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


def seed_demo_data() -> SeedStats:
    """Populate the database with demo records and return creation counts."""
    init_db()
    _ensure_current_schema()
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
            _ensure_log_file(db, log_repo, audit_repo, incident, spec, upload_dir, stats)

        db.commit()
        return stats
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main() -> None:
    stats = seed_demo_data()
    print("Oz AI demo data seed complete.")
    print(f"  Incidents created:      {stats.incidents}")
    print(f"  Investigations created: {stats.investigations}")
    print(f"  Evidence records:       {stats.evidence}")
    print(f"  Uploaded logs:          {stats.log_files}")
    print(f"  Audit records:          {stats.audit_logs}")
    if stats.skipped:
        print(f"  Skipped (already exist): {len(stats.skipped)}")


if __name__ == "__main__":
    main()
