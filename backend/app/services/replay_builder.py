"""Build sanitized explainability metadata from agent results."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal

from app.models.enums import ReplayStepStatus
from app.utils.sanitize import sanitize_text, sanitize_value, summarize_json

SourceType = Literal["AI", "FALLBACK", "SYSTEM"]


@dataclass
class ReplayStepRecord:
    """In-memory replay step captured during workflow execution."""

    step_number: int
    agent_name: str
    started_at: datetime
    completed_at: datetime | None
    duration_ms: int
    input_summary: str
    output_summary: str
    ai_used: bool
    fallback_used: bool
    status: ReplayStepStatus
    decision: str = ""
    reason: str = ""
    confidence: int | None = None
    evidence_used: list[str] = field(default_factory=list)
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    source: SourceType = "SYSTEM"


def _source_from_result(result: Any, fallback_used: bool) -> SourceType:
    if fallback_used:
        return "FALLBACK"
    if result is None:
        return "SYSTEM"
    source = getattr(result, "source", None)
    if source is not None:
        normalized = str(source).upper()
        if "FALLBACK" in normalized:
            return "FALLBACK"
        if normalized == "AI":
            return "AI"
    if hasattr(result, "model_dump"):
        payload = result.model_dump(mode="json")
        raw_source = str(payload.get("source", "")).upper()
        if "FALLBACK" in raw_source:
            return "FALLBACK"
        if raw_source == "AI":
            return "AI"
    return "SYSTEM"


def _confidence_from_result(result: Any) -> int | None:
    if result is None:
        return None
    if hasattr(result, "confidence"):
        try:
            return int(result.confidence)
        except (TypeError, ValueError):
            pass
    if hasattr(result, "risk_score"):
        try:
            return int(result.risk_score)
        except (TypeError, ValueError):
            pass
    if hasattr(result, "model_dump"):
        payload = result.model_dump(mode="json")
        for key in ("confidence", "risk_score", "evaluation_score"):
            if key in payload:
                try:
                    return int(payload[key])
                except (TypeError, ValueError):
                    continue
    return None


def build_evidence_replay(
    *,
    step_number: int,
    started_at: datetime,
    completed_at: datetime,
    duration_ms: int,
    success: bool,
    fallback_used: bool,
    result: Any,
    log_file_id: str | None,
    incident_id: str,
) -> ReplayStepRecord:
    """Build replay metadata for the Evidence stage."""
    source = _source_from_result(result, fallback_used)
    package = getattr(result, "evidence_package", None)
    evidence_refs: list[str] = []
    inputs: dict[str, Any] = {"incident_id": incident_id}
    outputs: dict[str, Any] = {}

    if log_file_id:
        inputs["log_file_id"] = log_file_id

    if package is not None:
        if hasattr(package, "model_dump"):
            pkg = sanitize_value(package.model_dump(mode="json"))
            outputs["evidence_package"] = pkg
            if isinstance(pkg, dict):
                evidence_refs.append(
                    f"Log file {pkg.get('uploaded_file_id', 'unknown')}"
                )
                sample = pkg.get("sample_entries", [])
                if sample:
                    evidence_refs.extend(
                        [sanitize_text(str(line))[:120] for line in sample[:3]]
                    )
        summary = getattr(result, "evidence_summary", None)
        if summary and hasattr(summary, "model_dump"):
            outputs["evidence_summary"] = sanitize_value(
                summary.model_dump(mode="json")
            )

    decision = (
        "Evidence collected and normalized"
        if success
        else "Evidence collection did not complete"
    )
    reason = (
        "Uploaded log was parsed into a structured evidence package for downstream agents."
        if success
        else "Evidence stage failed or was rejected by Guardian."
    )

    return ReplayStepRecord(
        step_number=step_number,
        agent_name="Evidence Agent",
        started_at=started_at,
        completed_at=completed_at,
        duration_ms=duration_ms,
        input_summary=summarize_json(inputs),
        output_summary=sanitize_text(decision),
        ai_used=source == "AI",
        fallback_used=fallback_used or source == "FALLBACK",
        status=ReplayStepStatus.COMPLETED if success else ReplayStepStatus.FAILED,
        decision=decision,
        reason=reason,
        confidence=_confidence_from_result(result) or 100 if success else None,
        evidence_used=evidence_refs,
        inputs=inputs,
        outputs=outputs,
        source=source,
    )


def build_threat_intel_replay(
    *,
    step_number: int,
    started_at: datetime,
    completed_at: datetime,
    duration_ms: int,
    success: bool,
    fallback_used: bool,
    result: Any,
    incident_id: str,
) -> ReplayStepRecord:
    """Build replay metadata for Threat Intelligence."""
    source = _source_from_result(result, fallback_used)
    outputs: dict[str, Any] = {}
    evidence_refs: list[str] = []
    ioc_count = 0

    if result is not None and hasattr(result, "model_dump"):
        payload = sanitize_value(result.model_dump(mode="json"))
        outputs = payload if isinstance(payload, dict) else {}
        ioc_count = int(outputs.get("ioc_count", 0) or 0)
        findings = outputs.get("findings", [])
        if isinstance(findings, list):
            for finding in findings[:5]:
                if isinstance(finding, dict):
                    evidence_refs.append(
                        f"{finding.get('indicator_type', 'IOC')}: {finding.get('indicator', '')}"
                    )

    decision = (
        f"Enriched {ioc_count} indicators"
        if success
        else "Threat intelligence enrichment failed"
    )
    reason = (
        "Extracted IOCs from evidence and applied reputation enrichment."
        if success
        else "Guardian rejected output or enrichment failed."
    )

    return ReplayStepRecord(
        step_number=step_number,
        agent_name="Threat Intelligence Agent",
        started_at=started_at,
        completed_at=completed_at,
        duration_ms=duration_ms,
        input_summary=summarize_json({"incident_id": incident_id}),
        output_summary=sanitize_text(decision),
        ai_used=source == "AI",
        fallback_used=fallback_used or source == "FALLBACK",
        status=ReplayStepStatus.COMPLETED if success else ReplayStepStatus.FAILED,
        decision=decision,
        reason=reason,
        confidence=_confidence_from_result(result),
        evidence_used=evidence_refs,
        inputs={"incident_id": incident_id},
        outputs=outputs,
        source=source,
    )


def build_mitre_replay(
    *,
    step_number: int,
    started_at: datetime,
    completed_at: datetime,
    duration_ms: int,
    success: bool,
    fallback_used: bool,
    result: Any,
    incident_id: str,
) -> ReplayStepRecord:
    """Build replay metadata for MITRE mapping."""
    source = _source_from_result(result, fallback_used)
    outputs: dict[str, Any] = {}
    evidence_refs: list[str] = []
    technique_count = 0

    if result is not None and hasattr(result, "model_dump"):
        payload = sanitize_value(result.model_dump(mode="json"))
        outputs = payload if isinstance(payload, dict) else {}
        techniques = outputs.get("techniques", [])
        if isinstance(techniques, list):
            technique_count = len(techniques)
            for tech in techniques[:5]:
                if isinstance(tech, dict):
                    evidence_refs.append(
                        f"{tech.get('technique_id', '')} {tech.get('technique_name', '')}"
                    )

    decision = (
        f"Mapped {technique_count} MITRE techniques"
        if success
        else "MITRE mapping failed"
    )
    reason = (
        "Evidence was correlated to ATT&CK techniques with confidence scores."
        if success
        else "No approved technique mapping was produced."
    )

    return ReplayStepRecord(
        step_number=step_number,
        agent_name="MITRE Mapping Agent",
        started_at=started_at,
        completed_at=completed_at,
        duration_ms=duration_ms,
        input_summary=summarize_json({"incident_id": incident_id}),
        output_summary=sanitize_text(decision),
        ai_used=source == "AI",
        fallback_used=fallback_used or source == "FALLBACK",
        status=ReplayStepStatus.COMPLETED if success else ReplayStepStatus.FAILED,
        decision=decision,
        reason=reason,
        confidence=_confidence_from_result(result),
        evidence_used=evidence_refs,
        inputs={"incident_id": incident_id},
        outputs=outputs,
        source=source,
    )


def build_risk_replay(
    *,
    step_number: int,
    started_at: datetime,
    completed_at: datetime,
    duration_ms: int,
    success: bool,
    fallback_used: bool,
    result: Any,
    incident_id: str,
) -> ReplayStepRecord:
    """Build replay metadata for Risk Assessment."""
    source = _source_from_result(result, fallback_used)
    outputs: dict[str, Any] = {}
    overall_risk = "Unknown"
    reasoning = ""

    if result is not None and hasattr(result, "model_dump"):
        payload = sanitize_value(result.model_dump(mode="json"))
        outputs = payload if isinstance(payload, dict) else {}
        overall_risk = str(outputs.get("overall_risk", "Unknown"))
        reasoning = sanitize_text(
            str(outputs.get("reasoning", outputs.get("summary", "")))
        )

    decision = (
        f"Overall risk assessed as {overall_risk}"
        if success
        else "Risk assessment failed"
    )
    reason = reasoning or (
        "Combined evidence, threat intelligence, and MITRE context into enterprise risk score."
        if success
        else "Risk assessment did not complete successfully."
    )

    return ReplayStepRecord(
        step_number=step_number,
        agent_name="Risk Assessment Agent",
        started_at=started_at,
        completed_at=completed_at,
        duration_ms=duration_ms,
        input_summary=summarize_json({"incident_id": incident_id}),
        output_summary=sanitize_text(decision),
        ai_used=source == "AI",
        fallback_used=fallback_used or source == "FALLBACK",
        status=ReplayStepStatus.COMPLETED if success else ReplayStepStatus.FAILED,
        decision=decision,
        reason=reason,
        confidence=_confidence_from_result(result),
        evidence_used=[],
        inputs={"incident_id": incident_id},
        outputs=outputs,
        source=source,
    )


def build_response_replay(
    *,
    step_number: int,
    started_at: datetime,
    completed_at: datetime,
    duration_ms: int,
    success: bool,
    fallback_used: bool,
    result: Any,
    incident_id: str,
) -> ReplayStepRecord:
    """Build replay metadata for Response Planning."""
    source = _source_from_result(result, fallback_used)
    outputs: dict[str, Any] = {}

    if result is not None and hasattr(result, "model_dump"):
        payload = sanitize_value(result.model_dump(mode="json"))
        outputs = payload if isinstance(payload, dict) else {}

    priority = str(outputs.get("priority", "P2"))
    decision = (
        f"Response plan drafted with priority {priority}"
        if success
        else "Response planning failed"
    )
    reason = sanitize_text(
        str(
            outputs.get(
                "executive_summary",
                "Containment and remediation actions were structured.",
            )
        )
    )

    return ReplayStepRecord(
        step_number=step_number,
        agent_name="Response Planning Agent",
        started_at=started_at,
        completed_at=completed_at,
        duration_ms=duration_ms,
        input_summary=summarize_json({"incident_id": incident_id}),
        output_summary=sanitize_text(decision),
        ai_used=source == "AI",
        fallback_used=fallback_used or source == "FALLBACK",
        status=ReplayStepStatus.COMPLETED if success else ReplayStepStatus.FAILED,
        decision=decision,
        reason=reason,
        confidence=_confidence_from_result(result),
        evidence_used=[],
        inputs={"incident_id": incident_id},
        outputs=outputs,
        source=source,
    )


def build_executive_report_replay(
    *,
    step_number: int,
    started_at: datetime,
    completed_at: datetime,
    duration_ms: int,
    success: bool,
    fallback_used: bool,
    result: Any,
    incident_id: str,
) -> ReplayStepRecord:
    """Build replay metadata for Executive Report."""
    source = _source_from_result(result, fallback_used)
    outputs: dict[str, Any] = {}

    if result is not None and hasattr(result, "model_dump"):
        payload = sanitize_value(result.model_dump(mode="json"))
        outputs = payload if isinstance(payload, dict) else {}

    decision = (
        "Executive report generated"
        if success
        else "Executive report generation failed"
    )
    reason = sanitize_text(
        str(
            outputs.get(
                "executive_summary",
                "Leadership summary prepared from investigation findings.",
            )
        )
    )

    return ReplayStepRecord(
        step_number=step_number,
        agent_name="Executive Report Agent",
        started_at=started_at,
        completed_at=completed_at,
        duration_ms=duration_ms,
        input_summary=summarize_json({"incident_id": incident_id}),
        output_summary=sanitize_text(decision),
        ai_used=source == "AI",
        fallback_used=fallback_used or source == "FALLBACK",
        status=ReplayStepStatus.COMPLETED if success else ReplayStepStatus.FAILED,
        decision=decision,
        reason=reason,
        confidence=_confidence_from_result(result),
        evidence_used=[],
        inputs={"incident_id": incident_id},
        outputs=outputs,
        source=source,
    )


def build_simple_replay(
    *,
    step_number: int,
    agent_name: str,
    started_at: datetime,
    completed_at: datetime,
    duration_ms: int,
    success: bool,
    decision: str,
    reason: str,
    inputs: dict[str, Any] | None = None,
    outputs: dict[str, Any] | None = None,
    confidence: int | None = None,
    source: SourceType = "SYSTEM",
    fallback_used: bool = False,
    skipped: bool = False,
) -> ReplayStepRecord:
    """Build replay metadata for system stages (Coordinator, Guardian, Timeline, Evaluation)."""
    status = (
        ReplayStepStatus.SKIPPED
        if skipped
        else (ReplayStepStatus.COMPLETED if success else ReplayStepStatus.FAILED)
    )
    return ReplayStepRecord(
        step_number=step_number,
        agent_name=agent_name,
        started_at=started_at,
        completed_at=completed_at,
        duration_ms=duration_ms,
        input_summary=summarize_json(inputs or {}),
        output_summary=sanitize_text(decision),
        ai_used=source == "AI",
        fallback_used=fallback_used,
        status=status,
        decision=decision,
        reason=sanitize_text(reason),
        confidence=confidence,
        evidence_used=[],
        inputs=sanitize_value(inputs or {}) if inputs else {},
        outputs=sanitize_value(outputs or {}) if outputs else {},
        source=source,
    )
