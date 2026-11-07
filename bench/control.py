"""User-facing start/stop/resume/status/plan command line."""
from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from .common import LOGS, ROOT, STATE, atomic_json, read_json, timestamp_id, utc_now
from .plan import load_config, make_plan


def running_pid():
    item = read_json(STATE / "controller.json")
    if not item:
        return None
    pid = item.get("pid")
    if not pid:
        return None
    try:
        raw = Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\x00", b" ")
    except OSError:
        return None
    if b"bench.runner" not in raw:
        return None
    return int(pid)


def select_list(text):
    return [x.strip() for x in text.split(",") if x.strip()] if text else None


def show_plan(plan):
    print(f"Plan {plan['plan_id']}: {len(plan['runs'])} runs, NUMA node {plan['node']['node']}, "
          f"socket {plan['node']['socket']}, {len(plan['node']['physical_cpus'])} physical cores")
    print("models:", ", ".join(plan["models"]))
    for item in plan["runs"]:
        print(f"  {item['model']}  {item['config_id']}  [{item['sweep']}]")


def start_controller(plan, *, foreground=False):
    if running_pid():
        raise RuntimeError(f"Bench controller already running (PID={running_pid()}); stop before starting")
    (STATE / "stop.flag").unlink(missing_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    log = LOGS / ("controller-" + timestamp_id() + ".log")
    cmd = [str(ROOT / ".venv/bin/python"), "-m", "bench.runner"]
    if foreground:
        print("Foreground controller; Ctrl-C stops after cleanup.")
        proc = subprocess.Popen(cmd, cwd=ROOT)
        atomic_json(STATE / "controller.json", {"pid": proc.pid, "started": utc_now(),
                                                      "plan_id": plan["plan_id"], "log": "console"})
        try:
            return proc.wait()
        except KeyboardInterrupt:
            stop()
            return 130
        finally:
            data = read_json(STATE / "controller.json")
            if data and data.get("pid") == proc.pid:
                (STATE / "controller.json").unlink(missing_ok=True)
    with log.open("w", buffering=1) as f:
        proc = subprocess.Popen(cmd, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT,
                                start_new_session=True)
    atomic_json(STATE / "controller.json", {"pid": proc.pid, "started": utc_now(),
                                                  "plan_id": plan["plan_id"], "log": str(log)})
    time.sleep(0.2)
    if proc.poll() is not None:
        raise RuntimeError(f"Controller exited immediately with {proc.returncode}; inspect {log}")
    print(f"Controller PID: {proc.pid}; log: {log}")
    print("Follow: tail -f", log)
    print("Stop:   ./experiment.sh stop")
    print("Resume: ./experiment.sh resume")
    return 0


def stop():
    STATE.mkdir(parents=True, exist_ok=True)
    (STATE / "stop.flag").write_text(utc_now() + "\n")
    pid = running_pid()
    if pid:
        print("Stopping controller PID", pid)
        os.kill(pid, signal.SIGTERM)
        for _ in range(70):
            if not running_pid():
                break
            time.sleep(.2)
        if running_pid():
            print("Controller still alive; forcing cleanup of owned bench container")
    active = read_json(STATE / "active_run.json")
    if active:
        name = active.get("container", "")
        if name.startswith("xeon6-bench-"):
            try:
                subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=12, check=False)
            except (OSError, subprocess.TimeoutExpired) as exc:
                print(f"WARNING: Docker cleanup failed for {name}: {exc}")
    if pid and running_pid():
        os.kill(pid, signal.SIGKILL)
    (STATE / "controller.json").unlink(missing_ok=True)
    print("Stopped. Use ./experiment.sh resume to retry unfinished runs.")


def status():
    plan = read_json(STATE / "plan.json")
    progress = read_json(STATE / "progress.json", {"runs": {}})
    pid = running_pid()
    print("Controller:", f"running (PID {pid})" if pid else "not running")
    active = read_json(STATE / "active_run.json")
    if active and pid:
        print("Current:", active.get("model"), active.get("output"))
    if plan:
        counts = Counter(v.get("status", "unknown") for v in progress.get("runs", {}).values())
        total = len(plan["runs"])
        print(f"Plan {plan['plan_id']}, completed {counts['done']}/{total}; statuses={dict(counts)}")
        print(f"Remaining/not-successful: {total - counts['done']}")
    else:
        print("No plan yet: ./experiment.sh start")
    info = read_json(STATE / "controller.json")
    if info:
        print("Controller log:", info.get("log"))
    return 0


def main():
    parser = argparse.ArgumentParser(prog="./experiment.sh",
                    description="NUMA-local vLLM CPU streaming decode benchmark")
    sub = parser.add_subparsers(dest="action", required=True)
    for action in ("start", "plan"):
        p = sub.add_parser(action, help="Create plan and run it" if action == "start" else "Preview plan without launching")
        p.add_argument("--config", type=Path, default=ROOT / "configs/default.json")
        p.add_argument("--models", help="Comma-separated model substrings or glob patterns")
        p.add_argument("--sweeps", help="Comma-separated: baseline,concurrency,cores,output_tokens")
        p.add_argument("--numa-node", default=None, help="NUMA node ID (default auto)")
        p.add_argument("--max-runs", type=int, help="Limit total runs, useful for smoke tests")
        if action == "start":
            p.add_argument("--foreground", action="store_true")
    sub.add_parser("resume", help="Resume saved plan; successful runs are skipped").add_argument("--foreground", action="store_true")
    sub.add_parser("stop", help="Stop controller and its owned vLLM container")
    sub.add_parser("status", help="Show active run and progress summary")
    sub.add_parser("report", help="Aggregate per-attempt summary CSV")
    args = parser.parse_args()
    if args.action == "stop":
        return stop()
    if args.action == "status":
        return status()
    if args.action == "report":
        return subprocess.call([sys.executable, str(ROOT / "scripts/summarize.py")], cwd=ROOT)
    if args.action in ("start", "plan"):
        cfg = load_config(args.config)
        if args.max_runs is not None and args.max_runs < 1:
            parser.error("--max-runs must be >=1")
        plan = make_plan(cfg, select_list(args.models), select_list(args.sweeps),
                         args.max_runs, args.numa_node)
        if args.action == "plan":
            return show_plan(plan)
        if running_pid():
            raise RuntimeError("Already running; ./experiment.sh stop first")
        setup = read_json(STATE / "setup.json")
        if not setup or not (ROOT / ".venv/bin/python").exists():
            raise RuntimeError("Setup not complete: run ./setup.sh")
        if cfg["image"] != setup["image"]:
            raise RuntimeError("Configured image differs from setup image; rerun ./setup.sh with new config")
        STATE.mkdir(parents=True, exist_ok=True)
        atomic_json(STATE / "plan.json", plan)
        atomic_json(STATE / "progress.json", {"plan_id": plan["plan_id"], "runs": {}})
        print(f"Starting new plan {plan['plan_id']} ({len(plan['runs'])} runs)")
        return start_controller(plan, foreground=args.foreground)
    if args.action == "resume":
        plan = read_json(STATE / "plan.json")
        if not plan:
            raise RuntimeError("No saved plan found; run ./experiment.sh start")
        if not read_json(STATE / "setup.json"):
            raise RuntimeError("Setup is missing; run ./setup.sh")
        return start_controller(plan, foreground=args.foreground)
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main() or 0)
    except Exception as exc:
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(1)
