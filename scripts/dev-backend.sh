#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/backend"

if [[ ! -x .venv/bin/uvicorn ]]; then
  echo "Backend venv not found. Create it first:"
  echo "  cd backend && uv venv && uv pip install -e '.[dev]'"
  exit 1
fi

uv pip install -e . -q 2>/dev/null || true
echo "Starting backend on http://localhost:8000"
exec .venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
