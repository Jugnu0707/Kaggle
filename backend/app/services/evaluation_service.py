"""Evaluation service — benchmarks, persistence, and API aggregation."""

from __future__ import annotations

from evaluation.engine import EvaluationEngine
from evaluation.metrics import AgentMetrics, ExecutionMetric
from evaluation.report_generator import generate_json_report, generate_markdown_report
from evaluation.scorer import calculate_health_breakdown
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ai.runtime import get_ai_runtime
from app.core.exceptions import NotFoundException
from app.models.evaluation_metric import EvaluationMetric
from app.models.investigation_run import InvestigationRun
from app.repositories.evaluation_metric_repository import EvaluationMetricRepository
from app.schemas.evaluation import (
    AgentEvaluationDetail,
    AgentEvaluationSummary,
    EvaluationOverview,
)


class EvaluationService:
    """Runs evaluation benchmarks and exposes aggregated metrics."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.metric_repository = EvaluationMetricRepository(db)
        self.engine = EvaluationEngine()

    def ensure_metrics(self) -> None:
        """Run benchmarks when no evaluation metrics exist."""
        if self.metric_repository.count_all() == 0:
            self.run_evaluation()

    def run_evaluation(self) -> EvaluationOverview:
        """Execute benchmarks, persist metrics, and return the overview."""
        self.metric_repository.delete_all()
        execution_metrics = self.engine.run_benchmarks(self.db)
        self._persist_metrics(execution_metrics)
        self.db.commit()
        summary = self.engine.build_summary(execution_metrics)
        generate_json_report(summary)
        generate_markdown_report(summary)
        return self.get_overview()

    def get_overview(self) -> EvaluationOverview:
        """Return aggregated evaluation metrics for all agents."""
        self.ensure_metrics()
        stored = self.metric_repository.list_all()
        execution_metrics = self._to_execution_metrics(stored)
        summary = self.engine.build_summary(execution_metrics)
        agents = [self._to_agent_summary(agent) for agent in summary.agents]
        runtime_metrics = get_ai_runtime().get_metrics_snapshot()
        mean_agent_ms = (
            sum(agent.mean_execution_time_ms for agent in agents) / len(agents)
            if agents
            else 0.0
        )
        mean_investigation_ms = self._mean_investigation_duration_ms()
        tool_count = int(runtime_metrics["tool_execution_count"])
        mean_mcp_ms = (
            float(runtime_metrics["total_mcp_latency_ms"]) / tool_count
            if tool_count
            else 0.0
        )
        return EvaluationOverview(
            overall_score=summary.overall_score,
            agents=agents,
            total_executions=summary.total_executions,
            overall_success_rate=round(summary.overall_success_rate * 100, 2),
            generated_at=summary.generated_at,
            tool_execution_count=tool_count,
            tool_failure_count=int(runtime_metrics["tool_failure_count"]),
            mean_adk_session_duration_ms=float(
                runtime_metrics["mean_adk_session_duration_ms"]
            ),
            mean_investigation_duration_ms=round(mean_investigation_ms, 2),
            mean_agent_execution_time_ms=round(mean_agent_ms, 2),
            mean_mcp_latency_ms=round(mean_mcp_ms, 2),
        )

    def get_agent_detail(self, agent_name: str) -> AgentEvaluationDetail:
        """Return detailed statistics for one agent."""
        self.ensure_metrics()
        stored = self.metric_repository.list_by_agent_name(agent_name)
        if not stored:
            raise NotFoundException(
                f"Evaluation metrics not found for agent: {agent_name}"
            )

        execution_metrics = self._to_execution_metrics(stored)
        agent_metrics = AgentMetrics(
            agent_name=agent_name, executions=execution_metrics
        )
        summary = self._to_agent_summary(agent_metrics)
        recent_executions = [
            {
                "execution_time_ms": metric.execution_time_ms,
                "success": metric.success,
                "ai_used": metric.ai_used,
                "fallback_used": metric.fallback_used,
                "confidence": metric.confidence,
                "retry_count": metric.retry_count,
                "output_size": metric.output_size,
            }
            for metric in execution_metrics[-20:]
        ]
        return AgentEvaluationDetail(
            **summary.model_dump(),
            recent_executions=recent_executions,
        )

    def _persist_metrics(self, metrics: list[ExecutionMetric]) -> None:
        records = [
            EvaluationMetric(
                agent_name=metric.agent_name,
                execution_time_ms=metric.execution_time_ms,
                ai_used=metric.ai_used,
                fallback_used=metric.fallback_used,
                success=metric.success,
                confidence=metric.confidence,
            )
            for metric in metrics
        ]
        self.metric_repository.create_batch(records)

    def _to_execution_metrics(
        self, records: list[EvaluationMetric]
    ) -> list[ExecutionMetric]:
        return [
            ExecutionMetric(
                agent_name=record.agent_name,
                execution_time_ms=record.execution_time_ms,
                success=record.success,
                ai_used=record.ai_used,
                fallback_used=record.fallback_used,
                confidence=record.confidence,
            )
            for record in records
        ]

    def _to_agent_summary(self, agent: AgentMetrics) -> AgentEvaluationSummary:
        breakdown = calculate_health_breakdown(agent)
        return AgentEvaluationSummary(
            agent_name=agent.agent_name,
            health_score=breakdown["health_score"],
            availability=breakdown["availability"],
            reliability=breakdown["reliability"],
            performance=breakdown["performance"],
            accuracy=breakdown["accuracy"],
            total_executions=agent.total_executions,
            success_count=agent.success_count,
            failure_count=agent.failure_count,
            success_rate=round(agent.success_rate * 100, 2),
            mean_execution_time_ms=round(agent.mean_execution_time_ms, 2),
            ai_used_count=agent.ai_used_count,
            fallback_used_count=agent.fallback_used_count,
            mean_confidence=(
                round(agent.mean_confidence, 2)
                if agent.mean_confidence is not None
                else None
            ),
            mean_retry_count=round(agent.mean_retry_count, 2),
            mean_output_size=round(agent.mean_output_size, 2),
        )

    def _mean_investigation_duration_ms(self) -> float:
        """Return the mean completed investigation duration in milliseconds."""
        value = self.db.scalar(
            select(func.avg(InvestigationRun.duration_ms)).where(
                InvestigationRun.duration_ms.isnot(None)
            )
        )
        return float(value or 0.0)
