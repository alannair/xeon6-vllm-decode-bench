"""One-factor-at-a-time sweep planning with stable identifiers."""
from __future__ import annotations

import fnmatch
import json
from pathlib import Path

from .common import ROOT, plan_hash, slug
from .topology import choose_node


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
    node = choose_node(node_override if node_override is not None else cfg.get("numa_node", "auto"))
    available = len(node["physical_cpus"]) - int(cfg["limits"]["reserve_cores"])
    if available < 1:
        raise RuntimeError("Not enough physical cores for inference plus reserves")
    baseline = min(int(cfg["sweeps"]["baseline_cores"]), available)
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
        variants += [(c, conc, out, "cores") for c in cfg["sweeps"]["cores"] if c <= available]
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
    result = {"config": cfg, "node": node, "runs": runs, "models": [m["id"] for m in selected]}
    result["plan_id"] = plan_hash(result)
    return result
