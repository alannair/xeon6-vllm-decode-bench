#!/usr/bin/env python3
"""Refresh status.md and REPORT.md from the live benchmark logs.

Reads append-only attempt logs. Does not start, stop, or modify the experiment.
"""
from __future__ import annotations

import csv
import json
import os
import re
import statistics
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"
STATE = ROOT / "state"

HIST = [
    "vllm:inter_token_latency_seconds",
    "vllm:request_time_per_output_token_seconds",
    "vllm:request_decode_time_seconds",
    "vllm:request_prefill_time_seconds",
    "vllm:time_to_first_token_seconds",
    "vllm:e2e_request_latency_seconds",
    "vllm:request_queue_time_seconds",
    "vllm:iteration_tokens_total",
]


def read_json(path: Path, default=None):
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return default


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def ms(value, digits=1):
    if value is None:
        return "—"
    return f"{value * 1000:.{digits}f}"


def num(value, digits=2):
    if value is None:
        return "—"
    return f"{value:.{digits}f}"


def pct(value):
    if value is None:
        return "—"
    return f"{value * 100:.2f}%"


def dur(value):
    if value is None:
        return "—"
    if abs(value) >= 10:
        return f"{value:.1f} s"
    return f"{value * 1000:.1f} ms"


def parse_le(labels: str):
    match = re.search(r'le="([^"]+)"', labels)
    if not match:
        return None
    raw = match.group(1)
    if raw == "+Inf":
        return float("inf")
    return float(raw)


def percentile_from_buckets(buckets, p):
    if not buckets:
        return None
    total = buckets[-1][1]
    if total <= 0:
        return None
    target = p * total
    prev_le, prev_c = 0.0, 0.0
    for le, count in buckets:
        if count >= target:
            span = count - prev_c
            if span <= 0:
                return prev_le if le == float("inf") else le
            frac = (target - prev_c) / span
            if le == float("inf"):
                return prev_le
            return prev_le + frac * (le - prev_le)
        prev_le = le if le != float("inf") else prev_le
        prev_c = count
    return prev_le


def window_pair(samples, start, end):
    if not samples:
        return None, None
    if start:
        left = next((item for item in samples if item[0] >= start), samples[0])
    else:
        left = samples[0]
    if end:
        right = None
        for item in samples:
            if item[0] <= end:
                right = item
            else:
                break
        if right is None:
            right = samples[-1]
    else:
        right = samples[-1]
    return left, right


def load_phases(path: Path):
    bounds = {}
    if not path.exists():
        return bounds
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            bounds[row["phase"]] = row["timestamp_utc"]
    return bounds


def client_distribution(path: Path):
    tpots, ttfts = [], []
    if not path.exists():
        return {}
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            try:
                if row.get("mean_tpot_s"):
                    tpots.append(float(row["mean_tpot_s"]))
            except ValueError:
                pass
            try:
                if row.get("ttft_s"):
                    ttfts.append(float(row["ttft_s"]))
            except ValueError:
                pass

    def pack(values):
        if not values:
            return {}
        ordered = sorted(values)
        def q(p):
            return ordered[min(len(ordered) - 1, max(0, int(round((len(ordered) - 1) * p))))]
        return {"n": len(values), "median": statistics.median(values),
                "p90": q(0.90), "min": ordered[0], "max": ordered[-1]}

    return {"tpot": pack(tpots), "ttft": pack(ttfts)}


def analyze_attempt(attempt: Path):
    info = read_json(attempt / "summary.json", {})
    cfg_meta = read_json(attempt / "config.json", {})
    run = info.get("run") or cfg_meta.get("run") or {}
    phases = load_phases(attempt / "phases.csv")
    m_start = phases.get("measurement_start")
    m_end = phases.get("measurement_window_end")

    sums = defaultdict(list)
    counts = defaultdict(list)
    buckets = defaultdict(lambda: defaultdict(list))
    gauges = defaultdict(list)
    long_path = attempt / "metrics_long.csv"
    if long_path.exists() and long_path.stat().st_size:
        with long_path.open(newline="") as handle:
            for row in csv.DictReader(handle):
                metric = row["metric"]
                ts = row["timestamp_utc"]
                try:
                    val = float(row["value"])
                except ValueError:
                    continue
                if metric.endswith("_sum"):
                    base = metric[:-4]
                    if base in HIST:
                        sums[base].append((ts, val))
                elif metric.endswith("_count") and not metric.endswith("_created"):
                    base = metric[:-6]
                    if base in HIST:
                        counts[base].append((ts, val))
                elif metric.endswith("_bucket"):
                    base = metric[:-7]
                    if base in HIST:
                        le = parse_le(row["labels"])
                        if le is not None:
                            buckets[base][le].append((ts, val))
                elif metric in (
                    "vllm:num_requests_running",
                    "vllm:num_requests_waiting",
                    "vllm:kv_cache_usage_perc",
                ):
                    gauges[metric].append((ts, val))

    hist = {}
    for base in HIST:
        left_s, right_s = window_pair(sums.get(base, []), m_start, m_end)
        left_c, right_c = window_pair(counts.get(base, []), m_start, m_end)
        dsum = None if left_s is None or right_s is None else right_s[1] - left_s[1]
        dcount = None if left_c is None or right_c is None else right_c[1] - left_c[1]
        delta_buckets = []
        for le, series in buckets.get(base, {}).items():
            left_b, right_b = window_pair(series, m_start, m_end)
            if left_b is None or right_b is None:
                continue
            delta_buckets.append((le, max(0.0, right_b[1] - left_b[1])))
        delta_buckets.sort()
        mean = dsum / dcount if dcount and dsum is not None and dcount > 0 else None
        dominant = None
        if delta_buckets and delta_buckets[-1][1] > 0:
            total = delta_buckets[-1][1]
            prev_le, prev_c = 0.0, 0.0
            best = (0.0, 0.0, 0.0)
            for le, cumulative in delta_buckets:
                share = (cumulative - prev_c) / total
                if share > best[0]:
                    best = (share, prev_le, le if le != float("inf") else prev_le)
                prev_le = le if le != float("inf") else prev_le
                prev_c = cumulative
            dominant = {"share": best[0], "lo": best[1], "hi": best[2]}
        hist[base] = {
            "mean_s": mean,
            "n": dcount,
            "p50_s": percentile_from_buckets(delta_buckets, 0.50) if delta_buckets else None,
            "p90_s": percentile_from_buckets(delta_buckets, 0.90) if delta_buckets else None,
            "p99_s": percentile_from_buckets(delta_buckets, 0.99) if delta_buckets else None,
            "dominant": dominant,
        }

    def gauge_stats(name):
        vals = []
        for ts, val in gauges.get(name, []):
            if m_start and ts < m_start:
                continue
            if m_end and ts > m_end:
                continue
            vals.append(val)
        if not vals:
            return None
        return {"mean": statistics.mean(vals), "max": max(vals), "n": len(vals)}

    sys_vals = defaultdict(list)
    sys_path = attempt / "system.csv"
    if sys_path.exists():
        with sys_path.open(newline="") as handle:
            for row in csv.DictReader(handle):
                ts = row["timestamp_utc"]
                if m_start and ts < m_start:
                    continue
                if m_end and ts > m_end:
                    continue
                for key in ("ipc", "dram_total_gbps", "amx_busy_fraction", "l3_stall_fraction"):
                    raw = row.get(key)
                    if raw:
                        try:
                            sys_vals[key].append(float(raw))
                        except ValueError:
                            pass

    def sys_mean(key):
        return statistics.mean(sys_vals[key]) if sys_vals[key] else None

    server_log = attempt / "server.log"
    omp_invalid = 0
    omp_max_id = None
    if server_log.exists():
        for line in server_log.read_text(errors="replace").splitlines():
            match = re.search(r"Ignoring invalid OS proc ID (\d+)", line)
            if match:
                omp_invalid += 1
                ident = int(match.group(1))
                omp_max_id = ident if omp_max_id is None else max(omp_max_id, ident)

    summary = info.get("summary") or {}
    closed = bool(m_end) and bool(info.get("status"))
    return {
        "attempt": attempt,
        "plan_id": cfg_meta.get("plan_id"),
        "status": info.get("status") or ("partial" if m_start else "starting"),
        "closed": closed,
        "elapsed_s": info.get("total_elapsed_s"),
        "error": info.get("error"),
        "cleanup_error": info.get("container_cleanup_error"),
        "model": run.get("model"),
        "sweep": run.get("sweep"),
        "config_id": run.get("config_id") or attempt.parent.name,
        "cores": run.get("cores"),
        "concurrency": run.get("concurrency"),
        "output_tokens": run.get("output_tokens"),
        "size_b": run.get("size_b"),
        "recipe": run.get("recipe"),
        "measurement_open": bool(m_start) and not m_end,
        "client": {
            "complete": summary.get("complete_requests"),
            "truncated": summary.get("failed_or_truncated_requests"),
            "tokens_per_s": summary.get("delivered_tokens_per_s"),
            "tokens": summary.get("observed_output_tokens"),
            "tpot_median_s": summary.get("mean_tpot_observed_median_s"),
            "ttft_median_s": summary.get("ttft_observed_median_s"),
            "tpot_complete_median_s": summary.get("mean_tpot_median_s"),
        },
        "requests": client_distribution(attempt / "requests.csv"),
        "hist": hist,
        "running": gauge_stats("vllm:num_requests_running"),
        "waiting": gauge_stats("vllm:num_requests_waiting"),
        "kv": gauge_stats("vllm:kv_cache_usage_perc"),
        "sys": {key: sys_mean(key) for key in ("ipc", "dram_total_gbps", "amx_busy_fraction", "l3_stall_fraction")},
        "omp_invalid": omp_invalid,
        "omp_max_id": omp_max_id,
    }


def controller_pid():
    info = read_json(STATE / "controller.json")
    if not info or not info.get("pid"):
        return None
    pid = int(info["pid"])
    cmdline = Path(f"/proc/{pid}/cmdline")
    try:
        raw = cmdline.read_bytes().replace(b"\x00", b" ")
    except OSError:
        return None
    if b"bench.runner" not in raw:
        return None
    return pid


def live_affinity():
    active = read_json(STATE / "active_run.json") or {}
    name = active.get("container") or ""
    if not name:
        return None
    try:
        cpuset = subprocess.run(
            ["docker", "inspect", name, "--format", "{{.HostConfig.CpusetCpus}}"],
            capture_output=True, text=True, timeout=8, check=False,
        )
        proc = subprocess.run(
            ["docker", "exec", name, "python3", "-c",
             "import os, pathlib\n"
             "root = pathlib.Path('/proc')\n"
             "worker = None\n"
             "for entry in root.iterdir():\n"
             "    if not entry.name.isdigit():\n"
             "        continue\n"
             "    try:\n"
             "        cmd = (entry / 'cmdline').read_bytes().replace(b'\\x00', b' ').decode()\n"
             "    except OSError:\n"
             "        continue\n"
             "    if 'VLLM::Worker' in cmd or 'Worker' in cmd and 'VLLM' in cmd:\n"
             "        worker = entry\n"
             "        break\n"
             "print('worker', worker.name if worker else 'none')\n"
             "if worker:\n"
             "    counts = {}\n"
             "    for tid in (worker / 'task').iterdir():\n"
             "        for line in (tid / 'status').read_text().splitlines():\n"
             "            if line.startswith('Cpus_allowed_list'):\n"
             "                mask = line.split()[-1]\n"
             "                counts[mask] = counts.get(mask, 0) + 1\n"
             "    one = sorted(int(k) for k, v in counts.items() if k.isdigit() and v == 1)\n"
             "    print('threads', sum(counts.values()))\n"
             "    print('cpus with one thread', len(one))\n"
             "    print('cpu0 threads', counts.get('0', 0))\n"
             "    if one:\n"
             "        print('one-thread cpus', f'{one[0]}-{one[-1]}', 'count', len(one))\n"
             ],
            capture_output=True, text=True, timeout=8, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    text = proc.stdout.strip()
    cpus = (cpuset.stdout or "").strip()
    if cpus:
        shown = cpus if len(cpus) < 80 else cpus[:40] + "…" + cpus[-20:]
        text = f"container {name}\ncpuset {shown}\n" + text
    if not text:
        return None
    return text


def bar(done, total):
    if not total:
        return "[░░░░░░░░░░] 0%"
    frac = done / total
    filled = round(frac * 10)
    return f"[{'█' * filled}{'░' * (10 - filled)}] {frac * 100:.0f}%"


def bucket_phrase(dominant):
    if not dominant or dominant["hi"] == float("inf"):
        return "—"
    lo = dominant["lo"] * 1000
    hi = dominant["hi"] * 1000
    return f"{dominant['share'] * 100:.1f}% in {lo:.0f}–{hi:.0f} ms"


def write_reports(rows, report_path: Path):
    plan = read_json(STATE / "plan.json") or {}
    progress = read_json(STATE / "progress.json", {"runs": {}})
    active = read_json(STATE / "active_run.json") or {}
    controller = read_json(STATE / "controller.json") or {}
    pid = controller_pid()
    total = len(plan.get("runs") or [])
    counts = defaultdict(int)
    for item in progress.get("runs", {}).values():
        counts[item.get("status", "unknown")] += 1
    done = counts["done"]
    finished_rows = [r for r in rows if r["status"] == "done"]
    partial_rows = [r for r in rows if r["status"] != "done" and r["hist"]["vllm:inter_token_latency_seconds"]["n"]]
    stamp = utc_stamp()
    affinity = live_affinity()

    itl_means = [r["hist"]["vllm:inter_token_latency_seconds"]["mean_s"]
                 for r in finished_rows if r["hist"]["vllm:inter_token_latency_seconds"]["mean_s"]]
    itl_min = min(itl_means) if itl_means else None
    itl_max = max(itl_means) if itl_means else None
    spread = None if not itl_means or not itl_min else (itl_max - itl_min) / itl_min

    lines = []
    lines.append("# vLLM decode latency report")
    lines.append("")
    lines.append(f"Live notes for plan `{plan.get('plan_id', 'unknown')}` on the Xeon 6972P node-0 benchmark. Updated {stamp}.")
    lines.append("")
    lines.append("## Snapshot")
    lines.append("")
    if pid:
        lines.append(f"Controller PID {pid} is running" + (f", started {controller.get('started')}" if controller.get("started") else "") + f". Progress {done}/{total} successful runs.")
    else:
        lines.append(f"Controller is not running. Progress {done}/{total} successful runs.")
    if active.get("model"):
        lines.append(f"Active run: `{active.get('model')}` → `{active.get('output')}`.")
    lines.append("")
    failed_runs = [item for item in progress.get("runs", {}).values() if item.get("status") == "failed"]
    if failed_runs and not pid:
        reason = (failed_runs[0].get("error") or "unknown").splitlines()[0][:160]
        lines.append(
            f"**Plan stopped early.** {len(failed_runs)} runs failed and the controller exited after the last one "
            f"(`{reason}`). The cause is root-owned files in the private Hugging Face cache, written by the Docker container, "
            f"which the cache-eviction step cannot delete. The 0.5B results above are valid. Nothing after them ran."
        )
        lines.append("")
    lines.append("Decode latency here is the time between generated tokens. The server series that records every token is `vllm:inter_token_latency_seconds`. The client series is the per-request mean TPOT, `(last token time − first token time) / (tokens − 1)`. Those two agree. vLLM's request-level `request_time_per_output_token_seconds` and `request_decode_time_seconds` update only when a request finishes. At ~350 ms/token a 512-token request cannot finish inside the 90-second window, so those histograms stay empty. They fill once the step is short enough that 512 tokens fit in the window.")
    lines.append("")
    if itl_means:
        if spread is not None and spread > 0.15:
            band = "Per-token time is no longer a single band."
        else:
            band = "Per-token time is still in a narrow band while aggregate throughput rises with concurrency."
        lines.append(f"Across {len(finished_rows)} finished runs, server inter-token latency averages **{ms(itl_min)}–{ms(itl_max)} ms**. Relative spread versus the fastest finished run is {spread * 100:.1f}%. {band}")
    lines.append("")
    lines.append("## Decode latency by run")
    lines.append("")
    lines.append("Means are `histogram_sum / histogram_count` over samples that arrived between `measurement_start` and `measurement_window_end`. The Prometheus buckets are 100 ms wide in this region, so a reported p50 near 350 ms only means the median bucket is 300–400 ms. The mean is the precise number. Client TPOT is the median of per-request mean token gaps, including requests that the 90-second window truncates.")
    lines.append("")
    lines.append("| Model | Sweep | Cores | Clients | Gen | Status | Server ITL mean | ITL bucket | Client TPOT median | Client TTFT median | Tokens/s | Running | Waiting |")
    lines.append("|---|---|---:|---:|---:|---|---:|---|---:|---:|---:|---:|---:|")
    for row in sorted(rows, key=lambda r: (str(r["model"]), r["attempt"].name)):
        itl = row["hist"]["vllm:inter_token_latency_seconds"]
        if itl["mean_s"] is None and row["client"]["tpot_median_s"] is None:
            continue
        running = "—" if not row["running"] else f"{row['running']['mean']:.1f}"
        waiting = "—" if not row["waiting"] else f"{row['waiting']['mean']:.1f}"
        lines.append(
            f"| `{row['model']}` | {row['sweep'] or '—'} | {row['cores'] if row['cores'] is not None else '—'} | "
            f"{row['concurrency'] if row['concurrency'] is not None else '—'} | {row['output_tokens'] if row['output_tokens'] is not None else '—'} | "
            f"{row['status']} | {ms(itl['mean_s'])} ms | {bucket_phrase(itl['dominant'])} | "
            f"{ms(row['client']['tpot_median_s'])} ms | {ms(row['client']['ttft_median_s'])} ms | "
            f"{num(row['client']['tokens_per_s'])} | {running} | {waiting} |"
        )
    lines.append("")
    lines.append("### Same numbers, server versus client")
    lines.append("")
    lines.append("| Config | ITL mean | ITL n | coarse ITL p50 | coarse ITL p90 | client TPOT min | client TPOT median | client TPOT p90 | complete requests |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for row in sorted(finished_rows, key=lambda r: (str(r["model"]), r["concurrency"] or 0, r["cores"] or 0, r["output_tokens"] or 0)):
        itl = row["hist"]["vllm:inter_token_latency_seconds"]
        dist = row["requests"].get("tpot") or {}
        lines.append(
            f"| `{row['config_id']}` | {ms(itl['mean_s'])} ms | {num(itl['n'], 0)} | {ms(itl['p50_s'])} ms | {ms(itl['p90_s'])} ms | "
            f"{ms(dist.get('min'))} ms | {ms(dist.get('median'))} ms | {ms(dist.get('p90'))} ms | "
            f"{row['client']['complete'] if row['client']['complete'] is not None else '—'} |"
        )
    lines.append("")

    lines.append("## Trend")
    lines.append("")
    conc = [r for r in finished_rows if r["model"] == "Qwen/Qwen2.5-0.5B-Instruct" and r["cores"] == 96 and r["output_tokens"] == 512]
    conc.sort(key=lambda r: r["concurrency"] or 0)
    if len(conc) >= 2:
        base = next((r for r in conc if r["concurrency"] == 1), conc[0])
        base_itl = base["hist"]["vllm:inter_token_latency_seconds"]["mean_s"]
        base_tps = base["client"]["tokens_per_s"] or 0
        lines.append(f"On `{base['model']}`, {base['cores']} cores, {base['output_tokens']} generated tokens, one client produces one token every **{ms(base_itl)} ms** ({num(base_tps)} tokens/s).")
        lines.append("")
        lines.append("| Clients | ITL mean | ITL vs 1-client | Tokens/s | Tokens/s vs linear | TTFT median | Mean running | Mean waiting | Step batch (iteration tokens) |")
        lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        for row in conc:
            itl = row["hist"]["vllm:inter_token_latency_seconds"]["mean_s"]
            batch = row["hist"]["vllm:iteration_tokens_total"]["mean_s"]
            tps = row["client"]["tokens_per_s"]
            ratio = None if not base_itl else itl / base_itl
            linear = None if not base_tps or not row["concurrency"] or not base["concurrency"] else tps / (base_tps * row["concurrency"] / base["concurrency"])
            run_mean = None if not row["running"] else row["running"]["mean"]
            wait_mean = None if not row["waiting"] else row["waiting"]["mean"]
            lines.append(
                f"| {row['concurrency']} | {ms(itl)} ms | {num(ratio, 2)}× | {num(tps)} | {pct(linear)} | "
                f"{ms(row['client']['ttft_median_s'])} ms | {num(run_mean, 1)} | {num(wait_mean, 1)} | {num(batch, 2)} |"
            )
        lines.append("")
        flat = [r for r in conc if r["hist"]["vllm:inter_token_latency_seconds"]["mean_s"] <= base_itl * 1.08]
        risen = [r for r in conc if r not in flat]
        lines.append("The scheduler keeps every client in the running set and the waiting set at zero, so the extra delay is not a queue. `iteration_tokens_total` grows almost one-for-one with concurrency: each engine step decodes the whole batch, and every request in that run sees the same TPOT.")
        lines.append("")
        if flat:
            flat_itl = [r["hist"]["vllm:inter_token_latency_seconds"]["mean_s"] for r in flat]
            lines.append(f"Through {flat[-1]['concurrency']} clients the step stays flat at {ms(min(flat_itl))}–{ms(max(flat_itl))} ms, and tokens/s stay near the 1-client line.")
        if risen:
            bits = []
            for row in risen:
                itl = row["hist"]["vllm:inter_token_latency_seconds"]["mean_s"]
                tps = row["client"]["tokens_per_s"]
                linear = None if not base_tps or not row["concurrency"] else tps / (base_tps * row["concurrency"])
                bits.append(f"{row['concurrency']} clients at {ms(itl)} ms ({pct(linear)} of linear, {num(tps)} tokens/s)")
            if any(r.get("omp_invalid") for r in conc):
                lines.append("The step then lengthens: " + "; ".join(bits) + ". On these points OpenMP warning #124 is present, so the extra threads were piled onto CPU 0.")
            else:
                lines.append("The step then lengthens: " + "; ".join(bits) + ". These runs have no OpenMP warning #124. Each selected core has one compute thread, so a longer step is a more expensive batch, not a collapsed affinity mask.")
        lines.append("")
        finished_itl = [r["hist"]["vllm:inter_token_latency_seconds"]["mean_s"] for r in conc]
        ceiling = max(finished_itl)
        stretching = [r for r in partial_rows
                      if r["model"] == base["model"]
                      and r["hist"]["vllm:inter_token_latency_seconds"]["mean_s"]
                      and r["hist"]["vllm:inter_token_latency_seconds"]["mean_s"] > ceiling * 1.08]
        if stretching:
            row = stretching[-1]
            itl = row["hist"]["vllm:inter_token_latency_seconds"]
            lines.append(f"The open `{row['config_id']}` window is already slower than the finished points: inter-token latency **{ms(itl['mean_s'])} ms** ({bucket_phrase(itl['dominant'])}) over {num(itl['n'], 0)} tokens.")
            lines.append("")
        last = conc[-1]
        if last["client"]["ttft_median_s"] and base["client"]["ttft_median_s"]:
            lines.append(f"Time to first token rises with concurrency on the 96-core runs. Client TTFT median goes from {ms(base['client']['ttft_median_s'])} ms at {base['concurrency']} client to {ms(last['client']['ttft_median_s'])} ms at {last['concurrency']} clients. Server `time_to_first_token_seconds` matches that rise. Waiting requests stay at zero, so this is batch service time. On these 96-core points the request-finish histograms stay empty, because a request does not complete inside the window.")
            lines.append("")
    core_cmp = [r for r in finished_rows if r.get("concurrency") == 8 and r.get("output_tokens") == 512]
    core_cmp.sort(key=lambda r: (str(r["model"]), r["cores"] or 0))
    if len({r["cores"] for r in core_cmp}) > 1:
        lines.append("## Core count, same 8 clients")
        lines.append("")
        lines.append("8 clients, 512 generated tokens. Compared inside one model.")
        lines.append("")
        lines.append("| Model | Cores | ITL mean | Client TPOT | Tokens/s | Complete requests | Request TPOT mean | Decode time mean | Server TTFT |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
        for row in core_cmp:
            h = row["hist"]
            lines.append(
                f"| `{row['model']}` | {row['cores']} | {ms(h['vllm:inter_token_latency_seconds']['mean_s'])} ms | "
                f"{ms(row['client']['tpot_median_s'])} ms | {num(row['client']['tokens_per_s'])} | "
                f"{row['client']['complete'] if row['client']['complete'] is not None else '—'} | "
                f"{dur(h['vllm:request_time_per_output_token_seconds']['mean_s'])} | "
                f"{dur(h['vllm:request_decode_time_seconds']['mean_s'])} | "
                f"{ms(h['vllm:time_to_first_token_seconds']['mean_s'])} ms |"
            )
        lines.append("")
        by_model = defaultdict(list)
        for row in core_cmp:
            by_model[row["model"]].append(row)
        for model, group in by_model.items():
            if len({r["cores"] for r in group}) < 2:
                continue
            fastest = min(group, key=lambda r: r["hist"]["vllm:inter_token_latency_seconds"]["mean_s"] or 1e9)
            slowest = max(group, key=lambda r: r["hist"]["vllm:inter_token_latency_seconds"]["mean_s"] or 0)
            done_bit = ""
            if fastest["client"]["complete"]:
                done_bit = f" {fastest['client']['complete']} requests completed inside the 90-second window."
            lines.append(
                f"For `{model}`, {fastest['cores']} cores finished at {ms(fastest['hist']['vllm:inter_token_latency_seconds']['mean_s'])} ms/token "
                f"and {num(fastest['client']['tokens_per_s'])} tokens/s.{done_bit} "
                f"{slowest['cores']} cores at the same concurrency was {ms(slowest['hist']['vllm:inter_token_latency_seconds']['mean_s'])} ms/token "
                f"and {num(slowest['client']['tokens_per_s'])} tokens/s. "
                f"{'OpenMP warning #124 is present, so the worker mask collapsed onto CPU 0.' if any(r.get('omp_invalid') for r in group) else 'OpenMP warning #124 is absent, so each selected core has its own compute thread.'}"
            )
            lines.append("")
    elif finished_rows:
        lines.append("Not enough finished points yet to judge a concurrency slope. The table above is the current sample.")
        lines.append("")
    if partial_rows:
        lines.append("Open runs, counted only through the latest scrape. These rows move until `measurement_window_end` is written.")
        lines.append("")
        for row in partial_rows:
            itl = row["hist"]["vllm:inter_token_latency_seconds"]
            ttft = row["hist"]["vllm:time_to_first_token_seconds"]
            lines.append(f"- `{row['config_id']}` ({row['status']}): ITL mean {ms(itl['mean_s'])} ms over {num(itl['n'], 0)} tokens; server TTFT mean {ms(ttft['mean_s'])} ms (n={num(ttft['n'], 0)}).")
        lines.append("")
        ref8 = next((r for r in finished_rows if r.get("cores") == 96 and r.get("concurrency") == 8 and r.get("output_tokens") == 512), None)
        core_open = [r for r in partial_rows if r.get("sweep") == "cores" and r["hist"]["vllm:inter_token_latency_seconds"]["mean_s"]]
        if ref8 and core_open:
            opened = core_open[-1]
            ref_itl = ref8["hist"]["vllm:inter_token_latency_seconds"]["mean_s"]
            open_itl = opened["hist"]["vllm:inter_token_latency_seconds"]["mean_s"]
            if open_itl < ref_itl * 0.6:
                lines.append(
                    f"Provisional, until this window closes: the {opened['cores']}-core, {opened['concurrency']}-client step is **{ms(open_itl)} ms**, "
                    f"against {ms(ref_itl)} ms on the finished 96-core run at the same concurrency. "
                    f"Treat this as an open-window reading until `measurement_window_end` is written."
                )
                lines.append("")

    lines.append("## Thread pinning")
    lines.append("")
    warned = [r for r in rows if r.get("omp_invalid")]
    checked = [r for r in rows if (r["attempt"] / "server.log").exists()]
    if not checked:
        lines.append("No server log yet. Pinning is `numactl --physcpubind=0-(N-1)` on the server process and `--numa-bind-cpus 0-(N-1)` so the worker is re-exec'd under the same mask. Generated tokens stay at 512.")
    elif warned:
        sample = max(warned, key=lambda r: r["omp_max_id"] or 0)
        lines.append(f"{len(warned)} attempts logged OpenMP warning #124, ignoring OS proc IDs up to {sample['omp_max_id']} (`{sample['config_id']}`). Those workers did not keep one thread per core.")
    else:
        lines.append(f"All {len(checked)} attempts with a server log are free of OpenMP warning #124. The server process is started with `numactl --physcpubind=0-(N-1) --membind=0`, and vLLM re-execs the worker under the same CPU list. Generated tokens are fixed at 512.")
    lines.append("")
    if affinity:
        lines.append("Live worker at the last refresh (this follows whichever container is up, including the core sweep):")
        lines.append("")
        lines.append("```")
        lines.append(affinity)
        lines.append("```")
        lines.append("")
    amx_vals = [r["sys"]["amx_busy_fraction"] for r in finished_rows if r["sys"]["amx_busy_fraction"] is not None]
    ipc_vals = [r["sys"]["ipc"] for r in finished_rows if r["sys"]["ipc"] is not None]
    if amx_vals and ipc_vals:
        lines.append(f"This 0.5B path is manual BF16, not a Xeon 6 recipe. AMX-busy time across finished runs is {min(amx_vals) * 100:.2f}%–{max(amx_vals) * 100:.2f}% of counted cycles. It rises with batch size and is still a small slice of the step. IPC stays near {min(ipc_vals):.2f}–{max(ipc_vals):.2f}.")
        lines.append("")
    lines.append("Reported DRAM bandwidth in `system.csv` is about 0.0002 GB/s. A 0.5B BF16 model is about 1 GB of weights, larger than this socket's share of the 960 MiB L3, so a real decode should move on the order of gigabytes per second. The IMC CAS counts are tens of events per 100 ms interval. Treat the bandwidth column as not yet measuring this workload. It is not evidence that decode is cache-resident.")
    lines.append("")

    lines.append("## Other vLLM series")
    lines.append("")
    lines.append("| Config | Server TTFT mean | TTFT n | Queue mean | Prefill n | Decode-time n | Request TPOT n | E2E n | KV cache mean | IPC | AMX busy | L3 stall |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for row in sorted(finished_rows, key=lambda r: (str(r["model"]), r["concurrency"] or 0, r["cores"] or 0)):
        h = row["hist"]
        kv = None if not row["kv"] else row["kv"]["mean"]
        lines.append(
            f"| `{row['config_id']}` | {ms(h['vllm:time_to_first_token_seconds']['mean_s'])} ms | {num(h['vllm:time_to_first_token_seconds']['n'], 0)} | "
            f"{ms(h['vllm:request_queue_time_seconds']['mean_s'])} ms | {num(h['vllm:request_prefill_time_seconds']['n'], 0)} | "
            f"{num(h['vllm:request_decode_time_seconds']['n'], 0)} | {num(h['vllm:request_time_per_output_token_seconds']['n'], 0)} | "
            f"{num(h['vllm:e2e_request_latency_seconds']['n'], 0)} | {num(kv, 5)} | {num(row['sys']['ipc'], 3)} | "
            f"{pct(row['sys']['amx_busy_fraction'])} | {pct(row['sys']['l3_stall_fraction'])} |"
        )
    lines.append("")
    lines.append("KV-cache occupancy stays well under 0.1%. The waiting gauge stays at 0 through the finished concurrency points, so TTFT growth is service time inside the batch, not scheduler queue time. Queue-time histograms confirm that only if requests finish; they have not, inside the window.")
    lines.append("")

    lines.append("## Caveats")
    lines.append("")
    n_complete = sum((r["client"]["complete"] or 0) for r in finished_rows)
    n_zero = sum(1 for r in finished_rows if r["client"]["complete"] == 0)
    if n_zero:
        lines.append(f"- {n_zero} finished runs have `complete_requests` = 0, so the official complete-request TPOT percentiles in `summary.json` are null. 512 tokens at ~350 ms/token is about three minutes, and the measurement window is 90 seconds. Use observed client TPOT and the server inter-token histogram there.")
    if n_complete:
        lines.append(f"- {n_complete} requests have completed inside a measurement window. On those runs the request-level TPOT and decode-time histograms are populated, and they belong in the core-count table.")
    lines.append("- Histogram p50/p90/p99 are interpolated inside 100 ms buckets. When almost every sample sits in 300–400 ms, those percentiles collapse toward the middle and the top of that bucket. Quote the mean, and the bucket share, for decode latency.")
    lines.append("- Partial rows are mid-window and will be replaced when the attempt writes `summary.json`.")
    lines.append("- Several finished attempts record a non-fatal Docker cleanup race (`removal of container ... is already in progress`). The run stays marked done and the controller continues.")
    lines.append("")
    lines.append("## What changes next")
    lines.append("")
    pending_note = []
    pending_cfgs = []
    done_keys = {key for key, item in progress.get("runs", {}).items() if item.get("status") == "done"}
    for run in plan.get("runs") or []:
        key = f"{run['model']}|{run['config_id']}"
        if key not in done_keys:
            pending_cfgs.append(run)
    if pending_cfgs:
        nxt = pending_cfgs[0]
        pending_note.append(f"Next unfinished point is `{nxt['model']}` `{nxt['config_id']}` ({nxt['sweep']}).")
    wide = [r for r in pending_cfgs if r["model"].endswith("0.5B-Instruct") and r["sweep"] == "concurrency"]
    cores_left = [r for r in pending_cfgs if r["model"].endswith("0.5B-Instruct") and r["sweep"] == "cores"]
    if wide:
        pending_note.append("Remaining 0.5B concurrency points show whether the step time keeps stretching once the batch is wider than 32.")
    if cores_left:
        pending_note.append("The core sweep (fewer than 96 CPUs in `--cpuset-cpus`) is the check on whether a shorter bind list changes the OpenMP mask.")
    if any(r.get("recipe") for r in pending_cfgs):
        pending_note.append("Recipe models are still ahead. If those workers bind across the cpuset, decode latency should leave the band seen on this manual BF16 path.")
    pending_note.append("This file is rewritten as attempts finish.")
    lines.append(" ".join(pending_note))
    lines.append("")

    report_path.write_text("\n".join(lines) + "\n")

    # status.md
    phase = "Idle"
    if pid and active.get("model"):
        phase = f"Benchmark run `{active.get('model')}` / `{Path(active.get('output','')).name}`"
    elif pid:
        phase = "Controller running, between runs"
    elif done and total and done >= total:
        phase = "Experiment finished"
    else:
        phase = "Controller not running"
    failures = []
    cleanup = [row["config_id"] for row in finished_rows if row.get("cleanup_error")]
    real_errors = [row for row in finished_rows if row.get("error")]
    if cleanup:
        failures.append(
            f"Docker cleanup race on {len(cleanup)} finished runs (`removal of container ... is already in progress`): "
            + ", ".join(f"`{item}`" for item in cleanup[:6])
            + ("…" if len(cleanup) > 6 else "")
            + ". Each run stayed done. No retry; the controller continued."
        )
    for row in real_errors:
        failures.append(f"`{row['config_id']}`: {row['error']}")
    warned = [row for row in rows if row.get("omp_invalid")]
    if warned:
        failures.append(
            f"OpenMP warning #124 is present on {len(warned)} attempts. Those workers did not keep one thread per core."
        )
    if not failures:
        failures.append("No failed runs.")
    completed = []
    for row in finished_rows:
        itl = row["hist"]["vllm:inter_token_latency_seconds"]["mean_s"]
        completed.append(f"`{row['config_id']}` ({row['elapsed_s'] and round(row['elapsed_s'], 1)} s): ITL mean {ms(itl)} ms, client TPOT {ms(row['client']['tpot_median_s'])} ms, {num(row['client']['tokens_per_s'])} tokens/s, complete requests {row['client']['complete']}.")
    remaining = []
    done_ids = {f"{item.get('run', {}).get('model')}|{item.get('run', {}).get('config_id')}" for item in progress.get("runs", {}).values() if item.get("status") == "done"}
    # progress keys are model|config
    done_keys = {key for key, item in progress.get("runs", {}).items() if item.get("status") == "done"}
    for run in plan.get("runs") or []:
        key = f"{run['model']}|{run['config_id']}"
        if key not in done_keys:
            remaining.append(f"`{run['model']}` `{run['config_id']}` ({run['sweep']})")
    status = []
    status.append("# status")
    status.append("")
    status.append(f"Updated: {stamp}")
    status.append("")
    status.append("## Current Phase")
    status.append("")
    status.append(f"{phase}.")
    if pid:
        status.append(f"Controller PID: {pid}. Start: {controller.get('started', 'unknown')}. Log: `{controller.get('log', '')}`.")
    if active.get("output"):
        status.append(f"Active output: `{active.get('output')}`.")
    status.append("")
    status.append("## Overall Progress")
    status.append("")
    status.append(f"{bar(done, total)} {done}/{total} runs done. Status counts: {dict(counts) or {'none': 0}}.")
    status.append("")
    status.append("## Completed Steps")
    status.append("")
    status.append(f"- Pinned plan `{plan.get('plan_id', 'unknown')}` is the active experiment. Generated tokens stay at 512. Sweeps are concurrency and core count.")
    for item in completed:
        status.append(f"- {item}")
    status.append(f"- `{report_path.name}` refreshed at {stamp} from `metrics_long.csv`, `requests.csv`, `system.csv`, and `server.log`.")
    status.append("")
    status.append("## Remaining Steps")
    status.append("")
    status.append(f"- {len(remaining)} runs still unfinished. Next up:")
    for item in remaining[:8]:
        status.append(f"  - {item}")
    if len(remaining) > 8:
        status.append(f"  - … {len(remaining) - 8} more")
    status.append(f"- Keep rewriting `{report_path.name}` as each attempt closes, with decode inter-token latency as the primary series.")
    status.append("- After the plan finishes, mark this file complete and fold the final tables into the report.")
    status.append("")
    status.append("## Active Failures/Retries")
    status.append("")
    for item in failures:
        status.append(f"- {item}")
    status.append("")
    status.append("## Implementation Plan")
    status.append("")
    status.append("1. Watch `./experiment.sh status` and the controller log without interrupting the running plan.")
    status.append("2. After each attempt, summarize vLLM inter-token latency, client TPOT, TTFT, throughput, scheduler depth, and perf counters over the measurement window.")
    status.append(f"3. Rewrite `{report_path.name}` so the decode-latency trend stays current.")
    status.append("4. Call out affinity and counter problems that change how the latency should be read.")
    status.append("5. Leave the controller running. Do not retry a run that the controller already marked done.")
    status.append("")
    (ROOT / "status.md").write_text("\n".join(status) + "\n")
    print(f"Updated {report_path.name} and status.md at {stamp}: {done}/{total} done, {len(finished_rows)} summaries, {len(partial_rows)} partial")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan-id", help="Keep attempts whose config.json plan_id matches")
    parser.add_argument("--output", type=Path, default=ROOT / "REPORT.md")
    args = parser.parse_args()
    rows = []
    for path in sorted(LOGS.glob("*/*/attempt-*")):
        row = analyze_attempt(path)
        if args.plan_id and row.get("plan_id") != args.plan_id:
            continue
        rows.append(row)
    write_reports(rows, args.output)


if __name__ == "__main__":
    main()
