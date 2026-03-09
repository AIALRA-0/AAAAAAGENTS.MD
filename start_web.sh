#!/usr/bin/env bash
set -euo pipefail

# Purpose:
#   Cross-platform launcher entry for Linux/WSL.
# Usage:
#   ./start_web.sh [start_web.py args...]

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="python3"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python not found" >&2
  exit 1
fi

exec "$PYTHON_BIN" ./start_web.py "$@"
