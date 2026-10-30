#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ -n "${PYTHON_BIN:-}" ]; then
  exec "$PYTHON_BIN" scripts/voice.py
elif [ -x .venv/bin/python ]; then
  exec .venv/bin/python scripts/voice.py
elif command -v python3 >/dev/null 2>&1; then
  exec python3 scripts/voice.py
else
  echo "Python 3 diperlukan: brew install python"
  exit 1
fi
