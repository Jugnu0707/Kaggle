"""Investigation replay and explainability service."""

from __future__ import annotations

import json
import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.core.logging import get_logger
from app.models.investigation_replay import InvestigationReplay
from app.repositories.investigation_replay_repository import (
    InvestigationReplayRepository,
)
from app.repositories.investigation_run_repository import InvestigationRunRepository
from app.schemas.investigation_replay import (
    ConfidenceDistribution,
    DecisionChainItem,
    InvestigationExplainResponse,
    InvestigationReplayExportResponse,
    InvestigationReplayResponse,
    InvestigationReplayStepResponse,
    ReplayStepExplainability,
)
from app.services.replay_builder import ReplayStepRecord

logger = get_logger(__name__)


class InvestigationReplayService:
    """Generates, stores, and exports investigation replay and explainability data."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.run_repository = InvestigationRunRepository(db)
        self.replay_repository = InvestigationReplayRepository(db)

    def persist_steps(
        self,
        run_id: uuid.UUID,
        records: list[ReplayStepRecord],
    ) -> list[InvestigationReplay]:
        """Persist replay step records for an investigation run."""
        self.replay_repository.delete_by_run_id(run_id)
        entities = [
            InvestigationReplay(
                investigation_run_id=run_id,
                step_number=record.step_number,
                agent_name=record.agent_name,
                started_at=record.started_at,
                completed_at=record.completed_at,
                duration_ms=record.duration_ms,
                input_summary=self._encode_explainability_blob(record),
                output_summary=record.output_summary,
                ai_used=record.ai_used,
                fallback_used=record.fallback_used,
                status=record.status,
            )
            for record in records
        ]
        saved = self.replay_repository.create_many(entities)
        logger.info(
            "Replay persisted: run_id=%s steps=%s",
            run_id,
            len(saved),
        )
        return saved

    def get_replay(self, run_id: uuid.UUID) -> InvestigationReplayResponse:
        """Return step-by-step replay for an investigation run."""
        run = self._get_run_or_404(run_id)
        logger.info("Replay requested: run_id=%s", run_id)

        steps = self.replay_repository.list_by_run_id(run_id)
        records = self._records_from_entities(steps)
        response = self._build_replay_response(run, records)

        logger.info("Replay completed: run_id=%s steps=%s", run_id, len(response.steps))
        return response

    def get_explain(self, run_id: uuid.UUID) -> InvestigationExplainResponse:
        """Return explainability summary for an investigation run."""
        run = self._get_run_or_404(run_id)
        logger.info("Explainability requested: run_id=%s", run_id)

        steps = self.replay_repository.list_by_run_id(run_id)
        records = self._records_from_entities(steps)
        response = self._build_explain_response(run, records)

        logger.info("Explainability generated: run_id=%s", run_id)
        return response

    def export_replay(
        self,
        run_id: uuid.UUID,
        *,
        format: str = "json",
    ) -> InvestigationReplayExportResponse:
        """Export replay as JSON or Markdown."""
        logger.info("Export generated: run_id=%s format=%s", run_id, format)

        if format == "markdown":
            explain = self.get_explain(run_id)
            replay = self.get_replay(run_id)
            content = self._to_markdown(replay, explain)
            return InvestigationReplayExportResponse(
                format="markdown",
                content=content,
                run_id=run_id,
            )

        explain = self.get_explain(run_id)
        replay = self.get_replay(run_id)
        payload = {
            "run_id": str(replay.run_id),
            "incident_id": str(replay.incident_id),
            "status": replay.status.value,
            "duration_ms": replay.duration_ms,
            "overall_risk": explain.overall_risk,
            "evaluation_score": explain.evaluation_score,
            "ai_usage_count": explain.ai_usage_count,
            "fallback_usage_count": explain.fallback_usage_count,
            "execution_order": [
                {
                    "step": step.step,
                    "agent": step.agent,
                    "duration_ms": step.duration_ms,
                    "source": step.source,
                    "status": step.status,
                    "summary": step.summary,
                    "confidence": step.confidence,
                    "decision": (
                        step.explainability.decision if step.explainability else None
                    ),
                    "reason": (
                        step.explainability.reason if step.explainability else None
                    ),
                }
                for step in replay.steps
            ],
            "decision_chain": [item.model_dump() for item in explain.decision_chain],
            "final_result": explain.overall_investigation_summary,
        }
        return InvestigationReplayExportResponse(
            format="json",
            content=json.dumps(payload, indent=2, default=str),
            run_id=run_id,
        )

    def _get_run_or_404(self, run_id: uuid.UUID):
        run = self.run_repository.get_by_id(run_id)
        if run is None:
            raise NotFoundException("Investigation run not found")
        return run

    def _encode_explainability_blob(self, record: ReplayStepRecord) -> str:
        """Store sanitized explainability metadata in input_summary."""
        return json.dumps(
            {
                "inputs": record.inputs,
                "outputs": record.outputs,
                "decision": record.decision,
                "reason": record.reason,
                "confidence": record.confidence,
                "evidence_used": record.evidence_used,
                "source": record.source,
                "input_summary": record.input_summary,
            },
            default=str,
        )

    def _decode_explainability_blob(self, input_summary: str) -> dict:
        try:
            payload = json.loads(input_summary)
            if isinstance(payload, dict):
                return payload
        except json.JSONDecodeError:
            pass
        return {"input_summary": input_summary}

    def _records_from_entities(
        self, steps: list[InvestigationReplay]
    ) -> list[ReplayStepRecord]:
        """Rebuild in-memory replay records from persisted rows."""
        records: list[ReplayStepRecord] = []
        for step in steps:
            blob = self._decode_explainability_blob(step.input_summary)
            source = str(blob.get("source", "SYSTEM"))
            if step.fallback_used:
                source = "FALLBACK"
            elif step.ai_used:
                source = "AI"
            records.append(
                ReplayStepRecord(
                    step_number=step.step_number,
                    agent_name=step.agent_name,
                    started_at=step.started_at,
                    completed_at=step.completed_at,
                    duration_ms=step.duration_ms,
                    input_summary=str(blob.get("input_summary", step.input_summary)),
                    output_summary=step.output_summary,
                    ai_used=step.ai_used,
                    fallback_used=step.fallback_used,
                    status=step.status,
                    decision=str(blob.get("decision", step.output_summary)),
                    reason=str(blob.get("reason", step.output_summary)),
                    confidence=blob.get("confidence"),
                    evidence_used=list(blob.get("evidence_used", [])),
                    inputs=(
                        blob.get("inputs", {})
                        if isinstance(blob.get("inputs"), dict)
                        else {}
                    ),
                    outputs=(
                        blob.get("outputs", {})
                        if isinstance(blob.get("outputs"), dict)
                        else {}
                    ),
                    source=source,
                )
            )
        return records

    def _build_replay_response(
        self,
        run,
        records: list[ReplayStepRecord],
    ) -> InvestigationReplayResponse:
        steps = [self._to_step_response(record) for record in records]
        return InvestigationReplayResponse(
            run_id=run.id,
            incident_id=run.incident_id,
            status=run.status,
            duration_ms=run.duration_ms or 0,
            steps=steps,
        )

    def _build_explain_response(
        self, run, records: list[ReplayStepRecord]
    ) -> InvestigationExplainResponse:
        overall = json.loads(run.overall_result or "{}")
        overall_risk = str(overall.get("overall_risk", "Medium"))
        evaluation_score = overall.get("evaluation_score")

        ai_count = sum(1 for record in records if record.source == "AI")
        fallback_count = sum(1 for record in records if record.source == "FALLBACK")
        system_count = sum(1 for record in records if record.source == "SYSTEM")

        decision_chain = [
            DecisionChainItem(
                step=record.step_number,
                agent=record.agent_name,
                decision=record.decision or record.output_summary,
                reason=record.reason,
                confidence=record.confidence,
                source=record.source,
            )
            for record in records
        ]

        agent_reasoning = [
            ReplayStepExplainability(
                decision=record.decision or record.output_summary,
                reason=record.reason,
                confidence=record.confidence,
                evidence_used=record.evidence_used,
                inputs=record.inputs,
                outputs=record.outputs,
                execution_time_ms=record.duration_ms,
                source=record.source,
            )
            for record in records
        ]

        confidences = [
            record.confidence for record in records if record.confidence is not None
        ]
        distribution = ConfidenceDistribution(
            min_confidence=min(confidences) if confidences else None,
            max_confidence=max(confidences) if confidences else None,
            average_confidence=(
                round(sum(confidences) / len(confidences), 1) if confidences else None
            ),
            steps_with_confidence=len(confidences),
        )

        summary_parts = [
            f"Investigation run {run.status.value} in {run.duration_ms or 0} ms.",
            f"Overall risk: {overall_risk}.",
            f"AI steps: {ai_count}, fallback steps: {fallback_count}, system steps: {system_count}.",
        ]
        if evaluation_score is not None:
            summary_parts.append(f"Evaluation score: {evaluation_score}.")

        return InvestigationExplainResponse(
            run_id=run.id,
            incident_id=run.incident_id,
            status=run.status,
            overall_investigation_summary=" ".join(summary_parts),
            overall_risk=overall_risk,
            ai_usage_count=ai_count,
            fallback_usage_count=fallback_count,
            system_steps_count=system_count,
            decision_chain=decision_chain,
            agent_reasoning=agent_reasoning,
            confidence_distribution=distribution,
            evaluation_score=evaluation_score,
            duration_ms=run.duration_ms or 0,
        )

    def _to_step_response(
        self, record: ReplayStepRecord
    ) -> InvestigationReplayStepResponse:
        explainability = ReplayStepExplainability(
            decision=record.decision or record.output_summary,
            reason=record.reason,
            confidence=record.confidence,
            evidence_used=record.evidence_used,
            inputs=record.inputs,
            outputs=record.outputs,
            execution_time_ms=record.duration_ms,
            source=record.source,
        )
        return InvestigationReplayStepResponse(
            step=record.step_number,
            agent=record.agent_name,
            duration_ms=record.duration_ms,
            source=record.source,
            summary=record.output_summary,
            confidence=record.confidence,
            status=record.status.value,
            fallback_used=record.fallback_used,
            started_at=record.started_at,
            completed_at=record.completed_at,
            explainability=explainability,
        )

    def _to_markdown(
        self, replay: InvestigationReplayResponse, explain: InvestigationExplainResponse
    ) -> str:
        lines = [
            "# Investigation Replay Export",
            "",
            f"- **Run ID:** `{replay.run_id}`",
            f"- **Incident ID:** `{replay.incident_id}`",
            f"- **Status:** {replay.status.value}",
            f"- **Duration:** {replay.duration_ms} ms",
            f"- **Overall risk:** {explain.overall_risk}",
            f"- **AI usage:** {explain.ai_usage_count} steps",
            f"- **Fallback usage:** {explain.fallback_usage_count} steps",
            "",
            "## Summary",
            "",
            explain.overall_investigation_summary,
            "",
            "## Execution Order",
            "",
        ]

        for step in replay.steps:
            lines.extend(
                [
                    f"### Step {step.step}: {step.agent}",
                    "",
                    f"- Status: {step.status}",
                    f"- Duration: {step.duration_ms} ms",
                    f"- Source: {step.source}",
                    f"- Confidence: {step.confidence if step.confidence is not None else 'n/a'}",
                    f"- Summary: {step.summary}",
                    "",
                ]
            )
            if step.explainability:
                lines.append(f"- Decision: {step.explainability.decision}")
                lines.append(f"- Reason: {step.explainability.reason}")
                if step.explainability.evidence_used:
                    lines.append("- Evidence:")
                    for ref in step.explainability.evidence_used:
                        lines.append(f"  - {ref}")
                lines.append("")

        lines.append("## Decision Chain")
        lines.append("")
        for item in explain.decision_chain:
            lines.append(
                f"{item.step}. **{item.agent}** — {item.decision} ({item.source}, "
                f"confidence {item.confidence if item.confidence is not None else 'n/a'})"
            )

        return "\n".join(lines)
