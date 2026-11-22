#!/usr/bin/env bash
# Run models the pinned plan never finished, then other Xeon 6 recipe models.
# Refreshes REPORT_PINNED.md while the controller is up.
set -Eeuo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
PY="${PWD}/.venv/bin/python"
LOG="${PWD}/logs/continuation-driver.log"
mkdir -p "$(dirname "$LOG")"

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
  local attempt
  for attempt in 1 2 3 4 5; do
    local left
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

finish_saved_plan() {
  local label="$1"
  local attempt left
  for attempt in 1 2 3 4 5; do
    left="$(pending)"
    echo "[$(date -u +%FT%TZ)] ${label} unfinished: ${left}" | tee -a "$LOG"
    if [[ "$left" == "0" ]]; then
      return 0
    fi
    if controller_running; then
      wait_controller
      continue
    fi
    echo "[$(date -u +%FT%TZ)] RESUME ${label} (${attempt})" | tee -a "$LOG"
    ./experiment.sh resume | tee -a "$LOG"
    wait_controller
  done
  echo "[$(date -u +%FT%TZ)] ${label} still has $(pending) unfinished runs; moving on" | tee -a "$LOG"
}

echo "[$(date -u +%FT%TZ)] continuation driver pid $$" | tee -a "$LOG"
if controller_running; then
  echo "[$(date -u +%FT%TZ)] controller already running; waiting for the current plan" | tee -a "$LOG"
fi
finish_saved_plan "queued-not-run"
run_phase "other-cpu-recipes" \
  --config configs/continuation.json \
  --models 'AMead10/,hugging-quants/,zai-org/glm-4-9b-hf,microsoft/Phi-4-reasoning,Qwen/Qwen3-14B,openai/gpt-oss-20b,Qwen/Qwen3-30B-A3B,QwQ-32B' \
  --sweeps baseline,concurrency,cores
refresh
echo "[$(date -u +%FT%TZ)] continuation driver finished" | tee -a "$LOG"
