#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")"
if [ -n "${PYTHON_BIN:-}" ]; then exec "$PYTHON_BIN" scripts/voice.py
elif [ -x .venv/bin/python ]; then exec .venv/bin/python scripts/voice.py
else exec python3 scripts/voice.py; fi
