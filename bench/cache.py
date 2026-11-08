"""Size tracking and guarded eviction for this benchmark's private HF cache.

Polling is not a hard filesystem quota: for strict byte limits use a filesystem
quota. The guard leaves write-burst headroom and stops an oversized container.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
import os
from pathlib import Path
import shutil
import stat
import threading
from collections.abc import Callable

GIB = 1024 ** 3


def parse_cache_limit(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        n = Decimal(value)
    except (InvalidOperation, TypeError) as exc:
        raise ValueError("MAX_HF_CACHE_SIZE_GB must be a finite positive number") from exc
    if not n.is_finite() or n <= 0 or int(n * GIB) < 1:
        raise ValueError("MAX_HF_CACHE_SIZE_GB must be a finite positive number")
    return int(n * GIB)


def cache_size_bytes(path: Path) -> int:
    """Count allocated blocks, deduplicating hardlinks, without following symlinks."""
    if not path.exists():
        return 0
    pending = [path]
    seen = set()
    total = 0
    while pending:
        item = pending.pop()
        try:
            st = item.lstat()
        except FileNotFoundError:
            continue
        key = (st.st_dev, st.st_ino)
        if key in seen:
            continue
        seen.add(key)
        total += st.st_blocks * 512
        if stat.S_ISDIR(st.st_mode):
            try:
                with os.scandir(item) as entries:
                    pending.extend(Path(entry.path) for entry in entries)
            except FileNotFoundError:
                continue
    return total


def model_cache_name(model_id: str) -> str:
    if model_id.count("/") != 1:
        raise ValueError(f"Expected owner/repo model ID: {model_id!r}")
    owner, repo = model_id.split("/", 1)
    if not owner or not repo or any(x in (".", "..") for x in (owner, repo)):
        raise ValueError(f"Unsafe model ID {model_id!r}")
    return f"models--{owner}--{repo}"


def _remove_repo(hf_home: Path, name: str) -> None:
    for item in (hf_home / "hub" / name, hf_home / "hub" / ".locks" / name):
        if item.is_symlink():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)
        elif item.exists():
            item.unlink()


def evict_other_models(hf_home: Path, active_model: str | None) -> dict:
    keep = model_cache_name(active_model) if active_model else None
    before = cache_size_bytes(hf_home)
    hub = hf_home / "hub"
    removed = []
    if hub.exists():
        for item in sorted(hub.iterdir()):
            if item.name.startswith("models--") and item.name != keep:
                _remove_repo(hf_home, item.name)
                removed.append(item.name)
    return {"before_bytes": before, "after_bytes": cache_size_bytes(hf_home),
            "removed_repositories": removed}


def evict_active_model(hf_home: Path, active_model: str) -> dict:
    before = cache_size_bytes(hf_home)
    _remove_repo(hf_home, model_cache_name(active_model))
    if (hf_home / "xet").is_dir():
        shutil.rmtree(hf_home / "xet")
    return {"before_bytes": before, "after_bytes": cache_size_bytes(hf_home),
            "removed_model": active_model}


def guard_threshold_bytes(limit: int) -> int:
    if limit <= 0:
        raise ValueError("Cache limit must be positive")
    reserve = min(limit // 4, max(128 * 1024**2, min(GIB, int(limit * .05))))
    return limit - reserve


class CacheQuotaGuard:
    def __init__(self, hf_home: Path, limit: int, on_violation: Callable[[], None],
                 interval_s: float = .25):
        self.hf_home = hf_home
        self.limit = limit
        self.threshold = guard_threshold_bytes(limit)
        self.on_violation = on_violation
        self.interval_s = interval_s
        self.error: str | None = None
        self.last_bytes = 0
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._watch, daemon=True, name="hf-cache-budget")

    def start(self):
        self.last_bytes = cache_size_bytes(self.hf_home)
        if self.last_bytes >= self.threshold:
            raise RuntimeError(f"HF cache already uses {self.last_bytes / GIB:.2f} GiB; "
                               f"too close to MAX_HF_CACHE_SIZE_GB={self.limit / GIB:g}. "
                               "Raise cap or clear benchmark private cache.")
        self._thread.start()

    def _watch(self):
        while not self._stop.is_set():
            try:
                self.last_bytes = cache_size_bytes(self.hf_home)
                if self.last_bytes >= self.threshold:
                    self.error = (f"HF cache approached MAX_HF_CACHE_SIZE_GB: "
                                  f"{self.last_bytes / GIB:.2f} / {self.limit / GIB:g} GiB")
                    self.on_violation()
                    return
            except Exception as exc:
                if not self.error:
                    self.error = f"Cannot monitor Hugging Face cache: {exc}"
                try:
                    self.on_violation()
                except Exception:
                    pass
                return
            self._stop.wait(self.interval_s)

    def stop(self):
        self._stop.set()
        if self._thread.is_alive():
            self._thread.join(timeout=3)
