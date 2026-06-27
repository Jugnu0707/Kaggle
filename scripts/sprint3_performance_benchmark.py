#!/usr/bin/env python3
"""Sprint 3 performance benchmark — measures key API and workflow timings.

Run from repository root:

    python scripts/sprint3_performance_benchmark.py

Outputs markdown report to docs/SPRINT3_PERFORMANCE_REPORT.md
"""

from __future__ import annotations

import os
import sys
import time
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))
os.chdir(BACKEND_ROOT)

import app.models  # noqa: E402, F401

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.db.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402

LOG_CONTENT = (
    b"2026-06-24T08:15:03Z HOST=WS-FIN-042 PROCESS=powershell.exe\n"
    b"2026-06-24T08:15:04Z EVENT=NetworkConnect DEST=185.234.72.19:443\n"
)


def _benchmark(label: str, func, iterations: int = 3) -> dict:
    samples: list[float] = []
    result = None
    for _ in range(iterations):
        start = time.perf_counter()
        result = func()
        samples.append((time.perf_counter() - start) * 1000)
    return {
        "label": label,
        "mean_ms": round(sum(samples) / len(samples), 2),
        "min_ms": round(min(samples), 2),
        "max_ms": round(max(samples), 2),
        "result": result,
    }


def main() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = session_local()

    upload_root = Path("/tmp/oz-ai-perf-uploads")
    upload_root.mkdir(exist_ok=True)

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    import agents.evidence.service as evidence_service  # noqa: E402
    import app.services.log_service as log_service  # noqa: E402

    original_upload = log_service.get_upload_path
    original_evidence_upload = evidence_service.get_upload_path
    log_service.get_upload_path = lambda: upload_root
    evidence_service.get_upload_path = lambda: upload_root

    client = TestClient(app)

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

    metrics: list[dict] = []

    metrics.append(
        _benchmark(
            "Dashboard load", lambda: client.get("/api/v1/dashboard/stats").status_code
        )
    )

    create = client.post(
        "/api/v1/incidents",
        json={
            "title": "Performance Benchmark Incident",
            "description": "Timing validation",
            "severity": "High",
            "source": "Benchmark",
        },
    )
    incident_id = create.json()["data"]["id"]

    metrics.append(
        _benchmark(
            "Incident details load",
            lambda: client.get(f"/api/v1/incidents/{incident_id}").status_code,
        )
    )

    client.post(
        "/api/v1/logs/upload",
        data={"incident_id": incident_id},
        files={"file": ("perf.log", BytesIO(LOG_CONTENT), "text/plain")},
    )

    investigation = _benchmark(
        "Full investigation execution",
        lambda: client.post(
            "/api/v1/investigations/run",
            json={"incident_id": incident_id},
        ),
    )
    metrics.append(investigation)
    run_id = investigation["result"].json()["data"]["execution_id"]

    run_payload = investigation["result"].json()["data"]
    for stage in run_payload.get("stages", []):
        metrics.append(
            {
                "label": f"Agent: {stage['agent']}",
                "mean_ms": stage["duration_ms"],
                "min_ms": stage["duration_ms"],
                "max_ms": stage["duration_ms"],
                "result": stage.get("success"),
            }
        )

    metrics.append(
        _benchmark(
            "Replay generation",
            lambda: client.get(f"/api/v1/investigations/{run_id}/replay").status_code,
        )
    )

    metrics.append(
        _benchmark(
            "Timeline generation (API)",
            lambda: client.get(f"/api/v1/incidents/{incident_id}/timeline").status_code,
        )
    )

    metrics.append(
        _benchmark(
            "Evaluation dashboard load",
            lambda: client.get("/api/v1/evaluation").status_code,
        )
    )

    app.dependency_overrides.clear()
    log_service.get_upload_path = original_upload
    evidence_service.get_upload_path = original_evidence_upload
    db.close()

    report_path = REPO_ROOT / "docs" / "SPRINT3_PERFORMANCE_REPORT.md"
    lines = [
        "# Sprint 3 Performance Report",
        "",
        f"**Generated:** {datetime.now(UTC).isoformat()}",
        "",
        "| Operation | Mean (ms) | Min (ms) | Max (ms) |",
        "|-----------|-----------|----------|----------|",
    ]
    for item in metrics:
        lines.append(
            f"| {item['label']} | {item['mean_ms']} | {item['min_ms']} | {item['max_ms']} |"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Benchmarks run in-process via FastAPI TestClient (no network overhead).",
            "- Investigation timing includes full Coordinator workflow with offline fallbacks.",
            "- Production timings vary with hardware, Gemini API latency, and dataset size.",
            "",
        ]
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Performance report written to {report_path}")
    for item in metrics[:8]:
        print(f"  {item['label']}: {item['mean_ms']} ms (mean)")


if __name__ == "__main__":
    main()
