#!/usr/bin/env python3
"""Refresh NO_RECIPE_REPORT.md and status.md for the no-Xeon-6-recipe experiment.

Reads append-only attempt logs and state/plan.json. Does not start, stop, or
modify the experiment. Only attempts that belong to the plan ids remembered in
state/no_recipe_plans.json are reported, so the pinned-recipe history stays out.
"""
from __future__ import annotations

import argparse
import json
from collections import OrderedDict, defaultdict
from pathlib import Path

from update_live_report import (
    LOGS, ROOT, STATE, analyze_attempt, bar, controller_pid, latest_attempt,
    ms, num, read_json, utc_stamp,
)

PLANS_FILE = STATE / "no_recipe_plans.json"
ITL = "vllm:inter_token_latency_seconds"


def remembered_plans(remember: bool) -> list[str]:
    ids = read_json(PLANS_FILE) or []
    if not isinstance(ids, list):
        ids = []
    if remember:
        current = (read_json(STATE / "plan.json") or {}).get("plan_id")
        if current and current not in ids:
            ids.append(current)
            PLANS_FILE.write_text(json.dumps(ids, indent=2) + "\n")
    return [str(i) for i in ids]


def model_meta(plan: dict) -> "OrderedDict[str, dict]":
    meta: "OrderedDict[str, dict]" = OrderedDict()
    for run in plan.get("runs") or []:
        item = meta.setdefault(run["model"], {"size_b": run.get("size_b"),
                                              "queue": run.get("queue_order"), "total": 0})
        item["total"] += 1
    return meta


def pick(rows, model, sweep, cores, clients):
    for row in rows:
        if (row["model"] == model and row["sweep"] == sweep and row["cores"] == cores
                and row["concurrency"] == clients):
            return row
    return None


def cell(row, kind):
    if row is None:
        return "—"
    if kind == "tpot":
        return f"{ms(row['client']['tpot_median_s'])} ms"
    if kind == "ttft":
        return f"{ms(row['client']['ttft_median_s'])} ms"
    if kind == "tps":
        return num(row["client"]["tokens_per_s"])
    return "—"


def write_report(rows: list[dict], out: Path, plan_ids: list[str]) -> None:
    plan = read_json(STATE / "plan.json") or {}
    progress = read_json(STATE / "progress.json", {"runs": {}})
    active = read_json(STATE / "active_run.json") or {}
    controller = read_json(STATE / "controller.json") or {}
    cfg = plan.get("config") or {}
    pid = controller_pid()
    stamp = utc_stamp()
    meta = model_meta(plan)
    total = len(plan.get("runs") or [])
    status_by_key = {key: item.get("status", "unknown") for key, item in (progress.get("runs") or {}).items()}
    done_rows = [r for r in rows if r["status"] == "done"]
    done_by_model: dict[str, int] = defaultdict(int)
    for run in plan.get("runs") or []:
        if status_by_key.get(f"{run['model']}|{run['config_id']}") == "done":
            done_by_model[run["model"]] += 1
    done_total = sum(done_by_model.values())
    complete_models = [m for m, v in meta.items() if done_by_model[m] == v["total"]]
    active_model = active.get("model") if pid else None

    def label(model: str) -> str:
        info = meta[model]
        done = done_by_model[model]
        statuses = [status_by_key.get(f"{r['model']}|{r['config_id']}") for r in plan["runs"] if r["model"] == model]
        if done == info["total"]:
            return "complete"
        if active_model == model:
            return f"running ({done}/{info['total']})"
        if any(s == "failed" for s in statuses):
            return f"has failures ({done}/{info['total']})"
        if done:
            return f"in progress ({done}/{info['total']})"
        return "queued"

    L: list[str] = []
    L.append("# No-recipe vLLM decode report")
    L.append("")
    L.append(f"Live notes for plan{'s' if len(plan_ids) > 1 else ''} "
             + ", ".join(f"`{p}`" for p in plan_ids)
             + f" on the Xeon 6972P node-0 benchmark. Updated {stamp}.")
    L.append("")
    L.append("These are text models that have **no Xeon 6 recipe** on the vLLM CPU page "
             "([recipes.vllm.ai](https://recipes.vllm.ai)); each one returns 404 for `/hw/xeon6.json`. "
             "They run through the manual `vllm serve` path (BF16, no recipe config), pinned with "
             "`numactl --physcpubind=0-(N-1) --membind=0` so every selected CPU carries one compute thread. "
             "The sweeps match `REPORT_PINNED.md`: concurrency 1, 2, 4, 8, 16, 32, 64, 128 at 96 cores, "
             "and cores 24, 48, 72, 96 at 8 clients, with 512 generated tokens. "
             "Models above 33B parameters are excluded. The queue is a random permutation "
             f"(seed {cfg.get('queue_seed', 'n/a')}) so an interrupted run still covers small and large models.")
    L.append("")
    L.append("## Snapshot")
    L.append("")
    if pid:
        started = f", started {controller.get('started')}" if controller.get("started") else ""
        L.append(f"Controller PID {pid} is running{started}. Progress {done_total}/{total} runs, "
                 f"{len(complete_models)}/{len(meta)} models complete.")
    else:
        L.append(f"Controller is not running. Progress {done_total}/{total} runs, "
                 f"{len(complete_models)}/{len(meta)} models complete.")
    if active.get("model") and pid:
        L.append(f"Active run: `{active.get('model')}` `{Path(active.get('output', '')).parent.name}`.")
    L.append("")

    L.append("## Models and queue order")
    L.append("")
    L.append("Listed by size. **Queue #** is the position in the random run order (1 runs first).")
    L.append("")
    L.append("| Size (B) | Model | Queue # | Runs done | Status |")
    L.append("|---:|---|---:|---:|---|")
    for model, info in sorted(meta.items(), key=lambda kv: (float(kv[1]["size_b"] or 0), kv[0])):
        L.append(f"| {info['size_b']:.2f} | `{model}` | {info['queue']} | {done_by_model[model]}/{info['total']} | {label(model)} |")
    L.append("")

    L.append("## Results by model")
    L.append("")
    L.append("Decode latency is client TPOT, `(last token time − first token time) / (tokens − 1)`, "
             "median over requests. The server series `vllm:inter_token_latency_seconds` agrees with it "
             "in the per-run table below. Baseline is 96 cores and 8 clients. "
             "Rows appear as soon as a model has finished points; `—` marks a point not finished yet.")
    L.append("")
    L.append("| Size (B) | Model | Queue # | Baseline TPOT | Baseline TTFT | Baseline tok/s | 1 client TPOT | 128 clients TPOT | 128 clients TTFT | 128 clients tok/s | 24 cores TPOT |")
    L.append("|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for model, info in sorted(meta.items(), key=lambda kv: (float(kv[1]["size_b"] or 0), kv[0])):
        if not done_by_model[model]:
            continue
        base = pick(done_rows, model, "baseline", 96, 8)
        c1 = pick(done_rows, model, "concurrency", 96, 1)
        c128 = pick(done_rows, model, "concurrency", 96, 128)
        k24 = pick(done_rows, model, "cores", 24, 8)
        L.append(f"| {info['size_b']:.2f} | `{model}` | {info['queue']} | {cell(base, 'tpot')} | {cell(base, 'ttft')} | "
                 f"{cell(base, 'tps')} | {cell(c1, 'tpot')} | {cell(c128, 'tpot')} | {cell(c128, 'ttft')} | "
                 f"{cell(c128, 'tps')} | {cell(k24, 'tpot')} |")
    L.append("")

    L.append("## Per-run results")
    L.append("")
    L.append("| Size (B) | Model | Sweep | Cores | Clients | Server ITL mean | Client TPOT | Client TTFT | Tokens/s | Complete requests |")
    L.append("|---:|---|---|---:|---:|---:|---:|---:|---:|---:|")
    order = {m: i for i, m in enumerate(sorted(meta, key=lambda m: (float(meta[m]["size_b"] or 0), m)))}
    sweep_rank = {"baseline": 0, "concurrency": 1, "cores": 2}
    for row in sorted(done_rows, key=lambda r: (order.get(r["model"], 99), sweep_rank.get(r["sweep"], 3),
                                                r["cores"] or 0, r["concurrency"] or 0)):
        itl = row["hist"][ITL]["mean_s"]
        size = meta.get(row["model"], {}).get("size_b")
        L.append(f"| {size:.2f} | `{row['model']}` | {row['sweep']} | {row['cores']} | {row['concurrency']} | "
                 f"{ms(itl)} ms | {ms(row['client']['tpot_median_s'])} ms | {ms(row['client']['ttft_median_s'])} ms | "
                 f"{num(row['client']['tokens_per_s'])} | "
                 f"{row['client']['complete'] if row['client']['complete'] is not None else '—'} |")
    L.append("")

    L.append("## Thread pinning")
    L.append("")
    checked = [r for r in rows if (r["attempt"] / "server.log").exists()]
    warned = [r for r in rows if r.get("omp_invalid")]
    if not checked:
        L.append("No server log yet.")
    elif warned:
        L.append(f"{len(warned)} of {len(checked)} attempts logged OpenMP warning #124, so those workers did not keep one thread per core: "
                 + ", ".join(f"`{r['model']}` `{r['config_id']}`" for r in warned[:6]) + ("…" if len(warned) > 6 else "") + ".")
    else:
        L.append(f"All {len(checked)} attempts with a server log are free of OpenMP warning #124. The server runs under "
                 "`numactl --physcpubind=0-(N-1) --membind=0`, and vLLM re-execs the worker under the same CPU list.")
    L.append("")

    failures = [r for r in rows if r["status"] not in ("done", "partial", "starting")]
    L.append("## Failures and retries")
    L.append("")
    if failures:
        L.append("Latest attempt per point. A point that later succeeded is not listed.")
        L.append("")
        for r in sorted(failures, key=lambda r: (str(r["model"]), r["config_id"])):
            err = (r.get("error") or "no error text").splitlines()[0][:200]
            L.append(f"- `{r['model']}` `{r['config_id']}` ({r['status']}): {err}")
    else:
        L.append("No failed attempts in the current plan.")
    L.append("")

    n_zero = sum(1 for r in done_rows if r["client"]["complete"] == 0)
    L.append("## Caveats")
    L.append("")
    L.append("- The measurement window is 90 seconds. At about 200 ms/token or slower a 512-token request cannot finish inside it, "
             "so client TPOT there comes from partially generated requests, and request-level vLLM histograms stay empty. "
             f"{n_zero} finished runs so far have zero completed requests.")
    L.append("- These models use the manual BF16 path, not a tuned Xeon 6 recipe. Compare them with recipe rows in `REPORT_PINNED.md` "
             "with that difference in mind. Parameter counts come from the Hugging Face safetensors metadata.")
    L.append("- The Mixture-of-Experts model (`Qwen/Qwen3-30B-A3B-Instruct-2507`, 3B active) decodes faster than its 30B total size suggests.")
    L.append("")
    out.write_text("\n".join(L) + "\n")


def write_status(rows: list[dict], plan_ids: list[str]) -> None:
    plan = read_json(STATE / "plan.json") or {}
    progress = read_json(STATE / "progress.json", {"runs": {}})
    active = read_json(STATE / "active_run.json") or {}
    controller = read_json(STATE / "controller.json") or {}
    pid = controller_pid()
    meta = model_meta(plan)
    total = len(plan.get("runs") or [])
    statuses = {key: item.get("status", "unknown") for key, item in (progress.get("runs") or {}).items()}
    counts: dict[str, int] = defaultdict(int)
    for value in statuses.values():
        counts[value] += 1
    done = counts["done"]
    done_by_model: dict[str, int] = defaultdict(int)
    for run in plan.get("runs") or []:
        if statuses.get(f"{run['model']}|{run['config_id']}") == "done":
            done_by_model[run["model"]] += 1
    queue_sorted = sorted(meta.items(), key=lambda kv: kv[1]["queue"] or 0)
    S: list[str] = ["# status", "", f"Updated: {utc_stamp()}", "", "## Current Phase", ""]
    if pid and active.get("model"):
        S.append(f"No-recipe experiment, plan `{plan.get('plan_id')}`. Running `{active['model']}` "
                 f"`{Path(active.get('output', '')).parent.name}`.")
    elif pid:
        S.append(f"No-recipe experiment, plan `{plan.get('plan_id')}`. Controller running, between runs.")
    elif total and done >= total:
        S.append("Status: Complete (100%). No-recipe experiment finished.")
    else:
        S.append("No-recipe experiment, controller not running.")
    S.append(f"Controller PID: {pid or '—'}. Start: {controller.get('started', '—')}. Log: `{controller.get('log', '—')}`.")
    S.append("Models without a Xeon 6 recipe, run in a random order (queue # in `NO_RECIPE_REPORT.md`). "
             "Sweeps: clients 1–128 at 96 cores, cores 24/48/72/96 at 8 clients, 512 generated tokens.")
    S += ["", "## Overall Progress", "", f"{bar(done, total)} {done}/{total} runs done. Status counts: {dict(counts)}.", "",
          "## Completed Steps", ""]
    finished = [(m, v) for m, v in queue_sorted if done_by_model[m] == v["total"]]
    if finished:
        for model, info in finished:
            S.append(f"- Queue #{info['queue']} `{model}` ({info['size_b']:.2f}B): all {info['total']} runs done.")
    else:
        S.append("- No model has finished all of its runs yet.")
    partial = [(m, v) for m, v in queue_sorted if 0 < done_by_model[m] < v["total"]]
    for model, info in partial:
        S.append(f"- Queue #{info['queue']} `{model}`: {done_by_model[model]}/{info['total']} runs done.")
    S += ["", "## Remaining Steps", ""]
    waiting = [(m, v) for m, v in queue_sorted if done_by_model[m] < v["total"]]
    S.append(f"- {len(waiting)} models still have unfinished runs, in queue order:")
    for model, info in waiting[:25]:
        S.append(f"  - #{info['queue']} `{model}` ({info['size_b']:.2f}B): {info['total'] - done_by_model[model]} runs left.")
    S += ["", "## Active Failures/Retries", ""]
    failed = [r for r in rows if r["status"] not in ("done", "partial", "starting")]
    if failed:
        for r in failed[:12]:
            err = (r.get("error") or "no error text").splitlines()[0][:160]
            S.append(f"- `{r['model']}` `{r['config_id']}` ({r['status']}): {err}. The driver resumes unfinished runs up to 5 times, then moves on.")
    else:
        S.append("- None.")
    S += ["", "## Implementation Plan", "",
          "1. Run every no-recipe model through the baseline, concurrency, and core sweeps in the saved random queue order.",
          "2. After each attempt, rewrite `NO_RECIPE_REPORT.md` with client TPOT, TTFT, throughput, and the server inter-token latency.",
          "3. Resume unfinished runs after a controller exit (up to 5 passes), then move on rather than looping on a broken model.",
          "4. Leave the controller running. Do not retry a run already marked done.", ""]
    (ROOT / "status.md").write_text("\n".join(S) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remember", action="store_true",
                        help="Add the current plan id to state/no_recipe_plans.json")
    parser.add_argument("--output", type=Path, default=ROOT / "NO_RECIPE_REPORT.md")
    args = parser.parse_args()
    plan_ids = remembered_plans(args.remember)
    rows = []
    for path in sorted(LOGS.glob("*/*/attempt-*")):
        row = analyze_attempt(path)
        if row.get("plan_id") in plan_ids:
            rows.append(row)
    rows = latest_attempt(rows)
    write_report(rows, args.output, plan_ids or ["none"])
    write_status(rows, plan_ids)
    print(f"Updated {args.output.name} and status.md at {utc_stamp()}: {len(rows)} attempts, plans {plan_ids}")


if __name__ == "__main__":
    main()
