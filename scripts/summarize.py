#!/usr/bin/env python3
"""Build one comparative summary CSV without modifying per-run append-only logs."""
from __future__ import annotations

import csv
import json
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"
FIELDS = ["model", "size_b", "sweep", "config_id", "numa_node", "socket", "cores", "concurrency",
          "generated_tokens", "status", "elapsed_s", "attempt", "num_requests", "complete_requests",
          "observed_output_tokens", "delivered_tokens_s", "ttft_p50_ms", "ttft_p90_ms", "ttft_p99_ms",
          "tpot_p50_ms", "tpot_p90_ms", "tpot_p99_ms", "dram_bw_mean_gbps",
          "dram_bw_p90_gbps", "amx_busy_mean_fraction", "l3_stall_mean_fraction", "perf_warnings"]


def summarize():
    items = []
    for summary_file in sorted(LOGS.glob("*/*/attempt-*/summary.json")):
        try:
            info = json.loads(summary_file.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        run, summary = info.get("run", {}), info.get("summary", {})
        system_file = summary_file.parent / "system.csv"
        phase_file = summary_file.parent / "phases.csv"
        measurement_bounds = {}
        if phase_file.exists():
            with phase_file.open(newline="") as f:
                for phase in csv.DictReader(f):
                    measurement_bounds[phase["phase"]] = phase["timestamp_utc"]
        metrics = {"dram_total_gbps": [], "amx_busy_fraction": [], "l3_stall_fraction": []}
        if system_file.exists():
            with system_file.open(newline="") as f:
                for row in csv.DictReader(f):
                    start = measurement_bounds.get("measurement_start")
                    end = measurement_bounds.get("measurement_window_end")
                    if start and row["timestamp_utc"] < start:
                        continue
                    if end and row["timestamp_utc"] > end:
                        continue
                    for k in metrics:
                        try:
                            metrics[k].append(float(row[k]))
                        except (KeyError, ValueError, TypeError):
                            pass
        def mean(key):
            return statistics.mean(metrics[key]) if metrics[key] else ""
        def p90(key):
            arr = sorted(metrics[key])
            return arr[int((len(arr) - 1) * .9)] if arr else ""
        def ms(key):
            v = summary.get(key)
            return round(v * 1000, 4) if v is not None else ""
        items.append({"model": run.get("model"), "size_b": run.get("size_b"),
                      "sweep": run.get("sweep"), "config_id": run.get("config_id"),
                      "numa_node": run.get("numa_node"), "socket": run.get("socket"),
                      "cores": run.get("cores"), "concurrency": run.get("concurrency"),
                      "generated_tokens": run.get("output_tokens"), "status": info.get("status"),
                      "elapsed_s": info.get("total_elapsed_s"), "attempt": str(summary_file.parent),
                      "num_requests": summary.get("finished_request_records"),
                      "complete_requests": summary.get("complete_requests"),
                      "observed_output_tokens": summary.get("observed_output_tokens"),
                      "delivered_tokens_s": summary.get("delivered_tokens_per_s"),
                      "ttft_p50_ms": ms("ttft_median_s"), "ttft_p90_ms": ms("ttft_p90_s"),
                      "ttft_p99_ms": ms("ttft_p99_s"),
                      "tpot_p50_ms": ms("mean_tpot_median_s"), "tpot_p90_ms": ms("mean_tpot_p90_s"),
                      "tpot_p99_ms": ms("mean_tpot_p99_s"),
                      "dram_bw_mean_gbps": mean("dram_total_gbps"),
                      "dram_bw_p90_gbps": p90("dram_total_gbps"),
                      "amx_busy_mean_fraction": mean("amx_busy_fraction"),
                      "l3_stall_mean_fraction": mean("l3_stall_fraction"),
                      "perf_warnings": " | ".join(info.get("perf", {}).get("warnings", []))})
    LOGS.mkdir(parents=True, exist_ok=True)
    out = LOGS / "results.csv"
    with out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(items)
    print(f"Wrote {len(items)} attempts to {out}")


if __name__ == "__main__":
    summarize()
