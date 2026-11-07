"""Bench run controller, strict watchdog, Docker isolation and resumable checkpoints."""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
import shlex
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
import traceback

from .client import run_measurement
from .common import LOGS, ROOT, STATE, atomic_json, execute, free_bytes, read_json, timestamp_id, utc_now
from .perf import PerfCollector
from .topology import cpulist, select_cores

STOP = False


class RunTimeout(RuntimeError):
    pass


def _on_signal(signum, frame):
    global STOP
    STOP = True
    if signum == signal.SIGALRM:
        raise RunTimeout("Per-run wall time exceeded hard limit")


def stopped():
    return STOP or (STATE / "stop.flag").exists()


def safe_docker_name(plan_id: str, num: int):
    return f"xeon6-bench-{plan_id}-{num:03d}"


def docker_args(cfg: dict, run: dict, cache_dir: Path, cpus: dict, name: str,
                kv_gb: int, output: Path | None = None) -> list[str]:
    server = cfg["server"]
    # Container cpus/mems pin ALL server processes to the selected NUMA domain;
    # OMP threads use the inference subset, reserving housekeeping cores for frontend.
    cmd = ["docker", "run", "--rm", "--name", name, "--network", "host",
           "--cpuset-cpus", cpulist(cpus["all"]), "--cpuset-mems", str(run["numa_node"]),
           "--shm-size", "4g", "--cap-add", "SYS_NICE", "--security-opt", "seccomp=unconfined",
           "-v", f"{cache_dir / 'cache/huggingface'}:/root/.cache/huggingface",
           "-v", f"{cache_dir / 'cache/torch'}:/cache/torch",
           "-v", f"{cache_dir / 'cache/vllm'}:/cache/vllm",
           "-v", f"{cache_dir / 'cache/xdg'}:/cache/xdg",
           "-v", f"{cache_dir / 'cache/tmp'}:/cache/tmp"]
    if output is not None:
        cmd.extend(["-v", f"{output}:/benchout"])
    env = {
        "HF_HOME": "/root/.cache/huggingface", "HF_HUB_CACHE": "/root/.cache/huggingface/hub",
        "HUGGINGFACE_HUB_CACHE": "/root/.cache/huggingface/hub",
        "TORCH_HOME": "/cache/torch", "VLLM_CACHE_ROOT": "/cache/vllm",
        "XDG_CACHE_HOME": "/cache/xdg", "TMPDIR": "/cache/tmp",
        "VLLM_CPU_OMP_THREADS_BIND": cpulist(cpus["infer"]),
        "OMP_NUM_THREADS": str(len(cpus["infer"])), "OMP_PROC_BIND": "close", "OMP_PLACES": "cores",
        "KMP_BLOCKTIME": "0", "VLLM_CPU_KVCACHE_SPACE": str(kv_gb),
        "ONEDNN_VERBOSE": str(server.get("one_dnn_verbose", 0)),
        "DNNL_VERBOSE": str(server.get("one_dnn_verbose", 0)),
        "VLLM_CPU_SGL_KERNEL": str(server.get("vllm_cpu_sgl_kernel", 0)),
    }
    for k, v in env.items():
        cmd.extend(["-e", f"{k}={v}"])
    if os.environ.get("HF_TOKEN"):
        cmd.extend(["-e", "HF_TOKEN"])  # Secrets never appear in server_command.json.
    cli_args = ["--host", "127.0.0.1", "--port", str(cfg["host_port"]),
                "--dtype", server["dtype"], "--max-model-len", str(server["max_model_len"]),
                "--max-num-seqs", str(server["max_num_seqs"]),
                "--max-num-batched-tokens", str(server["max_num_batched_tokens"]),
                "--tensor-parallel-size", "1"]
    cli_args.extend(server.get("extra_args", []))
    recipe = server.get("deployment", "manual") == "recipe" and run.get("recipe", False)
    if recipe:
        if output is None:
            raise ValueError("Recipe deployment requires an output directory")
        # vLLM Recipes produce config.yml + env.sh. Override selected options so
        # NUMA, fixed KV sizing and workload limits remain controlled across runs.
        # The generated files are persisted under the per-run log directory.
        python_cmd = ["python3", "tools/recipes/recipe_json_to_vllm_config.py",
                      "--model", run["model"], "--hardware", "xeon6", "--detect-hardware",
                      "--config-out", "/benchout/recipe-config.yml",
                      "--env-out", "/benchout/recipe-env.sh"]
        env_after_recipe = {"VLLM_CPU_OMP_THREADS_BIND": cpulist(cpus["infer"]),
                            "OMP_NUM_THREADS": str(len(cpus["infer"])),
                            "VLLM_CPU_KVCACHE_SPACE": str(kv_gb)}
        exports = " ".join(f"{k}={shlex.quote(v)}" for k, v in env_after_recipe.items())
        shell = ("cd /vllm-workspace && " + shlex.join(python_cmd) +
                 " && source /benchout/recipe-env.sh && export " + exports +
                 " && exec vllm serve " + shlex.quote(run["model"]) +
                 " --config /benchout/recipe-config.yml " + shlex.join(cli_args))
        cmd.extend(["--entrypoint", "/bin/bash", cfg["image"], "-lc", shell])
    else:
        cmd.extend([cfg["image"], run["model"]] + cli_args)
    return cmd


def kv_gb_for_node(cfg, node):
    specified = cfg["server"].get("kv_cache_gb", "auto")
    if specified != "auto":
        return int(specified)
    # Conservative allocation based on TOTAL local NUMA node memory. More memory
    # is needed for weights, PyTorch scratch space, Linux and the API frontend.
    memory = node.get("memory_gib") or 64
    return max(4, min(64, int(max(4, memory - 24) * 0.45)))


def stop_container(name: str, timeout_s=10):
    if not name:
        return
    try:
        execute(["docker", "stop", "-t", str(timeout_s), name], timeout=timeout_s + 7)
    finally:
        # Even if graceful stop times out, always attempt a forced removal.
        removed = execute(["docker", "rm", "-f", name], timeout=8)
        # Docker rm -f exits nonzero if container already disappeared, which is fine.
        if removed.returncode != 0 and "No such container" not in removed.stderr:
            raise RuntimeError(f"Unable to remove owned Docker container {name}: {removed.stderr[-300:]}")


def check_port_available(port: int):
    with socket.socket() as sock:
        if sock.connect_ex(("127.0.0.1", port)) == 0:
            raise RuntimeError(f"Port 127.0.0.1:{port} already occupied; change host_port in config")


def run_one(index: int, run: dict, plan: dict, setup: dict) -> dict:
    cfg = plan["config"]
    node = plan["node"]
    caps = select_cores(node, run["cores"], int(cfg["limits"]["reserve_cores"]))
    data_dir = Path(setup["data_root"])
    output = LOGS / run["model_slug"] / run["config_id"] / ("attempt-" + timestamp_id())
    output.mkdir(parents=True, exist_ok=False)
    name = safe_docker_name(plan["plan_id"], index)
    kv_gb = kv_gb_for_node(cfg, node)
    cmd = docker_args(cfg, run, data_dir, caps, name, kv_gb, output)
    base_url = f"http://127.0.0.1:{cfg['host_port']}"
    meta = {"run": run, "node": node, "selected_cpus": caps, "kv_cache_gb": kv_gb,
            "started": utc_now(), "plan_id": plan["plan_id"], "image_id": setup["docker"]["image_id"],
            "data_root": str(data_dir), "container_name": name, "cmd": cmd,
            "deployment": "recipe" if cfg["server"].get("deployment") == "recipe" and run.get("recipe") else "manual",
            "perf_prefix": setup["perf"]["perf_prefix"]}
    atomic_json(output / "config.json", meta)
    print(f"[{utc_now()}] START {index}: {run['model']} {run['config_id']} -> {output}", flush=True)
    result = {"run": run, "output": str(output), "status": "failed", "started": utc_now()}
    server_proc = None
    server_log = None
    perf = None
    old_affinity = os.sched_getaffinity(0)
    start_time = time.monotonic()
    max_s = min(int(cfg["limits"]["run_timeout_s"]), 1680)
    try:
        if stopped():
            raise InterruptedError("Stopped before run start")
        check_port_available(int(cfg["host_port"]))
        signal.setitimer(signal.ITIMER_REAL, max_s)
        os.sched_setaffinity(0, caps["reserved"])
        # Record storage continuously during potentially long model downloads.
        if free_bytes(data_dir) < cfg["measurement"]["storage_min_free_gib"] * 1024**3:
            raise RuntimeError("Cache disk below storage_min_free_gib before container start")
        server_log = (output / "server.log").open("w", encoding="utf-8", buffering=1)
        server_proc = subprocess.Popen(cmd, stdout=server_log, stderr=subprocess.STDOUT,
                                       text=True, start_new_session=True)
        atomic_json(STATE / "active_run.json", {"container": name, "output": str(output),
                                                    "model": run["model"], "pid": os.getpid()})
        from .common import csv_writer
        sf, sw = csv_writer(output / "startup_storage.csv", ["timestamp_utc", "free_gib", "elapsed_s"])
        try:
            deadline = time.monotonic() + min(int(cfg["limits"]["server_ready_timeout_s"]), max_s - 60)
            while time.monotonic() < deadline:
                if stopped():
                    raise InterruptedError("Stopped during model startup")
                if server_proc.poll() is not None:
                    raise RuntimeError(f"vLLM Docker process exited ({server_proc.returncode}); inspect server.log")
                free = free_bytes(data_dir)
                sw.writerow({"timestamp_utc": utc_now(), "free_gib": free / 1024**3,
                             "elapsed_s": time.monotonic() - start_time})
                if free / 1024**3 < cfg["measurement"]["storage_min_free_gib"]:
                    raise RuntimeError("Model download aborted: disk space below safety threshold")
                if execute(["curl", "--max-time", "2", "-fsS", base_url + "/health"], timeout=4).returncode == 0:
                    break
                time.sleep(5)
            else:
                raise RuntimeError("vLLM did not become healthy within server_ready_timeout_s; see server.log")
        finally:
            sf.close()
        # Health may be ready before API model registration finishes. Verify /v1/models.
        version = execute(["curl", "--max-time", "5", "-fsS", base_url + "/v1/models"], timeout=7)
        if version.returncode != 0:
            raise RuntimeError("API /v1/models failed after health became ready")
        atomic_json(output / "served_models.json", json.loads(version.stdout))
        if cfg["measurement"].get("require_perf", True):
            perf = PerfCollector(output, node, caps["infer"], setup["perf"]["perf_prefix"],
                                 interval_ms=int(cfg["measurement"]["perf_interval_ms"]),
                                 cas_bytes=int(cfg["measurement"].get("memory_cas_bytes", 64)))
            perf.start()
        # Warmup + data collection; background disk and vLLM metrics poll at independent cadences.
        times = cfg["measurement"]
        summary = asyncio.run(run_measurement(base_url, run["model"], output, data_dir,
                     concurrency=int(run["concurrency"]), output_tokens=int(run["output_tokens"]),
                     prompt_tokens=int(times["prompt_tokens"]), duration_s=int(times["duration_s"]),
                     drain_s=int(times["drain_s"]), request_timeout_s=int(times["request_timeout_s"]),
                     warmup_requests=int(times["warmup_requests"]),
                     warmup_output_tokens=int(times["warmup_output_tokens"]),
                     metrics_interval_s=float(times["metrics_interval_s"]),
                     storage_interval_s=float(times["storage_interval_s"]),
                     storage_min_free_gib=float(times["storage_min_free_gib"]), stopped=stopped))
        result.update({"status": "done", "summary": summary})
    except (InterruptedError, KeyboardInterrupt):
        result.update({"status": "interrupted", "error": "Stopped by user"})
    except BaseException as exc:
        result.update({"status": "timeout" if isinstance(exc, RunTimeout) else "failed",
                       "error": str(exc), "traceback": traceback.format_exc()})
        print(f"RUN FAILED: {run['model']} / {run['config_id']}: {exc}", flush=True)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        if perf:
            try:
                perf.stop()
                result["perf"] = perf.info()
            except Exception as exc:
                result["perf_error"] = str(exc)
        if server_proc:
            try:
                stop_container(name, int(cfg["limits"]["server_stop_timeout_s"]))
            except Exception as exc:
                result["container_cleanup_error"] = str(exc)
            try:
                server_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_proc.kill()
        if server_log:
            server_log.close()
        try:
            os.sched_setaffinity(0, old_affinity)
        except OSError:
            pass
        result["end"] = utc_now()
        result["total_elapsed_s"] = time.monotonic() - start_time
        atomic_json(output / "summary.json", result)
        active = read_json(STATE / "active_run.json")
        if active and active.get("container") == name:
            (STATE / "active_run.json").unlink(missing_ok=True)
        print(f"[{utc_now()}] {result['status'].upper()}: {run['model']} {run['config_id']} "
              f"({result['total_elapsed_s']:.1f}s)", flush=True)
    return result


def main():
    signal.signal(signal.SIGINT, _on_signal)
    signal.signal(signal.SIGTERM, _on_signal)
    signal.signal(signal.SIGALRM, _on_signal)
    plan = read_json(STATE / "plan.json")
    setup = read_json(STATE / "setup.json")
    if not plan or not setup:
        raise RuntimeError("Missing setup.json / plan.json; run setup.sh and experiment.sh start")
    if not Path(setup["data_root"]).exists():
        raise RuntimeError("Configured cache path no longer mounted; refusing to download onto root")
    progress = read_json(STATE / "progress.json", {"plan_id": plan["plan_id"], "runs": {}})
    if progress["plan_id"] != plan["plan_id"]:
        raise RuntimeError("Plan/progress mismatch; refusing to resume stale experiments")
    for idx, run in enumerate(plan["runs"]):
        if stopped():
            break
        key = run["model"] + "|" + run["config_id"]
        if progress["runs"].get(key, {}).get("status") == "done":
            continue
        try:
            result = run_one(idx, run, plan, setup)
        except BaseException as exc:
            result = {"status": "failed", "error": str(exc), "run": run}
        progress["runs"][key] = result
        atomic_json(STATE / "progress.json", progress)
        if result["status"] == "interrupted":
            break
    print(f"[{utc_now()}] Controller finished; status via ./experiment.sh status", flush=True)
    (STATE / "controller.json").unlink(missing_ok=True)


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        traceback.print_exc()
        sys.exit(1)
