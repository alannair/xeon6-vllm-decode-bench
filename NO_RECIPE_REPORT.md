# No-recipe vLLM decode report

Live notes for plan `5e2a9fe7a87a` on the Xeon 6972P node-0 benchmark. Updated 2026-11-22 05:18:24 UTC.

These are text models that have **no Xeon 6 recipe** on the vLLM CPU page ([recipes.vllm.ai](https://recipes.vllm.ai)); each one returns 404 for `/hw/xeon6.json`. They run through the manual `vllm serve` path (BF16, no recipe config), pinned with `numactl --physcpubind=0-(N-1) --membind=0` so every selected CPU carries one compute thread. The sweeps match `REPORT_PINNED.md`: concurrency 1, 2, 4, 8, 16, 32, 64, 128 at 96 cores, and cores 24, 48, 72, 96 at 8 clients, with 512 generated tokens. Models above 33B parameters are excluded. The queue is a random permutation (seed 20261121) so an interrupted run still covers small and large models.

## Snapshot

Controller is not running. Progress 220/220 runs, 20/20 models complete.

## Models and queue order

Listed by size. **Queue #** is the position in the random run order (1 runs first).

| Size (B) | Model | Queue # | Runs done | Status |
|---:|---|---:|---:|---|
| 0.75 | `Qwen/Qwen3-0.6B` | 13 | 11/11 | complete |
| 1.35 | `deepseek-ai/deepseek-coder-1.3b-instruct` | 18 | 11/11 | complete |
| 1.54 | `Qwen/Qwen2.5-1.5B-Instruct` | 7 | 11/11 | complete |
| 1.71 | `HuggingFaceTB/SmolLM2-1.7B-Instruct` | 4 | 11/11 | complete |
| 2.53 | `ibm-granite/granite-3.3-2b-instruct` | 8 | 11/11 | complete |
| 3.09 | `Qwen/Qwen2.5-3B-Instruct` | 5 | 11/11 | complete |
| 3.84 | `microsoft/Phi-4-mini-instruct` | 14 | 11/11 | complete |
| 4.02 | `Qwen/Qwen3-4B-Instruct-2507` | 11 | 11/11 | complete |
| 7.24 | `HuggingFaceH4/zephyr-7b-beta` | 10 | 11/11 | complete |
| 7.30 | `allenai/OLMo-2-1124-7B-Instruct` | 15 | 11/11 | complete |
| 7.62 | `Qwen/Qwen2.5-7B-Instruct` | 20 | 11/11 | complete |
| 8.17 | `ibm-granite/granite-3.3-8b-instruct` | 16 | 11/11 | complete |
| 8.83 | `01-ai/Yi-1.5-9B-Chat` | 1 | 11/11 | complete |
| 13.72 | `allenai/OLMo-2-1124-13B-Instruct` | 2 | 11/11 | complete |
| 14.66 | `microsoft/phi-4` | 19 | 11/11 | complete |
| 14.77 | `Qwen/Qwen2.5-14B-Instruct` | 3 | 11/11 | complete |
| 14.77 | `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B` | 12 | 11/11 | complete |
| 30.53 | `Qwen/Qwen3-30B-A3B-Instruct-2507` | 9 | 11/11 | complete |
| 32.23 | `allenai/OLMo-2-0325-32B-Instruct` | 6 | 11/11 | complete |
| 32.76 | `Qwen/Qwen3-32B` | 17 | 11/11 | complete |

## Results by model

Decode latency is client TPOT, `(last token time − first token time) / (tokens − 1)`, median over requests. The server series `vllm:inter_token_latency_seconds` agrees with it in the per-run table below. Baseline is 96 cores and 8 clients. Rows appear as soon as a model has finished points; `—` marks a point not finished yet.

| Size (B) | Model | Queue # | Baseline TPOT | Baseline TTFT | Baseline tok/s | 1 client TPOT | 128 clients TPOT | 128 clients TTFT | 128 clients tok/s | 24 cores TPOT |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.75 | `Qwen/Qwen3-0.6B` | 13 | 14.8 ms | 54.3 ms | 537.79 | 10.0 ms | 43.8 ms | 251.1 ms | 2894.26 | 13.8 ms |
| 1.35 | `deepseek-ai/deepseek-coder-1.3b-instruct` | 18 | 18.7 ms | 63.9 ms | 426.59 | 13.3 ms | 59.8 ms | 351.1 ms | 2127.66 | 20.4 ms |
| 1.54 | `Qwen/Qwen2.5-1.5B-Instruct` | 7 | 23.0 ms | 78.1 ms | 345.70 | 18.4 ms | 45.2 ms | 356.1 ms | 2794.70 | 23.1 ms |
| 1.71 | `HuggingFaceTB/SmolLM2-1.7B-Instruct` | 4 | 21.8 ms | 71.3 ms | 364.63 | 16.0 ms | 63.5 ms | 427.7 ms | 2019.58 | 24.6 ms |
| 2.53 | `ibm-granite/granite-3.3-2b-instruct` | 8 | 31.0 ms | 110.9 ms | 256.90 | 24.1 ms | 67.1 ms | 591.2 ms | 1892.32 | 34.0 ms |
| 3.09 | `Qwen/Qwen2.5-3B-Instruct` | 5 | 33.3 ms | 114.3 ms | 238.41 | 27.2 ms | 67.5 ms | 618.4 ms | 1861.70 | 38.4 ms |
| 3.84 | `microsoft/Phi-4-mini-instruct` | 14 | 34.1 ms | 125.0 ms | 233.34 | 31.8 ms | 86.9 ms | 725.8 ms | 1454.94 | 44.8 ms |
| 4.02 | `Qwen/Qwen3-4B-Instruct-2507` | 11 | 35.5 ms | 139.3 ms | 223.92 | 33.0 ms | 93.2 ms | 781.8 ms | 1369.62 | 48.3 ms |
| 7.24 | `HuggingFaceH4/zephyr-7b-beta` | 10 | 52.8 ms | 196.5 ms | 150.32 | 50.8 ms | 118.6 ms | 1153.4 ms | 1060.99 | 74.1 ms |
| 7.30 | `allenai/OLMo-2-1124-7B-Instruct` | 15 | 55.6 ms | 196.8 ms | 143.30 | 49.7 ms | 154.7 ms | 1223.8 ms | 736.74 | 76.5 ms |
| 7.62 | `Qwen/Qwen2.5-7B-Instruct` | 20 | 57.7 ms | 199.6 ms | 137.52 | 54.2 ms | 106.8 ms | 1123.5 ms | 1179.03 | 72.4 ms |
| 8.17 | `ibm-granite/granite-3.3-8b-instruct` | 16 | 62.1 ms | 231.8 ms | 128.10 | 58.4 ms | 145.9 ms | 1370.8 ms | 841.97 | 85.6 ms |
| 8.83 | `01-ai/Yi-1.5-9B-Chat` | 1 | 66.3 ms | 257.3 ms | 119.92 | 62.3 ms | 145.1 ms | 1488.0 ms | 859.14 | 90.6 ms |
| 13.72 | `allenai/OLMo-2-1124-13B-Instruct` | 2 | 96.1 ms | 313.1 ms | 83.12 | 88.1 ms | 247.0 ms | 2039.6 ms | 514.86 | 133.1 ms |
| 14.66 | `microsoft/phi-4` | 19 | 96.3 ms | 335.2 ms | 82.59 | 92.2 ms | 197.0 ms | 2107.4 ms | 638.59 | 135.4 ms |
| 14.77 | `Qwen/Qwen2.5-14B-Instruct` | 3 | 98.4 ms | 334.7 ms | 80.81 | 93.1 ms | 203.4 ms | 2117.2 ms | 618.70 | 136.9 ms |
| 14.77 | `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B` | 12 | 98.3 ms | 333.9 ms | 80.99 | 93.0 ms | 201.9 ms | 2072.9 ms | 624.37 | 136.8 ms |
| 30.53 | `Qwen/Qwen3-30B-A3B-Instruct-2507` | 9 | 55.2 ms | 276.4 ms | 143.92 | 34.9 ms | 114.0 ms | 970.1 ms | 1109.37 | 70.4 ms |
| 32.23 | `allenai/OLMo-2-0325-32B-Instruct` | 6 | 204.5 ms | 820.7 ms | 38.87 | 200.3 ms | 378.3 ms | 4548.3 ms | 322.88 | 292.4 ms |
| 32.76 | `Qwen/Qwen3-32B` | 17 | 203.8 ms | 784.1 ms | 38.94 | 199.3 ms | 374.3 ms | 4766.9 ms | 325.72 | 293.6 ms |

## Per-run results

| Size (B) | Model | Sweep | Cores | Clients | Server ITL mean | Client TPOT | Client TTFT | Tokens/s | Complete requests |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| 0.75 | `Qwen/Qwen3-0.6B` | baseline | 96 | 8 | 14.8 ms | 14.8 ms | 54.3 ms | 537.79 | 96 |
| 0.75 | `Qwen/Qwen3-0.6B` | concurrency | 96 | 1 | 10.0 ms | 10.0 ms | 20.4 ms | 100.08 | 18 |
| 0.75 | `Qwen/Qwen3-0.6B` | concurrency | 96 | 2 | 13.3 ms | 13.3 ms | 33.6 ms | 149.57 | 28 |
| 0.75 | `Qwen/Qwen3-0.6B` | concurrency | 96 | 4 | 13.9 ms | 13.9 ms | 39.8 ms | 286.56 | 52 |
| 0.75 | `Qwen/Qwen3-0.6B` | concurrency | 96 | 16 | 16.8 ms | 16.8 ms | 88.8 ms | 942.43 | 176 |
| 0.75 | `Qwen/Qwen3-0.6B` | concurrency | 96 | 32 | 20.6 ms | 20.8 ms | 103.8 ms | 1536.03 | 288 |
| 0.75 | `Qwen/Qwen3-0.6B` | concurrency | 96 | 64 | 28.8 ms | 28.7 ms | 132.2 ms | 2204.46 | 384 |
| 0.75 | `Qwen/Qwen3-0.6B` | concurrency | 96 | 128 | 43.7 ms | 43.8 ms | 251.1 ms | 2894.26 | 512 |
| 0.75 | `Qwen/Qwen3-0.6B` | cores | 24 | 8 | 13.8 ms | 13.8 ms | 61.7 ms | 577.17 | 104 |
| 0.75 | `Qwen/Qwen3-0.6B` | cores | 48 | 8 | 18.2 ms | 18.2 ms | 63.5 ms | 436.99 | 80 |
| 0.75 | `Qwen/Qwen3-0.6B` | cores | 72 | 8 | 23.9 ms | 23.8 ms | 93.7 ms | 332.63 | 64 |
| 1.35 | `deepseek-ai/deepseek-coder-1.3b-instruct` | baseline | 96 | 8 | 18.6 ms | 18.7 ms | 63.9 ms | 426.59 | 80 |
| 1.35 | `deepseek-ai/deepseek-coder-1.3b-instruct` | concurrency | 96 | 1 | 13.3 ms | 13.3 ms | 21.0 ms | 75.30 | 14 |
| 1.35 | `deepseek-ai/deepseek-coder-1.3b-instruct` | concurrency | 96 | 2 | 16.4 ms | 16.4 ms | 36.6 ms | 121.97 | 22 |
| 1.35 | `deepseek-ai/deepseek-coder-1.3b-instruct` | concurrency | 96 | 4 | 17.2 ms | 17.2 ms | 48.0 ms | 231.27 | 44 |
| 1.35 | `deepseek-ai/deepseek-coder-1.3b-instruct` | concurrency | 96 | 16 | 18.8 ms | 18.9 ms | 89.0 ms | 845.52 | 160 |
| 1.35 | `deepseek-ai/deepseek-coder-1.3b-instruct` | concurrency | 96 | 32 | 23.7 ms | 23.9 ms | 153.5 ms | 1332.14 | 224 |
| 1.35 | `deepseek-ai/deepseek-coder-1.3b-instruct` | concurrency | 96 | 64 | 36.1 ms | 36.4 ms | 224.8 ms | 1745.81 | 320 |
| 1.35 | `deepseek-ai/deepseek-coder-1.3b-instruct` | concurrency | 96 | 128 | 59.4 ms | 59.8 ms | 351.1 ms | 2127.66 | 384 |
| 1.35 | `deepseek-ai/deepseek-coder-1.3b-instruct` | cores | 24 | 8 | 20.4 ms | 20.4 ms | 88.1 ms | 389.99 | 72 |
| 1.35 | `deepseek-ai/deepseek-coder-1.3b-instruct` | cores | 48 | 8 | 16.4 ms | 16.5 ms | 72.5 ms | 483.21 | 88 |
| 1.35 | `deepseek-ai/deepseek-coder-1.3b-instruct` | cores | 72 | 8 | 15.2 ms | 15.2 ms | 67.5 ms | 524.10 | 96 |
| 1.54 | `Qwen/Qwen2.5-1.5B-Instruct` | baseline | 96 | 8 | 23.0 ms | 23.0 ms | 78.1 ms | 345.70 | 64 |
| 1.54 | `Qwen/Qwen2.5-1.5B-Instruct` | concurrency | 96 | 1 | 18.3 ms | 18.4 ms | 26.3 ms | 54.46 | 10 |
| 1.54 | `Qwen/Qwen2.5-1.5B-Instruct` | concurrency | 96 | 2 | 25.6 ms | 25.6 ms | 47.0 ms | 78.03 | 14 |
| 1.54 | `Qwen/Qwen2.5-1.5B-Instruct` | concurrency | 96 | 4 | 25.9 ms | 25.9 ms | 60.0 ms | 154.19 | 28 |
| 1.54 | `Qwen/Qwen2.5-1.5B-Instruct` | concurrency | 96 | 16 | 24.4 ms | 24.4 ms | 99.6 ms | 650.32 | 112 |
| 1.54 | `Qwen/Qwen2.5-1.5B-Instruct` | concurrency | 96 | 32 | 24.3 ms | 24.3 ms | 141.1 ms | 1299.21 | 224 |
| 1.54 | `Qwen/Qwen2.5-1.5B-Instruct` | concurrency | 96 | 64 | 34.8 ms | 34.8 ms | 219.3 ms | 1818.32 | 320 |
| 1.54 | `Qwen/Qwen2.5-1.5B-Instruct` | concurrency | 96 | 128 | 45.1 ms | 45.2 ms | 356.1 ms | 2794.70 | 512 |
| 1.54 | `Qwen/Qwen2.5-1.5B-Instruct` | cores | 24 | 8 | 23.1 ms | 23.1 ms | 93.8 ms | 344.54 | 64 |
| 1.54 | `Qwen/Qwen2.5-1.5B-Instruct` | cores | 48 | 8 | 20.7 ms | 20.8 ms | 80.3 ms | 383.30 | 72 |
| 1.54 | `Qwen/Qwen2.5-1.5B-Instruct` | cores | 72 | 8 | 21.6 ms | 21.6 ms | 74.7 ms | 368.10 | 64 |
| 1.71 | `HuggingFaceTB/SmolLM2-1.7B-Instruct` | baseline | 96 | 8 | 21.8 ms | 21.8 ms | 71.3 ms | 364.63 | 64 |
| 1.71 | `HuggingFaceTB/SmolLM2-1.7B-Instruct` | concurrency | 96 | 1 | 16.0 ms | 16.0 ms | 24.0 ms | 62.49 | 11 |
| 1.71 | `HuggingFaceTB/SmolLM2-1.7B-Instruct` | concurrency | 96 | 2 | 19.5 ms | 19.5 ms | 43.4 ms | 102.23 | 18 |
| 1.71 | `HuggingFaceTB/SmolLM2-1.7B-Instruct` | concurrency | 96 | 4 | 20.0 ms | 20.0 ms | 54.3 ms | 199.26 | 36 |
| 1.71 | `HuggingFaceTB/SmolLM2-1.7B-Instruct` | concurrency | 96 | 16 | 21.6 ms | 21.5 ms | 99.8 ms | 736.01 | 128 |
| 1.71 | `HuggingFaceTB/SmolLM2-1.7B-Instruct` | concurrency | 96 | 32 | 26.9 ms | 27.1 ms | 158.5 ms | 1173.37 | 192 |
| 1.71 | `HuggingFaceTB/SmolLM2-1.7B-Instruct` | concurrency | 96 | 64 | 39.4 ms | 39.8 ms | 274.8 ms | 1602.16 | 256 |
| 1.71 | `HuggingFaceTB/SmolLM2-1.7B-Instruct` | concurrency | 96 | 128 | 62.5 ms | 63.5 ms | 427.7 ms | 2019.58 | 256 |
| 1.71 | `HuggingFaceTB/SmolLM2-1.7B-Instruct` | cores | 24 | 8 | 24.6 ms | 24.6 ms | 102.0 ms | 322.59 | 56 |
| 1.71 | `HuggingFaceTB/SmolLM2-1.7B-Instruct` | cores | 48 | 8 | 19.1 ms | 19.1 ms | 78.0 ms | 416.90 | 72 |
| 1.71 | `HuggingFaceTB/SmolLM2-1.7B-Instruct` | cores | 72 | 8 | 18.2 ms | 18.2 ms | 75.8 ms | 437.70 | 80 |
| 2.53 | `ibm-granite/granite-3.3-2b-instruct` | baseline | 96 | 8 | 31.0 ms | 31.0 ms | 110.9 ms | 256.90 | 48 |
| 2.53 | `ibm-granite/granite-3.3-2b-instruct` | concurrency | 96 | 1 | 24.1 ms | 24.1 ms | 32.1 ms | 41.51 | 7 |
| 2.53 | `ibm-granite/granite-3.3-2b-instruct` | concurrency | 96 | 2 | 28.7 ms | 28.6 ms | 62.8 ms | 69.59 | 12 |
| 2.53 | `ibm-granite/granite-3.3-2b-instruct` | concurrency | 96 | 4 | 29.6 ms | 29.6 ms | 78.9 ms | 134.68 | 24 |
| 2.53 | `ibm-granite/granite-3.3-2b-instruct` | concurrency | 96 | 16 | 28.6 ms | 28.6 ms | 138.6 ms | 553.26 | 96 |
| 2.53 | `ibm-granite/granite-3.3-2b-instruct` | concurrency | 96 | 32 | 33.1 ms | 33.2 ms | 204.4 ms | 955.03 | 160 |
| 2.53 | `ibm-granite/granite-3.3-2b-instruct` | concurrency | 96 | 64 | 45.8 ms | 46.0 ms | 429.8 ms | 1370.34 | 256 |
| 2.53 | `ibm-granite/granite-3.3-2b-instruct` | concurrency | 96 | 128 | 66.3 ms | 67.1 ms | 591.2 ms | 1892.32 | 256 |
| 2.53 | `ibm-granite/granite-3.3-2b-instruct` | cores | 24 | 8 | 34.0 ms | 34.0 ms | 147.6 ms | 233.26 | 40 |
| 2.53 | `ibm-granite/granite-3.3-2b-instruct` | cores | 48 | 8 | 26.7 ms | 26.7 ms | 116.3 ms | 297.26 | 56 |
| 2.53 | `ibm-granite/granite-3.3-2b-instruct` | cores | 72 | 8 | 25.5 ms | 25.6 ms | 113.7 ms | 311.03 | 56 |
| 3.09 | `Qwen/Qwen2.5-3B-Instruct` | baseline | 96 | 8 | 33.4 ms | 33.3 ms | 114.3 ms | 238.41 | 40 |
| 3.09 | `Qwen/Qwen2.5-3B-Instruct` | concurrency | 96 | 1 | 27.2 ms | 27.2 ms | 35.9 ms | 36.76 | 7 |
| 3.09 | `Qwen/Qwen2.5-3B-Instruct` | concurrency | 96 | 2 | 31.2 ms | 31.2 ms | 72.1 ms | 63.92 | 12 |
| 3.09 | `Qwen/Qwen2.5-3B-Instruct` | concurrency | 96 | 4 | 31.5 ms | 31.5 ms | 86.7 ms | 126.50 | 24 |
| 3.09 | `Qwen/Qwen2.5-3B-Instruct` | concurrency | 96 | 16 | 30.8 ms | 30.8 ms | 160.2 ms | 515.08 | 96 |
| 3.09 | `Qwen/Qwen2.5-3B-Instruct` | concurrency | 96 | 32 | 34.6 ms | 34.6 ms | 235.4 ms | 911.33 | 160 |
| 3.09 | `Qwen/Qwen2.5-3B-Instruct` | concurrency | 96 | 64 | 49.3 ms | 49.0 ms | 392.4 ms | 1275.22 | 192 |
| 3.09 | `Qwen/Qwen2.5-3B-Instruct` | concurrency | 96 | 128 | 67.3 ms | 67.5 ms | 618.4 ms | 1861.70 | 256 |
| 3.09 | `Qwen/Qwen2.5-3B-Instruct` | cores | 24 | 8 | 38.4 ms | 38.4 ms | 158.9 ms | 206.68 | 32 |
| 3.09 | `Qwen/Qwen2.5-3B-Instruct` | cores | 48 | 8 | 30.0 ms | 30.0 ms | 124.0 ms | 264.63 | 48 |
| 3.09 | `Qwen/Qwen2.5-3B-Instruct` | cores | 72 | 8 | 30.8 ms | 30.9 ms | 117.5 ms | 257.79 | 48 |
| 3.84 | `microsoft/Phi-4-mini-instruct` | baseline | 96 | 8 | 34.1 ms | 34.1 ms | 125.0 ms | 233.34 | 40 |
| 3.84 | `microsoft/Phi-4-mini-instruct` | concurrency | 96 | 1 | 31.7 ms | 31.8 ms | 42.3 ms | 31.48 | 6 |
| 3.84 | `microsoft/Phi-4-mini-instruct` | concurrency | 96 | 2 | 31.6 ms | 31.7 ms | 79.8 ms | 62.99 | 12 |
| 3.84 | `microsoft/Phi-4-mini-instruct` | concurrency | 96 | 4 | 32.6 ms | 32.6 ms | 99.2 ms | 122.10 | 20 |
| 3.84 | `microsoft/Phi-4-mini-instruct` | concurrency | 96 | 16 | 36.2 ms | 36.2 ms | 183.2 ms | 438.06 | 80 |
| 3.84 | `microsoft/Phi-4-mini-instruct` | concurrency | 96 | 32 | 41.1 ms | 41.1 ms | 266.6 ms | 767.66 | 128 |
| 3.84 | `microsoft/Phi-4-mini-instruct` | concurrency | 96 | 64 | 60.8 ms | 61.0 ms | 418.2 ms | 1036.82 | 192 |
| 3.84 | `microsoft/Phi-4-mini-instruct` | concurrency | 96 | 128 | 86.5 ms | 86.9 ms | 725.8 ms | 1454.94 | 256 |
| 3.84 | `microsoft/Phi-4-mini-instruct` | cores | 24 | 8 | 44.8 ms | 44.8 ms | 183.7 ms | 177.37 | 32 |
| 3.84 | `microsoft/Phi-4-mini-instruct` | cores | 48 | 8 | 34.1 ms | 34.1 ms | 144.8 ms | 232.99 | 40 |
| 3.84 | `microsoft/Phi-4-mini-instruct` | cores | 72 | 8 | 34.1 ms | 34.1 ms | 136.3 ms | 233.17 | 40 |
| 4.02 | `Qwen/Qwen3-4B-Instruct-2507` | baseline | 96 | 8 | 35.5 ms | 35.5 ms | 139.3 ms | 223.92 | 40 |
| 4.02 | `Qwen/Qwen3-4B-Instruct-2507` | concurrency | 96 | 1 | 33.0 ms | 33.0 ms | 42.3 ms | 30.32 | 5 |
| 4.02 | `Qwen/Qwen3-4B-Instruct-2507` | concurrency | 96 | 2 | 32.7 ms | 32.7 ms | 75.2 ms | 60.97 | 10 |
| 4.02 | `Qwen/Qwen3-4B-Instruct-2507` | concurrency | 96 | 4 | 33.9 ms | 33.9 ms | 105.7 ms | 117.34 | 20 |
| 4.02 | `Qwen/Qwen3-4B-Instruct-2507` | concurrency | 96 | 16 | 37.9 ms | 37.9 ms | 208.6 ms | 417.97 | 64 |
| 4.02 | `Qwen/Qwen3-4B-Instruct-2507` | concurrency | 96 | 32 | 43.1 ms | 43.1 ms | 282.3 ms | 732.46 | 128 |
| 4.02 | `Qwen/Qwen3-4B-Instruct-2507` | concurrency | 96 | 64 | 66.4 ms | 67.0 ms | 482.2 ms | 948.66 | 128 |
| 4.02 | `Qwen/Qwen3-4B-Instruct-2507` | concurrency | 96 | 128 | 91.8 ms | 93.2 ms | 781.8 ms | 1369.62 | 256 |
| 4.02 | `Qwen/Qwen3-4B-Instruct-2507` | cores | 24 | 8 | 48.3 ms | 48.3 ms | 208.9 ms | 164.37 | 24 |
| 4.02 | `Qwen/Qwen3-4B-Instruct-2507` | cores | 48 | 8 | 35.7 ms | 35.7 ms | 155.9 ms | 222.41 | 40 |
| 4.02 | `Qwen/Qwen3-4B-Instruct-2507` | cores | 72 | 8 | 38.4 ms | 38.4 ms | 151.1 ms | 206.94 | 32 |
| 7.24 | `HuggingFaceH4/zephyr-7b-beta` | baseline | 96 | 8 | 52.8 ms | 52.8 ms | 196.5 ms | 150.32 | 24 |
| 7.24 | `HuggingFaceH4/zephyr-7b-beta` | concurrency | 96 | 1 | 50.8 ms | 50.8 ms | 66.5 ms | 19.68 | 3 |
| 7.24 | `HuggingFaceH4/zephyr-7b-beta` | concurrency | 96 | 2 | 50.8 ms | 50.8 ms | 122.5 ms | 39.23 | 6 |
| 7.24 | `HuggingFaceH4/zephyr-7b-beta` | concurrency | 96 | 4 | 51.5 ms | 51.5 ms | 154.0 ms | 77.34 | 12 |
| 7.24 | `HuggingFaceH4/zephyr-7b-beta` | concurrency | 96 | 16 | 58.1 ms | 58.1 ms | 277.3 ms | 272.98 | 48 |
| 7.24 | `HuggingFaceH4/zephyr-7b-beta` | concurrency | 96 | 32 | 65.4 ms | 65.7 ms | 441.6 ms | 482.50 | 64 |
| 7.24 | `HuggingFaceH4/zephyr-7b-beta` | concurrency | 96 | 64 | 87.0 ms | 87.4 ms | 675.9 ms | 723.92 | 128 |
| 7.24 | `HuggingFaceH4/zephyr-7b-beta` | concurrency | 96 | 128 | 117.5 ms | 118.6 ms | 1153.4 ms | 1060.99 | 128 |
| 7.24 | `HuggingFaceH4/zephyr-7b-beta` | cores | 24 | 8 | 74.0 ms | 74.1 ms | 338.1 ms | 107.03 | 16 |
| 7.24 | `HuggingFaceH4/zephyr-7b-beta` | cores | 48 | 8 | 52.9 ms | 53.0 ms | 226.6 ms | 149.88 | 24 |
| 7.24 | `HuggingFaceH4/zephyr-7b-beta` | cores | 72 | 8 | 51.9 ms | 51.9 ms | 213.2 ms | 152.99 | 24 |
| 7.30 | `allenai/OLMo-2-1124-7B-Instruct` | baseline | 96 | 8 | 55.5 ms | 55.6 ms | 196.8 ms | 143.30 | 24 |
| 7.30 | `allenai/OLMo-2-1124-7B-Instruct` | concurrency | 96 | 1 | 49.7 ms | 49.7 ms | 64.2 ms | 20.09 | 3 |
| 7.30 | `allenai/OLMo-2-1124-7B-Instruct` | concurrency | 96 | 2 | 50.7 ms | 50.7 ms | 117.8 ms | 39.34 | 6 |
| 7.30 | `allenai/OLMo-2-1124-7B-Instruct` | concurrency | 96 | 4 | 52.2 ms | 52.3 ms | 154.8 ms | 76.32 | 12 |
| 7.30 | `allenai/OLMo-2-1124-7B-Instruct` | concurrency | 96 | 16 | 63.0 ms | 63.3 ms | 295.6 ms | 251.59 | 32 |
| 7.30 | `allenai/OLMo-2-1124-7B-Instruct` | concurrency | 96 | 32 | 73.9 ms | 75.0 ms | 429.3 ms | 427.39 | 64 |
| 7.30 | `allenai/OLMo-2-1124-7B-Instruct` | concurrency | 96 | 64 | 106.0 ms | 107.1 ms | 719.4 ms | 593.09 | 64 |
| 7.30 | `allenai/OLMo-2-1124-7B-Instruct` | concurrency | 96 | 128 | 169.2 ms | 154.7 ms | 1223.8 ms | 736.74 | 128 |
| 7.30 | `allenai/OLMo-2-1124-7B-Instruct` | cores | 24 | 8 | 76.3 ms | 76.5 ms | 331.4 ms | 104.01 | 16 |
| 7.30 | `allenai/OLMo-2-1124-7B-Instruct` | cores | 48 | 8 | 55.8 ms | 55.9 ms | 228.9 ms | 142.23 | 24 |
| 7.30 | `allenai/OLMo-2-1124-7B-Instruct` | cores | 72 | 8 | 54.8 ms | 55.0 ms | 209.7 ms | 144.81 | 24 |
| 7.62 | `Qwen/Qwen2.5-7B-Instruct` | baseline | 96 | 8 | 57.7 ms | 57.7 ms | 199.6 ms | 137.52 | 24 |
| 7.62 | `Qwen/Qwen2.5-7B-Instruct` | concurrency | 96 | 1 | 54.2 ms | 54.2 ms | 69.6 ms | 18.42 | 3 |
| 7.62 | `Qwen/Qwen2.5-7B-Instruct` | concurrency | 96 | 2 | 54.1 ms | 54.1 ms | 117.5 ms | 36.83 | 6 |
| 7.62 | `Qwen/Qwen2.5-7B-Instruct` | concurrency | 96 | 4 | 54.9 ms | 54.9 ms | 152.6 ms | 72.46 | 12 |
| 7.62 | `Qwen/Qwen2.5-7B-Instruct` | concurrency | 96 | 16 | 62.0 ms | 62.0 ms | 276.2 ms | 256.22 | 48 |
| 7.62 | `Qwen/Qwen2.5-7B-Instruct` | concurrency | 96 | 32 | 66.2 ms | 66.2 ms | 384.2 ms | 477.17 | 64 |
| 7.62 | `Qwen/Qwen2.5-7B-Instruct` | concurrency | 96 | 64 | 82.1 ms | 81.9 ms | 643.4 ms | 763.76 | 128 |
| 7.62 | `Qwen/Qwen2.5-7B-Instruct` | concurrency | 96 | 128 | 105.8 ms | 106.8 ms | 1123.5 ms | 1179.03 | 128 |
| 7.62 | `Qwen/Qwen2.5-7B-Instruct` | cores | 24 | 8 | 72.4 ms | 72.4 ms | 300.6 ms | 109.52 | 16 |
| 7.62 | `Qwen/Qwen2.5-7B-Instruct` | cores | 48 | 8 | 54.3 ms | 54.3 ms | 218.2 ms | 146.14 | 24 |
| 7.62 | `Qwen/Qwen2.5-7B-Instruct` | cores | 72 | 8 | 52.1 ms | 52.1 ms | 193.9 ms | 152.54 | 24 |
| 8.17 | `ibm-granite/granite-3.3-8b-instruct` | baseline | 96 | 8 | 62.1 ms | 62.1 ms | 231.8 ms | 128.10 | 24 |
| 8.17 | `ibm-granite/granite-3.3-8b-instruct` | concurrency | 96 | 1 | 58.5 ms | 58.4 ms | 73.1 ms | 17.09 | 3 |
| 8.17 | `ibm-granite/granite-3.3-8b-instruct` | concurrency | 96 | 2 | 58.9 ms | 58.9 ms | 138.4 ms | 33.86 | 6 |
| 8.17 | `ibm-granite/granite-3.3-8b-instruct` | concurrency | 96 | 4 | 59.7 ms | 59.7 ms | 181.5 ms | 66.72 | 12 |
| 8.17 | `ibm-granite/granite-3.3-8b-instruct` | concurrency | 96 | 16 | 67.4 ms | 67.5 ms | 328.8 ms | 234.91 | 32 |
| 8.17 | `ibm-granite/granite-3.3-8b-instruct` | concurrency | 96 | 32 | 72.5 ms | 72.6 ms | 505.4 ms | 434.51 | 64 |
| 8.17 | `ibm-granite/granite-3.3-8b-instruct` | concurrency | 96 | 64 | 97.7 ms | 98.4 ms | 841.2 ms | 642.17 | 64 |
| 8.17 | `ibm-granite/granite-3.3-8b-instruct` | concurrency | 96 | 128 | 147.0 ms | 145.9 ms | 1370.8 ms | 841.97 | 128 |
| 8.17 | `ibm-granite/granite-3.3-8b-instruct` | cores | 24 | 8 | 85.6 ms | 85.6 ms | 393.8 ms | 92.57 | 16 |
| 8.17 | `ibm-granite/granite-3.3-8b-instruct` | cores | 48 | 8 | 61.8 ms | 61.8 ms | 262.2 ms | 128.63 | 24 |
| 8.17 | `ibm-granite/granite-3.3-8b-instruct` | cores | 72 | 8 | 60.0 ms | 60.1 ms | 247.0 ms | 132.28 | 24 |
| 8.83 | `01-ai/Yi-1.5-9B-Chat` | baseline | 96 | 8 | 66.3 ms | 66.3 ms | 257.3 ms | 119.92 | 16 |
| 8.83 | `01-ai/Yi-1.5-9B-Chat` | concurrency | 96 | 1 | 62.3 ms | 62.3 ms | 78.9 ms | 16.04 | 3 |
| 8.83 | `01-ai/Yi-1.5-9B-Chat` | concurrency | 96 | 2 | 62.9 ms | 63.0 ms | 148.5 ms | 31.68 | 6 |
| 8.83 | `01-ai/Yi-1.5-9B-Chat` | concurrency | 96 | 4 | 63.8 ms | 63.8 ms | 185.3 ms | 62.38 | 8 |
| 8.83 | `01-ai/Yi-1.5-9B-Chat` | concurrency | 96 | 16 | 71.1 ms | 71.2 ms | 359.4 ms | 222.77 | 32 |
| 8.83 | `01-ai/Yi-1.5-9B-Chat` | concurrency | 96 | 32 | 76.2 ms | 76.3 ms | 576.6 ms | 412.12 | 64 |
| 8.83 | `01-ai/Yi-1.5-9B-Chat` | concurrency | 96 | 64 | 105.9 ms | 106.1 ms | 906.8 ms | 592.39 | 64 |
| 8.83 | `01-ai/Yi-1.5-9B-Chat` | concurrency | 96 | 128 | 144.1 ms | 145.1 ms | 1488.0 ms | 859.14 | 128 |
| 8.83 | `01-ai/Yi-1.5-9B-Chat` | cores | 24 | 8 | 90.6 ms | 90.6 ms | 411.2 ms | 87.66 | 16 |
| 8.83 | `01-ai/Yi-1.5-9B-Chat` | cores | 48 | 8 | 65.5 ms | 65.5 ms | 291.2 ms | 121.08 | 16 |
| 8.83 | `01-ai/Yi-1.5-9B-Chat` | cores | 72 | 8 | 64.5 ms | 64.5 ms | 258.6 ms | 123.14 | 16 |
| 13.72 | `allenai/OLMo-2-1124-13B-Instruct` | baseline | 96 | 8 | 95.7 ms | 96.1 ms | 313.1 ms | 83.12 | 8 |
| 13.72 | `allenai/OLMo-2-1124-13B-Instruct` | concurrency | 96 | 1 | 88.0 ms | 88.1 ms | 110.6 ms | 11.34 | 2 |
| 13.72 | `allenai/OLMo-2-1124-13B-Instruct` | concurrency | 96 | 2 | 89.1 ms | 89.2 ms | 203.8 ms | 22.37 | 4 |
| 13.72 | `allenai/OLMo-2-1124-13B-Instruct` | concurrency | 96 | 4 | 91.2 ms | 91.3 ms | 256.0 ms | 43.70 | 8 |
| 13.72 | `allenai/OLMo-2-1124-13B-Instruct` | concurrency | 96 | 16 | 106.2 ms | 106.7 ms | 441.5 ms | 149.34 | 16 |
| 13.72 | `allenai/OLMo-2-1124-13B-Instruct` | concurrency | 96 | 32 | 121.7 ms | 121.6 ms | 650.1 ms | 259.21 | 32 |
| 13.72 | `allenai/OLMo-2-1124-13B-Instruct` | concurrency | 96 | 64 | 177.0 ms | 177.8 ms | 1380.6 ms | 356.29 | 64 |
| 13.72 | `allenai/OLMo-2-1124-13B-Instruct` | concurrency | 96 | 128 | 243.4 ms | 247.0 ms | 2039.6 ms | 514.86 | 0 |
| 13.72 | `allenai/OLMo-2-1124-13B-Instruct` | cores | 24 | 8 | 133.4 ms | 133.1 ms | 581.6 ms | 59.39 | 8 |
| 13.72 | `allenai/OLMo-2-1124-13B-Instruct` | cores | 48 | 8 | 98.1 ms | 98.6 ms | 373.3 ms | 80.90 | 8 |
| 13.72 | `allenai/OLMo-2-1124-13B-Instruct` | cores | 72 | 8 | 96.7 ms | 97.0 ms | 331.4 ms | 82.23 | 8 |
| 14.66 | `microsoft/phi-4` | baseline | 96 | 8 | 96.2 ms | 96.3 ms | 335.2 ms | 82.59 | 8 |
| 14.66 | `microsoft/phi-4` | concurrency | 96 | 1 | 92.2 ms | 92.2 ms | 111.7 ms | 10.84 | 2 |
| 14.66 | `microsoft/phi-4` | concurrency | 96 | 2 | 92.5 ms | 92.5 ms | 168.9 ms | 21.57 | 4 |
| 14.66 | `microsoft/phi-4` | concurrency | 96 | 4 | 93.2 ms | 93.2 ms | 265.8 ms | 42.72 | 8 |
| 14.66 | `microsoft/phi-4` | concurrency | 96 | 16 | 102.2 ms | 102.5 ms | 480.5 ms | 155.03 | 16 |
| 14.66 | `microsoft/phi-4` | concurrency | 96 | 32 | 109.7 ms | 110.5 ms | 718.2 ms | 287.30 | 32 |
| 14.66 | `microsoft/phi-4` | concurrency | 96 | 64 | 144.9 ms | 145.8 ms | 1220.4 ms | 430.26 | 64 |
| 14.66 | `microsoft/phi-4` | concurrency | 96 | 128 | 195.8 ms | 197.0 ms | 2107.4 ms | 638.59 | 0 |
| 14.66 | `microsoft/phi-4` | cores | 24 | 8 | 135.3 ms | 135.4 ms | 609.4 ms | 58.50 | 8 |
| 14.66 | `microsoft/phi-4` | cores | 48 | 8 | 98.8 ms | 98.9 ms | 401.6 ms | 80.37 | 8 |
| 14.66 | `microsoft/phi-4` | cores | 72 | 8 | 100.3 ms | 100.4 ms | 356.5 ms | 79.21 | 8 |
| 14.77 | `Qwen/Qwen2.5-14B-Instruct` | baseline | 96 | 8 | 98.4 ms | 98.4 ms | 334.7 ms | 80.81 | 8 |
| 14.77 | `Qwen/Qwen2.5-14B-Instruct` | concurrency | 96 | 1 | 93.1 ms | 93.1 ms | 110.4 ms | 10.73 | 2 |
| 14.77 | `Qwen/Qwen2.5-14B-Instruct` | concurrency | 96 | 2 | 93.4 ms | 93.5 ms | 165.2 ms | 21.34 | 4 |
| 14.77 | `Qwen/Qwen2.5-14B-Instruct` | concurrency | 96 | 4 | 94.2 ms | 94.3 ms | 267.6 ms | 42.23 | 8 |
| 14.77 | `Qwen/Qwen2.5-14B-Instruct` | concurrency | 96 | 16 | 103.7 ms | 103.8 ms | 458.6 ms | 152.90 | 16 |
| 14.77 | `Qwen/Qwen2.5-14B-Instruct` | concurrency | 96 | 32 | 111.3 ms | 111.8 ms | 796.1 ms | 282.70 | 32 |
| 14.77 | `Qwen/Qwen2.5-14B-Instruct` | concurrency | 96 | 64 | 148.5 ms | 149.0 ms | 1236.7 ms | 419.58 | 64 |
| 14.77 | `Qwen/Qwen2.5-14B-Instruct` | concurrency | 96 | 128 | 202.1 ms | 203.4 ms | 2117.2 ms | 618.70 | 0 |
| 14.77 | `Qwen/Qwen2.5-14B-Instruct` | cores | 24 | 8 | 136.8 ms | 136.9 ms | 606.4 ms | 57.88 | 8 |
| 14.77 | `Qwen/Qwen2.5-14B-Instruct` | cores | 48 | 8 | 99.2 ms | 99.3 ms | 408.6 ms | 80.01 | 8 |
| 14.77 | `Qwen/Qwen2.5-14B-Instruct` | cores | 72 | 8 | 97.4 ms | 97.5 ms | 364.1 ms | 81.52 | 8 |
| 14.77 | `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B` | baseline | 96 | 8 | 98.2 ms | 98.3 ms | 333.9 ms | 80.99 | 8 |
| 14.77 | `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B` | concurrency | 96 | 1 | 93.0 ms | 93.0 ms | 113.0 ms | 10.74 | 2 |
| 14.77 | `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B` | concurrency | 96 | 2 | 93.2 ms | 93.2 ms | 216.2 ms | 21.39 | 4 |
| 14.77 | `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B` | concurrency | 96 | 4 | 94.2 ms | 94.2 ms | 269.9 ms | 42.28 | 8 |
| 14.77 | `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B` | concurrency | 96 | 16 | 103.9 ms | 104.0 ms | 486.5 ms | 152.57 | 16 |
| 14.77 | `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B` | concurrency | 96 | 32 | 111.3 ms | 111.9 ms | 721.5 ms | 283.03 | 32 |
| 14.77 | `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B` | concurrency | 96 | 64 | 149.9 ms | 150.6 ms | 1247.9 ms | 416.04 | 64 |
| 14.77 | `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B` | concurrency | 96 | 128 | 200.7 ms | 201.9 ms | 2072.9 ms | 624.37 | 0 |
| 14.77 | `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B` | cores | 24 | 8 | 136.7 ms | 136.8 ms | 611.8 ms | 57.88 | 8 |
| 14.77 | `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B` | cores | 48 | 8 | 99.2 ms | 99.3 ms | 413.0 ms | 80.10 | 8 |
| 14.77 | `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B` | cores | 72 | 8 | 97.9 ms | 97.9 ms | 363.2 ms | 81.17 | 8 |
| 30.53 | `Qwen/Qwen3-30B-A3B-Instruct-2507` | baseline | 96 | 8 | 55.0 ms | 55.2 ms | 276.4 ms | 143.92 | 24 |
| 30.53 | `Qwen/Qwen3-30B-A3B-Instruct-2507` | concurrency | 96 | 1 | 34.9 ms | 34.9 ms | 111.7 ms | 28.51 | 5 |
| 30.53 | `Qwen/Qwen3-30B-A3B-Instruct-2507` | concurrency | 96 | 2 | 43.6 ms | 43.6 ms | 141.9 ms | 45.52 | 8 |
| 30.53 | `Qwen/Qwen3-30B-A3B-Instruct-2507` | concurrency | 96 | 4 | 54.1 ms | 54.1 ms | 240.3 ms | 73.39 | 12 |
| 30.53 | `Qwen/Qwen3-30B-A3B-Instruct-2507` | concurrency | 96 | 16 | 58.7 ms | 58.9 ms | 311.3 ms | 270.06 | 48 |
| 30.53 | `Qwen/Qwen3-30B-A3B-Instruct-2507` | concurrency | 96 | 32 | 62.7 ms | 63.6 ms | 407.9 ms | 503.83 | 64 |
| 30.53 | `Qwen/Qwen3-30B-A3B-Instruct-2507` | concurrency | 96 | 64 | 86.8 ms | 86.8 ms | 678.4 ms | 727.49 | 128 |
| 30.53 | `Qwen/Qwen3-30B-A3B-Instruct-2507` | concurrency | 96 | 128 | 113.1 ms | 114.0 ms | 970.1 ms | 1109.37 | 128 |
| 30.53 | `Qwen/Qwen3-30B-A3B-Instruct-2507` | cores | 24 | 8 | 69.9 ms | 70.4 ms | 361.3 ms | 113.26 | 16 |
| 30.53 | `Qwen/Qwen3-30B-A3B-Instruct-2507` | cores | 48 | 8 | 56.2 ms | 56.3 ms | 284.3 ms | 140.90 | 24 |
| 30.53 | `Qwen/Qwen3-30B-A3B-Instruct-2507` | cores | 72 | 8 | 54.0 ms | 54.1 ms | 268.4 ms | 146.77 | 24 |
| 32.23 | `allenai/OLMo-2-0325-32B-Instruct` | baseline | 96 | 8 | 204.5 ms | 204.5 ms | 820.7 ms | 38.87 | 0 |
| 32.23 | `allenai/OLMo-2-0325-32B-Instruct` | concurrency | 96 | 1 | 200.3 ms | 200.3 ms | 231.0 ms | 4.99 | 0 |
| 32.23 | `allenai/OLMo-2-0325-32B-Instruct` | concurrency | 96 | 2 | 201.2 ms | 201.3 ms | 320.0 ms | 9.91 | 0 |
| 32.23 | `allenai/OLMo-2-0325-32B-Instruct` | concurrency | 96 | 4 | 201.8 ms | 201.8 ms | 630.0 ms | 19.74 | 0 |
| 32.23 | `allenai/OLMo-2-0325-32B-Instruct` | concurrency | 96 | 16 | 214.4 ms | 214.4 ms | 1089.2 ms | 73.79 | 0 |
| 32.23 | `allenai/OLMo-2-0325-32B-Instruct` | concurrency | 96 | 32 | 228.0 ms | 228.4 ms | 1566.9 ms | 137.97 | 0 |
| 32.23 | `allenai/OLMo-2-0325-32B-Instruct` | concurrency | 96 | 64 | 296.1 ms | 296.4 ms | 2924.7 ms | 209.81 | 0 |
| 32.23 | `allenai/OLMo-2-0325-32B-Instruct` | concurrency | 96 | 128 | 378.0 ms | 378.3 ms | 4548.3 ms | 322.88 | 0 |
| 32.23 | `allenai/OLMo-2-0325-32B-Instruct` | cores | 24 | 8 | 292.9 ms | 292.4 ms | 1498.1 ms | 26.97 | 0 |
| 32.23 | `allenai/OLMo-2-0325-32B-Instruct` | cores | 48 | 8 | 214.1 ms | 214.1 ms | 923.7 ms | 37.08 | 0 |
| 32.23 | `allenai/OLMo-2-0325-32B-Instruct` | cores | 72 | 8 | 212.6 ms | 212.6 ms | 826.0 ms | 37.34 | 0 |
| 32.76 | `Qwen/Qwen3-32B` | baseline | 96 | 8 | 203.8 ms | 203.8 ms | 784.1 ms | 38.94 | 0 |
| 32.76 | `Qwen/Qwen3-32B` | concurrency | 96 | 1 | 199.2 ms | 199.3 ms | 230.1 ms | 5.01 | 0 |
| 32.76 | `Qwen/Qwen3-32B` | concurrency | 96 | 2 | 200.1 ms | 200.1 ms | 324.5 ms | 9.98 | 0 |
| 32.76 | `Qwen/Qwen3-32B` | concurrency | 96 | 4 | 201.2 ms | 201.2 ms | 659.0 ms | 19.79 | 0 |
| 32.76 | `Qwen/Qwen3-32B` | concurrency | 96 | 16 | 213.7 ms | 213.8 ms | 1135.9 ms | 74.16 | 0 |
| 32.76 | `Qwen/Qwen3-32B` | concurrency | 96 | 32 | 226.1 ms | 226.4 ms | 1583.2 ms | 139.39 | 0 |
| 32.76 | `Qwen/Qwen3-32B` | concurrency | 96 | 64 | 283.0 ms | 283.0 ms | 2843.4 ms | 219.79 | 0 |
| 32.76 | `Qwen/Qwen3-32B` | concurrency | 96 | 128 | 374.0 ms | 374.3 ms | 4766.9 ms | 325.72 | 0 |
| 32.76 | `Qwen/Qwen3-32B` | cores | 24 | 8 | 293.7 ms | 293.6 ms | 1429.7 ms | 26.86 | 0 |
| 32.76 | `Qwen/Qwen3-32B` | cores | 48 | 8 | 212.3 ms | 212.3 ms | 941.0 ms | 37.34 | 0 |
| 32.76 | `Qwen/Qwen3-32B` | cores | 72 | 8 | 214.1 ms | 214.2 ms | 810.7 ms | 37.08 | 0 |

## Thread pinning

All 220 attempts with a server log are free of OpenMP warning #124. The server runs under `numactl --physcpubind=0-(N-1) --membind=0`, and vLLM re-execs the worker under the same CPU list.

## Failures and retries

No failed attempts in the current plan.

## Caveats

- The measurement window is 90 seconds. At about 200 ms/token or slower a 512-token request cannot finish inside it, so client TPOT there comes from partially generated requests, and request-level vLLM histograms stay empty. 26 finished runs so far have zero completed requests.
- These models use the manual BF16 path, not a tuned Xeon 6 recipe. Compare them with recipe rows in `REPORT_PINNED.md` with that difference in mind. Parameter counts come from the Hugging Face safetensors metadata.
- The Mixture-of-Experts model (`Qwen/Qwen3-30B-A3B-Instruct-2507`, 3B active) decodes faster than its 30B total size suggests.

