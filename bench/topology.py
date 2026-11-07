"""NUMA node/physical-core selection from Linux sysfs, respecting cgroup affinity."""
from __future__ import annotations

import os
from pathlib import Path
import re


def parse_cpu_list(spec: str) -> list[int]:
    cpus = set()
    for part in spec.strip().split(","):
        if not part:
            continue
        if "-" in part:
            a, b = map(int, part.split("-", 1))
            if b < a:
                raise ValueError("invalid CPU range")
            cpus.update(range(a, b + 1))
        else:
            cpus.add(int(part))
    return sorted(cpus)


def cpulist(cpus: list[int]) -> str:
    return ",".join(map(str, cpus))


def node_memory_gib(node: int) -> float | None:
    p = Path(f"/sys/devices/system/node/node{node}/meminfo")
    if not p.exists():
        return None
    for line in p.read_text().splitlines():
        if re.search(r"\bMemTotal:\s*(\d+)\s+kB", line):
            return int(re.search(r"\bMemTotal:\s*(\d+)\s+kB", line).group(1)) / (1024 ** 2)
    return None


def cpu_package(cpu: int) -> int:
    p = Path(f"/sys/devices/system/cpu/cpu{cpu}/topology/physical_package_id")
    return int(p.read_text()) if p.exists() else 0


def get_nodes() -> list[dict]:
    allowed = set(os.sched_getaffinity(0))
    base = Path("/sys/devices/system/node")
    node_dirs = sorted(base.glob("node[0-9]*"), key=lambda p: int(p.name[4:]))
    if not node_dirs:
        return [{"node": 0, "socket": 0, "physical_cpus": sorted(allowed),
                 "logical_cpus": sorted(allowed), "memory_gib": None}]
    result = []
    for p in node_dirs:
        node = int(p.name[4:])
        logical = sorted(set(parse_cpu_list((p / "cpulist").read_text())) & allowed)
        seen = set()
        physical = []
        for cpu in logical:
            t = Path(f"/sys/devices/system/cpu/cpu{cpu}/topology")
            pkg = int((t / "physical_package_id").read_text())
            core = int((t / "core_id").read_text())
            die = int((t / "die_id").read_text()) if (t / "die_id").exists() else 0
            key = (pkg, die, core)
            if key not in seen:
                physical.append(cpu)
                seen.add(key)
        if physical:
            result.append({"node": node, "socket": cpu_package(physical[0]),
                           "logical_cpus": logical, "physical_cpus": physical,
                           "memory_gib": node_memory_gib(node)})
    return result


def choose_node(spec="auto") -> dict:
    nodes = get_nodes()
    if not nodes:
        raise RuntimeError("No accessible NUMA node CPUs (check cpuset/affinity)")
    if spec != "auto":
        candidates = [x for x in nodes if x["node"] == int(spec)]
        if not candidates:
            raise ValueError(f"NUMA node {spec} not available: {[x['node'] for x in nodes]}")
        return candidates[0]
    return max(nodes, key=lambda x: len(x["physical_cpus"]))


def select_cores(node: dict, inference_cores: int, reserved: int = 2) -> dict:
    cpus = node["physical_cpus"]
    if len(cpus) < reserved + 1:
        raise ValueError(f"NUMA node {node['node']} has only {len(cpus)} accessible physical cores")
    if inference_cores > len(cpus) - reserved:
        raise ValueError("Requested more inference cores than NUMA node can supply")
    infer = cpus[:inference_cores]
    housekeeping = cpus[-reserved:]
    return {"infer": infer, "reserved": housekeeping, "all": infer + housekeeping}
