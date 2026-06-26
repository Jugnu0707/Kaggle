"""Rule-based fallback response planning engine."""

from __future__ import annotations

from agents.response.models import ResponsePlanResult
from agents.response.schemas import ResponsePlanningContext, ResponsePlanSource

RANSOMWARE_TECHNIQUE = "T1486"
FAILED_LOGIN_TECHNIQUE = "T1110"
POWERSHELL_TECHNIQUE = "T1059.001"

RANSOMWARE_CONTAINMENT = [
    "Isolate affected host from the network",
    "Disable SMB on impacted segments",
    "Disconnect compromised systems from shared resources",
]
RANSOMWARE_ERADICATION = [
    "Preserve forensic evidence before remediation",
    "Remove ransomware binaries and persistence mechanisms",
    "Reset credentials for affected accounts",
]
RANSOMWARE_RECOVERY = [
    "Restore encrypted files from verified offline backups",
    "Rebuild compromised systems from known-good images",
    "Validate data integrity before returning to production",
]
RANSOMWARE_MONITORING = [
    "Monitor for re-encryption or lateral movement",
    "Track backup restoration progress and integrity checks",
    "Escalate to executive leadership and legal counsel",
]

POWERSHELL_CONTAINMENT = [
    "Isolate the affected endpoint",
    "Collect volatile memory for forensic analysis",
]
POWERSHELL_ERADICATION = [
    "Block unauthorized PowerShell execution via application control",
    "Remove malicious scripts and scheduled tasks",
    "Review and terminate suspicious parent processes",
]
POWERSHELL_RECOVERY = [
    "Validate endpoint integrity before reconnection",
    "Re-enable PowerShell only with constrained language mode if required",
]
POWERSHELL_MONITORING = [
    "Monitor endpoint for repeated script execution",
    "Review parent process lineage and command-line arguments",
    "Escalate to SOC lead if lateral movement is suspected",
]

FAILED_LOGIN_CONTAINMENT = [
    "Block source IP addresses at the network perimeter",
    "Disable or lock targeted user accounts pending review",
]
FAILED_LOGIN_ERADICATION = [
    "Reset passwords for affected accounts",
    "Revoke active sessions and refresh authentication tokens",
    "Enable multi-factor authentication for impacted identities",
]
FAILED_LOGIN_RECOVERY = [
    "Restore account access after credential reset and MFA enrollment",
    "Validate no unauthorized privilege changes occurred",
]
FAILED_LOGIN_MONITORING = [
    "Monitor authentication logs for repeated failures",
    "Alert on geo-anomalous or off-hours login attempts",
    "Escalate to identity team if brute-force patterns persist",
]

GENERIC_CONTAINMENT = [
    "Document current incident scope and affected assets",
    "Restrict access to impacted systems pending investigation",
]
GENERIC_ERADICATION = [
    "Remove identified malicious artifacts",
    "Patch vulnerable services linked to the incident",
]
GENERIC_RECOVERY = [
    "Restore affected services from known-good backups if required",
    "Validate system integrity before returning to production",
]
GENERIC_MONITORING = [
    "Monitor affected systems for recurrence",
    "Review audit and security logs for related activity",
]

PRIORITY_BY_SEVERITY = {
    "Critical": "P1",
    "High": "P2",
    "Medium": "P3",
    "Low": "P4",
}


def _technique_ids(context: ResponsePlanningContext) -> set[str]:
    return {technique.technique_id for technique in context.mitre_techniques}


def _contains_ransomware(context: ResponsePlanningContext) -> bool:
    if RANSOMWARE_TECHNIQUE in _technique_ids(context):
        return True
    combined = f"{context.incident.title} {context.incident.description}".lower()
    return "ransomware" in combined


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def _priority_for_context(context: ResponsePlanningContext) -> str:
    if context.risk_assessment is not None:
        return context.risk_assessment.priority
    return PRIORITY_BY_SEVERITY.get(context.incident.severity, "P4")


def plan_response_fallback(context: ResponsePlanningContext) -> ResponsePlanResult:
    """Generate a deterministic incident response plan without AI."""
    technique_ids = _technique_ids(context)
    matched_rules: list[str] = []
    containment: list[str] = []
    eradication: list[str] = []
    recovery: list[str] = []
    monitoring: list[str] = []

    if _contains_ransomware(context) or RANSOMWARE_TECHNIQUE in technique_ids:
        matched_rules.append("Ransomware response playbook")
        containment.extend(RANSOMWARE_CONTAINMENT)
        eradication.extend(RANSOMWARE_ERADICATION)
        recovery.extend(RANSOMWARE_RECOVERY)
        monitoring.extend(RANSOMWARE_MONITORING)

    if POWERSHELL_TECHNIQUE in technique_ids:
        matched_rules.append("PowerShell execution playbook")
        containment.extend(POWERSHELL_CONTAINMENT)
        eradication.extend(POWERSHELL_ERADICATION)
        recovery.extend(POWERSHELL_RECOVERY)
        monitoring.extend(POWERSHELL_MONITORING)

    if FAILED_LOGIN_TECHNIQUE in technique_ids:
        matched_rules.append("Failed login playbook")
        containment.extend(FAILED_LOGIN_CONTAINMENT)
        eradication.extend(FAILED_LOGIN_ERADICATION)
        recovery.extend(FAILED_LOGIN_RECOVERY)
        monitoring.extend(FAILED_LOGIN_MONITORING)

    if not matched_rules:
        matched_rules.append("Generic incident response playbook")
        containment.extend(GENERIC_CONTAINMENT)
        eradication.extend(GENERIC_ERADICATION)
        recovery.extend(GENERIC_RECOVERY)
        monitoring.extend(GENERIC_MONITORING)

    priority = _priority_for_context(context)
    executive_summary = (
        f"Fallback response plan generated at {priority} priority using "
        f"{len(matched_rules)} playbook(s): {', '.join(matched_rules)}. "
        "All actions are recommendations only and require human approval before execution."
    )

    return ResponsePlanResult(
        source=ResponsePlanSource.FALLBACK,
        priority=priority,
        containment=_dedupe(containment),
        eradication=_dedupe(eradication),
        recovery=_dedupe(recovery),
        monitoring=_dedupe(monitoring),
        executive_summary=executive_summary,
    )
