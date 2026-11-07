"""100 ms perf stat CSV collection; uncore CAS accounting is socket-scoped.

Actual local DRAM *load latency* is not exposed by perf stat's generic counters.
The system CSV therefore deliberately leaves local_dram_latency_ns blank.
"""
from __future__ import annotations

from collections import defaultdict
import csv
import json
import math
import os
import signal
from pathlib import Path
import queue
import re
import subprocess
import threading
import time

from .common import csv_writer, execute, utc_now
from .topology import cpu_package, parse_cpu_list, cpulist

CORE_CANDIDATES = ["cycles", "instructions", "LLC-load-misses",
                   "cycle_activity.stalls_l3_miss", "exe.amx_busy"]
CORE_NAMES = {"cycles": "cycles", "instructions": "instructions",
              "LLC-load-misses": "llc_load_misses",
              "cycle_activity.stalls_l3_miss": "stalled_cycles_l3_miss",
              "exe.amx_busy": "amx_busy_cycles"}
CORE_FIELDS = ["cycles", "instructions", "llc_load_misses", "stalled_cycles_l3_miss", "amx_busy_cycles"]
SYSTEM_FIELDS = ["timestamp_utc", "perf_elapsed_s", "node", "socket", "cycles", "instructions", "ipc",
                 "llc_load_misses", "stalled_cycles_l3_miss", "l3_stall_fraction", "amx_busy_cycles",
                 "amx_busy_fraction", "dram_read_gbps", "dram_write_gbps", "dram_total_gbps",
                 "dram_read_cas", "dram_write_cas", "local_dram_latency_ns",
                 "core_running_pct_min", "uncore_running_pct_min", "notes"]
RAW_FIELDS = ["timestamp_utc", "stream", "perf_elapsed_s", "pmu_event", "kind",
              "value", "unit", "running_pct", "perf_line"]


def perf_cmd(prefix: list[str], cpus: list[int], events: list[str], seconds: float = 0.08) -> list[str]:
    return prefix + ["stat", "-a", "-C", cpulist(cpus), "-e", ",".join(events), "--", "sleep", str(seconds)]


def available_core_events(prefix: list[str], cpus: list[int]) -> tuple[list[str], dict[str, str]]:
    ok = []
    errors = {}
    for event in CORE_CANDIDATES:
        try:
            p = execute(perf_cmd(prefix, cpus[:1], [event]), timeout=6)
            if p.returncode == 0 and ("not supported" not in p.stderr.lower()):
                ok.append(event)
            else:
                errors[event] = (p.stderr or p.stdout)[-350:]
        except Exception as exc:
            errors[event] = str(exc)
    return ok, errors


def discover_uncore(socket: int) -> tuple[list[tuple[str, str]], list[str]]:
    """Returns (event expression, read/write) for all IMCs on selected socket.

    Newer GNR kernels expose two schedulers per channel. If only legacy aliases
    exist, mark read/write as undercount risk rather than silently doubling.
    """
    result = []
    warnings = []
    for pmu in sorted(Path("/sys/bus/event_source/devices").glob("uncore_imc_[0-9]*")):
        cpumask = pmu / "cpumask"
        if not cpumask.exists():
            continue
        try:
            rep = parse_cpu_list(cpumask.read_text())[0]
        except (ValueError, IndexError):
            continue
        if cpu_package(rep) != socket:
            continue
        events = pmu / "events"
        newer = all((events / f"cas_count_{op}_sch{sch}").exists()
                    for op in ("read", "write") for sch in (0, 1))
        if newer:
            for op in ("read", "write"):
                for sch in (0, 1):
                    name = f"cas_count_{op}_sch{sch}"
                    result.append((f"{pmu.name}/{name}/", op))
        elif (events / "cas_count_read").exists() and (events / "cas_count_write").exists():
            for op in ("read", "write"):
                result.append((f"{pmu.name}/cas_count_{op}/", op))
            warnings.append(f"{pmu.name}: legacy CAS aliases; may count only scheduler 0 on GNR. Bandwidth is a lower bound.")
        else:
            warnings.append(f"{pmu.name}: usable CAS aliases not found")
    if not result:
        warnings.append("No readable uncore IMC event aliases for selected socket; DRAM bandwidth unavailable")
    return result, warnings


def parse_perf_line(line: str, expected: dict[str, str]):
    """Parse perf's semicolon-delimited interval format (handles optional aggregate columns)."""
    values = line.strip().split(";")
    if len(values) < 4:
        return None
    try:
        elapsed = float(values[0].strip())
    except ValueError:
        return None
    event_index = -1
    matched = None
    for i, val in enumerate(values[1:], 1):
        candidate = val.strip().lower()
        for e in expected:
            if candidate == e.lower() or candidate.startswith(e.lower() + ":"):
                matched, event_index = e, i
                break
        if matched:
            break
    if not matched:
        return None
    try:
        # value;unit;event is perf's normal layout, regardless of optional CPU/socket prefix.
        numeric = values[event_index - 2].strip().replace(",", "")
        if not numeric or "not" in numeric.lower() or "nan" in numeric.lower():
            return None
        value = float(numeric)
    except (IndexError, ValueError):
        return None
    if not math.isfinite(value):
        return None
    unit = values[event_index - 1].strip() if event_index > 0 else ""
    pct = None
    # Interval format usually follows event with runtime and percentage.
    for x in values[event_index + 2:event_index + 4]:
        try:
            candidate = float(x.strip().rstrip("%"))
            if 0 <= candidate <= 100:
                pct = candidate
                break
        except ValueError:
            continue
    return elapsed, matched, value, unit, pct


class PerfCollector:
    def __init__(self, directory: Path, node: dict, selected_cpus: list[int],
                 prefix: list[str], interval_ms: int = 100, cas_bytes: int = 64):
        self.directory = directory
        self.node = node
        self.cpus = selected_cpus
        self.prefix = prefix
        self.interval_ms = interval_ms
        self.cas_bytes = cas_bytes
        self.procs: list[subprocess.Popen] = []
        self.threads: list[threading.Thread] = []
        self.events = queue.Queue()
        self.warnings: list[str] = []
        self.core_available: list[str] = []
        self.uncore_available: list[str] = []
        self.started_wall_ns = 0
        self.closed = False
        self.worker: threading.Thread | None = None

    def start(self):
        self.core_available, failures = available_core_events(self.prefix, self.cpus)
        for key, value in failures.items():
            self.warnings.append(f"Core event {key} unavailable: {value}")
        if not {"cycles", "instructions"}.issubset(self.core_available):
            raise RuntimeError("perf cannot collect both cycles and instructions on selected cores; "
                               "check privilege and perf_event_paranoid")
        imc, warnings = discover_uncore(self.node["socket"])
        self.warnings.extend(warnings)
        self.uncore_available = [x[0] for x in imc]
        self.started_wall_ns = time.time_ns()
        self.worker = threading.Thread(target=self._aggregate, daemon=True)
        self.worker.start()
        self._launch("core", self.cpus, [(x, CORE_NAMES[x]) for x in self.core_available])
        time.sleep(max(0.15, self.interval_ms / 1000))
        if self.procs[-1].poll() is not None:
            raise RuntimeError("Combined perf core stream failed to start; inspect perf_core.stderr.txt")
        if imc:
            # Uncore PMUs are per socket, and a single representative CPU can count them all.
            rep = self._socket_representative()
            self._launch("uncore", [rep], [(event, f"cas_{kind}") for event, kind in imc])
            time.sleep(max(0.15, self.interval_ms / 1000))
            if self.procs[-1].poll() is not None:
                self.warnings.append("Uncore perf stream exited at startup; check perf_uncore.stderr.txt; DRAM bandwidth unavailable")
                self.uncore_available = []

    def _socket_representative(self):
        for pmu in Path("/sys/bus/event_source/devices").glob("uncore_imc_[0-9]*"):
            p = pmu / "cpumask"
            if p.exists():
                try:
                    cpu = parse_cpu_list(p.read_text())[0]
                    if cpu_package(cpu) == self.node["socket"]:
                        return cpu
                except (ValueError, IndexError):
                    pass
        return self.cpus[0]

    def _launch(self, stream: str, cpus: list[int], events: list[tuple[str, str]]):
        expected = dict(events)
        cmd = self.prefix + ["stat", "-a", "-C", cpulist(cpus), "-I", str(self.interval_ms),
                             "-x", ";", "--no-big-num", "-e", ",".join(expected), "--", "sleep", "1800"]
        raw_log = (self.directory / f"perf_{stream}.stderr.txt").open("w", encoding="utf-8", buffering=1)
        try:
            # Relative perf elapsed clocks originate at different process starts.
            # Anchor each to the same host wall clock before 100ms binning.
            stream_origin_ns = time.time_ns()
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                                    text=True, bufsize=1, start_new_session=True)
        except Exception:
            raw_log.close()
            raise
        self.procs.append(proc)

        def reader():
            try:
                assert proc.stderr
                for line in proc.stderr:
                    raw_log.write(line)
                    parsed = parse_perf_line(line, expected)
                    if parsed:
                        elapsed, key, value, unit, pct = parsed
                        common_elapsed = elapsed + (stream_origin_ns - self.started_wall_ns) / 1e9
                        self.events.put((stream, common_elapsed, elapsed, key,
                                         expected[key], value, unit, pct, line.rstrip()))
            finally:
                raw_log.close()
        thread = threading.Thread(target=reader, daemon=True)
        thread.start()
        self.threads.append(thread)

    def _aggregate(self):
        rawf, raww = csv_writer(self.directory / "perf_events.csv", RAW_FIELDS)
        widef, widew = csv_writer(self.directory / "system.csv", SYSTEM_FIELDS)
        # Keep at least 3 intervals of events in flight to allow both perf processes to arrive.
        bins = defaultdict(lambda: {"core": defaultdict(float), "uncore": defaultdict(float),
                                    "core_pct": [], "uncore_pct": [], "t": 0.0})
        dumped = set()
        interval = self.interval_ms / 1000

        def flush(index):
            if index in dumped:
                return
            item = bins.pop(index, None)
            if not item:
                return
            dumped.add(index)
            c, u = item["core"], item["uncore"]
            duration = interval
            read = u.get("cas_read")
            write = u.get("cas_write")
            cycles = c.get("cycles")
            instructions = c.get("instructions")
            stall = c.get("stalled_cycles_l3_miss")
            amx = c.get("amx_busy_cycles")
            row = {"timestamp_utc": self._approx_time(item["t"]),
                   "perf_elapsed_s": round(item["t"], 6),
                   "node": self.node["node"], "socket": self.node["socket"],
                   "cycles": cycles, "instructions": instructions,
                   "ipc": instructions / cycles if cycles else "",
                   "llc_load_misses": c.get("llc_load_misses", ""),
                   "stalled_cycles_l3_miss": stall if stall is not None else "",
                   "l3_stall_fraction": stall / cycles if stall is not None and cycles else "",
                   "amx_busy_cycles": amx if amx is not None else "",
                   "amx_busy_fraction": amx / cycles if amx is not None and cycles else "",
                   "dram_read_cas": read if read is not None else "",
                   "dram_write_cas": write if write is not None else "",
                   "dram_read_gbps": read * self.cas_bytes / duration / 1e9 if read is not None else "",
                   "dram_write_gbps": write * self.cas_bytes / duration / 1e9 if write is not None else "",
                   "dram_total_gbps": ((read or 0) + (write or 0)) * self.cas_bytes / duration / 1e9
                   if read is not None and write is not None else "",
                   "local_dram_latency_ns": "",  # Needs PEBS or PCM; do not synthesize it.
                   "core_running_pct_min": min(item["core_pct"]) if item["core_pct"] else "",
                   "uncore_running_pct_min": min(item["uncore_pct"]) if item["uncore_pct"] else "",
                   "notes": "socket-wide IMC, including other workloads; not per-process"}
            widew.writerow(row)

        try:
            while not self.closed or not self.events.empty():
                try:
                    stream, elapsed, stream_elapsed, key, kind, value, unit, pct, line = self.events.get(timeout=0.08)
                    raww.writerow({"timestamp_utc": self._approx_time(elapsed), "stream": stream,
                                  "perf_elapsed_s": stream_elapsed, "pmu_event": key, "kind": kind,
                                  "value": value, "unit": unit, "running_pct": pct, "perf_line": line})
                    index = max(1, round(elapsed / interval))
                    if index not in dumped:
                        item = bins[index]
                        item[stream][kind] += value
                        item["t"] = max(item["t"], elapsed)
                        if pct is not None:
                            item[f"{stream}_pct"].append(pct)
                except queue.Empty:
                    pass
                # Flush older intervals after waiting ~0.35s; never retroactively modify CSV rows.
                now_elapsed = (time.time_ns() - self.started_wall_ns) / 1e9
                for i in sorted(list(bins)):
                    if self.closed or i * interval < now_elapsed - 0.4:
                        flush(i)
            for i in sorted(list(bins)):
                flush(i)
        finally:
            rawf.close()
            widef.close()

    def _approx_time(self, elapsed: float) -> str:
        import datetime as dt
        return dt.datetime.fromtimestamp(self.started_wall_ns / 1e9 + elapsed, dt.timezone.utc).isoformat(timespec="milliseconds")

    def stop(self):
        for p in self.procs:
            if p.poll() is None:
                os.killpg(p.pid, signal.SIGTERM)
        for p in self.procs:
            try:
                p.wait(timeout=3)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid, signal.SIGKILL)
        for t in self.threads:
            t.join(timeout=3)
        self.closed = True
        if self.worker:
            self.worker.join(timeout=4)

    def info(self):
        return {"core_events": self.core_available, "uncore_events": self.uncore_available,
                "warnings": self.warnings, "scope": "CPU cores and selected socket-wide IMCs",
                "cas_bytes": self.cas_bytes, "interval_ms": self.interval_ms,
                "bin_alignment": "perf process elapsed time anchored to host wallclock before Popen; approx. startup jitter"}
