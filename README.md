# Xeon 6 vLLM CPU decode benchmark

A reproducible, host-initiated benchmark of **vLLM on Intel Xeon 6 / Granite Rapids**, with Intel Xeon 6 model recipes, single-NUMA-node execution, closed-loop streaming clients, per-token timing, periodic vLLM `/metrics`, and 100 ms `perf` counter time series. Each individual run has a hard **28-minute watchdog (with cleanup budget under 30 minutes)** including model download, server launch, measurement, and cleanup.

> **Validation note:** The Python controller, fake SSE client, sweep planner and parsers have unit/integration tests. Actual Xeon 6 AMX behaviour and platform IMC PMUs **must be verified on the target host**: this repository cannot simulate instruction execution or uncore PMU availability.

## Quick start

```bash
unzip xeon6-vllm-decode-bench.zip
cd xeon6-vllm-decode-bench
./setup.sh
./experiment.sh start
./experiment.sh status
./experiment.sh stop
./experiment.sh resume
./experiment.sh report
```

`start` creates a *new* saved plan and runs in the background. `stop` terminates the controller and its owned vLLM Docker container, without stopping unrelated containers. `resume` retries all unfinished/failed runs while skipping successful runs. It does not overwrite attempts.

**Small first run:**

```bash
./setup.sh
./experiment.sh plan --models 'Qwen/Qwen3-1.7B' --max-runs 3
./experiment.sh start --models 'Qwen/Qwen3-1.7B' --max-runs 3
# Follow the controller logfile shown at startup, then:
./experiment.sh report
```

If you have only remote SSH access, use `./experiment.sh start` (background mode) rather than `--foreground`, so the controller survives SSH disconnection.

### Prerequisites

- Linux **x86_64**, Python >= 3.10, a supported `apt`/`dnf`/`yum` environment and privileges to install packages and use Docker.
- Xeon 6 with AMX_TILE, AMX_BF16, AMX_INT8 and AVX-512 enabled in BIOS/OS for optimum performance. Setup records which flags are actually available; missing flags trigger a warning rather than a made-up AMX claim.
- A **writable data filesystem with at least 100 GiB free by default**, selected automatically from `/data`, `/data2`, `/scratch` and other real mounts by most available space. Or explicitly set `BENCH_DATA_DIR=/your/large/partition ./setup.sh`; an override can select a large root filesystem if intended. Setup fails instead of silently using `/` when no suitable disk is present. Set `MAX_HF_CACHE_SIZE_GB` before setup to allow smaller-than-100-GiB disks (subject to free-space safety thresholds).
- ~32 GiB+ of physical memory on the selected NUMA node for small models, significantly more for 8B or 9B, depending on quantization and KV-cache allocation. The script reports NUMA memory size.
- Working Docker daemon; **at least 10 GiB free in Docker's image-layer storage (larger CPU images may require much more)**. Hugging Face weights, Torch, vLLM, temp, XDG caches and `./logs` (a symlink) are placed on the selected data partition, *not* the root filesystem. If Docker's own data-root is cramped, move it before setup.
- Permission for **system-wide `perf stat -a -C`** on the selected cores. Setup first tries unprivileged, then `sudo -n perf` and (with permission) tries `sysctl kernel.perf_event_paranoid=-1`. `perf` collection defaults to **required**; setup fails closed without at least cycles and instructions.
- Internet to pull the Docker image and download public models. Gated models, if enabled, may require `HF_TOKEN=...` in the environment. Token is passed to Docker without writing its value in config files.

Setup installs missing `docker`, `numactl`, `perf`, `lscpu`/`util-linux`, and `curl` packages (using sudo if required); downloads the official `vllm/vllm-openai-cpu:latest-x86_64` image; checks CPU topology, available counters, ISA flags and **oneDNN/MKLDNN availability inside the CPU Docker image**; creates a local `.venv` with the lightweight `aiohttp` benchmark client; and writes `state/setup.json`. No explicit pre-download of all model weights is attempted: weights download on the first relevant run to the dedicated cache volume. During server/model startup the controller samples **free storage every five seconds** and aborts if the safety threshold is crossed. Weight-cache contents persist across runs.

To reuse an already-pulled image (offline setup): `./setup.sh --no-pull`.

### Optional bounded Hugging Face cache on small filesystems

```bash
export MAX_HF_CACHE_SIZE_GB=30
export BENCH_DATA_DIR=/data  # optional override
./setup.sh
./experiment.sh start
```

The export is a positive number of **GiB** limiting the benchmark-owned Hugging Face cache, including model downloads and partial files. It is stored in `state/setup.json` so `resume` uses the same budget even when the shell variable is unset; exporting a different value requires re-running setup. With no cap, setup retains its >=100 GiB free-space default. With a cap, setup accepts smaller partitions subject to a safety floor. Only the private benchmark HF cache is counted: logs, Docker layers and other caches have separate disk usage.

Before model loading, other model repositories in the private HF cache are evicted to avoid accumulating weights across models. A frequent background watcher stops the owned Docker container when cache use approaches the cap and discards oversized partial weights after shutdown. Infeasible models are skipped on subsequent configurations, with errors recorded in each attempt. CSV files report HF cache usage.

**A polling watchdog is not a strict atomic disk quota**: a fast write can briefly exceed the limit. If the filesystem must *never* exceed the cap, use a dedicated size-limited filesystem or filesystem project quota for the private cache. Use `MAX_HF_CACHE_SIZE_GB` for best-effort bounded benchmarking, not as a substitute for a storage quota.

## Experimental design

Default workloads are **32 prompt tokens** (actual tokenizer token IDs), **BF16** unless the model weights are already quantized, and **exactly N generated tokens** (both `min_tokens=N` and `max_tokens=N`, plus `ignore_eos=true`). Sending token IDs instead of natural-language text avoids tokenizer variability. Uses `/v1/completions` with `stream=true`, `return_token_ids=true` and `stream_options.include_usage=true`; server-side usage is kept in CSV for validation. A request failing to generate exactly N tokens is recorded as truncated/failed and excluded from **complete-request** latency-percentile summaries; their observed partial TTFT/TPOT remain in raw CSV and separate observed-sample summaries.

| Variable | Baseline | Swept values (one parameter at a time) |
|---|---:|---|
| Concurrent closed-loop clients | 8 | 1, 2, 4, 8, 16, 32, 64, 128 |
| Physical inference cores | **96 (required)** | **24, 48, 72, 96** (exact CPU IDs `0..N-1`) |
| Output tokens/request | 512 | 128, 512, 2048 |
| Input tokens/request | 32 | fixed |
| Measurement duration | 90 s | fixed; up to 8 s drain then cancel unfinished |
| Wall time per run | <=1680 s | enforced, *including first-download/startup* |
| CPU and memory placement | **NUMA node 0 only** | server `--cpuset-cpus=0..N-1`, `--cpuset-mems=0`; controller `numactl --membind=0` |

Each server run uses **exactly N physical CPU IDs `0..N-1`**, with memory allocations confined to NUMA node 0. Setup and planning fail if all 96 baseline CPU IDs are not distinct physical cores available on NUMA node 0; the baseline is never silently reduced. The host-side controller uses node-0 memory and prefers up to two spare node-0 housekeeping cores outside the server CPU set; it shares those CPUs when no spare cores exist. SMT siblings are excluded. This is not a fully isolated bare-metal environment.

Default sweep plans are unique baseline + concurrency sweep + core sweep + output-token sweep, **not a Cartesian product**. Runs are sorted by model size. Example baseline config ID: `node0_cores096_clients008_gen0512`.

### Default models

Models are deliberately selected across sizes, with Xeon 6 recipes where supported by the vLLM CPU [recommended models page](https://docs.vllm.ai/en/latest/models/hardware_supported_models/cpu/#recommended-models):

| Parameters | Model | Deployment |
|---|---|---|
| 0.5B | `Qwen/Qwen2.5-0.5B-Instruct` | manual, sub-1B control |
| 1B | `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | Xeon6 recipe, INT8 W8A8 |
| 1.7B | `Qwen/Qwen3-1.7B` | Xeon6 recipe |
| 2B | `ibm-granite/granite-3.2-2b-instruct` | Xeon6 recipe |
| 3B | `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | Xeon6 recipe, INT8 W8A8 |
| 4B | `Qwen/Qwen3-4B` | Xeon6 recipe |
| 8B | `Qwen/Qwen3-8B` | Xeon6 recipe |
| 8B | `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | Xeon6 recipe, INT8 W8A8 |
| 9B | `zai-org/glm-4-9b-hf` | Xeon6 recipe, **disabled by default** (enable in JSON to test) |

vLLM maintains the recipes in the CPU image. For each recipe run the code invokes the **image-bundled** `tools/recipes/recipe_json_to_vllm_config.py --model ... --hardware xeon6 --detect-hardware`, saves its generated YAML+environment to the run folder, sources recipe environment variables, then starts `vllm serve`. It reapplies selected NUMA/OMP/KV options after sourcing the recipe. The 0.5B manual baseline uses the default CPU backend. Model support, exact recipe names, and instruction use vary with the moving `latest-x86_64` image; `setup.json` records the actual image SHA for reproducibility.

### Control the test

Edit `configs/default.json` to change the models, sweep values, `server.extra_args`, timeouts or instrumentation interval. Useful commands:

```bash
./experiment.sh plan                               # preview on this host
./experiment.sh start --max-runs 1                 # quickest possible real smoke test
./experiment.sh start --models '*Qwen3-4B*' --sweeps baseline,cores
./experiment.sh start --models '*w8a8*' --sweeps concurrency --numa-node 0
./experiment.sh start --foreground --max-runs 1    # see output directly
./experiment.sh stop
./experiment.sh resume
./experiment.sh status
./experiment.sh report
python3 -m unittest discover -s tests -v          # no Xeon, Docker or perf needed
```

`start` intentionally replaces the saved **plan**, not the existing attempt logs. If you change the JSON configuration, `start` begins a fresh plan; `resume` uses the old saved plan exactly.

**Image pinning for fair comparisons:** Change `image` in `configs/default.json` to a versioned image/digest and rerun setup; `latest` changes over time. For testing actual peak performance, compare recipe vs manual mode, BF16 vs INT8 W8A8, and 1/2/4/8/16+ cores, holding *all other parameters* constant. Recipe configs and actual Docker commands are saved for review.

## Outputs

Each run writes into:

```
logs/
  Qwen__Qwen3-4B/
    node0_cores096_clients008_gen0512/
      attempt-20261107T.../
        config.json                 # exact CPU/core placement, Docker command, image id, cache path
        recipe-config.yml / recipe-env.sh  # for recipe deployments
        served_models.json
        prompt_token_ids.json
        server.log                  # vLLM, oneDNN and deployment messages
        startup_storage.csv        # disk free during model load
        phases.csv                 # UTC + monotonic boundaries for warmup/measurement
        requests.csv               # per request TTFT, TPOT, elapsed, completion, token count
        token_events.csv           # every generated token ID and MONOTONIC receive time
        metrics.csv                # vLLM scheduler queue/running counts etc
        metrics_long.csv           # all vllm:* prometheus values/labels
        storage.csv                # free/used capacity, HF cache usage, cap
        perf_core.stderr.txt       # original raw perf output
        perf_uncore.stderr.txt     # if IMC events discovered
        perf_events.csv            # every counter event by 100 ms interval
        system.csv                 # per-interval cycles, instructions, IPC, L3 misses,
                                   # L3-stall, AMX-busy, socket IMC bandwidth
        summary.json               # success/error/status & statistical summaries
  controller-*.log
  results.csv                      # regenerated via `./experiment.sh report`
state/
  setup.json                       # preflight inventory and chosen cache partition
  hardware_inventory.json          # lscpu, numactl, kernel, perf version
  plan.json                        # one-factor plan, immutable during resume
  progress.json                    # atomic status by run; determines resume
```

Setup creates `./logs` as a symlink to the large-cache partition, so growing per-token trace files do not consume a small root filesystem. If an existing nonempty `./logs` is on root, setup refuses to overwrite it and tells you to move it safely. CSV files are append-only **within an attempt**; new attempts use a unique folder. Note that `results.csv` is an aggregated *derived* report and is regenerated by `report`.

### Definitions and caveats

- **TTFT:** client monotonic time of **first streamed token** minus request-start time, including HTTP/network/queue time. CPU host clients use loopback with Docker host networking.
- **TPOT per request:** `(last_token_timestamp - first_token_timestamp)/(observed_tokens - 1)`. This excludes initial TTFT. We save every event so you can calculate p25/p75/p90/p99 inter-token latency or compute your own per-step series. SSE events sometimes coalesce multiple generated token IDs: IDs in the *same* chunk get the **same receive timestamp** and the CSV flags chunk grouping. The client cannot reconstruct precise internal model-token timings when coalesced; TPOT is a streaming approximation.
- **Throughput:** actual streamed token IDs received **inside** the scheduled 90-second measurement window divided by the window duration; drain tokens are logged but excluded from this numerator.
- **Concurrency vs batch size:** the benchmark uses **concurrent closed-loop streaming clients**; vLLM's actual continuously batched server request count is recorded separately in `metrics.csv`, and may differ from the client count. At high concurrency, queueing and TPOT inflation are expected.
- **Counters:** Linux `perf stat` observes inference core-CPU aggregates; uncore bandwidth observes **selected socket memory controllers** rather than per-process or per-NUMA-node exact traffic. Workload NUMA isolation makes this a useful approximation on an otherwise idle socket, but if Granite Rapids SNC splits a socket into multiple NUMA nodes or other jobs share the socket, this is not exact local-request DRAM bandwidth. Inspect `perf` warnings and exclude contaminated hosts.
- **Granite Rapids SCH0/SCH1:** on newer kernels each IMC reports two scheduler CAS events. Code detects and sums `cas_count_read_sch0/sch1` and `cas_count_write_sch0/sch1`; on kernels exposing only legacy aliases it warns that bandwidth **may be a lower bound**, instead of silently pretending they cover both schedulers. 64 bytes per CAS is the estimate; unit is decimal GB/s.
- **L3 stall counter:** `cycle_activity.stalls_l3_miss` is microarchitectural, not a generic perf alias, and may be unavailable or counted differently. The source parser leaves unavailable fields empty. `exe.amx_busy` provides positive evidence of tile execution **only when available**; its absence never proves AMX was unused. Some counter sets multiplex; `core_running_pct_min` and `uncore_running_pct_min` record minimum reported running percentages to spot multiplexing. Source file always contains the full event names. Two independent `perf stat` processes (core and uncore) are approximately aligned to a common host wall-clock origin before 100 ms binning, subject to process-start jitter.
- **OneDNN / AMX / AVX verification:** ISA flags show hardware exposure, not executed instructions. Set `"one_dnn_verbose": 1` for a **short** run, then inspect `server.log` for oneDNN kernel dispatch/AMX ISA selection and `system.csv` for `amx_busy_cycles`; this can produce **large** logs and is off by default. Some vLLM CPU ops use native, PyTorch/oneDNN or specialized CPU kernels: not every kernel necessarily calls oneDNN or uses AMX.
- **Local DRAM latency:** `perf stat` alone **cannot reliably measure a local DRAM-load latency in ns**. `system.csv.local_dram_latency_ns` is **empty by design**, not zero. For sampled access/use latency, run the optional `perf mem` diagnostic described below; it uses PEBS and measures *use-latency including queueing*, not a pure memory-controller service time. For controller-side per-socket DDR read latency use Intel PCM `pcm-latency` as a **separate profiling pass** (avoid PMU contention with perf). Neither measure can be inferred from L3 stall cycles.
- **Model integrity:** if a repo ID isn't published for the exact pinned image/recipe snapshot, the controller stores the server error in `summary.json` and continues to subsequent runs. Edit `models[]` to disable or substitute unsupported IDs.

### Optional PEBS memory-latency diagnostic

Since `perf stat` cannot supply per-memory-load latency, there is an **opt-in** PEBS capture helper in `scripts/perf_mem_diagnostic.sh` for an already-running vLLM process. Do not run it during the benchmark unless you accept extra profiling overhead. It stores `perf.data` and a raw sample listing (`local weight` in cycles and data-source codes), which you can analyze with `perf mem report` to distinguish local and remote memory. This is designed to be a **separate experiment**, not a fabricated 100 ms latency column.

```
# Run in a second terminal while vLLM server runs; CPU list should match inference core IDs.
sudo bash scripts/perf_mem_diagnostic.sh 0-31 /data/pebs-granite-01 20
```

For pure controller-side DDR service latency, Intel PCM has a separate [`pcm-latency`](https://github.com/intel/pcm) utility. Note that it may use the same PMUs as `perf stat`; do **not** run concurrently and interpret the results as if independent.

## Known limitations and next validation steps

1. The repository is a **benchmark harness**, not a custom oneDNN-compiled vLLM image; it uses vLLM's official CPU distribution and its hardware recipes, avoiding divergent/forked kernels. Recipe-level dispatch and AMX need to be checked against your host/image.
2. A container's root filesystem layers still live at Docker's data-root, which setup checks separately; only models and large caches are bind-mounted to the large partition.
3. CPU and IMC event aliases are kernel + microarchitecture-specific; setup checks cycles/instructions, while missing optional events produce warnings. Check `perf_core.stderr.txt` and `perf_uncore.stderr.txt` after the first real run.
4. A 28-minute bound can cause a large model download to time out; weights already downloaded stay in cache so `resume` may succeed.
5. This benchmark is a *CPU-only host* client and measures streaming receive time. Internal kernel timings and per-token decode wall-clock execution can require vLLM tracing/patches for precision. Reuse the generated per-token and perf traces to correlate the phases yourself.

## Source and references

- [vLLM CPU installation](https://docs.vllm.ai/en/latest/getting_started/installation/cpu/)
- [Intel CPU / Xeon 6 model recipes](https://docs.vllm.ai/en/latest/models/hardware_supported_models/cpu/#recommended-models)
- [Intel PCM / `pcm-latency`](https://github.com/intel/pcm)
- [Linux `perf mem` documentation](https://manpages.debian.org/trixie-backports/linux-perf/perf-mem.1.en.html)
