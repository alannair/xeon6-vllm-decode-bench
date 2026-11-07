#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
if [[ ! -x .venv/bin/python ]]; then
  if [[ "${1:-}" != "plan" && "${1:-}" != "status" && "${1:-}" != "stop" ]]; then
    echo 'Run ./setup.sh first.' >&2
    exit 1
  fi
  exec python3 -m bench.control "$@"
fi
exec .venv/bin/python -m bench.control "$@"
