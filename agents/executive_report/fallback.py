"""Template-based fallback executive report engine."""

from __future__ import annotations

from agents.executive_report.markdown_generator import generate_markdown_report
from agents.executive_report.models import ExecutiveReportResult
from agents.executive_report.schemas import (
    ExecutiveReportContext,
    ExecutiveReportSource,
    ReportSections,
)

DEFAULT_TITLE = "Executive Incident Report"


def _timeline_summary(context: ExecutiveReportContext) -> str:
    if not context.evidence_summaries:
        return (
            f"The incident was reported on {context.incident.created_at or 'the detection window'} "
            f"and remains in {context.incident.status.lower()} status. "
            "Investigation activities are underway to establish a complete timeline."
        )

    ranges = [
        summary.time_range
        for summary in context.evidence_summaries
        if summary.time_range
    ]
    if ranges:
        earliest_range = ranges[0]
        return (
            f"Activity was observed during {earliest_range}. "
            f"The incident is currently {context.incident.status.lower()} and under coordinated review."
        )

    return (
        f"The incident was detected through {context.incident.source} and is currently "
        f"{context.incident.status.lower()}. Analysts are validating the sequence of events."
    )


def _mitre_summary(context: ExecutiveReportContext) -> str:
    if not context.mitre_techniques:
        return (
            "No confirmed adversary techniques have been mapped yet. "
            "Security teams continue analysis to align activity with known attack patterns."
        )

    technique_names = [
        f"{technique.technique_name} ({technique.tactic})"
        for technique in context.mitre_techniques[:5]
    ]
    return (
        f"Analysis identified {len(context.mitre_techniques)} relevant attack technique(s), "
        f"including {', '.join(technique_names)}. "
        "These patterns indicate deliberate adversary behavior requiring coordinated response."
    )


def _risk_summary(context: ExecutiveReportContext) -> str:
    if context.risk_assessment is None:
        return (
            f"The incident is classified at {context.incident.severity} severity while "
            "formal enterprise risk scoring is finalized."
        )

    risk = context.risk_assessment
    return (
        f"Enterprise risk is assessed as {risk.overall_risk} with priority {risk.priority}. "
        f"Likelihood is {risk.likelihood.lower()} and business impact is {risk.business_impact.lower()}. "
        f"{risk.summary}"
    )


def _business_impact(context: ExecutiveReportContext) -> str:
    if context.risk_assessment is not None:
        return context.risk_assessment.business_impact

    severity_impacts = {
        "Critical": "Severe operational disruption and potential regulatory exposure.",
        "High": "Significant business disruption with elevated data and service risk.",
        "Medium": "Moderate operational impact requiring management oversight.",
        "Low": "Limited business impact with manageable operational consequences.",
    }
    return severity_impacts.get(
        context.incident.severity,
        "Business impact is being evaluated by security and operations leadership.",
    )


def _key_findings(context: ExecutiveReportContext) -> list[str]:
    findings: list[str] = [
        f"{context.incident.severity}-severity incident reported via {context.incident.source}.",
        context.incident.description,
    ]

    if context.mitre_techniques:
        top_technique = context.mitre_techniques[0]
        findings.append(
            f"Attack activity aligns with {top_technique.technique_name} under the "
            f"{top_technique.tactic} tactic."
        )

    if context.suspicious_indicator_count > 0:
        findings.append(
            f"{context.suspicious_indicator_count} suspicious indicator(s) require further review."
        )

    if context.response_plan is not None:
        findings.append(
            f"A {context.response_plan.priority}-priority response plan has been prepared for leadership review."
        )

    return findings[:6]


def _recommended_actions(context: ExecutiveReportContext) -> list[str]:
    actions: list[str] = []

    if context.response_plan is not None:
        actions.extend(context.response_plan.containment[:2])
        actions.extend(context.response_plan.recovery[:1])
        actions.extend(context.response_plan.monitoring[:1])
    else:
        actions.extend(
            [
                "Convene the incident response team for executive briefing.",
                "Approve containment measures for affected business systems.",
                "Communicate status updates to business stakeholders.",
            ]
        )

    deduped: list[str] = []
    seen: set[str] = set()
    for action in actions:
        if action not in seen:
            seen.add(action)
            deduped.append(action)
    return deduped[:6]


def _lessons_learned(context: ExecutiveReportContext) -> list[str]:
    lessons = [
        "Maintain regular executive briefings during active incident response.",
        "Ensure backup and recovery readiness for critical business services.",
    ]

    if context.mitre_techniques:
        lessons.append(
            "Strengthen detective controls for techniques observed in this incident."
        )

    if context.suspicious_indicator_count > 0:
        lessons.append(
            "Review threat intelligence sharing processes to accelerate future enrichment."
        )

    return lessons[:5]


def _executive_summary(context: ExecutiveReportContext, business_impact: str) -> str:
    return (
        f"{context.incident.title} is a {context.incident.severity.lower()}-severity security incident "
        f"currently in {context.incident.status.lower()} status. {business_impact} "
        "Leadership should review recommended actions and approve the response plan."
    )


def generate_executive_report_fallback(
    context: ExecutiveReportContext,
) -> ExecutiveReportResult:
    """Generate a deterministic executive report without AI."""
    business_impact = _business_impact(context)
    sections = ReportSections(
        title=DEFAULT_TITLE,
        executive_summary=_executive_summary(context, business_impact),
        business_impact=business_impact,
        incident_timeline_summary=_timeline_summary(context),
        key_findings=_key_findings(context),
        mitre_summary=_mitre_summary(context),
        risk_summary=_risk_summary(context),
        recommended_actions=_recommended_actions(context),
        lessons_learned=_lessons_learned(context),
    )
    markdown = generate_markdown_report(sections)

    return ExecutiveReportResult(
        source=ExecutiveReportSource.FALLBACK,
        title=sections.title,
        executive_summary=sections.executive_summary,
        business_impact=sections.business_impact,
        key_findings=sections.key_findings,
        recommended_actions=sections.recommended_actions,
        lessons_learned=sections.lessons_learned,
        markdown=markdown,
    )
