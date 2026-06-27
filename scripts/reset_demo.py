#!/usr/bin/env python3
"""One-click Oz AI demo reset.

Wipes the local SQLite database and uploaded logs, seeds 10 incidents with
25 log files, and runs the full investigation workflow for showcase incidents
so every demo tab (MITRE, threat intel, risk, response, report, guardian,
timeline, evaluation) has data without manual steps.

Usage (from repository root):

    python scripts/reset_demo.py

Environment:

    Uses the same DATABASE_URL and UPLOAD_DIR as the backend (.env supported).
    Works offline — agents use deterministic fallbacks when GOOGLE_API_KEY is unset.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

os.chdir(BACKEND_ROOT)

from scripts.demo_catalog import DEMO_INCIDENTS, EXPECTED_LOG_COUNT  # noqa: E402
from scripts.seed_demo_data import reset_and_seed_demo  # noqa: E402

from app.core.config import get_database_path  # noqa: E402


def main() -> None:
    print("Oz AI — resetting demo environment...")
    print(f"  Repository root: {REPO_ROOT}")
    stats = reset_and_seed_demo(run_investigations=True)

    print("\nDemo reset complete.")
    print(f"  Database path:           {get_database_path()}")
    print(f"  Incidents seeded:        {len(DEMO_INCIDENTS)}")
    print(f"  Incidents created:       {stats.incidents}")
    print(f"  Investigations created:  {stats.investigations}")
    print(f"  Investigation runs:      {stats.investigation_runs}")
    print(f"  Evidence records:        {stats.evidence}")
    print(
        f"  Uploaded logs:           {stats.log_files} (expected {EXPECTED_LOG_COUNT})"
    )
    print(f"  Audit records:           {stats.audit_logs}")
    print("\nStart the application:")
    print("  ./scripts/dev.sh")
    print("  or: docker compose up --build")
    print("\nOpen http://localhost:5173 and explore the dashboard and incidents.")


if __name__ == "__main__":
    main()
