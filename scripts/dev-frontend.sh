#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -d "$HOME/.local/node/bin" ]]; then
  export PATH="$HOME/.local/node/bin:$PATH"
fi

cd "$ROOT/frontend"

if [[ ! -d node_modules ]]; then
  echo "Installing frontend dependencies..."
  npm install
fi

echo "Starting frontend on http://localhost:5173"
exec npm run dev -- --host 0.0.0.0 --port 5173
