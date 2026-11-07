#!/usr/bin/env python3
"""Reproducible setup checks; must fail loudly if machine isn't benchmark-ready."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bench.common import STATE, atomic_json, execute, format_bytes, free_bytes, utc_now
from bench.topology import get_nodes


def find_data_root(required_gib: float) -> Path:
    override = os.environ.get("BENCH_DATA_DIR")
    if override:
        path = Path(override).expanduser().resolve()
        path.mkdir(parents=True, exist_ok=True)
        if free_bytes(path) < required_gib * (1024**3):
            raise RuntimeError(f"BENCH_DATA_DIR={path} has only {format_bytes(free_bytes(path))} free; "
                               f"need >= {required_gib:g} GiB")
        return path
    root_dev = Path("/").stat().st_dev
    candidates = []
    likely = ["/data", "/data2", "/scratch", "/mnt/data", "/work", "/local", "/storage", "/raid"]
    # Also consider arbitrary mounted filesystems; avoid /proc,/sys and Docker overlay paths.
    try:
        for line in Path("/proc/mounts").read_text().splitlines():
            parts = line.split()
            if len(parts) >= 3 and parts[2] in ("ext4", "xfs", "btrfs", "zfs", "nfs", "nfs4"):
                likely.append(parts[1].replace("\\040", " "))
    except OSError:
        pass
    for value in dict.fromkeys(likely):
        p = Path(value)
        if not p.is_dir() or not os.access(p, os.W_OK | os.X_OK):
            continue
        try:
            if p.stat().st_dev == root_dev:
                continue
            free = free_bytes(p)
            if free >= required_gib * 1024**3:
                candidates.append((free, p))
        except OSError:
            continue
    if not candidates:
        raise RuntimeError(f"No writable non-root filesystem with >= {required_gib:g} GiB free. "
                           "Mount /data (or another disk), or set BENCH_DATA_DIR=/your/big/partition. "
                           "To explicitly allow a large root filesystem, set BENCH_DATA_DIR=/path/on/root.")
    return max(candidates, key=lambda item: item[0])[1]


def maybe_install_missing():
    requirements = {"docker": "docker", "numactl": "numactl", "perf": "perf", "lscpu": "util-linux", "curl": "curl"}
    missing = [name for name in requirements if not shutil.which(name)]
    if not missing:
        return
    print("Missing system commands:", missing, flush=True)
    if not sys.stdin.isatty() and os.geteuid() != 0 and not (shutil.which("sudo") and
              execute(["sudo", "-n", "true"], timeout=3).returncode == 0):
        raise RuntimeError("Cannot install system packages noninteractively; run setup in a terminal with sudo access")
    prefix = [] if os.geteuid() == 0 else ["sudo"]
    if shutil.which("apt-get"):
        packages = ["docker.io" if "docker" in missing else "", "numactl" if "numactl" in missing else "",
                    "linux-perf" if "perf" in missing else "", "util-linux" if "lscpu" in missing else "", "curl" if "curl" in missing else ""]
        commands = [["apt-get", "update"], ["apt-get", "install", "-y"] + [p for p in packages if p]]
    elif shutil.which("dnf") or shutil.which("yum"):
        manager = "dnf" if shutil.which("dnf") else "yum"
        packages = ["docker" if "docker" in missing else "", "numactl" if "numactl" in missing else "",
                    "perf" if "perf" in missing else "", "util-linux" if "lscpu" in missing else "", "curl" if "curl" in missing else ""]
        commands = [[manager, "install", "-y"] + [p for p in packages if p]]
    else:
        raise RuntimeError("Automatic install supports apt/dnf/yum only. Please install: " + ", ".join(missing))
    for command in commands:
        print("Installing:", " ".join(prefix + command), flush=True)
        subprocess.run(prefix + command, check=True)
    for command in missing:
        if not shutil.which(command):
            raise RuntimeError(f"{command} still missing after system package installation")


def check_docker(image: str, no_pull: bool):
    p = execute(["docker", "info", "--format", "{{.DockerRootDir}}"], timeout=15)
    if p.returncode != 0:
        if shutil.which("systemctl"):
            prefix = [] if os.geteuid() == 0 else ["sudo"]
            subprocess.run(prefix + ["systemctl", "start", "docker"], timeout=40, check=False)
            p = execute(["docker", "info", "--format", "{{.DockerRootDir}}"], timeout=15)
        if p.returncode != 0:
            raise RuntimeError("Docker daemon unavailable to this user: " + p.stderr[-500:] +
                               "\nCheck docker group permissions or start the Docker service")
    docker_root = Path(p.stdout.strip())
    if docker_root.exists():
        print(f"Docker image-layer storage: {docker_root} ({format_bytes(free_bytes(docker_root))} free)")
        if free_bytes(docker_root) < 10 * 1024**3:
            raise RuntimeError("Less than 10 GiB free where Docker image layers live. "
                               "Consider moving Docker data-root to a larger filesystem.")
    if not no_pull:
        print("Pulling", image, flush=True)
        subprocess.run(["docker", "pull", image], check=True)
    if execute(["docker", "image", "inspect", image], timeout=15).returncode != 0:
        raise RuntimeError(f"Docker CPU image {image} is absent; rerun setup without --no-pull")
    digest = execute(["docker", "image", "inspect", "--format", "{{.Id}}", image], timeout=15)
    return {"docker_root": str(docker_root), "image_id": digest.stdout.strip()}


def check_onednn(image: str) -> dict:
    """Verify that the PyTorch library in the selected CPU image includes oneDNN.

    This is only a *library availability* check; actual selected model kernel
    instructions should be inspected via oneDNN_VERBOSE and AMX perf events.
    """
    code = ("import json, torch; "
            "print('BENCH_ONEDNN=' + json.dumps({"
            "'torch': torch.__version__, "
            "'mkldnn_available': bool(torch.backends.mkldnn.is_available()), "
            "'mkldnn_enabled': bool(torch.backends.mkldnn.enabled), "
            "'cpu_capability': getattr(torch.backends.cpu, 'get_cpu_capability', lambda: 'unknown')()}))")
    p = execute(["docker", "run", "--rm", "--network", "none", "--entrypoint", "python3",
                 image, "-c", code], timeout=90)
    if p.returncode != 0:
        raise RuntimeError("Unable to inspect CPU image's torch/oneDNN build: " + p.stderr[-1000:])
    for line in p.stdout.splitlines():
        if line.startswith("BENCH_ONEDNN="):
            info = json.loads(line.split("=", 1)[1])
            print("Container CPU acceleration:", info)
            if not info.get("mkldnn_available", False) or not info.get("mkldnn_enabled", False):
                raise RuntimeError("CPU image lacks torch oneDNN/MKLDNN support; cannot claim optimized CPU path")
            return info
    raise RuntimeError("Unable to read torch/oneDNN check response from CPU image: " + p.stdout[-500:])


def check_perf(node: dict, attempted_sysctl: bool = False):
    from bench.perf import available_core_events, discover_uncore
    cpu = node["physical_cpus"][0]
    for prefix in (["perf"], ["sudo", "-n", "perf"] if shutil.which("sudo") else []):
        if not prefix:
            continue
        events, errs = available_core_events(prefix, [cpu])
        if {"cycles", "instructions"}.issubset(events):
            uncore, warns = discover_uncore(node["socket"])
            print("perf available events:", events)
            for w in warns:
                print("WARNING:", w)
            if not uncore:
                print("WARNING: no uncore IMC counters discovered (DRAM bandwidth CSV will be empty)")
            return {"perf_prefix": prefix, "core_events": events,
                    "uncore_events": len(uncore), "warnings": warns}
        print(f"perf check failed via {' '.join(prefix)}:", errs.get("cycles", "unknown")[-250:])
    if not attempted_sysctl and (os.geteuid() == 0 or (shutil.which("sudo") and execute(["sudo", "-n", "true"], timeout=3).returncode == 0)):
        sudo = [] if os.geteuid() == 0 else ["sudo", "-n"]
        print("Attempting temporary kernel.perf_event_paranoid=-1 to enable system-wide counters")
        p = execute(sudo + ["sysctl", "-w", "kernel.perf_event_paranoid=-1"], timeout=10)
        if p.returncode == 0:
            return check_perf(node, attempted_sysctl=True)
    raise RuntimeError("Insufficient permission for perf stat -a -C. Ask your admin to enable "
                       "perf counters (e.g. sudo sysctl -w kernel.perf_event_paranoid=-1), "
                       "or provide passwordless sudo perf. Do not silently skip counters.")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--no-pull", action="store_true")
    p.add_argument("--min-free-gib", type=float, default=float(os.environ.get("BENCH_MIN_FREE_GIB", "100")))
    args = p.parse_args()
    if sys.version_info < (3, 10) or platform.system() != "Linux" or platform.machine() != "x86_64":
        raise RuntimeError("Requires Linux x86_64 and Python >= 3.10")
    config = json.loads((ROOT / "configs/default.json").read_text())
    data_root = find_data_root(args.min_free_gib)
    store = data_root / "xeon6-vllm-bench"
    store.mkdir(parents=True, exist_ok=True)
    for name in ("cache/huggingface", "cache/torch", "cache/vllm", "cache/xdg", "cache/tmp", "logs"):
        (store / name).mkdir(parents=True, exist_ok=True)
    # Append-heavy per-token trace files can dwarf model caches over long sweeps.
    # Preserve ./logs/<model>/<config> syntax but store its bytes on the big disk.
    logs_link = ROOT / "logs"
    target_logs = store / "logs"
    if logs_link.is_symlink():
        if logs_link.resolve() != target_logs.resolve():
            raise RuntimeError(f"Existing ./logs symlink points at {logs_link.resolve()}, not {target_logs}; move it first")
    elif logs_link.exists():
        if not logs_link.is_dir() or any(logs_link.iterdir()):
            raise RuntimeError("Nonempty ./logs exists on a potentially small filesystem. "
                               "Move it into " + str(target_logs) + " and replace it with a symlink, then rerun setup.")
        logs_link.rmdir()
        logs_link.symlink_to(target_logs, target_is_directory=True)
    else:
        logs_link.symlink_to(target_logs, target_is_directory=True)
    print(f"Attempt logs: {logs_link} -> {target_logs}")
    if free_bytes(store) < args.min_free_gib * 1024**3:
        raise RuntimeError(f"Insufficient storage free after cache directory creation on {store}")
    print(f"Model/cache storage: {store} ({format_bytes(free_bytes(store))} free)")
    maybe_install_missing()
    nodes = get_nodes()
    for node in nodes:
        print(f"NUMA node {node['node']} socket {node['socket']}: {len(node['physical_cpus'])} physical cores, "
              f"memory={node['memory_gib']} GiB")
    if not nodes:
        raise RuntimeError("No usable NUMA node found")
    selected = max(nodes, key=lambda x: len(x["physical_cpus"]))
    flags = set()
    for line in Path("/proc/cpuinfo").read_text().splitlines():
        if line.startswith("flags"):
            flags = set(line.split(":", 1)[1].split())
            break
    isa = {flag: flag in flags for flag in ("amx_tile", "amx_bf16", "amx_int8", "avx512f", "avx512_bf16", "avx2")}
    print("CPU ISA flags:", isa)
    if not isa["amx_tile"]:
        print("WARNING: AMX tile flag not exposed on this host; AMX performance cannot be proven")
    if selected["memory_gib"] and selected["memory_gib"] < 32:
        print("WARNING: <= 32 GiB node DRAM may not fit the 8B workloads")
    docker_info = check_docker(config["image"], args.no_pull)
    onednn_info = check_onednn(config["image"])
    perf_info = check_perf(selected)
    inventory = {
        "lscpu": execute(["lscpu"], timeout=10).stdout,
        "numactl_hardware": execute(["numactl", "--hardware"], timeout=10).stdout,
        "perf_version": execute(["perf", "--version"], timeout=10).stdout,
        "uname": platform.uname()._asdict(),
    }
    atomic_json(STATE / "hardware_inventory.json", inventory)
    # Build isolated client env once, independent of big PyTorch/vLLM container libraries.
    env = ROOT / ".venv"
    if not (env / "bin/python").exists():
        print("Creating Python environment", flush=True)
        venv.create(env, with_pip=True)
    subprocess.run([str(env / "bin/python"), "-m", "pip", "install", "--disable-pip-version-check",
                    "-r", str(ROOT / "requirements.txt")], check=True)
    atomic_json(STATE / "setup.json", {"setup_utc": utc_now(), "data_root": str(store),
                                       "node_snapshot": nodes, "isa": isa, "perf": perf_info,
                                       "docker": docker_info, "onednn": onednn_info, "image": config["image"]})
    print("\nREADY: ./experiment.sh start")
    print("Data/cache:", store)
    print("Logs:", ROOT / "logs")
    print("State:", ROOT / "state/setup.json")
    print("Note: model weights download on first use; free space is monitored during each startup.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("SETUP FAILED:", exc, file=sys.stderr)
        sys.exit(1)
