# vLLM decode latency report

Live notes for plan `5226854cadfd` on the Xeon 6972P node-0 benchmark. Updated 2026-11-09 14:03:01 UTC.

## Snapshot

Controller is not running. Progress 66/66 successful runs.

Decode latency here is the time between generated tokens. The server series that records every token is `vllm:inter_token_latency_seconds`. The client series is the per-request mean TPOT, `(last token time − first token time) / (tokens − 1)`. Those two agree. vLLM's request-level `request_time_per_output_token_seconds` and `request_decode_time_seconds` update only when a request finishes. At ~350 ms/token a 512-token request cannot finish inside the 90-second window, so those histograms stay empty. They fill once the step is short enough that 512 tokens fit in the window.

Across 66 finished runs, server inter-token latency averages **9.0–92.6 ms**. Relative spread versus the fastest finished run is 930.8%. Per-token time is no longer a single band.

## Decode latency by run

Means are `histogram_sum / histogram_count` over samples that arrived between `measurement_start` and `measurement_window_end`. The Prometheus buckets are 100 ms wide in this region, so a reported p50 near 350 ms only means the median bucket is 300–400 ms. The mean is the precise number. Client TPOT is the median of per-request mean token gaps, including requests that the 90-second window truncates.

| Model | Sweep | Cores | Clients | Gen | Status | Server ITL mean | ITL bucket | Client TPOT median | Client TTFT median | Tokens/s | Running | Waiting |
|---|---|---:|---:|---:|---|---:|---|---:|---:|---:|---:|---:|
| `Qwen/Qwen2.5-0.5B-Instruct` | baseline | 96 | 8 | 512 | done | 20.0 ms | 96.8% in 10–25 ms | 18.7 ms | 54.6 ms | 399.07 | 7.9 | 0.0 |
| `Qwen/Qwen2.5-0.5B-Instruct` | concurrency | 96 | 1 | 512 | done | 9.9 ms | 77.5% in 0–10 ms | 9.9 ms | 24.1 ms | 100.90 | 1.0 | 0.0 |
| `Qwen/Qwen2.5-0.5B-Instruct` | concurrency | 96 | 2 | 512 | done | 17.2 ms | 99.8% in 10–25 ms | 17.2 ms | 41.0 ms | 115.77 | 2.0 | 0.0 |
| `Qwen/Qwen2.5-0.5B-Instruct` | concurrency | 96 | 4 | 512 | done | 17.9 ms | 99.4% in 10–25 ms | 17.9 ms | 45.2 ms | 222.10 | 3.9 | 0.0 |
| `Qwen/Qwen2.5-0.5B-Instruct` | concurrency | 96 | 16 | 512 | done | 20.0 ms | 98.1% in 10–25 ms | 19.9 ms | 65.4 ms | 796.81 | 15.8 | 0.0 |
| `Qwen/Qwen2.5-0.5B-Instruct` | concurrency | 96 | 32 | 512 | done | 21.7 ms | 97.5% in 10–25 ms | 21.6 ms | 87.7 ms | 1465.97 | 31.6 | 0.0 |
| `Qwen/Qwen2.5-0.5B-Instruct` | concurrency | 96 | 64 | 512 | done | 29.2 ms | 99.8% in 25–50 ms | 29.2 ms | 124.6 ms | 2176.01 | 61.2 | 0.0 |
| `Qwen/Qwen2.5-0.5B-Instruct` | concurrency | 96 | 128 | 512 | done | 33.8 ms | 99.8% in 25–50 ms | 33.9 ms | 189.1 ms | 3734.77 | 123.7 | 0.0 |
| `Qwen/Qwen2.5-0.5B-Instruct` | cores | 24 | 8 | 512 | done | 11.6 ms | 99.9% in 10–25 ms | 11.5 ms | 46.0 ms | 687.39 | 7.8 | 0.0 |
| `Qwen/Qwen2.5-0.5B-Instruct` | cores | 48 | 8 | 512 | done | 23.0 ms | 95.8% in 10–25 ms | 23.1 ms | 78.4 ms | 345.36 | 7.9 | 0.0 |
| `Qwen/Qwen2.5-0.5B-Instruct` | cores | 72 | 8 | 512 | done | 32.9 ms | 99.6% in 25–50 ms | 32.9 ms | 95.0 ms | 242.26 | 7.9 | 0.0 |
| `Qwen/Qwen3-1.7B` | baseline | 96 | 8 | 512 | done | 22.5 ms | 94.9% in 10–25 ms | 22.5 ms | 78.4 ms | 352.90 | 7.9 | 0.0 |
| `Qwen/Qwen3-1.7B` | concurrency | 96 | 1 | 512 | done | 17.2 ms | 99.7% in 10–25 ms | 17.2 ms | 27.0 ms | 58.00 | 1.0 | 0.0 |
| `Qwen/Qwen3-1.7B` | concurrency | 96 | 2 | 512 | done | 20.6 ms | 97.9% in 10–25 ms | 20.6 ms | 48.8 ms | 96.63 | 2.0 | 0.0 |
| `Qwen/Qwen3-1.7B` | concurrency | 96 | 4 | 512 | done | 21.2 ms | 97.4% in 10–25 ms | 21.2 ms | 59.3 ms | 187.66 | 4.0 | 0.0 |
| `Qwen/Qwen3-1.7B` | concurrency | 96 | 16 | 512 | done | 21.9 ms | 95.7% in 10–25 ms | 22.0 ms | 107.0 ms | 723.21 | 15.8 | 0.0 |
| `Qwen/Qwen3-1.7B` | concurrency | 96 | 32 | 512 | done | 28.6 ms | 93.4% in 25–50 ms | 28.5 ms | 161.8 ms | 1106.50 | 31.3 | 0.0 |
| `Qwen/Qwen3-1.7B` | concurrency | 96 | 64 | 512 | done | 37.6 ms | 98.2% in 25–50 ms | 37.2 ms | 274.1 ms | 1674.00 | 62.6 | 0.0 |
| `Qwen/Qwen3-1.7B` | concurrency | 96 | 128 | 512 | done | 57.4 ms | 79.0% in 50–75 ms | 57.4 ms | 392.9 ms | 2194.36 | 126.6 | 0.0 |
| `Qwen/Qwen3-1.7B` | cores | 24 | 8 | 512 | done | 24.4 ms | 85.9% in 10–25 ms | 24.4 ms | 100.0 ms | 326.32 | 7.8 | 0.0 |
| `Qwen/Qwen3-1.7B` | cores | 48 | 8 | 512 | done | 19.3 ms | 99.8% in 10–25 ms | 19.3 ms | 86.2 ms | 410.69 | 7.8 | 0.0 |
| `Qwen/Qwen3-1.7B` | cores | 72 | 8 | 512 | done | 18.0 ms | 99.9% in 10–25 ms | 18.0 ms | 92.1 ms | 441.44 | 7.9 | 0.0 |
| `Qwen/Qwen3-4B` | baseline | 96 | 8 | 512 | done | 35.6 ms | 99.8% in 25–50 ms | 35.6 ms | 151.0 ms | 223.21 | 7.9 | 0.0 |
| `Qwen/Qwen3-4B` | concurrency | 96 | 1 | 512 | done | 33.1 ms | 99.9% in 25–50 ms | 33.1 ms | 43.2 ms | 30.19 | 1.0 | 0.0 |
| `Qwen/Qwen3-4B` | concurrency | 96 | 2 | 512 | done | 33.1 ms | 99.9% in 25–50 ms | 33.1 ms | 83.0 ms | 60.30 | 2.0 | 0.0 |
| `Qwen/Qwen3-4B` | concurrency | 96 | 4 | 512 | done | 34.0 ms | 99.8% in 25–50 ms | 33.9 ms | 106.2 ms | 117.12 | 4.0 | 0.0 |
| `Qwen/Qwen3-4B` | concurrency | 96 | 16 | 512 | done | 38.0 ms | 99.9% in 25–50 ms | 38.1 ms | 193.7 ms | 417.26 | 15.8 | 0.0 |
| `Qwen/Qwen3-4B` | concurrency | 96 | 32 | 512 | done | 43.3 ms | 97.4% in 25–50 ms | 43.1 ms | 285.2 ms | 728.19 | 31.3 | 0.0 |
| `Qwen/Qwen3-4B` | concurrency | 96 | 64 | 512 | done | 66.8 ms | 95.2% in 50–75 ms | 67.1 ms | 479.7 ms | 942.98 | 62.6 | 0.0 |
| `Qwen/Qwen3-4B` | concurrency | 96 | 128 | 512 | done | 92.6 ms | 78.0% in 75–100 ms | 93.6 ms | 790.3 ms | 1356.83 | 125.2 | 0.0 |
| `Qwen/Qwen3-4B` | cores | 24 | 8 | 512 | done | 48.6 ms | 93.8% in 25–50 ms | 48.6 ms | 197.8 ms | 163.58 | 7.8 | 0.0 |
| `Qwen/Qwen3-4B` | cores | 48 | 8 | 512 | done | 36.0 ms | 99.8% in 25–50 ms | 36.1 ms | 154.1 ms | 220.56 | 7.8 | 0.0 |
| `Qwen/Qwen3-4B` | cores | 72 | 8 | 512 | done | 38.4 ms | 99.7% in 25–50 ms | 38.4 ms | 154.3 ms | 206.96 | 7.8 | 0.0 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | baseline | 96 | 8 | 512 | done | 10.6 ms | 75.1% in 10–25 ms | 10.5 ms | 47.3 ms | 750.88 | 7.9 | 0.0 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | concurrency | 96 | 1 | 512 | done | 9.0 ms | 90.9% in 0–10 ms | 9.0 ms | 14.6 ms | 111.16 | 1.0 | 0.0 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | concurrency | 96 | 2 | 512 | done | 9.7 ms | 79.7% in 0–10 ms | 9.7 ms | 26.1 ms | 206.26 | 2.0 | 0.0 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | concurrency | 96 | 4 | 512 | done | 10.2 ms | 68.3% in 0–10 ms | 10.2 ms | 32.5 ms | 391.03 | 4.0 | 0.0 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | concurrency | 96 | 16 | 512 | done | 11.8 ms | 99.9% in 10–25 ms | 11.8 ms | 60.8 ms | 1343.12 | 15.8 | 0.0 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | concurrency | 96 | 32 | 512 | done | 13.9 ms | 99.9% in 10–25 ms | 14.0 ms | 85.8 ms | 2266.68 | 31.3 | 0.0 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | concurrency | 96 | 64 | 512 | done | 19.7 ms | 98.2% in 10–25 ms | 19.7 ms | 134.4 ms | 3212.10 | 63.3 | 0.0 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | concurrency | 96 | 128 | 512 | done | 28.8 ms | 92.2% in 25–50 ms | 28.9 ms | 219.4 ms | 4369.11 | 125.2 | 0.0 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | cores | 24 | 8 | 512 | done | 12.7 ms | 99.9% in 10–25 ms | 12.7 ms | 55.3 ms | 627.57 | 7.8 | 0.0 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | cores | 48 | 8 | 512 | done | 10.5 ms | 98.3% in 10–25 ms | 10.5 ms | 44.0 ms | 757.17 | 7.9 | 0.0 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | cores | 72 | 8 | 512 | done | 10.7 ms | 99.9% in 10–25 ms | 10.6 ms | 48.1 ms | 745.71 | 7.8 | 0.0 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | baseline | 96 | 8 | 512 | done | 20.1 ms | 97.9% in 10–25 ms | 20.2 ms | 106.7 ms | 394.51 | 7.8 | 0.0 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | concurrency | 96 | 1 | 512 | done | 17.6 ms | 99.6% in 10–25 ms | 17.6 ms | 26.0 ms | 56.69 | 1.0 | 0.0 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | concurrency | 96 | 2 | 512 | done | 18.4 ms | 98.9% in 10–25 ms | 18.4 ms | 45.1 ms | 108.48 | 2.0 | 0.0 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | concurrency | 96 | 4 | 512 | done | 19.2 ms | 98.5% in 10–25 ms | 19.2 ms | 65.2 ms | 206.86 | 3.9 | 0.0 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | concurrency | 96 | 16 | 512 | done | 22.3 ms | 94.4% in 10–25 ms | 22.3 ms | 143.8 ms | 710.78 | 15.7 | 0.0 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | concurrency | 96 | 32 | 512 | done | 26.3 ms | 66.9% in 25–50 ms | 26.3 ms | 162.2 ms | 1203.21 | 31.3 | 0.0 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | concurrency | 96 | 64 | 512 | done | 49.8 ms | 55.1% in 25–50 ms | 50.1 ms | 275.8 ms | 1271.48 | 62.6 | 0.0 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | concurrency | 96 | 128 | 512 | done | 65.9 ms | 90.2% in 50–75 ms | 66.7 ms | 458.9 ms | 1914.34 | 125.2 | 0.0 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | cores | 24 | 8 | 512 | done | 25.6 ms | 72.5% in 25–50 ms | 25.6 ms | 121.0 ms | 310.16 | 7.9 | 0.0 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | cores | 48 | 8 | 512 | done | 20.6 ms | 99.3% in 10–25 ms | 20.6 ms | 94.9 ms | 385.90 | 7.9 | 0.0 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | cores | 72 | 8 | 512 | done | 20.2 ms | 99.7% in 10–25 ms | 20.2 ms | 105.9 ms | 392.30 | 7.8 | 0.0 |
| `ibm-granite/granite-3.2-2b-instruct` | baseline | 96 | 8 | 512 | done | 30.7 ms | 99.8% in 25–50 ms | 30.8 ms | 106.7 ms | 258.88 | 7.9 | 0.0 |
| `ibm-granite/granite-3.2-2b-instruct` | concurrency | 96 | 1 | 512 | done | 24.0 ms | 79.6% in 10–25 ms | 24.0 ms | 32.5 ms | 41.62 | 1.0 | 0.0 |
| `ibm-granite/granite-3.2-2b-instruct` | concurrency | 96 | 2 | 512 | done | 29.3 ms | 99.9% in 25–50 ms | 29.3 ms | 60.5 ms | 68.06 | 2.0 | 0.0 |
| `ibm-granite/granite-3.2-2b-instruct` | concurrency | 96 | 4 | 512 | done | 29.3 ms | 99.9% in 25–50 ms | 29.3 ms | 85.7 ms | 135.79 | 3.8 | 0.0 |
| `ibm-granite/granite-3.2-2b-instruct` | concurrency | 96 | 16 | 512 | done | 28.8 ms | 99.9% in 25–50 ms | 28.7 ms | 146.6 ms | 550.06 | 15.5 | 0.0 |
| `ibm-granite/granite-3.2-2b-instruct` | concurrency | 96 | 32 | 512 | done | 33.2 ms | 99.8% in 25–50 ms | 33.3 ms | 214.0 ms | 951.13 | 31.6 | 0.0 |
| `ibm-granite/granite-3.2-2b-instruct` | concurrency | 96 | 64 | 512 | done | 46.0 ms | 91.2% in 25–50 ms | 46.3 ms | 397.8 ms | 1366.82 | 61.9 | 0.0 |
| `ibm-granite/granite-3.2-2b-instruct` | concurrency | 96 | 128 | 512 | done | 66.4 ms | 94.6% in 50–75 ms | 66.9 ms | 575.1 ms | 1890.14 | 125.2 | 0.0 |
| `ibm-granite/granite-3.2-2b-instruct` | cores | 24 | 8 | 512 | done | 34.1 ms | 99.9% in 25–50 ms | 34.1 ms | 145.0 ms | 232.63 | 7.8 | 0.0 |
| `ibm-granite/granite-3.2-2b-instruct` | cores | 48 | 8 | 512 | done | 26.9 ms | 99.9% in 25–50 ms | 26.9 ms | 118.5 ms | 295.58 | 7.9 | 0.0 |
| `ibm-granite/granite-3.2-2b-instruct` | cores | 72 | 8 | 512 | done | 25.5 ms | 63.9% in 25–50 ms | 25.5 ms | 113.2 ms | 311.57 | 7.8 | 0.0 |

### Same numbers, server versus client

| Config | ITL mean | ITL n | coarse ITL p50 | coarse ITL p90 | client TPOT min | client TPOT median | client TPOT p90 | complete requests |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `node0_cores096_clients001_gen0512` | 9.9 ms | 9028 | 6.5 ms | 18.4 ms | 9.7 ms | 9.9 ms | 10.0 ms | 18 |
| `node0_cores096_clients002_gen0512` | 17.2 ms | 10357 | 17.5 ms | 23.5 ms | 17.1 ms | 17.2 ms | 17.3 ms | 22 |
| `node0_cores096_clients004_gen0512` | 17.9 ms | 19881 | 17.5 ms | 23.6 ms | 17.8 ms | 17.9 ms | 18.0 ms | 40 |
| `node0_cores024_clients008_gen0512` | 11.6 ms | 61489 | 17.5 ms | 23.5 ms | 11.5 ms | 11.5 ms | 11.7 ms | 128 |
| `node0_cores048_clients008_gen0512` | 23.0 ms | 30954 | 17.8 ms | 24.1 ms | 22.8 ms | 23.1 ms | 23.2 ms | 64 |
| `node0_cores072_clients008_gen0512` | 32.9 ms | 21715 | 37.5 ms | 47.5 ms | 32.7 ms | 32.9 ms | 33.1 ms | 40 |
| `node0_cores096_clients008_gen0512` | 20.0 ms | 35700 | 17.8 ms | 24.0 ms | 18.4 ms | 18.7 ms | 25.0 ms | 72 |
| `node0_cores096_clients016_gen0512` | 20.0 ms | 71313 | 17.6 ms | 23.8 ms | 19.7 ms | 19.9 ms | 20.4 ms | 144 |
| `node0_cores096_clients032_gen0512` | 21.7 ms | 131169 | 17.7 ms | 23.9 ms | 21.5 ms | 21.6 ms | 21.8 ms | 256 |
| `node0_cores096_clients064_gen0512` | 29.2 ms | 194945 | 37.5 ms | 47.5 ms | 29.0 ms | 29.2 ms | 29.3 ms | 384 |
| `node0_cores096_clients128_gen0512` | 33.8 ms | 334465 | 37.5 ms | 47.5 ms | 33.4 ms | 33.9 ms | 34.0 ms | 640 |
| `node0_cores096_clients001_gen0512` | 17.2 ms | 5192 | 17.5 ms | 23.5 ms | 17.1 ms | 17.2 ms | 17.3 ms | 11 |
| `node0_cores096_clients002_gen0512` | 20.6 ms | 8651 | 17.7 ms | 23.8 ms | 20.5 ms | 20.6 ms | 20.8 ms | 18 |
| `node0_cores096_clients004_gen0512` | 21.2 ms | 16801 | 17.7 ms | 23.9 ms | 21.1 ms | 21.2 ms | 21.4 ms | 32 |
| `node0_cores024_clients008_gen0512` | 24.4 ms | 29201 | 18.7 ms | 32.4 ms | 24.1 ms | 24.4 ms | 24.4 ms | 56 |
| `node0_cores048_clients008_gen0512` | 19.3 ms | 36792 | 17.5 ms | 23.5 ms | 19.3 ms | 19.3 ms | 19.4 ms | 72 |
| `node0_cores072_clients008_gen0512` | 18.0 ms | 39530 | 17.5 ms | 23.5 ms | 17.9 ms | 18.0 ms | 18.1 ms | 80 |
| `node0_cores096_clients008_gen0512` | 22.5 ms | 31601 | 17.9 ms | 24.2 ms | 22.4 ms | 22.5 ms | 22.8 ms | 64 |
| `node0_cores096_clients016_gen0512` | 21.9 ms | 64769 | 17.8 ms | 24.1 ms | 21.7 ms | 22.0 ms | 22.2 ms | 128 |
| `node0_cores096_clients032_gen0512` | 28.6 ms | 99073 | 36.6 ms | 47.4 ms | 27.5 ms | 28.5 ms | 28.8 ms | 192 |
| `node0_cores096_clients064_gen0512` | 37.6 ms | 150148 | 37.7 ms | 47.9 ms | 36.8 ms | 37.2 ms | 43.6 ms | 256 |
| `node0_cores096_clients128_gen0512` | 57.4 ms | 196481 | 59.4 ms | 72.1 ms | 49.3 ms | 57.4 ms | 57.5 ms | 384 |
| `node0_cores096_clients001_gen0512` | 33.1 ms | 2703 | 37.5 ms | 47.5 ms | 32.9 ms | 33.1 ms | 33.2 ms | 5 |
| `node0_cores096_clients002_gen0512` | 33.1 ms | 5397 | 37.5 ms | 47.5 ms | 33.0 ms | 33.1 ms | 33.1 ms | 10 |
| `node0_cores096_clients004_gen0512` | 34.0 ms | 10481 | 37.5 ms | 47.5 ms | 33.7 ms | 33.9 ms | 34.2 ms | 20 |
| `node0_cores024_clients008_gen0512` | 48.6 ms | 14642 | 38.3 ms | 49.0 ms | 48.5 ms | 48.6 ms | 48.9 ms | 24 |
| `node0_cores048_clients008_gen0512` | 36.0 ms | 19746 | 37.5 ms | 47.5 ms | 35.9 ms | 36.1 ms | 36.2 ms | 40 |
| `node0_cores072_clients008_gen0512` | 38.4 ms | 18530 | 37.5 ms | 47.6 ms | 38.3 ms | 38.4 ms | 38.5 ms | 32 |
| `node0_cores096_clients008_gen0512` | 35.6 ms | 19985 | 37.5 ms | 47.5 ms | 35.5 ms | 35.6 ms | 35.8 ms | 40 |
| `node0_cores096_clients016_gen0512` | 38.0 ms | 37361 | 37.5 ms | 47.5 ms | 37.9 ms | 38.1 ms | 38.3 ms | 64 |
| `node0_cores096_clients032_gen0512` | 43.3 ms | 65313 | 37.8 ms | 48.1 ms | 40.7 ms | 43.1 ms | 43.6 ms | 128 |
| `node0_cores096_clients064_gen0512` | 66.8 ms | 84484 | 63.1 ms | 73.6 ms | 65.6 ms | 67.1 ms | 68.2 ms | 128 |
| `node0_cores096_clients128_gen0512` | 92.6 ms | 121603 | 91.0 ms | 127.4 ms | 93.3 ms | 93.6 ms | 93.6 ms | 256 |
| `node0_cores096_clients001_gen0512` | 9.0 ms | 9950 | 5.5 ms | 9.9 ms | 8.8 ms | 9.0 ms | 9.1 ms | 20 |
| `node0_cores096_clients002_gen0512` | 9.7 ms | 18455 | 6.3 ms | 17.6 ms | 9.6 ms | 9.7 ms | 9.7 ms | 38 |
| `node0_cores096_clients004_gen0512` | 10.2 ms | 34997 | 7.3 ms | 20.3 ms | 10.0 ms | 10.2 ms | 10.3 ms | 72 |
| `node0_cores024_clients008_gen0512` | 12.7 ms | 56169 | 17.5 ms | 23.5 ms | 12.6 ms | 12.7 ms | 12.7 ms | 112 |
| `node0_cores048_clients008_gen0512` | 10.5 ms | 67777 | 17.4 ms | 23.5 ms | 10.4 ms | 10.5 ms | 10.6 ms | 136 |
| `node0_cores072_clients008_gen0512` | 10.7 ms | 66754 | 17.5 ms | 23.5 ms | 10.6 ms | 10.6 ms | 10.8 ms | 136 |
| `node0_cores096_clients008_gen0512` | 10.6 ms | 67211 | 15.0 ms | 23.0 ms | 10.4 ms | 10.5 ms | 10.7 ms | 136 |
| `node0_cores096_clients016_gen0512` | 11.8 ms | 120241 | 17.5 ms | 23.5 ms | 11.7 ms | 11.8 ms | 12.0 ms | 240 |
| `node0_cores096_clients032_gen0512` | 13.9 ms | 203009 | 17.5 ms | 23.5 ms | 13.9 ms | 14.0 ms | 14.0 ms | 416 |
| `node0_cores096_clients064_gen0512` | 19.7 ms | 287745 | 17.6 ms | 23.8 ms | 19.5 ms | 19.7 ms | 20.5 ms | 576 |
| `node0_cores096_clients128_gen0512` | 28.8 ms | 392448 | 36.5 ms | 47.3 ms | 27.3 ms | 28.9 ms | 29.0 ms | 768 |
| `node0_cores096_clients001_gen0512` | 17.6 ms | 5074 | 17.5 ms | 23.6 ms | 17.5 ms | 17.6 ms | 17.8 ms | 10 |
| `node0_cores096_clients002_gen0512` | 18.4 ms | 9709 | 17.6 ms | 23.6 ms | 18.2 ms | 18.4 ms | 18.5 ms | 20 |
| `node0_cores096_clients004_gen0512` | 19.2 ms | 18513 | 17.6 ms | 23.7 ms | 19.0 ms | 19.2 ms | 19.5 ms | 36 |
| `node0_cores024_clients008_gen0512` | 25.6 ms | 27762 | 32.8 ms | 46.6 ms | 25.5 ms | 25.6 ms | 25.8 ms | 56 |
| `node0_cores048_clients008_gen0512` | 20.6 ms | 34547 | 17.6 ms | 23.6 ms | 20.5 ms | 20.6 ms | 20.7 ms | 72 |
| `node0_cores072_clients008_gen0512` | 20.2 ms | 35107 | 17.5 ms | 23.5 ms | 20.2 ms | 20.2 ms | 20.4 ms | 72 |
| `node0_cores096_clients008_gen0512` | 20.1 ms | 35322 | 17.7 ms | 23.8 ms | 20.0 ms | 20.2 ms | 20.3 ms | 72 |
| `node0_cores096_clients016_gen0512` | 22.3 ms | 63634 | 17.9 ms | 24.3 ms | 22.0 ms | 22.3 ms | 22.6 ms | 128 |
| `node0_cores096_clients032_gen0512` | 26.3 ms | 107809 | 31.4 ms | 46.3 ms | 26.2 ms | 26.3 ms | 26.7 ms | 224 |
| `node0_cores096_clients064_gen0512` | 49.8 ms | 113857 | 47.7 ms | 69.5 ms | 49.0 ms | 50.1 ms | 50.4 ms | 192 |
| `node0_cores096_clients128_gen0512` | 65.9 ms | 171523 | 63.9 ms | 74.9 ms | 65.4 ms | 66.7 ms | 67.0 ms | 256 |
| `node0_cores096_clients001_gen0512` | 24.0 ms | 3725 | 19.4 ms | 37.8 ms | 23.9 ms | 24.0 ms | 24.1 ms | 7 |
| `node0_cores096_clients002_gen0512` | 29.3 ms | 6091 | 37.5 ms | 47.5 ms | 29.2 ms | 29.3 ms | 29.5 ms | 12 |
| `node0_cores096_clients004_gen0512` | 29.3 ms | 12153 | 37.5 ms | 47.5 ms | 29.1 ms | 29.3 ms | 29.6 ms | 24 |
| `node0_cores024_clients008_gen0512` | 34.1 ms | 20809 | 37.5 ms | 47.5 ms | 33.9 ms | 34.1 ms | 34.2 ms | 40 |
| `node0_cores048_clients008_gen0512` | 26.9 ms | 26458 | 37.5 ms | 47.5 ms | 26.8 ms | 26.9 ms | 27.0 ms | 56 |
| `node0_cores072_clients008_gen0512` | 25.5 ms | 27881 | 30.5 ms | 46.1 ms | 25.3 ms | 25.5 ms | 25.7 ms | 56 |
| `node0_cores096_clients008_gen0512` | 30.7 ms | 23163 | 37.5 ms | 47.5 ms | 30.6 ms | 30.8 ms | 31.0 ms | 48 |
| `node0_cores096_clients016_gen0512` | 28.8 ms | 49217 | 37.5 ms | 47.5 ms | 28.5 ms | 28.7 ms | 29.2 ms | 96 |
| `node0_cores096_clients032_gen0512` | 33.2 ms | 85122 | 37.5 ms | 47.5 ms | 32.4 ms | 33.3 ms | 33.7 ms | 160 |
| `node0_cores096_clients064_gen0512` | 46.0 ms | 122502 | 38.7 ms | 49.7 ms | 46.0 ms | 46.3 ms | 46.4 ms | 256 |
| `node0_cores096_clients128_gen0512` | 66.4 ms | 169473 | 63.2 ms | 73.8 ms | 65.8 ms | 66.9 ms | 67.3 ms | 256 |

## Trend

On `Qwen/Qwen2.5-0.5B-Instruct`, 96 cores, 512 generated tokens, one client produces one token every **9.9 ms** (100.90 tokens/s).

| Clients | ITL mean | ITL vs 1-client | Tokens/s | Tokens/s vs linear | TTFT median | Mean running | Mean waiting | Step batch (iteration tokens) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 9.9 ms | 1.00× | 100.90 | 100.00% | 24.1 ms | 1.0 | 0.0 | 1.06 |
| 2 | 17.2 ms | 1.74× | 115.77 | 57.37% | 41.0 ms | 2.0 | 0.0 | 2.13 |
| 4 | 17.9 ms | 1.82× | 222.10 | 55.03% | 45.2 ms | 3.9 | 0.0 | 4.25 |
| 8 | 20.0 ms | 2.02× | 399.07 | 49.44% | 54.6 ms | 7.9 | 0.0 | 8.50 |
| 16 | 20.0 ms | 2.02× | 796.81 | 49.36% | 65.4 ms | 15.8 | 0.0 | 17.00 |
| 32 | 21.7 ms | 2.19× | 1465.97 | 45.40% | 87.7 ms | 31.6 | 0.0 | 34.17 |
| 64 | 29.2 ms | 2.95× | 2176.01 | 33.70% | 124.6 ms | 61.2 | 0.0 | 67.89 |
| 128 | 33.8 ms | 3.43× | 3734.77 | 28.92% | 189.1 ms | 123.7 | 0.0 | 137.07 |

The scheduler keeps every client in the running set and the waiting set at zero, so the extra delay is not a queue. `iteration_tokens_total` grows almost one-for-one with concurrency: each engine step decodes the whole batch, and every request in that run sees the same TPOT.

Through 1 clients the step stays flat at 9.9–9.9 ms, and tokens/s stay near the 1-client line.
The step then lengthens: 2 clients at 17.2 ms (57.37% of linear, 115.77 tokens/s); 4 clients at 17.9 ms (55.03% of linear, 222.10 tokens/s); 8 clients at 20.0 ms (49.44% of linear, 399.07 tokens/s); 16 clients at 20.0 ms (49.36% of linear, 796.81 tokens/s); 32 clients at 21.7 ms (45.40% of linear, 1465.97 tokens/s); 64 clients at 29.2 ms (33.70% of linear, 2176.01 tokens/s); 128 clients at 33.8 ms (28.92% of linear, 3734.77 tokens/s). These runs have no OpenMP warning #124. Each selected core has one compute thread, so a longer step is a more expensive batch, not a collapsed affinity mask.

Time to first token rises with concurrency on the 96-core runs. Client TTFT median goes from 24.1 ms at 1 client to 189.1 ms at 128 clients. Server `time_to_first_token_seconds` matches that rise. Waiting requests stay at zero, so this is batch service time. On these 96-core points the request-finish histograms stay empty, because a request does not complete inside the window.

## Core count, same 8 clients

8 clients, 512 generated tokens. Compared inside one model.

| Model | Cores | ITL mean | Client TPOT | Tokens/s | Complete requests | Request TPOT mean | Decode time mean | Server TTFT |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `Qwen/Qwen2.5-0.5B-Instruct` | 24 | 11.6 ms | 11.5 ms | 687.39 | 128 | 11.6 ms | 5909.6 ms | 43.5 ms |
| `Qwen/Qwen2.5-0.5B-Instruct` | 48 | 23.0 ms | 23.1 ms | 345.36 | 64 | 23.0 ms | 11.8 s | 74.9 ms |
| `Qwen/Qwen2.5-0.5B-Instruct` | 72 | 32.9 ms | 32.9 ms | 242.26 | 40 | 32.9 ms | 16.8 s | 93.3 ms |
| `Qwen/Qwen2.5-0.5B-Instruct` | 96 | 20.0 ms | 18.7 ms | 399.07 | 72 | 20.1 ms | 10.3 s | 56.4 ms |
| `Qwen/Qwen3-1.7B` | 24 | 24.4 ms | 24.4 ms | 326.32 | 56 | 24.4 ms | 12.5 s | 96.0 ms |
| `Qwen/Qwen3-1.7B` | 48 | 19.3 ms | 19.3 ms | 410.69 | 72 | 19.3 ms | 9881.0 ms | 81.2 ms |
| `Qwen/Qwen3-1.7B` | 72 | 18.0 ms | 18.0 ms | 441.44 | 80 | 18.0 ms | 9192.3 ms | 90.0 ms |
| `Qwen/Qwen3-1.7B` | 96 | 22.5 ms | 22.5 ms | 352.90 | 64 | 22.5 ms | 11.5 s | 77.3 ms |
| `Qwen/Qwen3-4B` | 24 | 48.6 ms | 48.6 ms | 163.58 | 24 | 48.7 ms | 24.9 s | 189.2 ms |
| `Qwen/Qwen3-4B` | 48 | 36.0 ms | 36.1 ms | 220.56 | 40 | 36.1 ms | 18.4 s | 149.3 ms |
| `Qwen/Qwen3-4B` | 72 | 38.4 ms | 38.4 ms | 206.96 | 32 | 38.4 ms | 19.6 s | 150.5 ms |
| `Qwen/Qwen3-4B` | 96 | 35.6 ms | 35.6 ms | 223.21 | 40 | 35.6 ms | 18.2 s | 141.4 ms |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | 24 | 12.7 ms | 12.7 ms | 627.57 | 112 | 12.7 ms | 6474.1 ms | 51.7 ms |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | 48 | 10.5 ms | 10.5 ms | 757.17 | 136 | 10.5 ms | 5365.6 ms | 41.0 ms |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | 72 | 10.7 ms | 10.6 ms | 745.71 | 136 | 10.7 ms | 5443.6 ms | 45.5 ms |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | 96 | 10.6 ms | 10.5 ms | 750.88 | 136 | 10.6 ms | 5408.4 ms | 43.4 ms |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | 24 | 25.6 ms | 25.6 ms | 310.16 | 56 | 25.6 ms | 13.1 s | 107.9 ms |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | 48 | 20.6 ms | 20.6 ms | 385.90 | 72 | 20.6 ms | 10.5 s | 84.7 ms |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | 72 | 20.2 ms | 20.2 ms | 392.30 | 72 | 20.3 ms | 10.4 s | 94.5 ms |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | 96 | 20.1 ms | 20.2 ms | 394.51 | 72 | 20.1 ms | 10.3 s | 98.7 ms |
| `ibm-granite/granite-3.2-2b-instruct` | 24 | 34.1 ms | 34.1 ms | 232.63 | 40 | 34.1 ms | 17.4 s | 139.4 ms |
| `ibm-granite/granite-3.2-2b-instruct` | 48 | 26.9 ms | 26.9 ms | 295.58 | 56 | 26.9 ms | 13.7 s | 112.6 ms |
| `ibm-granite/granite-3.2-2b-instruct` | 72 | 25.5 ms | 25.5 ms | 311.57 | 56 | 25.5 ms | 13.0 s | 110.7 ms |
| `ibm-granite/granite-3.2-2b-instruct` | 96 | 30.7 ms | 30.8 ms | 258.88 | 48 | 30.7 ms | 15.7 s | 101.6 ms |

For `Qwen/Qwen2.5-0.5B-Instruct`, 24 cores finished at 11.6 ms/token and 687.39 tokens/s. 128 requests completed inside the 90-second window. 72 cores at the same concurrency was 32.9 ms/token and 242.26 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `Qwen/Qwen3-1.7B`, 72 cores finished at 18.0 ms/token and 441.44 tokens/s. 80 requests completed inside the 90-second window. 24 cores at the same concurrency was 24.4 ms/token and 326.32 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `Qwen/Qwen3-4B`, 96 cores finished at 35.6 ms/token and 223.21 tokens/s. 40 requests completed inside the 90-second window. 24 cores at the same concurrency was 48.6 ms/token and 163.58 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8`, 48 cores finished at 10.5 ms/token and 757.17 tokens/s. 136 requests completed inside the 90-second window. 24 cores at the same concurrency was 12.7 ms/token and 627.57 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8`, 96 cores finished at 20.1 ms/token and 394.51 tokens/s. 72 requests completed inside the 90-second window. 24 cores at the same concurrency was 25.6 ms/token and 310.16 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `ibm-granite/granite-3.2-2b-instruct`, 72 cores finished at 25.5 ms/token and 311.57 tokens/s. 56 requests completed inside the 90-second window. 24 cores at the same concurrency was 34.1 ms/token and 232.63 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

## Thread pinning

All 66 attempts with a server log are free of OpenMP warning #124. The server process is started with `numactl --physcpubind=0-(N-1) --membind=0`, and vLLM re-execs the worker under the same CPU list. Generated tokens are fixed at 512.

This 0.5B path is manual BF16, not a Xeon 6 recipe. AMX-busy time across finished runs is 0.02%–4.21% of counted cycles. It rises with batch size and is still a small slice of the step. IPC stays near 0.38–0.88.

Reported DRAM bandwidth in `system.csv` is about 0.0002 GB/s. A 0.5B BF16 model is about 1 GB of weights, larger than this socket's share of the 960 MiB L3, so a real decode should move on the order of gigabytes per second. The IMC CAS counts are tens of events per 100 ms interval. Treat the bandwidth column as not yet measuring this workload. It is not evidence that decode is cache-resident.

## Other vLLM series

| Config | Server TTFT mean | TTFT n | Queue mean | Prefill n | Decode-time n | Request TPOT n | E2E n | KV cache mean | IPC | AMX busy | L3 stall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `node0_cores096_clients001_gen0512` | 22.8 ms | 18 | 0.0 ms | 17 | 17 | 17 | 17 | 0.00006 | 0.883 | 0.03% | 10.45% |
| `node0_cores096_clients002_gen0512` | 38.3 ms | 22 | 0.0 ms | 20 | 20 | 20 | 20 | 0.00012 | 0.695 | 0.04% | 5.72% |
| `node0_cores096_clients004_gen0512` | 46.4 ms | 40 | 0.0 ms | 36 | 36 | 36 | 36 | 0.00024 | 0.692 | 0.07% | 5.68% |
| `node0_cores024_clients008_gen0512` | 43.5 ms | 128 | 0.0 ms | 120 | 120 | 120 | 120 | 0.00048 | 0.717 | 0.85% | 25.60% |
| `node0_cores048_clients008_gen0512` | 74.9 ms | 64 | 0.0 ms | 56 | 56 | 56 | 56 | 0.00048 | 0.693 | 0.22% | 16.55% |
| `node0_cores072_clients008_gen0512` | 93.3 ms | 48 | 0.0 ms | 40 | 40 | 40 | 40 | 0.00048 | 0.674 | 0.10% | 9.48% |
| `node0_cores096_clients008_gen0512` | 56.4 ms | 72 | 0.0 ms | 64 | 64 | 64 | 64 | 0.00050 | 0.716 | 0.13% | 5.50% |
| `node0_cores096_clients016_gen0512` | 65.4 ms | 144 | 0.0 ms | 128 | 128 | 128 | 128 | 0.00098 | 0.699 | 0.26% | 6.07% |
| `node0_cores096_clients032_gen0512` | 84.9 ms | 288 | 0.1 ms | 256 | 256 | 256 | 256 | 0.00202 | 0.712 | 0.48% | 6.90% |
| `node0_cores096_clients064_gen0512` | 120.5 ms | 384 | 0.1 ms | 320 | 320 | 320 | 320 | 0.00379 | 0.697 | 0.72% | 4.55% |
| `node0_cores096_clients128_gen0512` | 171.9 ms | 768 | 0.2 ms | 640 | 640 | 640 | 640 | 0.00768 | 0.752 | 1.33% | 6.19% |
| `node0_cores096_clients001_gen0512` | 25.8 ms | 11 | 0.0 ms | 10 | 10 | 10 | 10 | 0.00057 | 0.576 | 0.07% | 41.67% |
| `node0_cores096_clients002_gen0512` | 46.0 ms | 18 | 0.0 ms | 16 | 16 | 16 | 16 | 0.00116 | 0.571 | 0.11% | 35.74% |
| `node0_cores096_clients004_gen0512` | 57.3 ms | 36 | 0.0 ms | 32 | 32 | 32 | 32 | 0.00226 | 0.576 | 0.22% | 35.42% |
| `node0_cores024_clients008_gen0512` | 96.0 ms | 64 | 0.0 ms | 56 | 56 | 56 | 56 | 0.00456 | 0.477 | 1.42% | 51.90% |
| `node0_cores048_clients008_gen0512` | 81.2 ms | 72 | 0.0 ms | 72 | 72 | 72 | 72 | 0.00455 | 0.534 | 0.91% | 45.14% |
| `node0_cores072_clients008_gen0512` | 90.0 ms | 80 | 0.0 ms | 72 | 72 | 72 | 72 | 0.00456 | 0.574 | 0.68% | 41.63% |
| `node0_cores096_clients008_gen0512` | 77.3 ms | 64 | 0.0 ms | 56 | 56 | 56 | 56 | 0.00462 | 0.574 | 0.41% | 35.19% |
| `node0_cores096_clients016_gen0512` | 104.9 ms | 128 | 0.0 ms | 112 | 112 | 112 | 112 | 0.00945 | 0.568 | 0.85% | 40.27% |
| `node0_cores096_clients032_gen0512` | 160.2 ms | 224 | 0.1 ms | 192 | 192 | 192 | 192 | 0.01869 | 0.587 | 1.30% | 34.20% |
| `node0_cores096_clients064_gen0512` | 268.0 ms | 320 | 0.1 ms | 256 | 256 | 256 | 256 | 0.03755 | 0.584 | 2.08% | 25.95% |
| `node0_cores096_clients128_gen0512` | 386.5 ms | 512 | 0.2 ms | 384 | 384 | 384 | 384 | 0.07689 | 0.547 | 2.90% | 29.87% |
| `node0_cores096_clients001_gen0512` | 41.2 ms | 6 | 0.0 ms | 5 | 5 | 5 | 5 | 0.00073 | 0.496 | 0.08% | 50.50% |
| `node0_cores096_clients002_gen0512` | 77.5 ms | 12 | 0.0 ms | 10 | 10 | 10 | 10 | 0.00144 | 0.479 | 0.17% | 52.02% |
| `node0_cores096_clients004_gen0512` | 101.2 ms | 24 | 0.0 ms | 20 | 20 | 20 | 20 | 0.00292 | 0.488 | 0.33% | 51.09% |
| `node0_cores024_clients008_gen0512` | 189.2 ms | 32 | 0.0 ms | 24 | 24 | 24 | 24 | 0.00567 | 0.384 | 1.68% | 61.66% |
| `node0_cores048_clients008_gen0512` | 149.3 ms | 40 | 0.0 ms | 32 | 32 | 32 | 32 | 0.00583 | 0.441 | 1.15% | 55.35% |
| `node0_cores072_clients008_gen0512` | 150.5 ms | 40 | 0.0 ms | 32 | 32 | 32 | 32 | 0.00567 | 0.494 | 0.76% | 48.73% |
| `node0_cores096_clients008_gen0512` | 141.4 ms | 40 | 0.0 ms | 32 | 32 | 32 | 32 | 0.00591 | 0.494 | 0.61% | 50.31% |
| `node0_cores096_clients016_gen0512` | 197.7 ms | 80 | 0.0 ms | 64 | 64 | 64 | 64 | 0.01163 | 0.494 | 1.16% | 49.51% |
| `node0_cores096_clients032_gen0512` | 301.4 ms | 128 | 0.1 ms | 96 | 96 | 96 | 96 | 0.02423 | 0.485 | 2.03% | 47.82% |
| `node0_cores096_clients064_gen0512` | 488.2 ms | 192 | 0.1 ms | 128 | 128 | 128 | 128 | 0.04554 | 0.544 | 2.88% | 27.91% |
| `node0_cores096_clients128_gen0512` | 803.5 ms | 256 | 0.2 ms | 128 | 128 | 128 | 128 | 0.09344 | 0.520 | 4.21% | 26.25% |
| `node0_cores096_clients001_gen0512` | 13.9 ms | 20 | 0.0 ms | 19 | 19 | 19 | 19 | 0.00017 | 0.810 | 0.02% | 21.93% |
| `node0_cores096_clients002_gen0512` | 24.9 ms | 38 | 0.0 ms | 36 | 36 | 36 | 36 | 0.00032 | 0.816 | 0.04% | 20.95% |
| `node0_cores096_clients004_gen0512` | 31.8 ms | 72 | 0.0 ms | 68 | 68 | 68 | 68 | 0.00066 | 0.825 | 0.08% | 20.47% |
| `node0_cores024_clients008_gen0512` | 51.7 ms | 112 | 0.0 ms | 104 | 104 | 104 | 104 | 0.00127 | 0.618 | 1.17% | 38.16% |
| `node0_cores048_clients008_gen0512` | 41.0 ms | 136 | 0.0 ms | 128 | 128 | 128 | 128 | 0.00131 | 0.713 | 0.72% | 28.47% |
| `node0_cores072_clients008_gen0512` | 45.5 ms | 136 | 0.0 ms | 128 | 128 | 128 | 128 | 0.00128 | 0.775 | 0.49% | 22.53% |
| `node0_cores096_clients008_gen0512` | 43.4 ms | 136 | 0.0 ms | 128 | 128 | 128 | 128 | 0.00132 | 0.786 | 0.37% | 21.35% |
| `node0_cores096_clients016_gen0512` | 56.6 ms | 240 | 0.0 ms | 224 | 224 | 224 | 224 | 0.00262 | 0.788 | 0.67% | 21.01% |
| `node0_cores096_clients032_gen0512` | 81.3 ms | 416 | 0.1 ms | 384 | 384 | 384 | 384 | 0.00527 | 0.780 | 1.13% | 21.07% |
| `node0_cores096_clients064_gen0512` | 123.6 ms | 576 | 0.1 ms | 512 | 512 | 512 | 512 | 0.01081 | 0.752 | 1.70% | 15.77% |
| `node0_cores096_clients128_gen0512` | 195.9 ms | 768 | 0.2 ms | 768 | 768 | 768 | 768 | 0.02153 | 0.746 | 2.35% | 15.78% |
| `node0_cores096_clients001_gen0512` | 24.1 ms | 10 | 0.0 ms | 9 | 9 | 9 | 9 | 0.00058 | 0.606 | 0.02% | 41.01% |
| `node0_cores096_clients002_gen0512` | 47.0 ms | 20 | 0.0 ms | 18 | 18 | 18 | 18 | 0.00115 | 0.636 | 0.04% | 38.43% |
| `node0_cores096_clients004_gen0512` | 64.2 ms | 40 | 0.0 ms | 36 | 36 | 36 | 36 | 0.00226 | 0.656 | 0.07% | 36.72% |
| `node0_cores024_clients008_gen0512` | 107.9 ms | 56 | 0.0 ms | 48 | 48 | 48 | 48 | 0.00463 | 0.481 | 1.42% | 51.23% |
| `node0_cores048_clients008_gen0512` | 84.7 ms | 72 | 0.0 ms | 64 | 64 | 64 | 64 | 0.00462 | 0.557 | 0.90% | 43.42% |
| `node0_cores072_clients008_gen0512` | 94.5 ms | 72 | 0.0 ms | 64 | 64 | 64 | 64 | 0.00454 | 0.636 | 0.63% | 35.82% |
| `node0_cores096_clients008_gen0512` | 98.7 ms | 72 | 0.0 ms | 64 | 64 | 64 | 64 | 0.00457 | 0.596 | 0.49% | 39.04% |
| `node0_cores096_clients016_gen0512` | 134.6 ms | 128 | 0.0 ms | 112 | 112 | 112 | 112 | 0.00916 | 0.594 | 0.88% | 38.68% |
| `node0_cores096_clients032_gen0512` | 157.3 ms | 224 | 0.1 ms | 192 | 192 | 192 | 192 | 0.01854 | 0.585 | 1.49% | 38.13% |
| `node0_cores096_clients064_gen0512` | 278.0 ms | 256 | 0.1 ms | 192 | 192 | 192 | 192 | 0.03586 | 0.568 | 1.75% | 24.06% |
| `node0_cores096_clients128_gen0512` | 429.3 ms | 384 | 0.2 ms | 256 | 256 | 256 | 256 | 0.07143 | 0.534 | 2.65% | 25.46% |
| `node0_cores096_clients001_gen0512` | 31.2 ms | 8 | 0.0 ms | 7 | 7 | 7 | 7 | 0.00041 | 0.548 | 0.07% | 44.55% |
| `node0_cores096_clients002_gen0512` | 55.4 ms | 12 | 0.0 ms | 10 | 10 | 10 | 10 | 0.00081 | 0.553 | 0.12% | 36.29% |
| `node0_cores096_clients004_gen0512` | 80.0 ms | 24 | 0.0 ms | 20 | 20 | 20 | 20 | 0.00157 | 0.553 | 0.24% | 36.71% |
| `node0_cores024_clients008_gen0512` | 139.4 ms | 48 | 0.0 ms | 40 | 40 | 40 | 40 | 0.00323 | 0.459 | 1.53% | 53.95% |
| `node0_cores048_clients008_gen0512` | 112.6 ms | 56 | 0.0 ms | 48 | 48 | 48 | 48 | 0.00323 | 0.511 | 0.98% | 47.16% |
| `node0_cores072_clients008_gen0512` | 110.7 ms | 56 | 0.0 ms | 48 | 48 | 48 | 48 | 0.00334 | 0.558 | 0.71% | 42.71% |
| `node0_cores096_clients008_gen0512` | 101.6 ms | 48 | 0.0 ms | 40 | 40 | 40 | 40 | 0.00323 | 0.564 | 0.45% | 35.89% |
| `node0_cores096_clients016_gen0512` | 141.6 ms | 112 | 0.0 ms | 96 | 96 | 96 | 96 | 0.00654 | 0.563 | 0.97% | 40.82% |
| `node0_cores096_clients032_gen0512` | 215.0 ms | 192 | 0.1 ms | 160 | 160 | 160 | 160 | 0.01332 | 0.572 | 1.68% | 37.64% |
| `node0_cores096_clients064_gen0512` | 389.1 ms | 256 | 0.1 ms | 192 | 192 | 192 | 192 | 0.02520 | 0.588 | 2.57% | 24.79% |
| `node0_cores096_clients128_gen0512` | 582.4 ms | 384 | 0.2 ms | 256 | 256 | 256 | 256 | 0.05080 | 0.566 | 3.73% | 20.49% |

KV-cache occupancy stays well under 0.1%. The waiting gauge stays at 0 through the finished concurrency points, so TTFT growth is service time inside the batch, not scheduler queue time. Queue-time histograms confirm that only if requests finish; they have not, inside the window.

## Caveats

- 8647 requests have completed inside a measurement window. On those runs the request-level TPOT and decode-time histograms are populated, and they belong in the core-count table.
- Histogram p50/p90/p99 are interpolated inside 100 ms buckets. When almost every sample sits in 300–400 ms, those percentiles collapse toward the middle and the top of that bucket. Quote the mean, and the bucket share, for decode latency.
- Partial rows are mid-window and will be replaced when the attempt writes `summary.json`.
- Several finished attempts record a non-fatal Docker cleanup race (`removal of container ... is already in progress`). The run stays marked done and the controller continues.

## What changes next

This file is rewritten as attempts finish.

