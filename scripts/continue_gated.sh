#!/usr/bin/env bash
# Run the recipe models that were missed or gated, in parameter-size order:
# RedHatAI 8B W8A8 (base), gated meta-llama 1B/3B/8B, then Qwen3-14B-FP8.
# Models above 33B parameters are out of scope.
# Refreshes REPORT_PINNED.md while the controller is up.
set -Eeuo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
PY="${PWD}/.venv/bin/python"
LOG="${PWD}/logs/continuation-driver.log"
TOKEN_FILE="${HOME}/.config/xeon6-bench/hf_token"
mkdir -p "$(dirname "$LOG")"

# Token stays in a 600-permission file outside the repo. Only this shell gets it.
if [[ -r "$TOKEN_FILE" ]]; then
  export HF_TOKEN="$(cat "$TOKEN_FILE")"
else
  echo "missing ${TOKEN_FILE}; gated models will 401" | tee -a "$LOG" >&2
fi

refresh() {
  "$PY" scripts/update_live_report.py --remember-plans --output REPORT_PINNED.md >>"$LOG" 2>&1 || true
}

controller_running() {
  "$PY" -c 'from bench.control import running_pid; import sys; sys.exit(0 if running_pid() else 1)'
}

wait_controller() {
  while controller_running; do
    refresh
    sleep 60
  done
  refresh
}

pending() {
  "$PY" - <<'PY'
import json
from pathlib import Path
plan = json.loads(Path("state/plan.json").read_text())
prog = json.loads(Path("state/progress.json").read_text())
terminal = {"done", "skipped_cache_limit"}
left = 0
for run in plan["runs"]:
    key = run["model"] + "|" + run["config_id"]
    if prog.get("runs", {}).get(key, {}).get("status") not in terminal:
        left += 1
print(left)
PY
}

run_phase() {
  local label="$1"
  shift
  echo "[$(date -u +%FT%TZ)] START ${label}" | tee -a "$LOG"
  ./experiment.sh start "$@" | tee -a "$LOG"
  wait_controller
  local attempt left
  for attempt in 1 2 3 4 5; do
    left="$(pending)"
    echo "[$(date -u +%FT%TZ)] ${label} unfinished after pass: ${left}" | tee -a "$LOG"
    if [[ "$left" == "0" ]]; then
      return 0
    fi
    echo "[$(date -u +%FT%TZ)] RESUME ${label} (${attempt})" | tee -a "$LOG"
    ./experiment.sh resume | tee -a "$LOG"
    wait_controller
  done
  echo "[$(date -u +%FT%TZ)] ${label} still has $(pending) unfinished runs; moving on" | tee -a "$LOG"
}

echo "[$(date -u +%FT%TZ)] gated/fp8/70b driver pid $$" | tee -a "$LOG"
run_phase "gated-fp8-70b" \
  --config configs/continuation.json \
  --models 'RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8,meta-llama/Llama-3.2-1B,meta-llama/Llama-3.2-3B-Instruct,meta-llama/Llama-3.1-8B,Qwen/Qwen3-14B-FP8' \
  --sweeps baseline,concurrency,cores
refresh
echo "[$(date -u +%FT%TZ)] gated/fp8/70b driver finished" | tee -a "$LOG"
