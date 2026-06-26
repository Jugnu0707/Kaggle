"""Rule-based fallback risk assessment engine."""

from __future__ import annotations

from agents.risk.models import RiskAssessmentResult
from agents.risk.schemas import RiskAssessmentContext, RiskAssessmentSource, RiskLevel

RANSOMWARE_TECHNIQUE = "T1486"
FAILED_LOGIN_TECHNIQUE = "T1110"
POWERSHELL_TECHNIQUE = "T1059.001"

RISK_SCORE_RANGES = {
    RiskLevel.CRITICAL: (90, 100),
    RiskLevel.HIGH: (70, 89),
    RiskLevel.MEDIUM: (40, 69),
    RiskLevel.LOW: (0, 39),
}

PRIORITY_BY_RISK = {
    RiskLevel.CRITICAL: "P1",
    RiskLevel.HIGH: "P2",
    RiskLevel.MEDIUM: "P3",
    RiskLevel.LOW: "P4",
}


def _technique_ids(context: RiskAssessmentContext) -> set[str]:
    return {technique.technique_id for technique in context.mitre_techniques}


def _max_mitre_confidence(context: RiskAssessmentContext) -> int:
    if not context.mitre_techniques:
        return 0
    return max(technique.confidence for technique in context.mitre_techniques)


def _contains_ransomware(context: RiskAssessmentContext) -> bool:
    if RANSOMWARE_TECHNIQUE in _technique_ids(context):
        return True
    combined = f"{context.incident.title} {context.incident.description}".lower()
    return "ransomware" in combined


def _score_for_level(level: RiskLevel) -> int:
    low, high = RISK_SCORE_RANGES[level]
    return (low + high) // 2


def _likelihood_for_level(level: RiskLevel) -> str:
    mapping = {
        RiskLevel.CRITICAL: "Very Likely",
        RiskLevel.HIGH: "Likely",
        RiskLevel.MEDIUM: "Possible",
        RiskLevel.LOW: "Unlikely",
    }
    return mapping[level]


def _impact_for_level(level: RiskLevel) -> str:
    mapping = {
        RiskLevel.CRITICAL: "Severe operational and data impact",
        RiskLevel.HIGH: "Significant business disruption",
        RiskLevel.MEDIUM: "Moderate operational impact",
        RiskLevel.LOW: "Limited business impact",
    }
    return mapping[level]


def assess_risk_fallback(context: RiskAssessmentContext) -> RiskAssessmentResult:
    """Compute enterprise risk using deterministic fallback rules."""
    technique_ids = _technique_ids(context)
    matched_rules: list[str] = []
    severity = context.incident.severity

    if severity == RiskLevel.CRITICAL.value:
        matched_rules.append("Incident severity is Critical")
    if _contains_ransomware(context):
        matched_rules.append("Ransomware activity detected")
    if RANSOMWARE_TECHNIQUE in technique_ids:
        matched_rules.append(f"MITRE technique {RANSOMWARE_TECHNIQUE} mapped")

    if matched_rules:
        level = RiskLevel.CRITICAL
    elif (
        severity == RiskLevel.HIGH.value
        or len(context.mitre_techniques) > 3
        or _max_mitre_confidence(context) > 90
    ):
        level = RiskLevel.HIGH
        if severity == RiskLevel.HIGH.value:
            matched_rules.append("Incident severity is High")
        if len(context.mitre_techniques) > 3:
            matched_rules.append("More than three MITRE techniques mapped")
        if _max_mitre_confidence(context) > 90:
            matched_rules.append("MITRE mapping confidence exceeds 90")
    elif (
        severity == RiskLevel.MEDIUM.value
        or FAILED_LOGIN_TECHNIQUE in technique_ids
        or POWERSHELL_TECHNIQUE in technique_ids
    ):
        level = RiskLevel.MEDIUM
        if severity == RiskLevel.MEDIUM.value:
            matched_rules.append("Incident severity is Medium")
        if FAILED_LOGIN_TECHNIQUE in technique_ids:
            matched_rules.append("Failed login attempts detected")
        if POWERSHELL_TECHNIQUE in technique_ids:
            matched_rules.append("PowerShell execution detected")
    else:
        level = RiskLevel.LOW
        matched_rules.append("No elevated risk indicators matched fallback rules")

    confidence = min(95, max(60, _max_mitre_confidence(context) or int(context.incident.confidence_score * 100)))
    summary = (
        f"Fallback risk assessment classified the incident as {level.value} "
        f"based on {len(matched_rules)} rule match(es)."
    )
    reasoning = "; ".join(matched_rules)

    return RiskAssessmentResult(
        source=RiskAssessmentSource.FALLBACK,
        overall_risk=level.value,
        risk_score=_score_for_level(level),
        likelihood=_likelihood_for_level(level),
        business_impact=_impact_for_level(level),
        confidence=confidence,
        priority=PRIORITY_BY_RISK[level],
        summary=summary,
        reasoning=reasoning,
    )
