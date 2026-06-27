"""Repository for evaluation metric persistence."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.evaluation_metric import EvaluationMetric


class EvaluationMetricRepository:
    """Handles database operations for evaluation metrics."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, metric: EvaluationMetric) -> EvaluationMetric:
        """Persist a new evaluation metric."""
        self.db.add(metric)
        self.db.flush()
        return metric

    def create_batch(self, metrics: list[EvaluationMetric]) -> list[EvaluationMetric]:
        """Persist multiple evaluation metrics."""
        for metric in metrics:
            self.db.add(metric)
        self.db.flush()
        return metrics

    def list_all(self) -> list[EvaluationMetric]:
        """Return all evaluation metrics ordered by creation time."""
        stmt = select(EvaluationMetric).order_by(EvaluationMetric.created_at.asc())
        return list(self.db.scalars(stmt).all())

    def list_by_agent_name(self, agent_name: str) -> list[EvaluationMetric]:
        """Return metrics for a specific agent."""
        stmt = (
            select(EvaluationMetric)
            .where(EvaluationMetric.agent_name == agent_name)
            .order_by(EvaluationMetric.created_at.asc())
        )
        return list(self.db.scalars(stmt).all())

    def count_all(self) -> int:
        """Return total metric count."""
        stmt = select(func.count()).select_from(EvaluationMetric)
        return int(self.db.scalar(stmt) or 0)

    def delete_all(self) -> None:
        """Remove all evaluation metrics."""
        for metric in self.list_all():
            self.db.delete(metric)
        self.db.flush()
