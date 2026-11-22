# status

Updated: 2026-11-22 05:18:24 UTC

## Current Phase

Status: Complete (100%). No-recipe experiment finished.
Controller PID: —. Start: —. Log: `—`.
Models without a Xeon 6 recipe, run in a random order (queue # in `NO_RECIPE_REPORT.md`). Sweeps: clients 1–128 at 96 cores, cores 24/48/72/96 at 8 clients, 512 generated tokens.

## Overall Progress

[██████████] 100% 220/220 runs done. Status counts: {'done': 220}.

## Completed Steps

- Queue #1 `01-ai/Yi-1.5-9B-Chat` (8.83B): all 11 runs done.
- Queue #2 `allenai/OLMo-2-1124-13B-Instruct` (13.72B): all 11 runs done.
- Queue #3 `Qwen/Qwen2.5-14B-Instruct` (14.77B): all 11 runs done.
- Queue #4 `HuggingFaceTB/SmolLM2-1.7B-Instruct` (1.71B): all 11 runs done.
- Queue #5 `Qwen/Qwen2.5-3B-Instruct` (3.09B): all 11 runs done.
- Queue #6 `allenai/OLMo-2-0325-32B-Instruct` (32.23B): all 11 runs done.
- Queue #7 `Qwen/Qwen2.5-1.5B-Instruct` (1.54B): all 11 runs done.
- Queue #8 `ibm-granite/granite-3.3-2b-instruct` (2.53B): all 11 runs done.
- Queue #9 `Qwen/Qwen3-30B-A3B-Instruct-2507` (30.53B): all 11 runs done.
- Queue #10 `HuggingFaceH4/zephyr-7b-beta` (7.24B): all 11 runs done.
- Queue #11 `Qwen/Qwen3-4B-Instruct-2507` (4.02B): all 11 runs done.
- Queue #12 `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B` (14.77B): all 11 runs done.
- Queue #13 `Qwen/Qwen3-0.6B` (0.75B): all 11 runs done.
- Queue #14 `microsoft/Phi-4-mini-instruct` (3.84B): all 11 runs done.
- Queue #15 `allenai/OLMo-2-1124-7B-Instruct` (7.30B): all 11 runs done.
- Queue #16 `ibm-granite/granite-3.3-8b-instruct` (8.17B): all 11 runs done.
- Queue #17 `Qwen/Qwen3-32B` (32.76B): all 11 runs done.
- Queue #18 `deepseek-ai/deepseek-coder-1.3b-instruct` (1.35B): all 11 runs done.
- Queue #19 `microsoft/phi-4` (14.66B): all 11 runs done.
- Queue #20 `Qwen/Qwen2.5-7B-Instruct` (7.62B): all 11 runs done.

## Remaining Steps

- 0 models still have unfinished runs, in queue order:

## Active Failures/Retries

- None.

## Implementation Plan

1. Run every no-recipe model through the baseline, concurrency, and core sweeps in the saved random queue order.
2. After each attempt, rewrite `NO_RECIPE_REPORT.md` with client TPOT, TTFT, throughput, and the server inter-token latency.
3. Resume unfinished runs after a controller exit (up to 5 passes), then move on rather than looping on a broken model.
4. Leave the controller running. Do not retry a run already marked done.

