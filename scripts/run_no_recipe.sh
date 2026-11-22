#!/usr/bin/env bash
# Run the models that have no Xeon 6 recipe, in the saved random queue order
# (configs/no_recipe.json, seed in the file). Rewrites NO_RECIPE_REPORT.md and
# status.md while the controller is up and after each pass.
set -Eeuo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
PY="${PWD}/.venv/bin/python"
LOG="${PWD}/logs/no-recipe-driver.log"
mkdir -p "$(dirname "$LOG")"

refresh() {
  "$PY" scripts/update_no_recipe_report.py --remember >>"$LOG" 2>&1 || true
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

echo "[$(date -u +%FT%TZ)] no-recipe driver pid $$" | tee -a "$LOG"
echo "[$(date -u +%FT%TZ)] START no-recipe" | tee -a "$LOG"
./experiment.sh start --config configs/no_recipe.json --sweeps baseline,concurrency,cores | tee -a "$LOG"
wait_controller

prev=""
for attempt in 1 2 3; do
  left="$(pending)"
  echo "[$(date -u +%FT%TZ)] no-recipe unfinished after pass: ${left}" | tee -a "$LOG"
  if [[ "$left" == "0" ]]; then
    break
  fi
  if [[ "$left" == "$prev" ]]; then
    echo "[$(date -u +%FT%TZ)] no progress since the last pass; moving on with ${left} unfinished" | tee -a "$LOG"
    break
  fi
  prev="$left"
  echo "[$(date -u +%FT%TZ)] RESUME no-recipe (${attempt})" | tee -a "$LOG"
  ./experiment.sh resume | tee -a "$LOG"
  wait_controller
done
refresh
echo "[$(date -u +%FT%TZ)] no-recipe driver finished; $(pending) unfinished" | tee -a "$LOG"
