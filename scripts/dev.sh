#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Oz AI dev servers"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both."
echo ""

chmod +x "$ROOT/scripts/dev-backend.sh" "$ROOT/scripts/dev-frontend.sh"

trap 'kill 0' EXIT INT TERM

"$ROOT/scripts/dev-backend.sh" &
"$ROOT/scripts/dev-frontend.sh" &

wait
