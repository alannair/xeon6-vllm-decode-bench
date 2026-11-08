"""One-factor-at-a-time sweep planning with stable identifiers."""
from __future__ import annotations

import fnmatch
import json
from pathlib import Path

from .common import ROOT, plan_hash, slug
from .topology import choose_node, contiguous_node0_cores


def load_config(path: Path | None = None) -> dict:
    cfg = json.loads((path or ROOT / "configs/default.json").read_text())
    if not isinstance(cfg.get("models"), list):
        raise ValueError("Config must specify models[]")
    if int(cfg["limits"]["run_timeout_s"]) > 1680:
        raise ValueError("Run timeout must be <=1680 seconds to stay below the 30 minute limit")
    if int(cfg["measurement"]["perf_interval_ms"]) < 100:
        raise ValueError("Perf interval <100ms is not recommended for this benchmark")
    if cfg["server"]["max_model_len"] < max(cfg["sweeps"]["output_tokens"]) + cfg["measurement"]["prompt_tokens"]:
        raise ValueError("max_model_len too short for longest prompt + output")
    return cfg


def make_plan(cfg: dict, model_patterns: list[str] | None = None, sweeps: list[str] | None = None,
              max_runs: int | None = None, node_override: str | None = None) -> dict:
    selected_node = node_override if node_override is not None else cfg.get("numa_node", 0)
    if str(selected_node) != "0":
        raise ValueError("This benchmark uses only NUMA node 0; --numa-node must be 0")
    node = choose_node(0)
    available = contiguous_node0_cores(node)
    configured = [int(c) for c in cfg["sweeps"]["cores"]]
    preferred = int(cfg["sweeps"]["baseline_cores"])
    if preferred > available or any(c > available for c in configured):
        raise RuntimeError(
            f"Requested baseline={preferred} and CPU sweep={configured}, but NUMA node 0 "
            f"exposes only contiguous physical CPU IDs 0..{available-1}. "
            "The benchmark will not silently shrink the 96-core baseline or "
            "substitute other NUMA nodes. Inspect lscpu -e and numactl --hardware."
        )
    allowed = configured
    baseline = preferred
    conc = int(cfg["sweeps"]["baseline_concurrency"])
    out = int(cfg["sweeps"]["baseline_output_tokens"])
    requested = set(sweeps or ["concurrency", "cores", "output_tokens"])
    invalid = requested - {"concurrency", "cores", "output_tokens", "baseline"}
    if invalid:
        raise ValueError(f"Unknown sweep(s): {sorted(invalid)}")
    variants = [(baseline, conc, out, "baseline")]
    if "concurrency" in requested:
        variants += [(baseline, c, out, "concurrency") for c in cfg["sweeps"]["concurrency"]]
    if "cores" in requested:
        variants += [(c, conc, out, "cores") for c in allowed]
    if "output_tokens" in requested:
        variants += [(baseline, conc, n, "output_tokens") for n in cfg["sweeps"]["output_tokens"]]
    seen = set()
    unique = []
    for cores, concurrency, tokens, sweep in variants:
        if cores < 1 or concurrency < 1 or tokens < 1 or concurrency > int(cfg["server"]["max_num_seqs"]):
            continue
        key = (cores, concurrency, tokens)
        if key in seen:
            continue
        seen.add(key)
        unique.append((cores, concurrency, tokens, sweep))
    selected = []
    for model in cfg["models"]:
        if model.get("enabled", True) is False:
            continue
        name = model["id"]
        if model_patterns and not any(fnmatch.fnmatch(name, x) or fnmatch.fnmatch(name.split("/")[-1], x)
                                      or x in name for x in model_patterns):
            continue
        selected.append(model)
    if not selected:
        raise ValueError("No enabled models match --models patterns")
    selected.sort(key=lambda m: (float(m.get("size_b", 999)), m["id"]))
    runs = []
    # Each config varies only one independent variable relative to the baseline.
    for model in selected:
        for cores, concurrency, tokens, sweep in unique:
            cfg_id = f"node{node['node']}_cores{cores:03d}_clients{concurrency:03d}_gen{tokens:04d}"
            runs.append({"model": model["id"], "size_b": model.get("size_b"),
                         "model_slug": slug(model["id"].replace("/", "__")),
                         "recipe": bool(model.get("recipe", False)),
                         "config_id": cfg_id, "sweep": sweep, "numa_node": node["node"],
                         "socket": node["socket"], "cores": cores, "concurrency": concurrency,
                         "output_tokens": tokens})
    if max_runs is not None:
        runs = runs[:max_runs]
    if not runs:
        raise ValueError("Empty benchmark plan")
    result = {"config": cfg, "node": node, "runs": runs, "models": [m["id"] for m in selected],
              "cpu_id_policy": "0..N-1 physical CPUs on node 0", "max_contiguous_node0_cpus": available,
              "skipped_cpu_counts": sorted(set(configured) - set(allowed))}
    result["plan_id"] = plan_hash(result)
    return result
