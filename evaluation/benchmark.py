"""Offline agent benchmarks for the Oz AI evaluation framework."""

from __future__ import annotations

import json
import time
import uuid
from unittest.mock import patch

from agents.coordinator.models import CoordinatorInput
from agents.coordinator.orchestrator import CoordinatorOrchestrator
from agents.evidence.models import EvidenceInput
from agents.evidence.service import EvidenceCollectionService
from agents.executive_report.fallback import generate_executive_report_fallback
from agents.executive_report.schemas import ExecutiveReportContext, IncidentContext
from agents.executive_report.schemas import (
    RiskAssessmentContext as ExecutiveRiskContext,
)
from agents.guardian.schemas import GuardianAgentName, GuardianValidateInput
from agents.guardian.validator import GuardianValidator
from agents.mitre.mappings import map_evidence_text
from agents.response.fallback import plan_response_fallback
from agents.response.schemas import IncidentContext as ResponseIncidentContext
from agents.response.schemas import ResponsePlanningContext
from agents.response.schemas import RiskAssessmentContext as ResponseRiskContext
from agents.risk.fallback import assess_risk_fallback
from agents.risk.schemas import IncidentContext as RiskIncidentContext
from agents.risk.schemas import RiskAssessmentContext as RiskInputContext
from agents.threat_intelligence.fallback import enrich_ioc_fallback
from agents.threat_intelligence.ioc_extractor import IOCExtractor
from sqlalchemy.orm import Session

from app.core.config import get_upload_path
from app.models.enums import IncidentStatus, Severity, UploadStatus
from app.models.incident import Incident
from app.models.log_file import LogFile
from app.services.timeline.engine import TimelineEngine
from evaluation.datasets import (
    EVIDENCE_SCENARIOS,
    GUARDIAN_SCENARIOS,
    MITRE_SCENARIOS,
    THREAT_INTEL_SCENARIOS,
)
from evaluation.metrics import ExecutionMetric


def _measure(callable_obj, *args, **kwargs) -> tuple[object | None, int, bool]:
    start = time.perf_counter()
    try:
        result = callable_obj(*args, **kwargs)
        duration_ms = int((time.perf_counter() - start) * 1000)
        return result, duration_ms, True
    except Exception:
        duration_ms = int((time.perf_counter() - start) * 1000)
        return None, duration_ms, False


def _create_incident(
    db: Session, title: str = "Evaluation benchmark incident"
) -> uuid.UUID:
    incident = Incident(
        title=title,
        description="Synthetic incident for evaluation benchmarks",
        severity=Severity.HIGH,
        status=IncidentStatus.NEW,
        source="Evaluation",
        confidence_score=0.75,
    )
    db.add(incident)
    db.flush()
    return incident.id


def _create_log_file(
    db: Session,
    incident_id: uuid.UUID,
    content: str,
    filename: str = "benchmark.log",
) -> uuid.UUID:
    upload_dir = get_upload_path()
    stored_filename = f"{uuid.uuid4()}-{filename}"
    file_path = upload_dir / stored_filename
    file_path.write_text(content, encoding="utf-8")
    log_file = LogFile(
        incident_id=incident_id,
        original_filename=filename,
        stored_filename=stored_filename,
        file_extension=".log",
        mime_type="text/plain",
        file_size_bytes=len(content.encode("utf-8")),
        upload_status=UploadStatus.COMPLETED,
        storage_path=f"storage/uploads/{stored_filename}",
        checksum_sha256="0" * 64,
    )
    db.add(log_file)
    db.flush()
    return log_file.id


def benchmark_coordinator(db: Session) -> list[ExecutionMetric]:
    """Benchmark Coordinator plan generation."""
    incident_id = _create_incident(db, "Coordinator benchmark")
    log_id = _create_log_file(
        db,
        incident_id,
        EVIDENCE_SCENARIOS[0].log_content,
        "coordinator.log",
    )
    orchestrator = CoordinatorOrchestrator()

    def run() -> object:
        plan, _ = orchestrator.build_plan(
            CoordinatorInput(incident_id=incident_id, log_id=log_id),
            db,
        )
        return plan

    result, duration_ms, success = _measure(run)
    output_size = (
        len(json.dumps(result.model_dump(mode="json"))) if result is not None else 0
    )
    return [
        ExecutionMetric(
            agent_name="Coordinator Agent",
            execution_time_ms=duration_ms,
            success=success,
            ai_used=False,
            fallback_used=False,
            confidence=100.0 if success else 0.0,
            output_size=output_size,
        )
    ]


def benchmark_evidence(db: Session) -> list[ExecutionMetric]:
    """Benchmark Evidence Agent collection."""
    metrics: list[ExecutionMetric] = []
    service = EvidenceCollectionService(db)

    for scenario in EVIDENCE_SCENARIOS:
        incident_id = _create_incident(db, f"Evidence benchmark: {scenario.title}")
        log_id = _create_log_file(
            db, incident_id, scenario.log_content, f"{scenario.title}.log"
        )

        def run() -> object:
            return service.collect(
                EvidenceInput(incident_id=incident_id, log_file_id=log_id),
            )

        result, duration_ms, success = _measure(run)
        output_size = (
            len(json.dumps(result.model_dump(mode="json"))) if result is not None else 0
        )
        metrics.append(
            ExecutionMetric(
                agent_name="Evidence Agent",
                execution_time_ms=duration_ms,
                success=success and scenario.expected_success,
                ai_used=False,
                fallback_used=False,
                confidence=90.0 if success else 0.0,
                output_size=output_size,
            )
        )
    return metrics


def benchmark_threat_intelligence(db: Session) -> list[ExecutionMetric]:
    """Benchmark Threat Intelligence offline enrichment."""
    metrics: list[ExecutionMetric] = []
    extractor = IOCExtractor()

    for scenario in THREAT_INTEL_SCENARIOS:

        def run() -> object:
            iocs = extractor.extract(scenario.text)
            return [
                enrich_ioc_fallback(ioc, context_text=scenario.text) for ioc in iocs
            ]

        result, duration_ms, success = _measure(run)
        confidence = None
        if result:
            values = [item.confidence for item in result]
            confidence = sum(values) / len(values) if values else 70.0
        output_size = (
            len(json.dumps([item.model_dump() for item in result])) if result else 0
        )
        metrics.append(
            ExecutionMetric(
                agent_name="Threat Intelligence Agent",
                execution_time_ms=duration_ms,
                success=success and scenario.expected_success,
                ai_used=False,
                fallback_used=True,
                confidence=confidence,
                output_size=output_size,
            )
        )
    return metrics


def benchmark_mitre(db: Session) -> list[ExecutionMetric]:
    """Benchmark MITRE mapping rules."""
    metrics: list[ExecutionMetric] = []

    for scenario in MITRE_SCENARIOS:

        def run() -> object:
            return map_evidence_text(scenario.text)

        result, duration_ms, success = _measure(run)
        confidence = None
        if result:
            values = [item.confidence for item in result]
            confidence = sum(values) / len(values) if values else 0.0
        output_size = (
            len(json.dumps([item.model_dump() for item in result])) if result else 0
        )
        metrics.append(
            ExecutionMetric(
                agent_name="MITRE Mapping Agent",
                execution_time_ms=duration_ms,
                success=success and scenario.expected_success,
                ai_used=False,
                fallback_used=True,
                confidence=confidence,
                output_size=output_size,
            )
        )
    return metrics


def benchmark_risk(db: Session) -> list[ExecutionMetric]:
    """Benchmark Risk Assessment fallback path."""
    incident_id = _create_incident(db, "Risk benchmark")
    context = RiskInputContext(
        incident=RiskIncidentContext(
            id=incident_id,
            title="Risk benchmark",
            description="Suspicious PowerShell execution",
            severity="High",
            status="New",
            source="Evaluation",
            confidence_score=0.75,
        ),
        suspicious_indicators=["powershell.exe"],
        total_iocs=1,
    )

    def run() -> object:
        with patch(
            "agents.risk.service.RiskAssessmentService._try_ai_assessment",
            return_value=None,
        ):
            return assess_risk_fallback(context)

    result, duration_ms, success = _measure(run)
    output_size = (
        len(json.dumps(result.model_dump(mode="json"))) if result is not None else 0
    )
    return [
        ExecutionMetric(
            agent_name="Risk Assessment Agent",
            execution_time_ms=duration_ms,
            success=success,
            ai_used=False,
            fallback_used=True,
            confidence=float(result.confidence) if result is not None else None,
            output_size=output_size,
        )
    ]


def benchmark_response(db: Session) -> list[ExecutionMetric]:
    """Benchmark Response Planning fallback path."""
    incident_id = _create_incident(db, "Response benchmark")
    context = ResponsePlanningContext(
        incident=ResponseIncidentContext(
            id=incident_id,
            title="Response benchmark",
            description="Suspicious PowerShell execution",
            severity="High",
            status="New",
            source="Evaluation",
            confidence_score=0.75,
        ),
        suspicious_indicators=["powershell.exe"],
        risk_assessment=ResponseRiskContext(
            overall_risk="High",
            risk_score=80,
            priority="P2",
            summary="High severity incident",
            reasoning="Incident severity is High",
        ),
    )

    def run() -> object:
        with patch(
            "agents.response.service.ResponsePlanningService._try_ai_plan",
            return_value=None,
        ):
            return plan_response_fallback(context)

    result, duration_ms, success = _measure(run)
    output_size = (
        len(json.dumps(result.model_dump(mode="json"))) if result is not None else 0
    )
    return [
        ExecutionMetric(
            agent_name="Response Planning Agent",
            execution_time_ms=duration_ms,
            success=success,
            ai_used=False,
            fallback_used=True,
            confidence=85.0 if success else 0.0,
            output_size=output_size,
        )
    ]


def benchmark_executive_report(db: Session) -> list[ExecutionMetric]:
    """Benchmark Executive Report fallback path."""
    incident_id = _create_incident(db, "Executive report benchmark")
    context = ExecutiveReportContext(
        incident=IncidentContext(
            id=incident_id,
            title="Executive report benchmark",
            description="Suspicious PowerShell execution",
            severity="High",
            status="New",
            source="Evaluation",
            confidence_score=0.75,
        ),
        risk_assessment=ExecutiveRiskContext(
            overall_risk="High",
            risk_score=80,
            priority="P2",
            likelihood="Likely",
            business_impact="Significant business disruption",
            summary="High severity incident",
            reasoning="Incident severity is High",
        ),
    )

    def run() -> object:
        with patch(
            "agents.executive_report.service.ExecutiveReportService._try_ai_report",
            return_value=None,
        ):
            return generate_executive_report_fallback(context)

    result, duration_ms, success = _measure(run)
    output_size = (
        len(json.dumps(result.model_dump(mode="json"))) if result is not None else 0
    )
    return [
        ExecutionMetric(
            agent_name="Executive Report Agent",
            execution_time_ms=duration_ms,
            success=success,
            ai_used=False,
            fallback_used=True,
            confidence=85.0 if success else 0.0,
            output_size=output_size,
        )
    ]


def benchmark_guardian(db: Session) -> list[ExecutionMetric]:
    """Benchmark Guardian validation pipeline."""
    metrics: list[ExecutionMetric] = []
    validator = GuardianValidator()

    for scenario in GUARDIAN_SCENARIOS:
        agent_name = str(scenario["agent"])
        response = scenario["response"]

        def run() -> object:
            return validator.validate(
                GuardianValidateInput(
                    agent=GuardianAgentName(agent_name),
                    response=response,
                )
            )

        result, duration_ms, success = _measure(run)
        output_size = (
            len(json.dumps(result.model_dump(mode="json"))) if result is not None else 0
        )
        metrics.append(
            ExecutionMetric(
                agent_name="Guardian Agent",
                execution_time_ms=duration_ms,
                success=success and bool(scenario.get("expected_success", True)),
                ai_used=False,
                fallback_used=False,
                confidence=95.0 if success else 0.0,
                output_size=output_size,
            )
        )
    return metrics


def benchmark_timeline(db: Session) -> list[ExecutionMetric]:
    """Benchmark Timeline Engine reconstruction."""
    incident_id = _create_incident(db, "Timeline benchmark")
    _create_log_file(
        db,
        incident_id,
        EVIDENCE_SCENARIOS[0].log_content,
        "timeline.log",
    )
    engine = TimelineEngine(db)

    def run() -> object:
        return engine.build(incident_id)

    result, duration_ms, success = _measure(run)
    output_size = (
        len(json.dumps(result.model_dump(mode="json"))) if result is not None else 0
    )
    return [
        ExecutionMetric(
            agent_name="Timeline Engine",
            execution_time_ms=duration_ms,
            success=success,
            ai_used=False,
            fallback_used=False,
            confidence=90.0 if success else 0.0,
            output_size=output_size,
        )
    ]


def run_all_benchmarks(db: Session) -> list[ExecutionMetric]:
    """Execute every agent benchmark and return collected metrics."""
    collectors = [
        benchmark_coordinator,
        benchmark_evidence,
        benchmark_threat_intelligence,
        benchmark_mitre,
        benchmark_risk,
        benchmark_response,
        benchmark_executive_report,
        benchmark_guardian,
        benchmark_timeline,
    ]
    metrics: list[ExecutionMetric] = []
    for collector in collectors:
        metrics.extend(collector(db))
    return metrics
