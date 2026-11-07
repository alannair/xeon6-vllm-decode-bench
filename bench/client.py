"""Closed-loop concurrent streaming OpenAI completions with true token-id accounting."""
from __future__ import annotations

import asyncio
from collections import Counter
import json
import math
from pathlib import Path
import statistics
import time
from urllib.parse import quote

import aiohttp

from .common import csv_writer, utc_now

REQUEST_COLUMNS = ["request_id", "client_id", "start_utc", "end_utc", "start_ns_monotonic", "end_ns_monotonic",
                   "ttft_s", "mean_tpot_s", "latency_s", "output_tokens", "target_output_tokens",
                   "complete", "finish_reason", "prompt_tokens", "chunk_count", "max_tokens_in_chunk",
                   "http_status", "error", "usage_output_tokens", "tokens_within_window"]
TOKEN_COLUMNS = ["request_id", "client_id", "token_index", "token_id", "time_utc", "receive_ns_monotonic",
                 "time_since_request_s", "time_since_previous_chunk_s", "chunk_index", "tokens_in_chunk", "index_in_chunk"]
METRICS_COLUMNS = ["timestamp_utc", "metric", "labels", "value"]
METRICS_SELECTED = ["timestamp_utc", "num_requests_running", "num_requests_waiting", "num_requests_swapped",
                    "kv_cache_usage_perc", "generation_tokens_total", "prompt_tokens_total", "scrape_error"]
STORAGE_COLUMNS = ["timestamp_utc", "free_gib", "used_gib", "total_gib", "threshold_gib"]


def percentile(values, q: float):
    if not values:
        return None
    items = sorted(values)
    pos = (len(items) - 1) * q
    i = int(pos)
    return items[i] + (items[min(len(items) - 1, i + 1)] - items[i]) * (pos - i)


def metric_lines(text: str):
    """Yield (metric name, JSON labels, value) for Prometheus text format."""
    import re
    p = re.compile(r'^([^\s{]+)(\{.*?\})?\s+([-+\d.eE]+)(?:\s+.*)?$')
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        m = p.match(line)
        if not m:
            continue
        try:
            yield m.group(1), m.group(2) or "", float(m.group(3))
        except ValueError:
            continue


async def prepare_prompt(session: aiohttp.ClientSession, url: str, model: str, n: int) -> list[int]:
    """Use server tokenizer; submit exactly n model token IDs, not word-count guesses."""
    base = ("The measured experiment examines numerical reasoning and server performance "
            "in controlled conditions. Continue this neutral laboratory note with details. ")
    async with session.post(url + "/tokenize", json={"model": model, "prompt": base * max(2, n // 10)}) as response:
        body = await response.text()
        if response.status != 200:
            raise RuntimeError(f"/tokenize returned {response.status}: {body[:300]}")
        result = json.loads(body)
    tokens = result.get("tokens", result.get("token_ids"))
    if not isinstance(tokens, list) or len(tokens) < n or not all(isinstance(x, int) for x in tokens[:n]):
        raise RuntimeError(f"Unexpected /tokenize response: keys={list(result)}; tokens={str(tokens)[:80]}")
    return tokens[:n]


async def do_stream(session: aiohttp.ClientSession, url: str, model: str, token_prompt: list[int],
                    out_tokens: int, request_id: str, client_id: int, req_writer, token_writer,
                    *, warmup: bool = False, request_timeout_s: float = 900, on_record=None,
                    measurement_deadline_ns: int | None = None) -> dict:
    start_wall = utc_now()
    start = time.perf_counter_ns()
    count = 0
    within_window = 0
    times = []
    chunks = 0
    max_chunk = 0
    status = 0
    finish_reason = None
    output_usage = None
    error = ""
    normal_end = False
    payload = {"model": model, "prompt": token_prompt, "max_tokens": out_tokens,
               "min_tokens": out_tokens, "ignore_eos": True, "temperature": 0,
               "return_token_ids": True, "stream": True, "stream_options": {"include_usage": True},
               "seed": 42}
    try:
        async with session.post(url + "/v1/completions", json=payload,
                                timeout=aiohttp.ClientTimeout(total=request_timeout_s)) as response:
            status = response.status
            if status != 200:
                raise RuntimeError(f"HTTP {status}: {(await response.text())[:300]}")
            async for raw_line in response.content:
                # aiohttp iterates complete lines; one SSE event may contain >1 model token.
                if not raw_line.startswith(b"data:"):
                    continue
                stamp = time.perf_counter_ns()
                value = raw_line[5:].strip()
                if value == b"[DONE]":
                    normal_end = True
                    break
                try:
                    event = json.loads(value)
                except json.JSONDecodeError as exc:
                    raise RuntimeError(f"Malformed SSE JSON: {value[:100]!r}") from exc
                usage = event.get("usage")
                if isinstance(usage, dict):
                    output_usage = usage.get("completion_tokens", output_usage)
                for choice in event.get("choices", []):
                    if choice.get("index", 0) != 0:
                        continue
                    if choice.get("finish_reason") is not None:
                        finish_reason = choice["finish_reason"]
                    ids = choice.get("token_ids")
                    if ids is None:
                        # Do not fabricate timings by treating text characters as tokens.
                        if choice.get("text"):
                            raise RuntimeError("Server did not return stream token_ids; upgrade vLLM CPU image")
                        continue
                    if not isinstance(ids, list):
                        raise RuntimeError("Invalid streamed token_ids")
                    if not ids:
                        continue
                    if measurement_deadline_ns is None or stamp <= measurement_deadline_ns:
                        within_window += len(ids)
                    chunks += 1
                    max_chunk = max(max_chunk, len(ids))
                    previous_chunk_ns = times[-1] if times else None
                    for j, token_id in enumerate(ids):
                        count += 1
                        times.append(stamp)
                        if not warmup:
                            token_writer.writerow({"request_id": request_id, "client_id": client_id,
                                                  "token_index": count, "token_id": token_id,
                                                  "time_utc": utc_now(), "receive_ns_monotonic": stamp,
                                                  "time_since_request_s": (stamp - start) / 1e9,
                                                  "time_since_previous_chunk_s":
                                                  (stamp - previous_chunk_ns) / 1e9 if j == 0 and previous_chunk_ns else "",
                                                  "chunk_index": chunks, "tokens_in_chunk": len(ids),
                                                  "index_in_chunk": j})
    except asyncio.CancelledError:
        error = "cancelled_at_measurement_deadline"
        raise
    except Exception as exc:
        error = str(exc)
    finally:
        end = time.perf_counter_ns()
        # The mean inter-token interval only has meaning with >=2 received tokens.
        tpot = (times[-1] - times[0]) / 1e9 / (len(times) - 1) if len(times) >= 2 else None
        done = normal_end and not error and count == out_tokens
        record = {"request_id": request_id, "client_id": client_id, "start_utc": start_wall,
                  "end_utc": utc_now(), "start_ns_monotonic": start, "end_ns_monotonic": end,
                  "ttft_s": (times[0] - start) / 1e9 if times else None,
                  "mean_tpot_s": tpot, "latency_s": (end - start) / 1e9,
                  "output_tokens": count, "target_output_tokens": out_tokens,
                  "complete": int(done), "finish_reason": finish_reason, "prompt_tokens": len(token_prompt),
                  "chunk_count": chunks, "max_tokens_in_chunk": max_chunk,
                  "http_status": status, "error": error, "usage_output_tokens": output_usage,
                  "tokens_within_window": within_window}
        if not warmup:
            req_writer.writerow(record)
            if on_record is not None:
                on_record(record)
    return record


async def poll_metrics(session, base_url: str, interval: float, out_dir: Path, stop: asyncio.Event):
    all_file, all_writer = csv_writer(out_dir / "metrics_long.csv", METRICS_COLUMNS)
    summary_file, summary_writer = csv_writer(out_dir / "metrics.csv", METRICS_SELECTED)
    try:
        while not stop.is_set():
            timestamp = utc_now()
            sample = {"timestamp_utc": timestamp}
            try:
                async with session.get(base_url + "/metrics", timeout=aiohttp.ClientTimeout(total=4)) as response:
                    body = await response.text()
                    if response.status != 200:
                        raise RuntimeError(f"HTTP {response.status}")
                # Keep every time series with labels, plus normalized time-series of scheduler queues.
                totals = {}
                for name, labels, value in metric_lines(body):
                    if name.startswith("vllm:"):
                        all_writer.writerow({"timestamp_utc": timestamp, "metric": name,
                                            "labels": labels, "value": value})
                        totals[name] = totals.get(name, 0.0) + value
                mapping = {"num_requests_running": "vllm:num_requests_running",
                           "num_requests_waiting": "vllm:num_requests_waiting",
                           "num_requests_swapped": "vllm:num_requests_swapped",
                           "kv_cache_usage_perc": "vllm:kv_cache_usage_perc",
                           "generation_tokens_total": "vllm:generation_tokens_total",
                           "prompt_tokens_total": "vllm:prompt_tokens_total"}
                sample.update({key: totals.get(name, "") for key, name in mapping.items()})
            except Exception as exc:
                sample["scrape_error"] = str(exc)
            summary_writer.writerow(sample)
            try:
                await asyncio.wait_for(stop.wait(), timeout=interval)
            except asyncio.TimeoutError:
                pass
    finally:
        all_file.close()
        summary_file.close()


async def poll_storage(data_dir: Path, interval: float, threshold_gib: float,
                       out_dir: Path, stop: asyncio.Event, failures: list[str]):
    import shutil
    f, writer = csv_writer(out_dir / "storage.csv", STORAGE_COLUMNS)
    try:
        while not stop.is_set():
            stats = shutil.disk_usage(data_dir)
            free_gib = stats.free / 1024**3
            writer.writerow({"timestamp_utc": utc_now(), "free_gib": free_gib,
                             "used_gib": stats.used / 1024**3, "total_gib": stats.total / 1024**3,
                             "threshold_gib": threshold_gib})
            if free_gib < threshold_gib:
                failures.append(f"Low storage: {free_gib:.1f} GiB free on {data_dir}")
                stop.set()
                return
            try:
                await asyncio.wait_for(stop.wait(), timeout=interval)
            except asyncio.TimeoutError:
                pass
    finally:
        f.close()


async def run_measurement(base_url: str, model: str, out_dir: Path, data_dir: Path,
                          *, concurrency: int, output_tokens: int, prompt_tokens: int,
                          duration_s: int, drain_s: int, request_timeout_s: int,
                          warmup_requests: int, warmup_output_tokens: int,
                          metrics_interval_s: float, storage_interval_s: float,
                          storage_min_free_gib: float, stopped) -> dict:
    request_file, request_writer = csv_writer(out_dir / "requests.csv", REQUEST_COLUMNS)
    token_file, token_writer = csv_writer(out_dir / "token_events.csv", TOKEN_COLUMNS, buffering=256*1024)
    phase_file, phase_writer = csv_writer(out_dir / "phases.csv", ["timestamp_utc", "monotonic_ns", "phase"])
    def mark(phase):
        phase_writer.writerow({"timestamp_utc": utc_now(), "monotonic_ns": time.perf_counter_ns(), "phase": phase})
        phase_file.flush()
    samples = []
    stop_polling = asyncio.Event()
    failures: list[str] = []
    limit = aiohttp.TCPConnector(limit=concurrency + 8, limit_per_host=0)
    timeout = aiohttp.ClientTimeout(total=None, sock_connect=10)
    started = 0
    async with aiohttp.ClientSession(timeout=timeout, connector=limit) as session:
        try:
            prompt_ids = await prepare_prompt(session, base_url, model, prompt_tokens)
            (out_dir / "prompt_token_ids.json").write_text(json.dumps(prompt_ids))
            mark("warmup_start")
            for idx in range(warmup_requests):
                result = await do_stream(session, base_url, model, prompt_ids, warmup_output_tokens,
                                         f"warmup-{idx}", idx, request_writer, token_writer,
                                         warmup=True, request_timeout_s=min(60, request_timeout_s))
                if not result["complete"]:
                    raise RuntimeError("Warmup failed: " + str(result["error"] or result["finish_reason"]))
            mark("warmup_end")
            metric_task = asyncio.create_task(poll_metrics(session, base_url, metrics_interval_s, out_dir, stop_polling))
            storage_task = asyncio.create_task(poll_storage(data_dir, storage_interval_s,
                                                             storage_min_free_gib, out_dir, stop_polling, failures))
            mark("measurement_start")
            start = time.perf_counter()
            end = start + duration_s
            deadline_ns = time.perf_counter_ns() + int(duration_s * 1e9)

            async def worker(client_id: int):
                nonlocal started
                while time.perf_counter() < end and not stopped() and not failures:
                    started += 1
                    request_id = f"client{client_id:03d}-request{started:07d}"
                    # Mutate the last few tokens to prevent 100% prompt reuse from dominating TTFT.
                    ids = prompt_ids.copy()
                    if len(ids) >= 4:
                        ids[-1] = prompt_ids[-1 - (started % 3)]
                    result = await do_stream(session, base_url, model, ids, output_tokens,
                                             request_id, client_id, request_writer, token_writer,
                                             request_timeout_s=request_timeout_s, on_record=samples.append,
                                             measurement_deadline_ns=deadline_ns)
                    if result["error"] and "HTTP " in result["error"]:
                        # Preserve errors but don't storm a failed server.
                        await asyncio.sleep(0.5)
            tasks = [asyncio.create_task(worker(i)) for i in range(concurrency)]
            try:
                while time.perf_counter() < end and not stopped() and not failures:
                    await asyncio.sleep(0.2)
                mark("measurement_window_end")
                remaining = max(0, end + drain_s - time.perf_counter())
                if remaining:
                    done, pending = await asyncio.wait(tasks, timeout=remaining)
                else:
                    pending = set(t for t in tasks if not t.done())
                for task in pending:
                    task.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)
            finally:
                mark("drain_end")
                stop_polling.set()
                await asyncio.gather(metric_task, storage_task, return_exceptions=True)
            seconds = time.perf_counter() - start
            if failures:
                raise RuntimeError("; ".join(failures))
            if stopped():
                raise InterruptedError("Stopped by user")
        finally:
            request_file.close()
            token_file.close()
            phase_file.close()
    completed = [s for s in samples if s["complete"]]
    observed = sum(s["tokens_within_window"] for s in samples)
    total_observed = sum(s["output_tokens"] for s in samples)
    ttfts = [s["ttft_s"] for s in completed if s["ttft_s"] is not None]
    tpots = [s["mean_tpot_s"] for s in completed if s["mean_tpot_s"] is not None]
    observed_ttfts = [s["ttft_s"] for s in samples if s["ttft_s"] is not None]
    observed_tpots = [s["mean_tpot_s"] for s in samples if s["mean_tpot_s"] is not None]
    # Throughput denominator is the actual measurement window, not (window + cancellation drain).
    measured_s = min(seconds, duration_s)
    return {"started_requests": started, "finished_request_records": len(samples),
            "complete_requests": len(completed), "failed_or_truncated_requests": len(samples) - len(completed),
            "observed_output_tokens": observed, "observed_output_tokens_including_drain": total_observed,
            "measurement_window_s": measured_s,
            "delivered_tokens_per_s": observed / measured_s if measured_s else None,
            "ttft_median_s": statistics.median(ttfts) if ttfts else None,
            "ttft_p25_s": percentile(ttfts, .25), "ttft_p75_s": percentile(ttfts, .75),
            "ttft_p90_s": percentile(ttfts, .90), "ttft_p99_s": percentile(ttfts, .99),
            "ttft_max_s": max(ttfts) if ttfts else None,
            "ttft_observed_median_s": percentile(observed_ttfts, .50),
            "mean_tpot_median_s": statistics.median(tpots) if tpots else None,
            "mean_tpot_p25_s": percentile(tpots, .25), "mean_tpot_p75_s": percentile(tpots, .75),
            "mean_tpot_p90_s": percentile(tpots, .90), "mean_tpot_p99_s": percentile(tpots, .99),
            "mean_tpot_max_s": max(tpots) if tpots else None,
            "mean_tpot_observed_median_s": percentile(observed_tpots, .50),
            "client_streaming_overhead": "TTFT includes HTTP/scheduling/client transport",
            "tpot_definition": "(last observed token timestamp - first observed token timestamp)/(N-1)"}
