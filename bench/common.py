"""Small dependency-free helpers for the benchmark controller."""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state"
LOGS = ROOT / "logs"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds")


def slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_.")


def atomic_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, sort_keys=True)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def read_json(path: Path, default=None):
    return json.loads(path.read_text()) if path.exists() else default


def csv_writer(path: Path, fields: list[str], buffering: int = 1):
    path.parent.mkdir(parents=True, exist_ok=True)
    f = path.open("a", newline="", encoding="utf-8", buffering=buffering)
    writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
    if path.stat().st_size == 0:
        writer.writeheader()
    return f, writer


def execute(args: list[str], *, timeout: float = 10, check: bool = False, **kwargs):
    return subprocess.run(args, text=True, capture_output=True, timeout=timeout, check=check, **kwargs)


def free_bytes(path: Path) -> int:
    s = os.statvfs(path)
    return s.f_bavail * s.f_frsize


def format_bytes(value: int | float) -> str:
    return f"{value / (1024 ** 3):.1f} GiB"


def plan_hash(data: dict) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:12]


def timestamp_id() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + f"-{time.time_ns() % 1000000:06d}"
