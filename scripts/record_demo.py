#!/usr/bin/env python3
"""Record the Oz AI competition demo — single entry point.

Must run with the backend virtual environment Python:

    backend/.venv/bin/python scripts/record_demo.py

The script re-execs automatically when invoked with a different interpreter.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_PYTHON = REPO_ROOT / "backend" / ".venv" / "bin" / "python"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _ensure_backend_python() -> None:
    if not BACKEND_PYTHON.is_file():
        print(
            f"ERROR: Backend virtual environment not found at {BACKEND_PYTHON}\n"
            "Create it with: cd backend && uv venv && uv pip install -e '.[dev]'",
            file=sys.stderr,
        )
        raise SystemExit(1)

    current = Path(sys.executable).resolve()
    expected = BACKEND_PYTHON.resolve()
    if current != expected:
        print(f"Re-launching with backend interpreter: {expected}", file=sys.stderr)
        os.execv(str(expected), [str(expected), str(Path(__file__).resolve()), *sys.argv[1:]])


def main() -> int:
    _ensure_backend_python()
    from demo.recorder import run_recording

    return run_recording()


if __name__ == "__main__":
    raise SystemExit(main())
