# vLLM decode latency report

Live notes for plan `8dd40a98cc85` on the Xeon 6972P node-0 benchmark. Updated 2026-11-21 14:34:50 UTC.
Tables keep every finished pinned attempt from plans `5226854cadfd`, `597329c364ef`, `21fada0d01d0`, `8dd40a98cc85`. The progress count is the active plan. Sweeps match the pinned run: concurrency 1, 2, 4, 8, 16, 32, 64, 128 at 96 cores, and cores 24, 48, 72, 96 at 8 clients. Generated tokens stay at 512.

## Snapshot

Controller is not running. Progress 77/77 successful runs.

Decode latency here is the time between generated tokens. The server series that records every token is `vllm:inter_token_latency_seconds`. The client series is the per-request mean TPOT, `(last token time − first token time) / (tokens − 1)`. Those two agree. vLLM's request-level `request_time_per_output_token_seconds` and `request_decode_time_seconds` update only when a request finishes. At ~350 ms/token a 512-token request cannot finish inside the 90-second window, so those histograms stay empty. They fill once the step is short enough that 512 tokens fit in the window.

Across 297 finished runs, server inter-token latency averages **7.8–377.8 ms**. Relative spread versus the fastest finished run is 4718.4%. Per-token time is no longer a single band.

## Decode latency by run

Means are `histogram_sum / histogram_count` over samples that arrived between `measurement_start` and `measurement_window_end`. The Prometheus buckets are 100 ms wide in this region, so a reported p50 near 350 ms only means the median bucket is 300–400 ms. The mean is the precise number. Client TPOT is the median of per-request mean token gaps, including requests that the 90-second window truncates.

| Model | Sweep | Cores | Clients | Gen | Status | Server ITL mean | ITL bucket | Client TPOT median | Client TTFT median | Tokens/s | Running | Waiting |
|---|---|---:|---:|---:|---|---:|---|---:|---:|---:|---:|---:|
| `AMead10/Llama-3.2-1B-Instruct-AWQ` | baseline | 96 | 8 | 512 | done | 10.2 ms | 64.0% in 0–10 ms | 10.2 ms | 45.1 ms | 777.70 | 7.8 | 0.0 |
| `AMead10/Llama-3.2-1B-Instruct-AWQ` | concurrency | 96 | 1 | 512 | done | 7.8 ms | 97.8% in 0–10 ms | 7.8 ms | 16.0 ms | 127.21 | 1.0 | 0.0 |
| `AMead10/Llama-3.2-1B-Instruct-AWQ` | concurrency | 96 | 2 | 512 | done | 8.4 ms | 94.4% in 0–10 ms | 8.4 ms | 25.5 ms | 236.94 | 2.0 | 0.0 |
| `AMead10/Llama-3.2-1B-Instruct-AWQ` | concurrency | 96 | 4 | 512 | done | 8.9 ms | 93.1% in 0–10 ms | 8.8 ms | 36.5 ms | 447.80 | 3.8 | 0.0 |
| `AMead10/Llama-3.2-1B-Instruct-AWQ` | concurrency | 96 | 16 | 512 | done | 11.5 ms | 99.9% in 10–25 ms | 11.4 ms | 74.7 ms | 1377.28 | 15.6 | 0.0 |
| `AMead10/Llama-3.2-1B-Instruct-AWQ` | concurrency | 96 | 32 | 512 | done | 14.2 ms | 99.9% in 10–25 ms | 14.2 ms | 100.6 ms | 2217.28 | 31.0 | 0.0 |
| `AMead10/Llama-3.2-1B-Instruct-AWQ` | concurrency | 96 | 64 | 512 | done | 19.6 ms | 97.9% in 10–25 ms | 19.6 ms | 170.8 ms | 3207.89 | 61.9 | 0.0 |
| `AMead10/Llama-3.2-1B-Instruct-AWQ` | concurrency | 96 | 128 | 512 | done | 29.8 ms | 99.2% in 25–50 ms | 30.0 ms | 301.2 ms | 4198.43 | 123.7 | 0.0 |
| `AMead10/Llama-3.2-1B-Instruct-AWQ` | cores | 24 | 8 | 512 | done | 23.7 ms | 67.1% in 10–25 ms | 23.5 ms | 144.5 ms | 334.59 | 7.8 | 0.0 |
| `AMead10/Llama-3.2-1B-Instruct-AWQ` | cores | 48 | 8 | 512 | done | 20.7 ms | 98.4% in 10–25 ms | 20.7 ms | 114.7 ms | 383.67 | 7.9 | 0.0 |
| `AMead10/Llama-3.2-1B-Instruct-AWQ` | cores | 72 | 8 | 512 | done | 18.1 ms | 99.8% in 10–25 ms | 18.1 ms | 87.7 ms | 438.68 | 7.8 | 0.0 |
| `AMead10/Llama-3.2-3B-Instruct-AWQ` | baseline | 96 | 8 | 512 | done | 19.1 ms | 98.6% in 10–25 ms | 19.1 ms | 88.4 ms | 416.19 | 7.9 | 0.0 |
| `AMead10/Llama-3.2-3B-Instruct-AWQ` | concurrency | 96 | 1 | 512 | done | 14.6 ms | 100.0% in 10–25 ms | 14.6 ms | 30.2 ms | 68.22 | 1.0 | 0.0 |
| `AMead10/Llama-3.2-3B-Instruct-AWQ` | concurrency | 96 | 2 | 512 | done | 15.9 ms | 99.9% in 10–25 ms | 15.9 ms | 50.7 ms | 125.32 | 2.0 | 0.0 |
| `AMead10/Llama-3.2-3B-Instruct-AWQ` | concurrency | 96 | 4 | 512 | done | 16.3 ms | 99.8% in 10–25 ms | 16.3 ms | 62.8 ms | 243.27 | 4.0 | 0.0 |
| `AMead10/Llama-3.2-3B-Instruct-AWQ` | concurrency | 96 | 16 | 512 | done | 21.3 ms | 97.3% in 10–25 ms | 21.2 ms | 147.6 ms | 741.52 | 15.1 | 0.0 |
| `AMead10/Llama-3.2-3B-Instruct-AWQ` | concurrency | 96 | 32 | 512 | done | 26.9 ms | 75.6% in 25–50 ms | 26.8 ms | 219.9 ms | 1172.99 | 31.3 | 0.0 |
| `AMead10/Llama-3.2-3B-Instruct-AWQ` | concurrency | 96 | 64 | 512 | done | 37.8 ms | 99.5% in 25–50 ms | 38.0 ms | 378.6 ms | 1660.48 | 61.9 | 0.0 |
| `AMead10/Llama-3.2-3B-Instruct-AWQ` | concurrency | 96 | 128 | 512 | done | 59.3 ms | 86.5% in 50–75 ms | 59.8 ms | 687.0 ms | 2110.63 | 123.8 | 0.0 |
| `AMead10/Llama-3.2-3B-Instruct-AWQ` | cores | 24 | 8 | 512 | done | 35.9 ms | 99.9% in 25–50 ms | 35.6 ms | 329.3 ms | 219.74 | 7.7 | 0.0 |
| `AMead10/Llama-3.2-3B-Instruct-AWQ` | cores | 48 | 8 | 512 | done | 29.7 ms | 99.7% in 25–50 ms | 29.6 ms | 213.5 ms | 266.32 | 7.9 | 0.0 |
| `AMead10/Llama-3.2-3B-Instruct-AWQ` | cores | 72 | 8 | 512 | done | 25.0 ms | 61.0% in 10–25 ms | 25.0 ms | 181.7 ms | 316.28 | 7.9 | 0.0 |
| `Qwen/QwQ-32B` | baseline | 96 | 8 | 512 | done | 203.8 ms | 97.4% in 200–300 ms | 203.9 ms | 733.5 ms | 39.03 | 7.9 | 0.0 |
| `Qwen/QwQ-32B` | concurrency | 96 | 1 | 512 | done | 199.4 ms | 79.9% in 150–200 ms | 199.4 ms | 228.6 ms | 5.01 | 1.0 | 0.0 |
| `Qwen/QwQ-32B` | concurrency | 96 | 2 | 512 | done | 199.9 ms | 78.2% in 150–200 ms | 200.0 ms | 360.5 ms | 9.97 | 2.0 | 0.0 |
| `Qwen/QwQ-32B` | concurrency | 96 | 4 | 512 | done | 201.3 ms | 52.3% in 200–300 ms | 201.2 ms | 619.6 ms | 19.79 | 4.0 | 0.0 |
| `Qwen/QwQ-32B` | concurrency | 96 | 16 | 512 | done | 213.6 ms | 99.9% in 200–300 ms | 213.5 ms | 1113.1 ms | 74.20 | 15.7 | 0.0 |
| `Qwen/QwQ-32B` | concurrency | 96 | 32 | 512 | done | 226.4 ms | 100.0% in 200–300 ms | 226.7 ms | 1756.4 ms | 138.69 | 31.3 | 0.0 |
| `Qwen/QwQ-32B` | concurrency | 96 | 64 | 512 | done | 293.2 ms | 89.9% in 200–300 ms | 293.1 ms | 2701.7 ms | 212.69 | 62.0 | 0.0 |
| `Qwen/QwQ-32B` | concurrency | 96 | 128 | 512 | done | 377.8 ms | 99.5% in 300–400 ms | 378.4 ms | 4578.4 ms | 322.88 | 121.0 | 0.0 |
| `Qwen/QwQ-32B` | cores | 24 | 8 | 512 | done | 292.9 ms | 99.6% in 200–300 ms | 292.5 ms | 1370.0 ms | 27.04 | 7.8 | 0.0 |
| `Qwen/QwQ-32B` | cores | 48 | 8 | 512 | done | 214.1 ms | 100.0% in 200–300 ms | 214.1 ms | 917.9 ms | 37.08 | 7.9 | 0.0 |
| `Qwen/QwQ-32B` | cores | 72 | 8 | 512 | done | 213.0 ms | 100.0% in 200–300 ms | 213.0 ms | 822.9 ms | 37.26 | 7.9 | 0.0 |
| `Qwen/QwQ-32B-AWQ` | baseline | 96 | 8 | 512 | done | 96.3 ms | 84.8% in 75–100 ms | 96.4 ms | 581.1 ms | 82.23 | 7.9 | 0.0 |
| `Qwen/QwQ-32B-AWQ` | concurrency | 96 | 1 | 512 | done | 77.8 ms | 97.6% in 75–100 ms | 77.8 ms | 135.6 ms | 12.81 | 1.0 | 0.0 |
| `Qwen/QwQ-32B-AWQ` | concurrency | 96 | 2 | 512 | done | 82.8 ms | 99.8% in 75–100 ms | 82.7 ms | 242.4 ms | 24.01 | 2.0 | 0.0 |
| `Qwen/QwQ-32B-AWQ` | concurrency | 96 | 4 | 512 | done | 85.2 ms | 99.8% in 75–100 ms | 85.1 ms | 356.2 ms | 46.54 | 3.9 | 0.0 |
| `Qwen/QwQ-32B-AWQ` | concurrency | 96 | 16 | 512 | done | 105.5 ms | 100.0% in 100–150 ms | 105.9 ms | 986.0 ms | 148.63 | 15.5 | 0.0 |
| `Qwen/QwQ-32B-AWQ` | concurrency | 96 | 32 | 512 | done | 134.4 ms | 99.7% in 100–150 ms | 134.2 ms | 2094.9 ms | 228.67 | 30.4 | 0.0 |
| `Qwen/QwQ-32B-AWQ` | concurrency | 96 | 64 | 512 | done | 194.4 ms | 75.2% in 150–200 ms | 195.0 ms | 3466.2 ms | 317.19 | 61.3 | 0.0 |
| `Qwen/QwQ-32B-AWQ` | concurrency | 96 | 128 | 512 | done | 292.2 ms | 75.5% in 200–300 ms | 293.1 ms | 6127.8 ms | 409.63 | 118.2 | 0.0 |
| `Qwen/QwQ-32B-AWQ` | cores | 24 | 8 | 512 | done | 224.4 ms | 100.0% in 200–300 ms | 223.9 ms | 2407.0 ms | 34.86 | 7.8 | 0.0 |
| `Qwen/QwQ-32B-AWQ` | cores | 48 | 8 | 512 | done | 137.4 ms | 99.5% in 100–150 ms | 137.4 ms | 1296.7 ms | 56.81 | 7.7 | 0.0 |
| `Qwen/QwQ-32B-AWQ` | cores | 72 | 8 | 512 | done | 108.5 ms | 99.8% in 100–150 ms | 108.5 ms | 901.4 ms | 72.54 | 7.8 | 0.0 |
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
| `Qwen/Qwen3-14B` | baseline | 96 | 8 | 512 | done | 94.9 ms | 92.6% in 75–100 ms | 95.0 ms | 340.1 ms | 83.74 | 7.9 | 0.0 |
| `Qwen/Qwen3-14B` | concurrency | 96 | 1 | 512 | done | 90.9 ms | 99.8% in 75–100 ms | 90.9 ms | 111.1 ms | 10.99 | 1.0 | 0.0 |
| `Qwen/Qwen3-14B` | concurrency | 96 | 2 | 512 | done | 91.5 ms | 99.7% in 75–100 ms | 91.5 ms | 210.6 ms | 21.79 | 2.0 | 0.0 |
| `Qwen/Qwen3-14B` | concurrency | 96 | 4 | 512 | done | 92.4 ms | 99.4% in 75–100 ms | 92.4 ms | 251.5 ms | 43.09 | 4.0 | 0.0 |
| `Qwen/Qwen3-14B` | concurrency | 96 | 16 | 512 | done | 100.8 ms | 56.9% in 100–150 ms | 100.9 ms | 458.5 ms | 157.33 | 15.7 | 0.0 |
| `Qwen/Qwen3-14B` | concurrency | 96 | 32 | 512 | done | 108.3 ms | 100.0% in 100–150 ms | 108.9 ms | 699.2 ms | 291.21 | 31.6 | 0.0 |
| `Qwen/Qwen3-14B` | concurrency | 96 | 64 | 512 | done | 145.1 ms | 78.2% in 100–150 ms | 145.9 ms | 1151.8 ms | 430.23 | 61.9 | 0.0 |
| `Qwen/Qwen3-14B` | concurrency | 96 | 128 | 512 | done | 194.9 ms | 67.0% in 150–200 ms | 195.9 ms | 2074.8 ms | 642.86 | 125.2 | 0.0 |
| `Qwen/Qwen3-14B` | cores | 24 | 8 | 512 | done | 134.9 ms | 99.8% in 100–150 ms | 135.0 ms | 611.6 ms | 58.68 | 7.9 | 0.0 |
| `Qwen/Qwen3-14B` | cores | 48 | 8 | 512 | done | 97.6 ms | 90.4% in 75–100 ms | 97.7 ms | 399.7 ms | 81.34 | 7.9 | 0.0 |
| `Qwen/Qwen3-14B` | cores | 72 | 8 | 512 | done | 99.2 ms | 87.2% in 75–100 ms | 99.3 ms | 362.9 ms | 80.10 | 7.8 | 0.0 |
| `Qwen/Qwen3-14B-AWQ` | baseline | 96 | 8 | 512 | done | 49.1 ms | 79.9% in 25–50 ms | 49.1 ms | 277.2 ms | 161.43 | 7.9 | 0.0 |
| `Qwen/Qwen3-14B-AWQ` | concurrency | 96 | 1 | 512 | done | 39.6 ms | 100.0% in 25–50 ms | 39.6 ms | 70.7 ms | 25.20 | 1.0 | 0.0 |
| `Qwen/Qwen3-14B-AWQ` | concurrency | 96 | 2 | 512 | done | 42.3 ms | 98.8% in 25–50 ms | 42.3 ms | 125.6 ms | 47.01 | 2.0 | 0.0 |
| `Qwen/Qwen3-14B-AWQ` | concurrency | 96 | 4 | 512 | done | 43.4 ms | 97.4% in 25–50 ms | 43.4 ms | 172.2 ms | 91.43 | 4.0 | 0.0 |
| `Qwen/Qwen3-14B-AWQ` | concurrency | 96 | 16 | 512 | done | 54.9 ms | 99.8% in 50–75 ms | 54.9 ms | 453.1 ms | 286.23 | 15.7 | 0.0 |
| `Qwen/Qwen3-14B-AWQ` | concurrency | 96 | 32 | 512 | done | 67.8 ms | 97.0% in 50–75 ms | 68.2 ms | 876.1 ms | 459.40 | 31.0 | 0.0 |
| `Qwen/Qwen3-14B-AWQ` | concurrency | 96 | 64 | 512 | done | 98.8 ms | 61.0% in 75–100 ms | 99.4 ms | 1534.6 ms | 627.24 | 61.2 | 0.0 |
| `Qwen/Qwen3-14B-AWQ` | concurrency | 96 | 128 | 512 | done | 156.2 ms | 66.4% in 150–200 ms | 157.3 ms | 2654.5 ms | 773.70 | 120.9 | 0.0 |
| `Qwen/Qwen3-14B-AWQ` | cores | 24 | 8 | 512 | done | 107.0 ms | 99.8% in 100–150 ms | 106.7 ms | 1244.4 ms | 73.09 | 7.8 | 0.0 |
| `Qwen/Qwen3-14B-AWQ` | cores | 48 | 8 | 512 | done | 66.6 ms | 99.7% in 50–75 ms | 66.4 ms | 639.1 ms | 117.97 | 7.7 | 0.0 |
| `Qwen/Qwen3-14B-AWQ` | cores | 72 | 8 | 512 | done | 55.2 ms | 99.8% in 50–75 ms | 55.2 ms | 452.7 ms | 142.50 | 7.8 | 0.0 |
| `Qwen/Qwen3-14B-FP8` | baseline | 96 | 8 | 512 | done | 100.4 ms | 51.1% in 100–150 ms | 100.7 ms | 485.9 ms | 79.06 | 7.8 | 0.0 |
| `Qwen/Qwen3-14B-FP8` | concurrency | 96 | 1 | 512 | done | 58.2 ms | 99.9% in 50–75 ms | 57.6 ms | 138.9 ms | 17.10 | 1.0 | 0.0 |
| `Qwen/Qwen3-14B-FP8` | concurrency | 96 | 2 | 512 | done | 61.4 ms | 99.9% in 50–75 ms | 61.4 ms | 175.5 ms | 32.41 | 2.0 | 0.0 |
| `Qwen/Qwen3-14B-FP8` | concurrency | 96 | 4 | 512 | done | 65.6 ms | 99.6% in 50–75 ms | 65.6 ms | 348.9 ms | 60.46 | 3.9 | 0.0 |
| `Qwen/Qwen3-14B-FP8` | concurrency | 96 | 16 | 512 | done | 97.5 ms | 81.0% in 75–100 ms | 97.9 ms | 789.4 ms | 161.61 | 15.7 | 0.0 |
| `Qwen/Qwen3-14B-FP8` | concurrency | 96 | 32 | 512 | done | 129.2 ms | 99.7% in 100–150 ms | 129.8 ms | 1332.7 ms | 241.46 | 31.0 | 0.0 |
| `Qwen/Qwen3-14B-FP8` | concurrency | 96 | 64 | 512 | done | 176.7 ms | 99.8% in 150–200 ms | 176.7 ms | 2207.1 ms | 354.18 | 62.0 | 0.0 |
| `Qwen/Qwen3-14B-FP8` | concurrency | 96 | 128 | 512 | done | 231.1 ms | 100.0% in 200–300 ms | 231.9 ms | 3961.3 ms | 530.53 | 122.4 | 0.0 |
| `Qwen/Qwen3-14B-FP8` | cores | 24 | 8 | 512 | done | 115.7 ms | 100.0% in 100–150 ms | 115.9 ms | 773.9 ms | 68.10 | 7.8 | 0.0 |
| `Qwen/Qwen3-14B-FP8` | cores | 48 | 8 | 512 | done | 86.5 ms | 99.9% in 75–100 ms | 86.4 ms | 562.1 ms | 91.03 | 7.8 | 0.0 |
| `Qwen/Qwen3-14B-FP8` | cores | 72 | 8 | 512 | done | 86.5 ms | 99.6% in 75–100 ms | 86.4 ms | 497.2 ms | 91.21 | 7.8 | 0.0 |
| `Qwen/Qwen3-30B-A3B` | baseline | 96 | 8 | 512 | done | 57.0 ms | 98.6% in 50–75 ms | 57.0 ms | 267.9 ms | 139.03 | 7.9 | 0.0 |
| `Qwen/Qwen3-30B-A3B` | concurrency | 96 | 1 | 512 | done | 34.3 ms | 100.0% in 25–50 ms | 34.3 ms | 108.9 ms | 28.99 | 1.0 | 0.0 |
| `Qwen/Qwen3-30B-A3B` | concurrency | 96 | 2 | 512 | done | 43.3 ms | 97.6% in 25–50 ms | 43.3 ms | 181.6 ms | 45.83 | 2.0 | 0.0 |
| `Qwen/Qwen3-30B-A3B` | concurrency | 96 | 4 | 512 | done | 55.8 ms | 97.0% in 50–75 ms | 55.8 ms | 237.1 ms | 71.12 | 3.9 | 0.0 |
| `Qwen/Qwen3-30B-A3B` | concurrency | 96 | 16 | 512 | done | 69.6 ms | 91.3% in 50–75 ms | 69.8 ms | 345.5 ms | 227.94 | 15.6 | 0.0 |
| `Qwen/Qwen3-30B-A3B` | concurrency | 96 | 32 | 512 | done | 76.1 ms | 57.5% in 75–100 ms | 76.5 ms | 402.8 ms | 415.71 | 31.6 | 0.0 |
| `Qwen/Qwen3-30B-A3B` | concurrency | 96 | 64 | 512 | done | 82.0 ms | 93.3% in 75–100 ms | 82.1 ms | 587.7 ms | 765.88 | 62.6 | 0.0 |
| `Qwen/Qwen3-30B-A3B` | concurrency | 96 | 128 | 512 | done | 106.5 ms | 81.1% in 100–150 ms | 107.7 ms | 956.4 ms | 1177.61 | 125.2 | 0.0 |
| `Qwen/Qwen3-30B-A3B` | cores | 24 | 8 | 512 | done | 85.4 ms | 96.8% in 75–100 ms | 85.3 ms | 367.6 ms | 92.92 | 7.9 | 0.0 |
| `Qwen/Qwen3-30B-A3B` | cores | 48 | 8 | 512 | done | 58.2 ms | 99.3% in 50–75 ms | 58.2 ms | 282.1 ms | 136.53 | 7.8 | 0.0 |
| `Qwen/Qwen3-30B-A3B` | cores | 72 | 8 | 512 | done | 56.3 ms | 97.7% in 50–75 ms | 56.3 ms | 267.3 ms | 140.72 | 7.9 | 0.0 |
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
| `Qwen/Qwen3-8B` | baseline | 96 | 8 | 512 | done | 57.2 ms | 99.8% in 50–75 ms | 57.1 ms | 201.6 ms | 138.77 | 7.9 | 0.0 |
| `Qwen/Qwen3-8B` | concurrency | 96 | 1 | 512 | done | 54.2 ms | 99.9% in 50–75 ms | 54.2 ms | 68.4 ms | 18.42 | 1.0 | 0.0 |
| `Qwen/Qwen3-8B` | concurrency | 96 | 2 | 512 | done | 54.2 ms | 99.8% in 50–75 ms | 54.2 ms | 124.1 ms | 36.77 | 2.0 | 0.0 |
| `Qwen/Qwen3-8B` | concurrency | 96 | 4 | 512 | done | 55.1 ms | 99.8% in 50–75 ms | 55.1 ms | 149.3 ms | 72.26 | 4.0 | 0.0 |
| `Qwen/Qwen3-8B` | concurrency | 96 | 16 | 512 | done | 61.9 ms | 99.9% in 50–75 ms | 62.0 ms | 277.6 ms | 256.19 | 15.8 | 0.0 |
| `Qwen/Qwen3-8B` | concurrency | 96 | 32 | 512 | done | 67.5 ms | 97.5% in 50–75 ms | 67.7 ms | 453.2 ms | 467.23 | 31.0 | 0.0 |
| `Qwen/Qwen3-8B` | concurrency | 96 | 64 | 512 | done | 86.8 ms | 99.6% in 75–100 ms | 86.9 ms | 733.9 ms | 725.38 | 62.6 | 0.0 |
| `Qwen/Qwen3-8B` | concurrency | 96 | 128 | 512 | done | 128.3 ms | 98.5% in 100–150 ms | 128.3 ms | 1204.5 ms | 971.40 | 123.8 | 0.0 |
| `Qwen/Qwen3-8B` | cores | 24 | 8 | 512 | done | 78.3 ms | 99.9% in 75–100 ms | 78.3 ms | 349.2 ms | 101.17 | 7.9 | 0.0 |
| `Qwen/Qwen3-8B` | cores | 48 | 8 | 512 | done | 57.1 ms | 99.8% in 50–75 ms | 57.0 ms | 253.3 ms | 138.77 | 7.9 | 0.0 |
| `Qwen/Qwen3-8B` | cores | 72 | 8 | 512 | done | 55.6 ms | 99.9% in 50–75 ms | 55.6 ms | 210.8 ms | 142.77 | 7.8 | 0.0 |
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
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | baseline | 96 | 8 | 512 | done | 35.3 ms | 99.9% in 25–50 ms | 35.3 ms | 145.3 ms | 224.99 | 7.9 | 0.0 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | concurrency | 96 | 1 | 512 | done | 31.9 ms | 100.0% in 25–50 ms | 31.9 ms | 43.4 ms | 31.33 | 1.0 | 0.0 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | concurrency | 96 | 2 | 512 | done | 33.6 ms | 99.8% in 25–50 ms | 33.6 ms | 76.7 ms | 59.37 | 2.0 | 0.0 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | concurrency | 96 | 4 | 512 | done | 34.7 ms | 99.9% in 25–50 ms | 34.7 ms | 115.9 ms | 114.72 | 4.0 | 0.0 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | concurrency | 96 | 16 | 512 | done | 37.7 ms | 99.9% in 25–50 ms | 37.7 ms | 242.6 ms | 419.74 | 15.6 | 0.0 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | concurrency | 96 | 32 | 512 | done | 42.9 ms | 98.2% in 25–50 ms | 42.9 ms | 333.8 ms | 733.88 | 31.6 | 0.0 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | concurrency | 96 | 64 | 512 | done | 75.3 ms | 50.3% in 75–100 ms | 75.6 ms | 494.5 ms | 837.03 | 61.9 | 0.0 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | concurrency | 96 | 128 | 512 | done | 101.9 ms | 57.8% in 100–150 ms | 103.2 ms | 879.3 ms | 1231.66 | 125.2 | 0.0 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | cores | 24 | 8 | 512 | done | 48.0 ms | 94.7% in 25–50 ms | 48.0 ms | 214.8 ms | 165.61 | 7.9 | 0.0 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | cores | 48 | 8 | 512 | done | 35.8 ms | 99.8% in 25–50 ms | 35.8 ms | 155.8 ms | 221.79 | 7.8 | 0.0 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | cores | 72 | 8 | 512 | done | 34.5 ms | 99.8% in 25–50 ms | 34.4 ms | 173.4 ms | 230.06 | 7.8 | 0.0 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | baseline | 96 | 8 | 512 | done | 35.4 ms | 99.9% in 25–50 ms | 35.4 ms | 144.7 ms | 224.81 | 7.9 | 0.0 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | concurrency | 96 | 1 | 512 | done | 32.1 ms | 100.0% in 25–50 ms | 32.1 ms | 44.9 ms | 31.16 | 1.0 | 0.0 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | concurrency | 96 | 2 | 512 | done | 33.4 ms | 99.9% in 25–50 ms | 33.4 ms | 87.6 ms | 59.70 | 2.0 | 0.0 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | concurrency | 96 | 4 | 512 | done | 35.0 ms | 99.9% in 25–50 ms | 35.0 ms | 119.9 ms | 113.61 | 4.0 | 0.0 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | concurrency | 96 | 16 | 512 | done | 37.5 ms | 99.9% in 25–50 ms | 37.5 ms | 263.3 ms | 421.00 | 15.7 | 0.0 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | concurrency | 96 | 32 | 512 | done | 42.8 ms | 98.1% in 25–50 ms | 42.7 ms | 343.8 ms | 735.66 | 30.6 | 0.0 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | concurrency | 96 | 64 | 512 | done | 74.7 ms | 54.1% in 50–75 ms | 74.9 ms | 497.7 ms | 843.40 | 63.3 | 0.0 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | concurrency | 96 | 128 | 512 | done | 101.1 ms | 51.0% in 100–150 ms | 102.4 ms | 920.0 ms | 1241.61 | 126.6 | 0.0 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | cores | 24 | 8 | 512 | done | 47.9 ms | 94.9% in 25–50 ms | 47.9 ms | 219.3 ms | 165.88 | 7.9 | 0.0 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | cores | 48 | 8 | 512 | done | 35.8 ms | 99.9% in 25–50 ms | 35.8 ms | 153.5 ms | 221.97 | 7.8 | 0.0 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | cores | 72 | 8 | 512 | done | 34.2 ms | 99.9% in 25–50 ms | 34.2 ms | 171.5 ms | 231.57 | 7.9 | 0.0 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | baseline | 96 | 8 | 512 | done | 119.6 ms | 99.7% in 100–150 ms | 119.8 ms | 496.4 ms | 66.32 | 7.9 | 0.0 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | concurrency | 96 | 1 | 512 | done | 111.9 ms | 99.9% in 100–150 ms | 111.9 ms | 140.9 ms | 8.92 | 1.0 | 0.0 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | concurrency | 96 | 2 | 512 | done | 114.6 ms | 99.7% in 100–150 ms | 114.6 ms | 287.4 ms | 17.39 | 2.0 | 0.0 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | concurrency | 96 | 4 | 512 | done | 117.0 ms | 99.8% in 100–150 ms | 117.0 ms | 402.8 ms | 33.97 | 3.9 | 0.0 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | concurrency | 96 | 16 | 512 | done | 127.7 ms | 99.5% in 100–150 ms | 127.8 ms | 752.7 ms | 123.59 | 15.7 | 0.0 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | concurrency | 96 | 32 | 512 | done | 138.6 ms | 97.1% in 100–150 ms | 139.4 ms | 1368.0 ms | 224.74 | 31.0 | 0.0 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | concurrency | 96 | 64 | 512 | done | 231.0 ms | 99.7% in 200–300 ms | 231.6 ms | 1970.9 ms | 271.68 | 62.6 | 0.0 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | concurrency | 96 | 128 | 512 | done | 314.0 ms | 94.9% in 300–400 ms | 314.9 ms | 3461.1 ms | 392.57 | 122.4 | 0.0 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | cores | 24 | 8 | 512 | done | 167.4 ms | 99.8% in 150–200 ms | 167.2 ms | 890.2 ms | 47.03 | 7.8 | 0.0 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | cores | 48 | 8 | 512 | done | 123.3 ms | 99.8% in 100–150 ms | 123.6 ms | 587.4 ms | 64.19 | 7.9 | 0.0 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | cores | 72 | 8 | 512 | done | 119.6 ms | 99.8% in 100–150 ms | 119.7 ms | 510.8 ms | 66.32 | 7.9 | 0.0 |
| `hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4` | baseline | 96 | 8 | 512 | done | 31.7 ms | 99.9% in 25–50 ms | 31.7 ms | 159.6 ms | 250.59 | 7.9 | 0.0 |
| `hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4` | concurrency | 96 | 1 | 512 | done | 24.8 ms | 67.1% in 10–25 ms | 24.8 ms | 45.9 ms | 40.22 | 1.0 | 0.0 |
| `hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4` | concurrency | 96 | 2 | 512 | done | 26.7 ms | 99.1% in 25–50 ms | 26.7 ms | 80.6 ms | 74.61 | 2.0 | 0.0 |
| `hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4` | concurrency | 96 | 4 | 512 | done | 27.4 ms | 99.9% in 25–50 ms | 27.5 ms | 110.5 ms | 144.99 | 4.0 | 0.0 |
| `hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4` | concurrency | 96 | 16 | 512 | done | 35.5 ms | 99.8% in 25–50 ms | 35.5 ms | 303.7 ms | 443.94 | 15.8 | 0.0 |
| `hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4` | concurrency | 96 | 32 | 512 | done | 44.3 ms | 96.4% in 25–50 ms | 44.7 ms | 473.9 ms | 707.92 | 31.0 | 0.0 |
| `hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4` | concurrency | 96 | 64 | 512 | done | 63.9 ms | 98.7% in 50–75 ms | 64.2 ms | 850.8 ms | 975.70 | 61.9 | 0.0 |
| `hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4` | concurrency | 96 | 128 | 512 | done | 100.1 ms | 52.8% in 75–100 ms | 101.3 ms | 1463.7 ms | 1237.34 | 122.3 | 0.0 |
| `hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4` | cores | 24 | 8 | 512 | done | 61.6 ms | 99.8% in 50–75 ms | 61.4 ms | 669.2 ms | 127.39 | 7.8 | 0.0 |
| `hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4` | cores | 48 | 8 | 512 | done | 40.8 ms | 99.8% in 25–50 ms | 40.6 ms | 464.5 ms | 192.29 | 7.9 | 0.0 |
| `hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4` | cores | 72 | 8 | 512 | done | 32.9 ms | 99.8% in 25–50 ms | 32.8 ms | 300.2 ms | 239.68 | 7.7 | 0.0 |
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
| `meta-llama/Llama-3.1-8B` | baseline | 96 | 8 | 512 | done | 55.5 ms | 99.9% in 50–75 ms | 55.4 ms | 201.7 ms | 143.12 | 7.9 | 0.0 |
| `meta-llama/Llama-3.1-8B` | concurrency | 96 | 1 | 512 | done | 52.5 ms | 99.9% in 50–75 ms | 52.5 ms | 68.6 ms | 19.02 | 1.0 | 0.0 |
| `meta-llama/Llama-3.1-8B` | concurrency | 96 | 2 | 512 | done | 52.7 ms | 99.9% in 50–75 ms | 52.7 ms | 124.5 ms | 37.79 | 2.0 | 0.0 |
| `meta-llama/Llama-3.1-8B` | concurrency | 96 | 4 | 512 | done | 53.5 ms | 99.9% in 50–75 ms | 53.5 ms | 158.8 ms | 74.46 | 3.9 | 0.0 |
| `meta-llama/Llama-3.1-8B` | concurrency | 96 | 16 | 512 | done | 60.6 ms | 99.9% in 50–75 ms | 60.7 ms | 297.0 ms | 261.70 | 15.8 | 0.0 |
| `meta-llama/Llama-3.1-8B` | concurrency | 96 | 32 | 512 | done | 68.1 ms | 97.5% in 50–75 ms | 68.3 ms | 414.1 ms | 463.30 | 31.6 | 0.0 |
| `meta-llama/Llama-3.1-8B` | concurrency | 96 | 64 | 512 | done | 89.1 ms | 99.0% in 75–100 ms | 89.6 ms | 686.3 ms | 706.86 | 62.6 | 0.0 |
| `meta-llama/Llama-3.1-8B` | concurrency | 96 | 128 | 512 | done | 122.1 ms | 99.7% in 100–150 ms | 122.5 ms | 1168.7 ms | 1021.19 | 123.8 | 0.0 |
| `meta-llama/Llama-3.1-8B` | cores | 24 | 8 | 512 | done | 77.3 ms | 99.9% in 75–100 ms | 77.3 ms | 342.0 ms | 102.59 | 7.9 | 0.0 |
| `meta-llama/Llama-3.1-8B` | cores | 48 | 8 | 512 | done | 55.8 ms | 99.9% in 50–75 ms | 55.8 ms | 232.7 ms | 142.23 | 7.9 | 0.0 |
| `meta-llama/Llama-3.1-8B` | cores | 72 | 8 | 512 | done | 53.9 ms | 99.9% in 50–75 ms | 53.8 ms | 215.6 ms | 147.39 | 7.9 | 0.0 |
| `meta-llama/Llama-3.1-8B-Instruct` | baseline | 96 | 8 | 512 | done | 55.5 ms | 99.9% in 50–75 ms | 55.5 ms | 206.5 ms | 142.94 | 7.9 | 0.0 |
| `meta-llama/Llama-3.1-8B-Instruct` | concurrency | 96 | 1 | 512 | done | 52.6 ms | 99.9% in 50–75 ms | 52.6 ms | 70.5 ms | 19.00 | 1.0 | 0.0 |
| `meta-llama/Llama-3.1-8B-Instruct` | concurrency | 96 | 2 | 512 | done | 52.8 ms | 99.9% in 50–75 ms | 52.8 ms | 120.1 ms | 37.74 | 1.9 | 0.0 |
| `meta-llama/Llama-3.1-8B-Instruct` | concurrency | 96 | 4 | 512 | done | 54.0 ms | 99.9% in 50–75 ms | 54.0 ms | 155.2 ms | 73.70 | 3.9 | 0.0 |
| `meta-llama/Llama-3.1-8B-Instruct` | concurrency | 96 | 16 | 512 | done | 60.6 ms | 99.9% in 50–75 ms | 60.6 ms | 286.7 ms | 261.70 | 15.8 | 0.0 |
| `meta-llama/Llama-3.1-8B-Instruct` | concurrency | 96 | 32 | 512 | done | 68.2 ms | 97.2% in 50–75 ms | 68.3 ms | 413.5 ms | 463.30 | 31.6 | 0.0 |
| `meta-llama/Llama-3.1-8B-Instruct` | concurrency | 96 | 64 | 512 | done | 90.3 ms | 98.5% in 75–100 ms | 91.0 ms | 689.3 ms | 697.66 | 62.6 | 0.0 |
| `meta-llama/Llama-3.1-8B-Instruct` | concurrency | 96 | 128 | 512 | done | 122.1 ms | 99.7% in 100–150 ms | 122.7 ms | 1155.8 ms | 1019.74 | 123.8 | 0.0 |
| `meta-llama/Llama-3.1-8B-Instruct` | cores | 24 | 8 | 512 | done | 77.4 ms | 99.8% in 75–100 ms | 77.3 ms | 355.7 ms | 102.42 | 7.8 | 0.0 |
| `meta-llama/Llama-3.1-8B-Instruct` | cores | 48 | 8 | 512 | done | 55.7 ms | 99.9% in 50–75 ms | 55.6 ms | 231.9 ms | 142.50 | 7.8 | 0.0 |
| `meta-llama/Llama-3.1-8B-Instruct` | cores | 72 | 8 | 512 | done | 54.0 ms | 99.9% in 50–75 ms | 53.9 ms | 212.8 ms | 147.13 | 7.9 | 0.0 |
| `meta-llama/Llama-3.2-1B` | baseline | 96 | 8 | 512 | done | 14.8 ms | 99.9% in 10–25 ms | 14.8 ms | 51.1 ms | 539.30 | 7.8 | 0.0 |
| `meta-llama/Llama-3.2-1B` | concurrency | 96 | 1 | 512 | done | 11.6 ms | 100.0% in 10–25 ms | 11.6 ms | 17.0 ms | 86.27 | 1.0 | 0.0 |
| `meta-llama/Llama-3.2-1B` | concurrency | 96 | 2 | 512 | done | 13.6 ms | 100.0% in 10–25 ms | 13.6 ms | 31.1 ms | 146.50 | 2.0 | 0.0 |
| `meta-llama/Llama-3.2-1B` | concurrency | 96 | 4 | 512 | done | 13.9 ms | 100.0% in 10–25 ms | 13.9 ms | 39.1 ms | 285.89 | 3.9 | 0.0 |
| `meta-llama/Llama-3.2-1B` | concurrency | 96 | 16 | 512 | done | 14.1 ms | 99.9% in 10–25 ms | 14.1 ms | 73.0 ms | 1121.62 | 15.5 | 0.0 |
| `meta-llama/Llama-3.2-1B` | concurrency | 96 | 32 | 512 | done | 16.5 ms | 99.9% in 10–25 ms | 16.5 ms | 100.4 ms | 1916.89 | 31.0 | 0.0 |
| `meta-llama/Llama-3.2-1B` | concurrency | 96 | 64 | 512 | done | 22.9 ms | 91.9% in 10–25 ms | 22.9 ms | 197.2 ms | 2744.92 | 61.1 | 0.0 |
| `meta-llama/Llama-3.2-1B` | concurrency | 96 | 128 | 512 | done | 34.3 ms | 99.9% in 25–50 ms | 34.2 ms | 279.6 ms | 3663.67 | 122.4 | 0.0 |
| `meta-llama/Llama-3.2-1B` | cores | 24 | 8 | 512 | done | 16.7 ms | 100.0% in 10–25 ms | 16.7 ms | 68.7 ms | 476.54 | 7.9 | 0.0 |
| `meta-llama/Llama-3.2-1B` | cores | 48 | 8 | 512 | done | 13.3 ms | 100.0% in 10–25 ms | 13.3 ms | 55.6 ms | 597.29 | 7.8 | 0.0 |
| `meta-llama/Llama-3.2-1B` | cores | 72 | 8 | 512 | done | 12.6 ms | 100.0% in 10–25 ms | 12.6 ms | 55.3 ms | 628.37 | 7.8 | 0.0 |
| `meta-llama/Llama-3.2-1B-Instruct` | baseline | 96 | 8 | 512 | done | 14.9 ms | 99.9% in 10–25 ms | 14.9 ms | 55.9 ms | 531.93 | 7.8 | 0.0 |
| `meta-llama/Llama-3.2-1B-Instruct` | concurrency | 96 | 1 | 512 | done | 11.7 ms | 100.0% in 10–25 ms | 11.7 ms | 16.8 ms | 85.54 | 1.0 | 0.0 |
| `meta-llama/Llama-3.2-1B-Instruct` | concurrency | 96 | 2 | 512 | done | 13.5 ms | 100.0% in 10–25 ms | 13.5 ms | 30.6 ms | 147.66 | 2.0 | 0.0 |
| `meta-llama/Llama-3.2-1B-Instruct` | concurrency | 96 | 4 | 512 | done | 13.9 ms | 100.0% in 10–25 ms | 13.8 ms | 39.0 ms | 287.03 | 4.0 | 0.0 |
| `meta-llama/Llama-3.2-1B-Instruct` | concurrency | 96 | 16 | 512 | done | 14.2 ms | 100.0% in 10–25 ms | 14.1 ms | 70.7 ms | 1119.66 | 15.5 | 0.0 |
| `meta-llama/Llama-3.2-1B-Instruct` | concurrency | 96 | 32 | 512 | done | 16.6 ms | 99.8% in 10–25 ms | 16.6 ms | 113.1 ms | 1906.52 | 31.6 | 0.0 |
| `meta-llama/Llama-3.2-1B-Instruct` | concurrency | 96 | 64 | 512 | done | 23.0 ms | 91.5% in 10–25 ms | 23.1 ms | 178.9 ms | 2740.38 | 62.6 | 0.0 |
| `meta-llama/Llama-3.2-1B-Instruct` | concurrency | 96 | 128 | 512 | done | 33.7 ms | 99.9% in 25–50 ms | 33.7 ms | 283.7 ms | 3727.92 | 123.7 | 0.0 |
| `meta-llama/Llama-3.2-1B-Instruct` | cores | 24 | 8 | 512 | done | 16.8 ms | 100.0% in 10–25 ms | 16.8 ms | 69.9 ms | 474.14 | 7.8 | 0.0 |
| `meta-llama/Llama-3.2-1B-Instruct` | cores | 48 | 8 | 512 | done | 13.0 ms | 100.0% in 10–25 ms | 13.0 ms | 54.9 ms | 610.68 | 7.8 | 0.0 |
| `meta-llama/Llama-3.2-1B-Instruct` | cores | 72 | 8 | 512 | done | 12.5 ms | 100.0% in 10–25 ms | 12.5 ms | 54.1 ms | 637.08 | 7.9 | 0.0 |
| `meta-llama/Llama-3.2-3B-Instruct` | baseline | 96 | 8 | 512 | done | 29.1 ms | 99.9% in 25–50 ms | 29.0 ms | 115.7 ms | 273.09 | 7.8 | 0.0 |
| `meta-llama/Llama-3.2-3B-Instruct` | concurrency | 96 | 1 | 512 | done | 26.8 ms | 100.0% in 25–50 ms | 26.8 ms | 35.8 ms | 37.33 | 1.0 | 0.0 |
| `meta-llama/Llama-3.2-3B-Instruct` | concurrency | 96 | 2 | 512 | done | 26.8 ms | 100.0% in 25–50 ms | 26.9 ms | 69.7 ms | 74.37 | 2.0 | 0.0 |
| `meta-llama/Llama-3.2-3B-Instruct` | concurrency | 96 | 4 | 512 | done | 27.8 ms | 100.0% in 25–50 ms | 27.7 ms | 84.1 ms | 143.39 | 3.9 | 0.0 |
| `meta-llama/Llama-3.2-3B-Instruct` | concurrency | 96 | 16 | 512 | done | 31.0 ms | 100.0% in 25–50 ms | 30.9 ms | 158.9 ms | 512.01 | 15.7 | 0.0 |
| `meta-llama/Llama-3.2-3B-Instruct` | concurrency | 96 | 32 | 512 | done | 34.9 ms | 100.0% in 25–50 ms | 34.8 ms | 234.4 ms | 904.90 | 31.3 | 0.0 |
| `meta-llama/Llama-3.2-3B-Instruct` | concurrency | 96 | 64 | 512 | done | 52.7 ms | 69.1% in 50–75 ms | 53.0 ms | 367.8 ms | 1196.12 | 62.6 | 0.0 |
| `meta-llama/Llama-3.2-3B-Instruct` | concurrency | 96 | 128 | 512 | done | 74.2 ms | 55.3% in 50–75 ms | 74.9 ms | 627.1 ms | 1686.77 | 123.8 | 0.0 |
| `meta-llama/Llama-3.2-3B-Instruct` | cores | 24 | 8 | 512 | done | 38.1 ms | 99.9% in 25–50 ms | 38.1 ms | 159.9 ms | 208.46 | 7.9 | 0.0 |
| `meta-llama/Llama-3.2-3B-Instruct` | cores | 48 | 8 | 512 | done | 29.1 ms | 99.9% in 25–50 ms | 29.1 ms | 119.6 ms | 273.08 | 7.9 | 0.0 |
| `meta-llama/Llama-3.2-3B-Instruct` | cores | 72 | 8 | 512 | done | 29.1 ms | 99.9% in 25–50 ms | 29.0 ms | 116.2 ms | 273.17 | 7.9 | 0.0 |
| `microsoft/Phi-4-reasoning` | baseline | 96 | 8 | 512 | done | 96.0 ms | 91.1% in 75–100 ms | 96.1 ms | 340.9 ms | 82.86 | 7.9 | 0.0 |
| `microsoft/Phi-4-reasoning` | concurrency | 96 | 1 | 512 | done | 91.9 ms | 99.7% in 75–100 ms | 91.9 ms | 110.4 ms | 10.88 | 1.0 | 0.0 |
| `microsoft/Phi-4-reasoning` | concurrency | 96 | 2 | 512 | done | 92.5 ms | 99.5% in 75–100 ms | 92.5 ms | 212.3 ms | 21.57 | 2.0 | 0.0 |
| `microsoft/Phi-4-reasoning` | concurrency | 96 | 4 | 512 | done | 93.2 ms | 98.2% in 75–100 ms | 93.3 ms | 264.8 ms | 42.72 | 4.0 | 0.0 |
| `microsoft/Phi-4-reasoning` | concurrency | 96 | 16 | 512 | done | 102.0 ms | 79.4% in 100–150 ms | 102.2 ms | 475.5 ms | 155.23 | 15.8 | 0.0 |
| `microsoft/Phi-4-reasoning` | concurrency | 96 | 32 | 512 | done | 109.6 ms | 100.0% in 100–150 ms | 110.3 ms | 712.1 ms | 287.30 | 31.3 | 0.0 |
| `microsoft/Phi-4-reasoning` | concurrency | 96 | 64 | 512 | done | 144.9 ms | 77.2% in 100–150 ms | 145.7 ms | 1208.7 ms | 430.26 | 61.9 | 0.0 |
| `microsoft/Phi-4-reasoning` | concurrency | 96 | 128 | 512 | done | 196.7 ms | 58.1% in 150–200 ms | 197.8 ms | 2148.8 ms | 635.77 | 123.8 | 0.0 |
| `microsoft/Phi-4-reasoning` | cores | 24 | 8 | 512 | done | 135.5 ms | 99.8% in 100–150 ms | 135.7 ms | 612.4 ms | 58.41 | 7.8 | 0.0 |
| `microsoft/Phi-4-reasoning` | cores | 48 | 8 | 512 | done | 99.0 ms | 86.8% in 75–100 ms | 99.1 ms | 402.6 ms | 80.28 | 7.8 | 0.0 |
| `microsoft/Phi-4-reasoning` | cores | 72 | 8 | 512 | done | 100.6 ms | 52.8% in 100–150 ms | 100.7 ms | 361.1 ms | 78.96 | 7.9 | 0.0 |
| `openai/gpt-oss-20b` | baseline | 96 | 8 | 512 | done | 34.3 ms | 99.9% in 25–50 ms | 34.4 ms | 149.1 ms | 231.39 | 7.8 | 0.0 |
| `openai/gpt-oss-20b` | concurrency | 96 | 1 | 512 | done | 19.0 ms | 98.6% in 10–25 ms | 19.0 ms | 52.0 ms | 52.49 | 1.0 | 0.0 |
| `openai/gpt-oss-20b` | concurrency | 96 | 2 | 512 | done | 22.8 ms | 94.8% in 10–25 ms | 22.8 ms | 92.9 ms | 87.12 | 2.0 | 0.0 |
| `openai/gpt-oss-20b` | concurrency | 96 | 4 | 512 | done | 28.5 ms | 99.5% in 25–50 ms | 28.5 ms | 118.8 ms | 139.30 | 4.0 | 0.0 |
| `openai/gpt-oss-20b` | concurrency | 96 | 16 | 512 | done | 33.7 ms | 99.9% in 25–50 ms | 34.1 ms | 188.7 ms | 468.99 | 15.8 | 0.0 |
| `openai/gpt-oss-20b` | concurrency | 96 | 32 | 512 | done | 39.9 ms | 99.4% in 25–50 ms | 40.0 ms | 265.1 ms | 791.49 | 31.3 | 0.0 |
| `openai/gpt-oss-20b` | concurrency | 96 | 64 | 512 | done | 52.9 ms | 86.8% in 50–75 ms | 53.0 ms | 407.9 ms | 1188.28 | 62.6 | 0.0 |
| `openai/gpt-oss-20b` | concurrency | 96 | 128 | 512 | done | 73.6 ms | 66.2% in 50–75 ms | 73.1 ms | 694.7 ms | 1698.17 | 123.8 | 0.0 |
| `openai/gpt-oss-20b` | cores | 24 | 8 | 512 | done | 52.9 ms | 84.5% in 50–75 ms | 52.9 ms | 264.8 ms | 149.70 | 7.8 | 0.0 |
| `openai/gpt-oss-20b` | cores | 48 | 8 | 512 | done | 38.1 ms | 99.9% in 25–50 ms | 38.0 ms | 184.2 ms | 208.10 | 7.9 | 0.0 |
| `openai/gpt-oss-20b` | cores | 72 | 8 | 512 | done | 34.2 ms | 99.9% in 25–50 ms | 34.7 ms | 149.5 ms | 231.74 | 7.9 | 0.0 |
| `zai-org/glm-4-9b-hf` | baseline | 96 | 8 | 512 | done | 66.7 ms | 99.5% in 50–75 ms | 66.7 ms | 237.7 ms | 119.21 | 7.9 | 0.0 |
| `zai-org/glm-4-9b-hf` | concurrency | 96 | 1 | 512 | done | 64.3 ms | 99.9% in 50–75 ms | 64.4 ms | 76.1 ms | 15.52 | 1.0 | 0.0 |
| `zai-org/glm-4-9b-hf` | concurrency | 96 | 2 | 512 | done | 64.2 ms | 99.9% in 50–75 ms | 64.2 ms | 132.5 ms | 31.10 | 2.0 | 0.0 |
| `zai-org/glm-4-9b-hf` | concurrency | 96 | 4 | 512 | done | 65.3 ms | 99.7% in 50–75 ms | 65.4 ms | 143.9 ms | 61.00 | 4.0 | 0.0 |
| `zai-org/glm-4-9b-hf` | concurrency | 96 | 16 | 512 | done | 71.2 ms | 92.9% in 50–75 ms | 71.2 ms | 300.9 ms | 222.84 | 15.6 | 0.0 |
| `zai-org/glm-4-9b-hf` | concurrency | 96 | 32 | 512 | done | 76.1 ms | 62.4% in 75–100 ms | 76.0 ms | 559.3 ms | 413.54 | 31.6 | 0.0 |
| `zai-org/glm-4-9b-hf` | concurrency | 96 | 64 | 512 | done | 94.3 ms | 93.8% in 75–100 ms | 94.5 ms | 816.6 ms | 666.37 | 61.9 | 0.0 |
| `zai-org/glm-4-9b-hf` | concurrency | 96 | 128 | 512 | done | 134.0 ms | 99.1% in 100–150 ms | 134.8 ms | 1396.9 ms | 925.90 | 122.4 | 0.0 |
| `zai-org/glm-4-9b-hf` | cores | 24 | 8 | 512 | done | 91.1 ms | 99.9% in 75–100 ms | 91.1 ms | 398.0 ms | 87.12 | 7.8 | 0.0 |
| `zai-org/glm-4-9b-hf` | cores | 48 | 8 | 512 | done | 66.3 ms | 99.7% in 50–75 ms | 66.3 ms | 279.1 ms | 119.77 | 7.8 | 0.0 |
| `zai-org/glm-4-9b-hf` | cores | 72 | 8 | 512 | done | 65.0 ms | 99.9% in 50–75 ms | 64.9 ms | 258.5 ms | 122.23 | 7.9 | 0.0 |

### Same numbers, server versus client

| Config | ITL mean | ITL n | coarse ITL p50 | coarse ITL p90 | client TPOT min | client TPOT median | client TPOT p90 | complete requests |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `node0_cores096_clients001_gen0512` | 7.8 ms | 11383 | 5.1 ms | 9.2 ms | 7.6 ms | 7.8 ms | 8.0 ms | 23 |
| `node0_cores096_clients002_gen0512` | 8.4 ms | 21205 | 5.3 ms | 9.5 ms | 8.3 ms | 8.4 ms | 8.5 ms | 42 |
| `node0_cores096_clients004_gen0512` | 8.9 ms | 40074 | 5.4 ms | 9.7 ms | 8.7 ms | 8.8 ms | 9.1 ms | 80 |
| `node0_cores024_clients008_gen0512` | 23.7 ms | 29969 | 21.2 ms | 42.4 ms | 23.1 ms | 23.5 ms | 23.7 ms | 64 |
| `node0_cores048_clients008_gen0512` | 20.7 ms | 34394 | 17.6 ms | 23.7 ms | 20.2 ms | 20.7 ms | 20.9 ms | 72 |
| `node0_cores072_clients008_gen0512` | 18.1 ms | 39329 | 17.5 ms | 23.5 ms | 18.0 ms | 18.1 ms | 18.2 ms | 80 |
| `node0_cores096_clients008_gen0512` | 10.2 ms | 69593 | 7.8 ms | 20.9 ms | 10.0 ms | 10.2 ms | 10.4 ms | 144 |
| `node0_cores096_clients016_gen0512` | 11.5 ms | 123251 | 17.5 ms | 23.5 ms | 11.4 ms | 11.4 ms | 11.7 ms | 256 |
| `node0_cores096_clients032_gen0512` | 14.2 ms | 198531 | 17.5 ms | 23.5 ms | 14.1 ms | 14.2 ms | 14.3 ms | 416 |
| `node0_cores096_clients064_gen0512` | 19.6 ms | 287238 | 17.7 ms | 23.8 ms | 19.1 ms | 19.6 ms | 19.9 ms | 576 |
| `node0_cores096_clients128_gen0512` | 29.8 ms | 376835 | 37.4 ms | 47.5 ms | 29.7 ms | 30.0 ms | 30.4 ms | 768 |
| `node0_cores096_clients001_gen0512` | 14.6 ms | 6108 | 17.5 ms | 23.5 ms | 14.5 ms | 14.6 ms | 14.7 ms | 12 |
| `node0_cores096_clients002_gen0512` | 15.9 ms | 11225 | 17.5 ms | 23.5 ms | 15.8 ms | 15.9 ms | 16.0 ms | 23 |
| `node0_cores096_clients004_gen0512` | 16.3 ms | 21778 | 17.5 ms | 23.5 ms | 16.2 ms | 16.3 ms | 16.5 ms | 44 |
| `node0_cores024_clients008_gen0512` | 35.9 ms | 19665 | 37.5 ms | 47.5 ms | 35.0 ms | 35.6 ms | 36.8 ms | 40 |
| `node0_cores048_clients008_gen0512` | 29.7 ms | 23841 | 37.5 ms | 47.5 ms | 29.4 ms | 29.6 ms | 29.9 ms | 48 |
| `node0_cores072_clients008_gen0512` | 25.0 ms | 28305 | 22.3 ms | 43.6 ms | 24.8 ms | 25.0 ms | 25.1 ms | 56 |
| `node0_cores096_clients008_gen0512` | 19.1 ms | 37249 | 17.6 ms | 23.7 ms | 18.9 ms | 19.1 ms | 19.2 ms | 72 |
| `node0_cores096_clients016_gen0512` | 21.3 ms | 66369 | 17.7 ms | 23.9 ms | 21.1 ms | 21.2 ms | 21.5 ms | 128 |
| `node0_cores096_clients032_gen0512` | 26.9 ms | 105025 | 33.5 ms | 46.7 ms | 26.8 ms | 26.8 ms | 27.2 ms | 224 |
| `node0_cores096_clients064_gen0512` | 37.8 ms | 148739 | 37.6 ms | 47.6 ms | 37.7 ms | 38.0 ms | 38.2 ms | 256 |
| `node0_cores096_clients128_gen0512` | 59.3 ms | 189317 | 60.9 ms | 72.5 ms | 59.2 ms | 59.8 ms | 59.9 ms | 384 |
| `node0_cores096_clients001_gen0512` | 199.4 ms | 448 | 181.3 ms | 250.2 ms | 199.4 ms | 199.4 ms | 199.4 ms | 0 |
| `node0_cores096_clients002_gen0512` | 199.9 ms | 893 | 182.0 ms | 254.2 ms | 199.9 ms | 200.0 ms | 200.0 ms | 0 |
| `node0_cores096_clients004_gen0512` | 201.3 ms | 1773 | 204.6 ms | 281.0 ms | 201.2 ms | 201.2 ms | 201.6 ms | 0 |
| `node0_cores024_clients008_gen0512` | 292.9 ms | 2418 | 250.2 ms | 290.4 ms | 292.5 ms | 292.5 ms | 294.3 ms | 0 |
| `node0_cores048_clients008_gen0512` | 214.1 ms | 3321 | 250.0 ms | 290.0 ms | 214.1 ms | 214.1 ms | 214.1 ms | 0 |
| `node0_cores072_clients008_gen0512` | 213.0 ms | 3337 | 250.0 ms | 290.0 ms | 213.0 ms | 213.0 ms | 213.0 ms | 0 |
| `node0_cores096_clients008_gen0512` | 203.8 ms | 3489 | 248.7 ms | 289.8 ms | 203.9 ms | 203.9 ms | 203.9 ms | 0 |
| `node0_cores096_clients016_gen0512` | 213.6 ms | 6646 | 250.0 ms | 290.1 ms | 213.5 ms | 213.5 ms | 214.4 ms | 0 |
| `node0_cores096_clients032_gen0512` | 226.4 ms | 12450 | 250.0 ms | 290.0 ms | 226.7 ms | 226.7 ms | 226.7 ms | 0 |
| `node0_cores096_clients064_gen0512` | 293.2 ms | 19078 | 255.6 ms | 300.9 ms | 293.1 ms | 293.1 ms | 293.1 ms | 0 |
| `node0_cores096_clients128_gen0512` | 377.8 ms | 28931 | 350.2 ms | 390.4 ms | 378.3 ms | 378.4 ms | 378.4 ms | 0 |
| `node0_cores096_clients001_gen0512` | 77.8 ms | 1147 | 87.2 ms | 97.5 ms | 77.4 ms | 77.8 ms | 78.0 ms | 2 |
| `node0_cores096_clients002_gen0512` | 82.8 ms | 2149 | 87.5 ms | 97.6 ms | 82.2 ms | 82.7 ms | 82.9 ms | 4 |
| `node0_cores096_clients004_gen0512` | 85.2 ms | 4165 | 87.5 ms | 97.5 ms | 84.2 ms | 85.1 ms | 85.4 ms | 8 |
| `node0_cores024_clients008_gen0512` | 224.4 ms | 3121 | 250.0 ms | 290.0 ms | 223.9 ms | 223.9 ms | 223.9 ms | 0 |
| `node0_cores048_clients008_gen0512` | 137.4 ms | 5081 | 125.1 ms | 145.2 ms | 136.2 ms | 137.4 ms | 139.1 ms | 8 |
| `node0_cores072_clients008_gen0512` | 108.5 ms | 6489 | 125.0 ms | 145.1 ms | 108.2 ms | 108.5 ms | 109.3 ms | 8 |
| `node0_cores096_clients008_gen0512` | 96.3 ms | 7361 | 89.7 ms | 117.2 ms | 96.1 ms | 96.4 ms | 96.7 ms | 8 |
| `node0_cores096_clients016_gen0512` | 105.5 ms | 13297 | 125.0 ms | 145.0 ms | 105.3 ms | 105.9 ms | 105.9 ms | 16 |
| `node0_cores096_clients032_gen0512` | 134.4 ms | 20452 | 125.1 ms | 145.2 ms | 132.6 ms | 134.2 ms | 137.3 ms | 32 |
| `node0_cores096_clients064_gen0512` | 194.4 ms | 28419 | 183.2 ms | 259.7 ms | 195.0 ms | 195.0 ms | 195.0 ms | 0 |
| `node0_cores096_clients128_gen0512` | 292.2 ms | 36611 | 266.2 ms | 359.2 ms | 293.1 ms | 293.1 ms | 293.1 ms | 0 |
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
| `node0_cores096_clients001_gen0512` | 90.9 ms | 984 | 87.5 ms | 97.5 ms | 90.9 ms | 90.9 ms | 90.9 ms | 2 |
| `node0_cores096_clients002_gen0512` | 91.5 ms | 1951 | 87.5 ms | 97.6 ms | 91.5 ms | 91.5 ms | 91.6 ms | 4 |
| `node0_cores096_clients004_gen0512` | 92.4 ms | 3862 | 87.6 ms | 97.6 ms | 92.4 ms | 92.4 ms | 92.5 ms | 8 |
| `node0_cores024_clients008_gen0512` | 134.9 ms | 5241 | 125.0 ms | 145.1 ms | 134.2 ms | 135.0 ms | 135.7 ms | 8 |
| `node0_cores048_clients008_gen0512` | 97.6 ms | 7281 | 88.8 ms | 99.9 ms | 97.5 ms | 97.7 ms | 97.9 ms | 8 |
| `node0_cores072_clients008_gen0512` | 99.2 ms | 7169 | 89.3 ms | 111.3 ms | 99.2 ms | 99.3 ms | 99.5 ms | 8 |
| `node0_cores096_clients008_gen0512` | 94.9 ms | 7505 | 88.5 ms | 99.3 ms | 94.9 ms | 95.0 ms | 95.2 ms | 16 |
| `node0_cores096_clients016_gen0512` | 100.8 ms | 14081 | 106.1 ms | 141.2 ms | 100.9 ms | 100.9 ms | 100.9 ms | 16 |
| `node0_cores096_clients032_gen0512` | 108.3 ms | 26081 | 125.0 ms | 145.0 ms | 107.4 ms | 108.9 ms | 109.2 ms | 32 |
| `node0_cores096_clients064_gen0512` | 145.1 ms | 38465 | 132.0 ms | 177.1 ms | 139.9 ms | 145.9 ms | 146.1 ms | 64 |
| `node0_cores096_clients128_gen0512` | 194.9 ms | 57729 | 187.3 ms | 269.7 ms | 195.9 ms | 195.9 ms | 195.9 ms | 0 |
| `node0_cores096_clients001_gen0512` | 39.6 ms | 2257 | 37.5 ms | 47.5 ms | 39.5 ms | 39.6 ms | 39.7 ms | 4 |
| `node0_cores096_clients002_gen0512` | 42.3 ms | 4207 | 37.6 ms | 47.8 ms | 41.9 ms | 42.3 ms | 42.4 ms | 8 |
| `node0_cores096_clients004_gen0512` | 43.4 ms | 8185 | 37.8 ms | 48.1 ms | 42.8 ms | 43.4 ms | 43.5 ms | 16 |
| `node0_cores024_clients008_gen0512` | 107.0 ms | 6546 | 125.0 ms | 145.1 ms | 106.5 ms | 106.7 ms | 108.5 ms | 8 |
| `node0_cores048_clients008_gen0512` | 66.6 ms | 10561 | 62.5 ms | 72.6 ms | 66.3 ms | 66.4 ms | 67.2 ms | 16 |
| `node0_cores072_clients008_gen0512` | 55.2 ms | 12761 | 62.5 ms | 72.5 ms | 54.5 ms | 55.2 ms | 55.6 ms | 24 |
| `node0_cores096_clients008_gen0512` | 49.1 ms | 14457 | 40.6 ms | 62.7 ms | 48.9 ms | 49.1 ms | 49.2 ms | 24 |
| `node0_cores096_clients016_gen0512` | 54.9 ms | 25617 | 62.5 ms | 72.5 ms | 53.5 ms | 54.9 ms | 55.1 ms | 48 |
| `node0_cores096_clients032_gen0512` | 67.8 ms | 41122 | 62.9 ms | 73.2 ms | 65.6 ms | 68.2 ms | 68.9 ms | 64 |
| `node0_cores096_clients064_gen0512` | 98.8 ms | 56196 | 95.5 ms | 137.2 ms | 98.8 ms | 99.4 ms | 99.5 ms | 64 |
| `node0_cores096_clients128_gen0512` | 156.2 ms | 69249 | 162.5 ms | 192.6 ms | 138.6 ms | 157.3 ms | 157.3 ms | 128 |
| `node0_cores096_clients001_gen0512` | 58.2 ms | 1533 | 62.5 ms | 72.5 ms | 55.4 ms | 57.6 ms | 59.6 ms | 3 |
| `node0_cores096_clients002_gen0512` | 61.4 ms | 2903 | 62.5 ms | 72.5 ms | 61.3 ms | 61.4 ms | 61.5 ms | 6 |
| `node0_cores096_clients004_gen0512` | 65.6 ms | 5417 | 62.5 ms | 72.6 ms | 65.4 ms | 65.6 ms | 65.8 ms | 8 |
| `node0_cores024_clients008_gen0512` | 115.7 ms | 6097 | 125.0 ms | 145.0 ms | 115.3 ms | 115.9 ms | 116.8 ms | 8 |
| `node0_cores048_clients008_gen0512` | 86.5 ms | 8176 | 87.5 ms | 97.5 ms | 86.0 ms | 86.4 ms | 87.1 ms | 16 |
| `node0_cores072_clients008_gen0512` | 86.5 ms | 8176 | 87.5 ms | 97.6 ms | 85.5 ms | 86.4 ms | 86.9 ms | 16 |
| `node0_cores096_clients008_gen0512` | 100.4 ms | 7083 | 101.2 ms | 140.3 ms | 99.5 ms | 100.7 ms | 101.9 ms | 8 |
| `node0_cores096_clients016_gen0512` | 97.5 ms | 14481 | 90.4 ms | 123.7 ms | 95.9 ms | 97.9 ms | 98.8 ms | 16 |
| `node0_cores096_clients032_gen0512` | 129.2 ms | 21603 | 125.1 ms | 145.1 ms | 125.3 ms | 129.8 ms | 130.2 ms | 32 |
| `node0_cores096_clients064_gen0512` | 176.7 ms | 31748 | 175.1 ms | 195.1 ms | 176.7 ms | 176.7 ms | 176.7 ms | 64 |
| `node0_cores096_clients128_gen0512` | 231.1 ms | 47620 | 250.0 ms | 290.0 ms | 231.9 ms | 231.9 ms | 231.9 ms | 0 |
| `node0_cores096_clients001_gen0512` | 34.3 ms | 2594 | 37.5 ms | 47.5 ms | 34.0 ms | 34.3 ms | 34.3 ms | 5 |
| `node0_cores096_clients002_gen0512` | 43.3 ms | 4101 | 37.8 ms | 48.0 ms | 42.5 ms | 43.3 ms | 43.7 ms | 8 |
| `node0_cores096_clients004_gen0512` | 55.8 ms | 6365 | 62.1 ms | 72.5 ms | 54.5 ms | 55.8 ms | 56.0 ms | 12 |
| `node0_cores024_clients008_gen0512` | 85.4 ms | 8307 | 87.1 ms | 97.5 ms | 81.7 ms | 85.3 ms | 85.7 ms | 16 |
| `node0_cores048_clients008_gen0512` | 58.2 ms | 12225 | 62.4 ms | 72.5 ms | 55.6 ms | 58.2 ms | 58.3 ms | 24 |
| `node0_cores072_clients008_gen0512` | 56.3 ms | 12593 | 62.2 ms | 72.5 ms | 55.0 ms | 56.3 ms | 56.7 ms | 24 |
| `node0_cores096_clients008_gen0512` | 57.0 ms | 12441 | 62.3 ms | 72.5 ms | 55.3 ms | 57.0 ms | 57.2 ms | 24 |
| `node0_cores096_clients016_gen0512` | 69.6 ms | 20403 | 63.7 ms | 74.6 ms | 69.0 ms | 69.8 ms | 70.0 ms | 32 |
| `node0_cores096_clients032_gen0512` | 76.1 ms | 37219 | 78.3 ms | 95.7 ms | 73.8 ms | 76.5 ms | 76.7 ms | 64 |
| `node0_cores096_clients064_gen0512` | 82.0 ms | 68545 | 86.6 ms | 97.3 ms | 79.3 ms | 82.1 ms | 82.2 ms | 128 |
| `node0_cores096_clients128_gen0512` | 106.5 ms | 105601 | 119.2 ms | 143.8 ms | 105.8 ms | 107.7 ms | 108.0 ms | 128 |
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
| `node0_cores096_clients001_gen0512` | 54.2 ms | 1649 | 62.5 ms | 72.5 ms | 54.2 ms | 54.2 ms | 54.2 ms | 3 |
| `node0_cores096_clients002_gen0512` | 54.2 ms | 3291 | 62.5 ms | 72.5 ms | 53.8 ms | 54.2 ms | 54.3 ms | 6 |
| `node0_cores096_clients004_gen0512` | 55.1 ms | 6467 | 62.5 ms | 72.5 ms | 54.7 ms | 55.1 ms | 55.3 ms | 12 |
| `node0_cores024_clients008_gen0512` | 78.3 ms | 9049 | 87.5 ms | 97.5 ms | 77.6 ms | 78.3 ms | 78.4 ms | 16 |
| `node0_cores048_clients008_gen0512` | 57.1 ms | 12417 | 62.5 ms | 72.5 ms | 56.8 ms | 57.0 ms | 57.3 ms | 24 |
| `node0_cores072_clients008_gen0512` | 55.6 ms | 12777 | 62.5 ms | 72.5 ms | 55.2 ms | 55.6 ms | 55.7 ms | 24 |
| `node0_cores096_clients008_gen0512` | 57.2 ms | 12417 | 62.5 ms | 72.5 ms | 56.8 ms | 57.1 ms | 57.5 ms | 24 |
| `node0_cores096_clients016_gen0512` | 61.9 ms | 22961 | 62.5 ms | 72.5 ms | 61.9 ms | 62.0 ms | 62.1 ms | 48 |
| `node0_cores096_clients032_gen0512` | 67.5 ms | 41859 | 62.8 ms | 73.1 ms | 67.2 ms | 67.7 ms | 68.0 ms | 64 |
| `node0_cores096_clients064_gen0512` | 86.8 ms | 65028 | 87.6 ms | 97.6 ms | 86.6 ms | 86.9 ms | 86.9 ms | 128 |
| `node0_cores096_clients128_gen0512` | 128.3 ms | 87042 | 125.4 ms | 145.7 ms | 121.7 ms | 128.3 ms | 131.1 ms | 128 |
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
| `node0_cores096_clients001_gen0512` | 31.9 ms | 2804 | 37.5 ms | 47.5 ms | 31.8 ms | 31.9 ms | 31.9 ms | 5 |
| `node0_cores096_clients002_gen0512` | 33.6 ms | 5313 | 37.5 ms | 47.5 ms | 33.3 ms | 33.6 ms | 33.7 ms | 10 |
| `node0_cores096_clients004_gen0512` | 34.7 ms | 10265 | 37.5 ms | 47.5 ms | 34.5 ms | 34.7 ms | 34.8 ms | 20 |
| `node0_cores024_clients008_gen0512` | 48.0 ms | 14825 | 38.2 ms | 48.8 ms | 48.0 ms | 48.0 ms | 48.1 ms | 24 |
| `node0_cores048_clients008_gen0512` | 35.8 ms | 19857 | 37.5 ms | 47.5 ms | 35.8 ms | 35.8 ms | 35.9 ms | 40 |
| `node0_cores072_clients008_gen0512` | 34.5 ms | 20585 | 37.5 ms | 47.5 ms | 34.0 ms | 34.4 ms | 34.6 ms | 40 |
| `node0_cores096_clients008_gen0512` | 35.3 ms | 20145 | 37.5 ms | 47.5 ms | 35.2 ms | 35.3 ms | 35.5 ms | 40 |
| `node0_cores096_clients016_gen0512` | 37.7 ms | 37585 | 37.5 ms | 47.5 ms | 37.5 ms | 37.7 ms | 38.2 ms | 80 |
| `node0_cores096_clients032_gen0512` | 42.9 ms | 65665 | 37.7 ms | 47.9 ms | 41.2 ms | 42.9 ms | 43.0 ms | 128 |
| `node0_cores096_clients064_gen0512` | 75.3 ms | 75013 | 75.3 ms | 95.1 ms | 72.5 ms | 75.6 ms | 76.2 ms | 128 |
| `node0_cores096_clients128_gen0512` | 101.9 ms | 110465 | 106.9 ms | 141.5 ms | 101.5 ms | 103.2 ms | 103.5 ms | 128 |
| `node0_cores096_clients001_gen0512` | 32.1 ms | 2790 | 37.5 ms | 47.5 ms | 32.0 ms | 32.1 ms | 32.1 ms | 5 |
| `node0_cores096_clients002_gen0512` | 33.4 ms | 5343 | 37.5 ms | 47.5 ms | 33.1 ms | 33.4 ms | 33.5 ms | 10 |
| `node0_cores096_clients004_gen0512` | 35.0 ms | 10173 | 37.5 ms | 47.5 ms | 34.9 ms | 35.0 ms | 35.1 ms | 20 |
| `node0_cores024_clients008_gen0512` | 47.9 ms | 14841 | 38.2 ms | 48.7 ms | 47.9 ms | 47.9 ms | 48.1 ms | 24 |
| `node0_cores048_clients008_gen0512` | 35.8 ms | 19881 | 37.5 ms | 47.5 ms | 35.8 ms | 35.8 ms | 35.9 ms | 40 |
| `node0_cores072_clients008_gen0512` | 34.2 ms | 20713 | 37.5 ms | 47.5 ms | 33.8 ms | 34.2 ms | 34.3 ms | 40 |
| `node0_cores096_clients008_gen0512` | 35.4 ms | 20129 | 37.5 ms | 47.5 ms | 35.3 ms | 35.4 ms | 35.5 ms | 40 |
| `node0_cores096_clients016_gen0512` | 37.5 ms | 37682 | 37.5 ms | 47.5 ms | 37.4 ms | 37.5 ms | 37.8 ms | 80 |
| `node0_cores096_clients032_gen0512` | 42.8 ms | 65857 | 37.7 ms | 47.9 ms | 41.2 ms | 42.7 ms | 43.1 ms | 128 |
| `node0_cores096_clients064_gen0512` | 74.7 ms | 75586 | 73.1 ms | 94.6 ms | 72.0 ms | 74.9 ms | 75.9 ms | 128 |
| `node0_cores096_clients128_gen0512` | 101.1 ms | 111489 | 101.2 ms | 140.4 ms | 100.2 ms | 102.4 ms | 103.1 ms | 128 |
| `node0_cores096_clients001_gen0512` | 111.9 ms | 799 | 125.0 ms | 145.1 ms | 111.8 ms | 111.9 ms | 112.0 ms | 1 |
| `node0_cores096_clients002_gen0512` | 114.6 ms | 1557 | 125.1 ms | 145.1 ms | 114.4 ms | 114.6 ms | 114.7 ms | 2 |
| `node0_cores096_clients004_gen0512` | 117.0 ms | 3041 | 125.0 ms | 145.1 ms | 116.7 ms | 117.0 ms | 117.2 ms | 4 |
| `node0_cores024_clients008_gen0512` | 167.4 ms | 4209 | 175.1 ms | 195.1 ms | 165.2 ms | 167.2 ms | 168.2 ms | 8 |
| `node0_cores048_clients008_gen0512` | 123.3 ms | 5745 | 125.0 ms | 145.1 ms | 122.5 ms | 123.6 ms | 123.6 ms | 8 |
| `node0_cores072_clients008_gen0512` | 119.6 ms | 5937 | 125.0 ms | 145.1 ms | 119.1 ms | 119.7 ms | 119.9 ms | 8 |
| `node0_cores096_clients008_gen0512` | 119.6 ms | 5937 | 125.1 ms | 145.1 ms | 119.1 ms | 119.8 ms | 119.9 ms | 8 |
| `node0_cores096_clients016_gen0512` | 127.7 ms | 11059 | 125.1 ms | 145.2 ms | 127.3 ms | 127.8 ms | 128.5 ms | 16 |
| `node0_cores096_clients032_gen0512` | 138.6 ms | 20099 | 125.7 ms | 146.3 ms | 134.7 ms | 139.4 ms | 139.5 ms | 32 |
| `node0_cores096_clients064_gen0512` | 231.0 ms | 24323 | 250.1 ms | 290.2 ms | 231.6 ms | 231.6 ms | 231.6 ms | 0 |
| `node0_cores096_clients128_gen0512` | 314.0 ms | 35203 | 347.3 ms | 389.5 ms | 314.8 ms | 314.9 ms | 314.9 ms | 0 |
| `node0_cores096_clients001_gen0512` | 24.8 ms | 3601 | 21.2 ms | 42.4 ms | 24.6 ms | 24.8 ms | 24.9 ms | 7 |
| `node0_cores096_clients002_gen0512` | 26.7 ms | 6681 | 37.4 ms | 47.5 ms | 26.6 ms | 26.7 ms | 26.8 ms | 14 |
| `node0_cores096_clients004_gen0512` | 27.4 ms | 12981 | 37.5 ms | 47.5 ms | 27.3 ms | 27.5 ms | 27.6 ms | 24 |
| `node0_cores024_clients008_gen0512` | 61.6 ms | 11401 | 62.5 ms | 72.5 ms | 61.2 ms | 61.4 ms | 62.1 ms | 24 |
| `node0_cores048_clients008_gen0512` | 40.8 ms | 17218 | 37.5 ms | 47.5 ms | 40.3 ms | 40.6 ms | 41.1 ms | 32 |
| `node0_cores072_clients008_gen0512` | 32.9 ms | 21459 | 37.5 ms | 47.5 ms | 32.6 ms | 32.8 ms | 33.2 ms | 40 |
| `node0_cores096_clients008_gen0512` | 31.7 ms | 22433 | 37.5 ms | 47.5 ms | 31.6 ms | 31.7 ms | 31.8 ms | 40 |
| `node0_cores096_clients016_gen0512` | 35.5 ms | 39763 | 37.5 ms | 47.5 ms | 35.3 ms | 35.5 ms | 35.8 ms | 80 |
| `node0_cores096_clients032_gen0512` | 44.3 ms | 63425 | 38.0 ms | 48.3 ms | 43.5 ms | 44.7 ms | 45.0 ms | 128 |
| `node0_cores096_clients064_gen0512` | 63.9 ms | 87365 | 62.7 ms | 72.8 ms | 63.9 ms | 64.2 ms | 64.3 ms | 128 |
| `node0_cores096_clients128_gen0512` | 100.1 ms | 110977 | 98.7 ms | 139.5 ms | 100.2 ms | 101.3 ms | 101.3 ms | 128 |
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
| `node0_cores096_clients001_gen0512` | 52.5 ms | 1703 | 62.5 ms | 72.5 ms | 52.5 ms | 52.5 ms | 52.6 ms | 3 |
| `node0_cores096_clients002_gen0512` | 52.7 ms | 3383 | 62.5 ms | 72.5 ms | 52.6 ms | 52.7 ms | 52.8 ms | 6 |
| `node0_cores096_clients004_gen0512` | 53.5 ms | 6661 | 62.5 ms | 72.5 ms | 52.9 ms | 53.5 ms | 53.6 ms | 12 |
| `node0_cores024_clients008_gen0512` | 77.3 ms | 9177 | 87.5 ms | 97.5 ms | 76.5 ms | 77.3 ms | 77.4 ms | 16 |
| `node0_cores048_clients008_gen0512` | 55.8 ms | 12721 | 62.5 ms | 72.5 ms | 55.2 ms | 55.8 ms | 55.8 ms | 24 |
| `node0_cores072_clients008_gen0512` | 53.9 ms | 13185 | 62.5 ms | 72.5 ms | 53.6 ms | 53.8 ms | 54.0 ms | 24 |
| `node0_cores096_clients008_gen0512` | 55.5 ms | 12801 | 62.5 ms | 72.5 ms | 55.1 ms | 55.4 ms | 55.6 ms | 24 |
| `node0_cores096_clients016_gen0512` | 60.6 ms | 23441 | 62.5 ms | 72.5 ms | 60.6 ms | 60.7 ms | 60.7 ms | 48 |
| `node0_cores096_clients032_gen0512` | 68.1 ms | 41505 | 62.8 ms | 73.1 ms | 67.8 ms | 68.3 ms | 68.6 ms | 64 |
| `node0_cores096_clients064_gen0512` | 89.1 ms | 63361 | 87.6 ms | 97.7 ms | 88.9 ms | 89.6 ms | 89.6 ms | 128 |
| `node0_cores096_clients128_gen0512` | 122.1 ms | 91395 | 125.1 ms | 145.1 ms | 117.3 ms | 122.5 ms | 124.6 ms | 128 |
| `node0_cores096_clients001_gen0512` | 52.6 ms | 1700 | 62.5 ms | 72.5 ms | 52.5 ms | 52.6 ms | 52.7 ms | 3 |
| `node0_cores096_clients002_gen0512` | 52.8 ms | 3377 | 62.5 ms | 72.5 ms | 52.7 ms | 52.8 ms | 52.9 ms | 6 |
| `node0_cores096_clients004_gen0512` | 54.0 ms | 6601 | 62.5 ms | 72.5 ms | 53.7 ms | 54.0 ms | 54.2 ms | 12 |
| `node0_cores024_clients008_gen0512` | 77.4 ms | 9162 | 87.5 ms | 97.5 ms | 76.9 ms | 77.3 ms | 77.6 ms | 16 |
| `node0_cores048_clients008_gen0512` | 55.7 ms | 12753 | 62.5 ms | 72.5 ms | 55.1 ms | 55.6 ms | 55.8 ms | 24 |
| `node0_cores072_clients008_gen0512` | 54.0 ms | 13170 | 62.5 ms | 72.5 ms | 53.6 ms | 53.9 ms | 54.1 ms | 24 |
| `node0_cores096_clients008_gen0512` | 55.5 ms | 12801 | 62.5 ms | 72.5 ms | 55.1 ms | 55.5 ms | 55.7 ms | 24 |
| `node0_cores096_clients016_gen0512` | 60.6 ms | 23441 | 62.5 ms | 72.5 ms | 60.6 ms | 60.6 ms | 60.7 ms | 48 |
| `node0_cores096_clients032_gen0512` | 68.2 ms | 41473 | 62.9 ms | 73.1 ms | 67.9 ms | 68.3 ms | 68.7 ms | 64 |
| `node0_cores096_clients064_gen0512` | 90.3 ms | 62533 | 87.7 ms | 97.9 ms | 89.7 ms | 91.0 ms | 91.2 ms | 128 |
| `node0_cores096_clients128_gen0512` | 122.1 ms | 91521 | 125.1 ms | 145.1 ms | 117.7 ms | 122.7 ms | 124.5 ms | 128 |
| `node0_cores096_clients001_gen0512` | 11.6 ms | 7721 | 17.5 ms | 23.5 ms | 11.5 ms | 11.6 ms | 11.7 ms | 16 |
| `node0_cores096_clients002_gen0512` | 13.6 ms | 13113 | 17.5 ms | 23.5 ms | 13.5 ms | 13.6 ms | 13.7 ms | 26 |
| `node0_cores096_clients004_gen0512` | 13.9 ms | 25586 | 17.5 ms | 23.5 ms | 13.8 ms | 13.9 ms | 14.1 ms | 52 |
| `node0_cores024_clients008_gen0512` | 16.7 ms | 42633 | 17.5 ms | 23.5 ms | 16.6 ms | 16.7 ms | 16.7 ms | 88 |
| `node0_cores048_clients008_gen0512` | 13.3 ms | 53449 | 17.5 ms | 23.5 ms | 13.2 ms | 13.3 ms | 13.4 ms | 112 |
| `node0_cores072_clients008_gen0512` | 12.6 ms | 56249 | 17.5 ms | 23.5 ms | 12.6 ms | 12.6 ms | 12.7 ms | 112 |
| `node0_cores096_clients008_gen0512` | 14.8 ms | 48273 | 17.5 ms | 23.5 ms | 14.6 ms | 14.8 ms | 14.9 ms | 96 |
| `node0_cores096_clients016_gen0512` | 14.1 ms | 100386 | 17.5 ms | 23.5 ms | 14.0 ms | 14.1 ms | 14.3 ms | 208 |
| `node0_cores096_clients032_gen0512` | 16.5 ms | 171681 | 17.5 ms | 23.5 ms | 16.5 ms | 16.5 ms | 16.6 ms | 352 |
| `node0_cores096_clients064_gen0512` | 22.9 ms | 246595 | 18.2 ms | 24.7 ms | 15.1 ms | 22.9 ms | 23.1 ms | 512 |
| `node0_cores096_clients128_gen0512` | 34.3 ms | 328706 | 37.5 ms | 47.5 ms | 32.3 ms | 34.2 ms | 34.7 ms | 640 |
| `node0_cores096_clients001_gen0512` | 11.7 ms | 7659 | 17.5 ms | 23.5 ms | 11.6 ms | 11.7 ms | 11.7 ms | 16 |
| `node0_cores096_clients002_gen0512` | 13.5 ms | 13217 | 17.5 ms | 23.5 ms | 13.4 ms | 13.5 ms | 13.6 ms | 26 |
| `node0_cores096_clients004_gen0512` | 13.9 ms | 25693 | 17.5 ms | 23.5 ms | 13.8 ms | 13.8 ms | 14.0 ms | 52 |
| `node0_cores024_clients008_gen0512` | 16.8 ms | 42425 | 17.5 ms | 23.5 ms | 16.7 ms | 16.8 ms | 16.8 ms | 88 |
| `node0_cores048_clients008_gen0512` | 13.0 ms | 54657 | 17.5 ms | 23.5 ms | 13.0 ms | 13.0 ms | 13.0 ms | 112 |
| `node0_cores072_clients008_gen0512` | 12.5 ms | 57057 | 17.5 ms | 23.5 ms | 11.5 ms | 12.5 ms | 12.5 ms | 113 |
| `node0_cores096_clients008_gen0512` | 14.9 ms | 47626 | 17.5 ms | 23.5 ms | 14.7 ms | 14.9 ms | 15.2 ms | 96 |
| `node0_cores096_clients016_gen0512` | 14.2 ms | 100241 | 17.5 ms | 23.5 ms | 14.1 ms | 14.1 ms | 14.3 ms | 208 |
| `node0_cores096_clients032_gen0512` | 16.6 ms | 170659 | 17.5 ms | 23.5 ms | 16.5 ms | 16.6 ms | 16.7 ms | 352 |
| `node0_cores096_clients064_gen0512` | 23.0 ms | 245509 | 18.2 ms | 24.8 ms | 22.9 ms | 23.1 ms | 23.2 ms | 512 |
| `node0_cores096_clients128_gen0512` | 33.7 ms | 334338 | 37.5 ms | 47.5 ms | 32.1 ms | 33.7 ms | 33.9 ms | 640 |
| `node0_cores096_clients001_gen0512` | 26.8 ms | 3343 | 37.5 ms | 47.5 ms | 26.7 ms | 26.8 ms | 26.8 ms | 7 |
| `node0_cores096_clients002_gen0512` | 26.8 ms | 6659 | 37.5 ms | 47.5 ms | 26.7 ms | 26.9 ms | 26.9 ms | 14 |
| `node0_cores096_clients004_gen0512` | 27.8 ms | 12833 | 37.5 ms | 47.5 ms | 27.7 ms | 27.7 ms | 27.9 ms | 24 |
| `node0_cores024_clients008_gen0512` | 38.1 ms | 18657 | 37.5 ms | 47.5 ms | 38.1 ms | 38.1 ms | 38.2 ms | 32 |
| `node0_cores048_clients008_gen0512` | 29.1 ms | 24457 | 37.5 ms | 47.5 ms | 28.7 ms | 29.1 ms | 29.2 ms | 48 |
| `node0_cores072_clients008_gen0512` | 29.1 ms | 24481 | 37.5 ms | 47.5 ms | 28.7 ms | 29.0 ms | 29.2 ms | 48 |
| `node0_cores096_clients008_gen0512` | 29.1 ms | 24474 | 37.5 ms | 47.5 ms | 28.7 ms | 29.0 ms | 29.3 ms | 48 |
| `node0_cores096_clients016_gen0512` | 31.0 ms | 45841 | 37.5 ms | 47.5 ms | 30.9 ms | 30.9 ms | 31.3 ms | 96 |
| `node0_cores096_clients032_gen0512` | 34.9 ms | 81025 | 37.5 ms | 47.5 ms | 34.7 ms | 34.8 ms | 35.6 ms | 160 |
| `node0_cores096_clients064_gen0512` | 52.7 ms | 107075 | 57.0 ms | 71.5 ms | 51.1 ms | 53.0 ms | 53.1 ms | 192 |
| `node0_cores096_clients128_gen0512` | 74.2 ms | 151041 | 72.6 ms | 94.5 ms | 70.0 ms | 74.9 ms | 75.7 ms | 256 |
| `node0_cores096_clients001_gen0512` | 91.9 ms | 974 | 87.5 ms | 97.6 ms | 91.9 ms | 91.9 ms | 91.9 ms | 2 |
| `node0_cores096_clients002_gen0512` | 92.5 ms | 1931 | 87.6 ms | 97.6 ms | 92.5 ms | 92.5 ms | 92.6 ms | 4 |
| `node0_cores096_clients004_gen0512` | 93.2 ms | 3825 | 87.7 ms | 97.9 ms | 93.1 ms | 93.3 ms | 93.3 ms | 8 |
| `node0_cores024_clients008_gen0512` | 135.5 ms | 5217 | 125.0 ms | 145.1 ms | 134.4 ms | 135.7 ms | 136.0 ms | 8 |
| `node0_cores048_clients008_gen0512` | 99.0 ms | 7185 | 89.4 ms | 112.1 ms | 98.9 ms | 99.1 ms | 99.3 ms | 8 |
| `node0_cores072_clients008_gen0512` | 100.6 ms | 7074 | 102.8 ms | 140.7 ms | 100.5 ms | 100.7 ms | 101.1 ms | 8 |
| `node0_cores096_clients008_gen0512` | 96.0 ms | 7417 | 88.7 ms | 99.7 ms | 95.9 ms | 96.1 ms | 96.3 ms | 8 |
| `node0_cores096_clients016_gen0512` | 102.0 ms | 13907 | 118.5 ms | 143.7 ms | 101.9 ms | 102.2 ms | 102.4 ms | 16 |
| `node0_cores096_clients032_gen0512` | 109.6 ms | 25729 | 125.0 ms | 145.0 ms | 108.8 ms | 110.3 ms | 110.5 ms | 32 |
| `node0_cores096_clients064_gen0512` | 144.9 ms | 38531 | 132.4 ms | 178.3 ms | 139.7 ms | 145.7 ms | 145.9 ms | 64 |
| `node0_cores096_clients128_gen0512` | 196.7 ms | 57091 | 193.1 ms | 276.2 ms | 197.8 ms | 197.8 ms | 197.8 ms | 0 |
| `node0_cores096_clients001_gen0512` | 19.0 ms | 4701 | 17.6 ms | 23.7 ms | 18.9 ms | 19.0 ms | 19.0 ms | 10 |
| `node0_cores096_clients002_gen0512` | 22.8 ms | 7801 | 17.9 ms | 24.2 ms | 22.7 ms | 22.8 ms | 22.9 ms | 16 |
| `node0_cores096_clients004_gen0512` | 28.5 ms | 12469 | 37.5 ms | 47.5 ms | 28.2 ms | 28.5 ms | 28.8 ms | 24 |
| `node0_cores024_clients008_gen0512` | 52.9 ms | 13401 | 60.2 ms | 72.1 ms | 51.9 ms | 52.9 ms | 54.1 ms | 24 |
| `node0_cores048_clients008_gen0512` | 38.1 ms | 18633 | 37.5 ms | 47.5 ms | 38.0 ms | 38.0 ms | 38.3 ms | 32 |
| `node0_cores072_clients008_gen0512` | 34.2 ms | 20737 | 37.5 ms | 47.5 ms | 33.2 ms | 34.7 ms | 35.2 ms | 40 |
| `node0_cores096_clients008_gen0512` | 34.3 ms | 20713 | 37.5 ms | 47.5 ms | 34.2 ms | 34.4 ms | 34.4 ms | 40 |
| `node0_cores096_clients016_gen0512` | 33.7 ms | 41985 | 37.5 ms | 47.5 ms | 32.7 ms | 34.1 ms | 34.8 ms | 80 |
| `node0_cores096_clients032_gen0512` | 39.9 ms | 70882 | 37.6 ms | 47.6 ms | 39.5 ms | 40.0 ms | 40.1 ms | 128 |
| `node0_cores096_clients064_gen0512` | 52.9 ms | 106497 | 60.6 ms | 72.1 ms | 51.9 ms | 53.0 ms | 53.3 ms | 192 |
| `node0_cores096_clients128_gen0512` | 73.6 ms | 152323 | 68.9 ms | 92.7 ms | 73.0 ms | 73.1 ms | 74.9 ms | 256 |
| `node0_cores096_clients001_gen0512` | 64.3 ms | 1390 | 62.5 ms | 72.5 ms | 64.3 ms | 64.4 ms | 64.4 ms | 2 |
| `node0_cores096_clients002_gen0512` | 64.2 ms | 2783 | 62.5 ms | 72.5 ms | 64.1 ms | 64.2 ms | 64.2 ms | 4 |
| `node0_cores096_clients004_gen0512` | 65.3 ms | 5462 | 62.5 ms | 72.6 ms | 65.2 ms | 65.4 ms | 65.4 ms | 8 |
| `node0_cores024_clients008_gen0512` | 91.1 ms | 7801 | 87.5 ms | 97.5 ms | 91.0 ms | 91.1 ms | 91.4 ms | 16 |
| `node0_cores048_clients008_gen0512` | 66.3 ms | 10715 | 62.5 ms | 72.6 ms | 66.2 ms | 66.3 ms | 66.6 ms | 16 |
| `node0_cores072_clients008_gen0512` | 65.0 ms | 10945 | 62.5 ms | 72.5 ms | 64.9 ms | 64.9 ms | 65.1 ms | 16 |
| `node0_cores096_clients008_gen0512` | 66.7 ms | 10673 | 62.6 ms | 72.6 ms | 66.6 ms | 66.7 ms | 66.9 ms | 16 |
| `node0_cores096_clients016_gen0512` | 71.2 ms | 19944 | 63.5 ms | 74.2 ms | 70.8 ms | 71.2 ms | 71.4 ms | 32 |
| `node0_cores096_clients032_gen0512` | 76.1 ms | 37027 | 80.0 ms | 96.1 ms | 75.6 ms | 76.0 ms | 76.0 ms | 64 |
| `node0_cores096_clients064_gen0512` | 94.3 ms | 59653 | 88.3 ms | 99.0 ms | 94.1 ms | 94.5 ms | 94.6 ms | 64 |
| `node0_cores096_clients128_gen0512` | 134.0 ms | 82947 | 125.2 ms | 145.4 ms | 131.6 ms | 134.8 ms | 134.8 ms | 128 |

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
| `AMead10/Llama-3.2-1B-Instruct-AWQ` | 24 | 23.7 ms | 23.5 ms | 334.59 | 64 | 23.5 ms | 12.0 s | 138.6 ms |
| `AMead10/Llama-3.2-1B-Instruct-AWQ` | 48 | 20.7 ms | 20.7 ms | 383.67 | 72 | 20.7 ms | 10.6 s | 104.4 ms |
| `AMead10/Llama-3.2-1B-Instruct-AWQ` | 72 | 18.1 ms | 18.1 ms | 438.68 | 80 | 18.1 ms | 9245.8 ms | 82.6 ms |
| `AMead10/Llama-3.2-1B-Instruct-AWQ` | 96 | 10.2 ms | 10.2 ms | 777.70 | 144 | 10.2 ms | 5214.6 ms | 45.4 ms |
| `AMead10/Llama-3.2-3B-Instruct-AWQ` | 24 | 35.9 ms | 35.6 ms | 219.74 | 40 | 35.8 ms | 18.3 s | 300.1 ms |
| `AMead10/Llama-3.2-3B-Instruct-AWQ` | 48 | 29.7 ms | 29.6 ms | 266.32 | 48 | 29.6 ms | 15.1 s | 196.6 ms |
| `AMead10/Llama-3.2-3B-Instruct-AWQ` | 72 | 25.0 ms | 25.0 ms | 316.28 | 56 | 25.0 ms | 12.8 s | 167.9 ms |
| `AMead10/Llama-3.2-3B-Instruct-AWQ` | 96 | 19.1 ms | 19.1 ms | 416.19 | 72 | 19.1 ms | 9742.8 ms | 88.9 ms |
| `Qwen/QwQ-32B` | 24 | 292.9 ms | 292.5 ms | 27.04 | 0 | — | — | 1143.6 ms |
| `Qwen/QwQ-32B` | 48 | 214.1 ms | 214.1 ms | 37.08 | 0 | — | — | 831.3 ms |
| `Qwen/QwQ-32B` | 72 | 213.0 ms | 213.0 ms | 37.26 | 0 | — | — | 746.1 ms |
| `Qwen/QwQ-32B` | 96 | 203.8 ms | 203.9 ms | 39.03 | 0 | — | — | 663.6 ms |
| `Qwen/QwQ-32B-AWQ` | 24 | 224.4 ms | 223.9 ms | 34.86 | 0 | — | — | 2156.2 ms |
| `Qwen/QwQ-32B-AWQ` | 48 | 137.4 ms | 137.4 ms | 56.81 | 8 | 137.6 ms | 70.3 s | 1176.1 ms |
| `Qwen/QwQ-32B-AWQ` | 72 | 108.5 ms | 108.5 ms | 72.54 | 8 | 108.3 ms | 55.4 s | 821.3 ms |
| `Qwen/QwQ-32B-AWQ` | 96 | 96.3 ms | 96.4 ms | 82.23 | 8 | 96.1 ms | 49.1 s | 539.7 ms |
| `Qwen/Qwen2.5-0.5B-Instruct` | 24 | 11.6 ms | 11.5 ms | 687.39 | 128 | 11.6 ms | 5909.6 ms | 43.5 ms |
| `Qwen/Qwen2.5-0.5B-Instruct` | 48 | 23.0 ms | 23.1 ms | 345.36 | 64 | 23.0 ms | 11.8 s | 74.9 ms |
| `Qwen/Qwen2.5-0.5B-Instruct` | 72 | 32.9 ms | 32.9 ms | 242.26 | 40 | 32.9 ms | 16.8 s | 93.3 ms |
| `Qwen/Qwen2.5-0.5B-Instruct` | 96 | 20.0 ms | 18.7 ms | 399.07 | 72 | 20.1 ms | 10.3 s | 56.4 ms |
| `Qwen/Qwen3-1.7B` | 24 | 24.4 ms | 24.4 ms | 326.32 | 56 | 24.4 ms | 12.5 s | 96.0 ms |
| `Qwen/Qwen3-1.7B` | 48 | 19.3 ms | 19.3 ms | 410.69 | 72 | 19.3 ms | 9881.0 ms | 81.2 ms |
| `Qwen/Qwen3-1.7B` | 72 | 18.0 ms | 18.0 ms | 441.44 | 80 | 18.0 ms | 9192.3 ms | 90.0 ms |
| `Qwen/Qwen3-1.7B` | 96 | 22.5 ms | 22.5 ms | 352.90 | 64 | 22.5 ms | 11.5 s | 77.3 ms |
| `Qwen/Qwen3-14B` | 24 | 134.9 ms | 135.0 ms | 58.68 | 8 | 135.1 ms | 69.0 s | 596.1 ms |
| `Qwen/Qwen3-14B` | 48 | 97.6 ms | 97.7 ms | 81.34 | 8 | 97.8 ms | 50.0 s | 400.5 ms |
| `Qwen/Qwen3-14B` | 72 | 99.2 ms | 99.3 ms | 80.10 | 8 | 99.3 ms | 50.8 s | 379.9 ms |
| `Qwen/Qwen3-14B` | 96 | 94.9 ms | 95.0 ms | 83.74 | 16 | 95.0 ms | 48.6 s | 344.6 ms |
| `Qwen/Qwen3-14B-AWQ` | 24 | 107.0 ms | 106.7 ms | 73.09 | 8 | 107.1 ms | 54.7 s | 1074.0 ms |
| `Qwen/Qwen3-14B-AWQ` | 48 | 66.6 ms | 66.4 ms | 117.97 | 16 | 66.8 ms | 34.1 s | 584.4 ms |
| `Qwen/Qwen3-14B-AWQ` | 72 | 55.2 ms | 55.2 ms | 142.50 | 24 | 55.2 ms | 28.2 s | 418.1 ms |
| `Qwen/Qwen3-14B-AWQ` | 96 | 49.1 ms | 49.1 ms | 161.43 | 24 | 49.2 ms | 25.1 s | 257.0 ms |
| `Qwen/Qwen3-14B-FP8` | 24 | 115.7 ms | 115.9 ms | 68.10 | 8 | 116.0 ms | 59.3 s | 725.4 ms |
| `Qwen/Qwen3-14B-FP8` | 48 | 86.5 ms | 86.4 ms | 91.03 | 16 | 86.5 ms | 44.2 s | 490.6 ms |
| `Qwen/Qwen3-14B-FP8` | 72 | 86.5 ms | 86.4 ms | 91.21 | 16 | 86.5 ms | 44.2 s | 445.0 ms |
| `Qwen/Qwen3-14B-FP8` | 96 | 100.4 ms | 100.7 ms | 79.06 | 8 | 99.6 ms | 50.9 s | 410.5 ms |
| `Qwen/Qwen3-30B-A3B` | 24 | 85.4 ms | 85.3 ms | 92.92 | 16 | 85.5 ms | 43.7 s | 317.1 ms |
| `Qwen/Qwen3-30B-A3B` | 48 | 58.2 ms | 58.2 ms | 136.53 | 24 | 58.2 ms | 29.8 s | 268.6 ms |
| `Qwen/Qwen3-30B-A3B` | 72 | 56.3 ms | 56.3 ms | 140.72 | 24 | 56.4 ms | 28.8 s | 253.9 ms |
| `Qwen/Qwen3-30B-A3B` | 96 | 57.0 ms | 57.0 ms | 139.03 | 24 | 57.0 ms | 29.1 s | 255.6 ms |
| `Qwen/Qwen3-4B` | 24 | 48.6 ms | 48.6 ms | 163.58 | 24 | 48.7 ms | 24.9 s | 189.2 ms |
| `Qwen/Qwen3-4B` | 48 | 36.0 ms | 36.1 ms | 220.56 | 40 | 36.1 ms | 18.4 s | 149.3 ms |
| `Qwen/Qwen3-4B` | 72 | 38.4 ms | 38.4 ms | 206.96 | 32 | 38.4 ms | 19.6 s | 150.5 ms |
| `Qwen/Qwen3-4B` | 96 | 35.6 ms | 35.6 ms | 223.21 | 40 | 35.6 ms | 18.2 s | 141.4 ms |
| `Qwen/Qwen3-8B` | 24 | 78.3 ms | 78.3 ms | 101.17 | 16 | 78.4 ms | 40.1 s | 336.4 ms |
| `Qwen/Qwen3-8B` | 48 | 57.1 ms | 57.0 ms | 138.77 | 24 | 57.1 ms | 29.2 s | 246.3 ms |
| `Qwen/Qwen3-8B` | 72 | 55.6 ms | 55.6 ms | 142.77 | 24 | 55.6 ms | 28.4 s | 211.0 ms |
| `Qwen/Qwen3-8B` | 96 | 57.2 ms | 57.1 ms | 138.77 | 24 | 57.2 ms | 29.2 s | 217.1 ms |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | 24 | 12.7 ms | 12.7 ms | 627.57 | 112 | 12.7 ms | 6474.1 ms | 51.7 ms |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | 48 | 10.5 ms | 10.5 ms | 757.17 | 136 | 10.5 ms | 5365.6 ms | 41.0 ms |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | 72 | 10.7 ms | 10.6 ms | 745.71 | 136 | 10.7 ms | 5443.6 ms | 45.5 ms |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | 96 | 10.6 ms | 10.5 ms | 750.88 | 136 | 10.6 ms | 5408.4 ms | 43.4 ms |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | 24 | 25.6 ms | 25.6 ms | 310.16 | 56 | 25.6 ms | 13.1 s | 107.9 ms |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | 48 | 20.6 ms | 20.6 ms | 385.90 | 72 | 20.6 ms | 10.5 s | 84.7 ms |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | 72 | 20.2 ms | 20.2 ms | 392.30 | 72 | 20.3 ms | 10.4 s | 94.5 ms |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | 96 | 20.1 ms | 20.2 ms | 394.51 | 72 | 20.1 ms | 10.3 s | 98.7 ms |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | 24 | 48.0 ms | 48.0 ms | 165.61 | 24 | 48.0 ms | 24.5 s | 199.8 ms |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | 48 | 35.8 ms | 35.8 ms | 221.79 | 40 | 35.8 ms | 18.3 s | 145.9 ms |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | 72 | 34.5 ms | 34.4 ms | 230.06 | 40 | 34.5 ms | 17.6 s | 161.9 ms |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | 96 | 35.3 ms | 35.3 ms | 224.99 | 40 | 35.3 ms | 18.1 s | 138.5 ms |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | 24 | 47.9 ms | 47.9 ms | 165.88 | 24 | 47.9 ms | 24.5 s | 204.1 ms |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | 48 | 35.8 ms | 35.8 ms | 221.97 | 40 | 35.8 ms | 18.3 s | 144.8 ms |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | 72 | 34.2 ms | 34.2 ms | 231.57 | 40 | 34.2 ms | 17.5 s | 161.0 ms |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | 96 | 35.4 ms | 35.4 ms | 224.81 | 40 | 35.4 ms | 18.1 s | 138.2 ms |
| `RedHatAI/QwQ-32B-quantized.w8a8` | 24 | 167.4 ms | 167.2 ms | 47.03 | 8 | 167.3 ms | 85.5 s | 813.6 ms |
| `RedHatAI/QwQ-32B-quantized.w8a8` | 48 | 123.3 ms | 123.6 ms | 64.19 | 8 | 123.7 ms | 63.2 s | 543.1 ms |
| `RedHatAI/QwQ-32B-quantized.w8a8` | 72 | 119.6 ms | 119.7 ms | 66.32 | 8 | 119.8 ms | 61.2 s | 479.2 ms |
| `RedHatAI/QwQ-32B-quantized.w8a8` | 96 | 119.6 ms | 119.8 ms | 66.32 | 8 | 119.9 ms | 61.3 s | 463.5 ms |
| `hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4` | 24 | 61.6 ms | 61.4 ms | 127.39 | 24 | 61.4 ms | 31.4 s | 612.0 ms |
| `hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4` | 48 | 40.8 ms | 40.6 ms | 192.29 | 32 | 40.8 ms | 20.8 s | 394.7 ms |
| `hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4` | 72 | 32.9 ms | 32.8 ms | 239.68 | 40 | 32.9 ms | 16.8 s | 235.4 ms |
| `hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4` | 96 | 31.7 ms | 31.7 ms | 250.59 | 40 | 31.7 ms | 16.2 s | 152.6 ms |
| `ibm-granite/granite-3.2-2b-instruct` | 24 | 34.1 ms | 34.1 ms | 232.63 | 40 | 34.1 ms | 17.4 s | 139.4 ms |
| `ibm-granite/granite-3.2-2b-instruct` | 48 | 26.9 ms | 26.9 ms | 295.58 | 56 | 26.9 ms | 13.7 s | 112.6 ms |
| `ibm-granite/granite-3.2-2b-instruct` | 72 | 25.5 ms | 25.5 ms | 311.57 | 56 | 25.5 ms | 13.0 s | 110.7 ms |
| `ibm-granite/granite-3.2-2b-instruct` | 96 | 30.7 ms | 30.8 ms | 258.88 | 48 | 30.7 ms | 15.7 s | 101.6 ms |
| `meta-llama/Llama-3.1-8B` | 24 | 77.3 ms | 77.3 ms | 102.59 | 16 | 77.4 ms | 39.6 s | 332.8 ms |
| `meta-llama/Llama-3.1-8B` | 48 | 55.8 ms | 55.8 ms | 142.23 | 24 | 55.8 ms | 28.5 s | 231.1 ms |
| `meta-llama/Llama-3.1-8B` | 72 | 53.9 ms | 53.8 ms | 147.39 | 24 | 53.9 ms | 27.5 s | 218.8 ms |
| `meta-llama/Llama-3.1-8B` | 96 | 55.5 ms | 55.4 ms | 143.12 | 24 | 55.5 ms | 28.4 s | 201.0 ms |
| `meta-llama/Llama-3.1-8B-Instruct` | 24 | 77.4 ms | 77.3 ms | 102.42 | 16 | 77.4 ms | 39.6 s | 333.6 ms |
| `meta-llama/Llama-3.1-8B-Instruct` | 48 | 55.7 ms | 55.6 ms | 142.50 | 24 | 55.7 ms | 28.5 s | 230.6 ms |
| `meta-llama/Llama-3.1-8B-Instruct` | 72 | 54.0 ms | 53.9 ms | 147.13 | 24 | 54.0 ms | 27.6 s | 209.0 ms |
| `meta-llama/Llama-3.1-8B-Instruct` | 96 | 55.5 ms | 55.5 ms | 142.94 | 24 | 55.6 ms | 28.4 s | 204.7 ms |
| `meta-llama/Llama-3.2-1B` | 24 | 16.7 ms | 16.7 ms | 476.54 | 88 | 16.7 ms | 8525.3 ms | 65.5 ms |
| `meta-llama/Llama-3.2-1B` | 48 | 13.3 ms | 13.3 ms | 597.29 | 112 | 13.3 ms | 6797.1 ms | 53.3 ms |
| `meta-llama/Llama-3.2-1B` | 72 | 12.6 ms | 12.6 ms | 628.37 | 112 | 12.6 ms | 6461.8 ms | 53.3 ms |
| `meta-llama/Llama-3.2-1B` | 96 | 14.8 ms | 14.8 ms | 539.30 | 96 | 14.8 ms | 7544.7 ms | 50.9 ms |
| `meta-llama/Llama-3.2-1B-Instruct` | 24 | 16.8 ms | 16.8 ms | 474.14 | 88 | 16.8 ms | 8566.6 ms | 67.1 ms |
| `meta-llama/Llama-3.2-1B-Instruct` | 48 | 13.0 ms | 13.0 ms | 610.68 | 112 | 13.0 ms | 6648.5 ms | 53.6 ms |
| `meta-llama/Llama-3.2-1B-Instruct` | 72 | 12.5 ms | 12.5 ms | 637.08 | 113 | 12.5 ms | 6373.2 ms | 52.5 ms |
| `meta-llama/Llama-3.2-1B-Instruct` | 96 | 14.9 ms | 14.9 ms | 531.93 | 96 | 15.0 ms | 7646.1 ms | 56.1 ms |
| `meta-llama/Llama-3.2-3B-Instruct` | 24 | 38.1 ms | 38.1 ms | 208.46 | 32 | 38.2 ms | 19.5 s | 155.9 ms |
| `meta-llama/Llama-3.2-3B-Instruct` | 48 | 29.1 ms | 29.1 ms | 273.08 | 48 | 29.1 ms | 14.9 s | 117.4 ms |
| `meta-llama/Llama-3.2-3B-Instruct` | 72 | 29.1 ms | 29.0 ms | 273.17 | 48 | 29.1 ms | 14.8 s | 115.0 ms |
| `meta-llama/Llama-3.2-3B-Instruct` | 96 | 29.1 ms | 29.0 ms | 273.09 | 48 | 29.0 ms | 14.8 s | 114.1 ms |
| `microsoft/Phi-4-reasoning` | 24 | 135.5 ms | 135.7 ms | 58.41 | 8 | 135.8 ms | 69.4 s | 587.5 ms |
| `microsoft/Phi-4-reasoning` | 48 | 99.0 ms | 99.1 ms | 80.28 | 8 | 99.1 ms | 50.6 s | 399.8 ms |
| `microsoft/Phi-4-reasoning` | 72 | 100.6 ms | 100.7 ms | 78.96 | 8 | 100.8 ms | 51.5 s | 368.7 ms |
| `microsoft/Phi-4-reasoning` | 96 | 96.0 ms | 96.1 ms | 82.86 | 8 | 96.0 ms | 49.0 s | 347.5 ms |
| `openai/gpt-oss-20b` | 24 | 52.9 ms | 52.9 ms | 149.70 | 24 | 53.1 ms | 27.1 s | 252.5 ms |
| `openai/gpt-oss-20b` | 48 | 38.1 ms | 38.0 ms | 208.10 | 32 | 38.2 ms | 19.5 s | 174.6 ms |
| `openai/gpt-oss-20b` | 72 | 34.2 ms | 34.7 ms | 231.74 | 40 | 34.3 ms | 17.5 s | 146.8 ms |
| `openai/gpt-oss-20b` | 96 | 34.3 ms | 34.4 ms | 231.39 | 40 | 34.3 ms | 17.5 s | 143.2 ms |
| `zai-org/glm-4-9b-hf` | 24 | 91.1 ms | 91.1 ms | 87.12 | 16 | 91.2 ms | 46.6 s | 394.9 ms |
| `zai-org/glm-4-9b-hf` | 48 | 66.3 ms | 66.3 ms | 119.77 | 16 | 66.4 ms | 33.9 s | 261.9 ms |
| `zai-org/glm-4-9b-hf` | 72 | 65.0 ms | 64.9 ms | 122.23 | 16 | 65.0 ms | 33.2 s | 261.8 ms |
| `zai-org/glm-4-9b-hf` | 96 | 66.7 ms | 66.7 ms | 119.21 | 16 | 66.7 ms | 34.1 s | 236.0 ms |

For `AMead10/Llama-3.2-1B-Instruct-AWQ`, 96 cores finished at 10.2 ms/token and 777.70 tokens/s. 144 requests completed inside the 90-second window. 24 cores at the same concurrency was 23.7 ms/token and 334.59 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `AMead10/Llama-3.2-3B-Instruct-AWQ`, 96 cores finished at 19.1 ms/token and 416.19 tokens/s. 72 requests completed inside the 90-second window. 24 cores at the same concurrency was 35.9 ms/token and 219.74 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `Qwen/QwQ-32B`, 96 cores finished at 203.8 ms/token and 39.03 tokens/s. 24 cores at the same concurrency was 292.9 ms/token and 27.04 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `Qwen/QwQ-32B-AWQ`, 96 cores finished at 96.3 ms/token and 82.23 tokens/s. 8 requests completed inside the 90-second window. 24 cores at the same concurrency was 224.4 ms/token and 34.86 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `Qwen/Qwen2.5-0.5B-Instruct`, 24 cores finished at 11.6 ms/token and 687.39 tokens/s. 128 requests completed inside the 90-second window. 72 cores at the same concurrency was 32.9 ms/token and 242.26 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `Qwen/Qwen3-1.7B`, 72 cores finished at 18.0 ms/token and 441.44 tokens/s. 80 requests completed inside the 90-second window. 24 cores at the same concurrency was 24.4 ms/token and 326.32 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `Qwen/Qwen3-14B`, 96 cores finished at 94.9 ms/token and 83.74 tokens/s. 16 requests completed inside the 90-second window. 24 cores at the same concurrency was 134.9 ms/token and 58.68 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `Qwen/Qwen3-14B-AWQ`, 96 cores finished at 49.1 ms/token and 161.43 tokens/s. 24 requests completed inside the 90-second window. 24 cores at the same concurrency was 107.0 ms/token and 73.09 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `Qwen/Qwen3-14B-FP8`, 72 cores finished at 86.5 ms/token and 91.21 tokens/s. 16 requests completed inside the 90-second window. 24 cores at the same concurrency was 115.7 ms/token and 68.10 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `Qwen/Qwen3-30B-A3B`, 72 cores finished at 56.3 ms/token and 140.72 tokens/s. 24 requests completed inside the 90-second window. 24 cores at the same concurrency was 85.4 ms/token and 92.92 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `Qwen/Qwen3-4B`, 96 cores finished at 35.6 ms/token and 223.21 tokens/s. 40 requests completed inside the 90-second window. 24 cores at the same concurrency was 48.6 ms/token and 163.58 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `Qwen/Qwen3-8B`, 72 cores finished at 55.6 ms/token and 142.77 tokens/s. 24 requests completed inside the 90-second window. 24 cores at the same concurrency was 78.3 ms/token and 101.17 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8`, 48 cores finished at 10.5 ms/token and 757.17 tokens/s. 136 requests completed inside the 90-second window. 24 cores at the same concurrency was 12.7 ms/token and 627.57 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8`, 96 cores finished at 20.1 ms/token and 394.51 tokens/s. 72 requests completed inside the 90-second window. 24 cores at the same concurrency was 25.6 ms/token and 310.16 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8`, 72 cores finished at 34.5 ms/token and 230.06 tokens/s. 40 requests completed inside the 90-second window. 24 cores at the same concurrency was 48.0 ms/token and 165.61 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8`, 72 cores finished at 34.2 ms/token and 231.57 tokens/s. 40 requests completed inside the 90-second window. 24 cores at the same concurrency was 47.9 ms/token and 165.88 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `RedHatAI/QwQ-32B-quantized.w8a8`, 72 cores finished at 119.6 ms/token and 66.32 tokens/s. 8 requests completed inside the 90-second window. 24 cores at the same concurrency was 167.4 ms/token and 47.03 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4`, 96 cores finished at 31.7 ms/token and 250.59 tokens/s. 40 requests completed inside the 90-second window. 24 cores at the same concurrency was 61.6 ms/token and 127.39 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `ibm-granite/granite-3.2-2b-instruct`, 72 cores finished at 25.5 ms/token and 311.57 tokens/s. 56 requests completed inside the 90-second window. 24 cores at the same concurrency was 34.1 ms/token and 232.63 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `meta-llama/Llama-3.1-8B`, 72 cores finished at 53.9 ms/token and 147.39 tokens/s. 24 requests completed inside the 90-second window. 24 cores at the same concurrency was 77.3 ms/token and 102.59 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `meta-llama/Llama-3.1-8B-Instruct`, 72 cores finished at 54.0 ms/token and 147.13 tokens/s. 24 requests completed inside the 90-second window. 24 cores at the same concurrency was 77.4 ms/token and 102.42 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `meta-llama/Llama-3.2-1B`, 72 cores finished at 12.6 ms/token and 628.37 tokens/s. 112 requests completed inside the 90-second window. 24 cores at the same concurrency was 16.7 ms/token and 476.54 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `meta-llama/Llama-3.2-1B-Instruct`, 72 cores finished at 12.5 ms/token and 637.08 tokens/s. 113 requests completed inside the 90-second window. 24 cores at the same concurrency was 16.8 ms/token and 474.14 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `meta-llama/Llama-3.2-3B-Instruct`, 72 cores finished at 29.1 ms/token and 273.17 tokens/s. 48 requests completed inside the 90-second window. 24 cores at the same concurrency was 38.1 ms/token and 208.46 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `microsoft/Phi-4-reasoning`, 96 cores finished at 96.0 ms/token and 82.86 tokens/s. 8 requests completed inside the 90-second window. 24 cores at the same concurrency was 135.5 ms/token and 58.41 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `openai/gpt-oss-20b`, 72 cores finished at 34.2 ms/token and 231.74 tokens/s. 40 requests completed inside the 90-second window. 24 cores at the same concurrency was 52.9 ms/token and 149.70 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

For `zai-org/glm-4-9b-hf`, 72 cores finished at 65.0 ms/token and 122.23 tokens/s. 16 requests completed inside the 90-second window. 24 cores at the same concurrency was 91.1 ms/token and 87.12 tokens/s. OpenMP warning #124 is absent, so each selected core has its own compute thread.

## Thread pinning

All 297 attempts with a server log are free of OpenMP warning #124. The server process is started with `numactl --physcpubind=0-(N-1) --membind=0`, and vLLM re-execs the worker under the same CPU list. Generated tokens are fixed at 512.

This 0.5B path is manual BF16, not a Xeon 6 recipe. AMX-busy time across finished runs is 0.01%–8.61% of counted cycles. It rises with batch size and is still a small slice of the step. IPC stays near 0.19–1.12.

Reported DRAM bandwidth in `system.csv` is about 0.0002 GB/s. A 0.5B BF16 model is about 1 GB of weights, larger than this socket's share of the 960 MiB L3, so a real decode should move on the order of gigabytes per second. The IMC CAS counts are tens of events per 100 ms interval. Treat the bandwidth column as not yet measuring this workload. It is not evidence that decode is cache-resident.

## Other vLLM series

| Config | Server TTFT mean | TTFT n | Queue mean | Prefill n | Decode-time n | Request TPOT n | E2E n | KV cache mean | IPC | AMX busy | L3 stall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `node0_cores096_clients001_gen0512` | 15.8 ms | 23 | 0.0 ms | 22 | 22 | 22 | 22 | 0.00017 | 0.932 | 0.02% | 9.96% |
| `node0_cores096_clients002_gen0512` | 26.5 ms | 42 | 0.0 ms | 40 | 40 | 40 | 40 | 0.00034 | 0.926 | 0.05% | 9.82% |
| `node0_cores096_clients004_gen0512` | 37.9 ms | 80 | 0.0 ms | 76 | 76 | 76 | 76 | 0.00064 | 0.947 | 0.09% | 9.49% |
| `node0_cores024_clients008_gen0512` | 138.6 ms | 64 | 0.0 ms | 56 | 56 | 56 | 56 | 0.00128 | 0.733 | 0.63% | 22.82% |
| `node0_cores048_clients008_gen0512` | 104.4 ms | 72 | 0.0 ms | 64 | 64 | 64 | 64 | 0.00131 | 0.758 | 0.37% | 16.83% |
| `node0_cores072_clients008_gen0512` | 82.6 ms | 80 | 0.0 ms | 72 | 72 | 72 | 72 | 0.00127 | 0.784 | 0.29% | 15.67% |
| `node0_cores096_clients008_gen0512` | 45.4 ms | 144 | 0.0 ms | 136 | 136 | 136 | 136 | 0.00130 | 0.931 | 0.39% | 12.26% |
| `node0_cores096_clients016_gen0512` | 72.2 ms | 256 | 0.0 ms | 240 | 240 | 240 | 240 | 0.00257 | 0.893 | 0.70% | 12.71% |
| `node0_cores096_clients032_gen0512` | 98.8 ms | 416 | 0.1 ms | 384 | 384 | 384 | 384 | 0.00519 | 0.874 | 1.12% | 12.82% |
| `node0_cores096_clients064_gen0512` | 161.7 ms | 576 | 0.1 ms | 512 | 512 | 512 | 512 | 0.01051 | 0.815 | 1.69% | 9.51% |
| `node0_cores096_clients128_gen0512` | 291.4 ms | 768 | 0.2 ms | 640 | 640 | 640 | 640 | 0.02075 | 0.827 | 2.33% | 10.31% |
| `node0_cores096_clients001_gen0512` | 28.4 ms | 12 | 0.0 ms | 11 | 11 | 11 | 11 | 0.00058 | 0.834 | 0.02% | 15.70% |
| `node0_cores096_clients002_gen0512` | 49.5 ms | 22 | 0.0 ms | 20 | 20 | 20 | 20 | 0.00114 | 0.849 | 0.04% | 14.96% |
| `node0_cores096_clients004_gen0512` | 63.0 ms | 44 | 0.0 ms | 40 | 40 | 40 | 40 | 0.00229 | 0.876 | 0.08% | 14.46% |
| `node0_cores024_clients008_gen0512` | 300.1 ms | 40 | 0.0 ms | 32 | 32 | 32 | 32 | 0.00439 | 0.840 | 1.03% | 25.60% |
| `node0_cores048_clients008_gen0512` | 196.6 ms | 48 | 0.0 ms | 40 | 40 | 40 | 40 | 0.00448 | 0.790 | 0.63% | 21.75% |
| `node0_cores072_clients008_gen0512` | 167.9 ms | 56 | 0.0 ms | 48 | 48 | 48 | 48 | 0.00452 | 0.854 | 0.52% | 18.28% |
| `node0_cores096_clients008_gen0512` | 88.9 ms | 80 | 0.0 ms | 72 | 72 | 72 | 72 | 0.00458 | 0.891 | 0.52% | 19.77% |
| `node0_cores096_clients016_gen0512` | 143.8 ms | 144 | 0.0 ms | 128 | 128 | 128 | 128 | 0.00866 | 0.833 | 0.94% | 20.31% |
| `node0_cores096_clients032_gen0512` | 217.1 ms | 224 | 0.1 ms | 192 | 192 | 192 | 192 | 0.01824 | 0.803 | 1.47% | 20.09% |
| `node0_cores096_clients064_gen0512` | 364.4 ms | 320 | 0.1 ms | 256 | 256 | 256 | 256 | 0.03629 | 0.727 | 2.18% | 17.90% |
| `node0_cores096_clients128_gen0512` | 664.2 ms | 384 | 0.2 ms | 256 | 256 | 256 | 256 | 0.07329 | 0.733 | 3.00% | 19.87% |
| `node0_cores096_clients001_gen0512` | 226.0 ms | 1 | — ms | 0 | 0 | 0 | 0 | 0.00122 | 0.247 | 0.11% | 75.41% |
| `node0_cores096_clients002_gen0512` | 355.9 ms | 2 | — ms | 0 | 0 | 0 | 0 | 0.00242 | 0.248 | 0.22% | 75.22% |
| `node0_cores096_clients004_gen0512` | 518.3 ms | 4 | — ms | 0 | 0 | 0 | 0 | 0.00482 | 0.251 | 0.44% | 74.83% |
| `node0_cores024_clients008_gen0512` | 1143.6 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00744 | 0.191 | 2.29% | 80.49% |
| `node0_cores048_clients008_gen0512` | 831.3 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00921 | 0.252 | 1.55% | 74.81% |
| `node0_cores072_clients008_gen0512` | 746.1 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00922 | 0.322 | 1.08% | 68.04% |
| `node0_cores096_clients008_gen0512` | 663.6 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00952 | 0.256 | 0.87% | 73.98% |
| `node0_cores096_clients016_gen0512` | 871.6 ms | 16 | — ms | 0 | 0 | 0 | 0 | 0.01836 | 0.298 | 1.66% | 69.55% |
| `node0_cores096_clients032_gen0512` | 1657.0 ms | 32 | — ms | 0 | 0 | 0 | 0 | 0.03493 | 0.303 | 3.11% | 67.16% |
| `node0_cores096_clients064_gen0512` | 2464.9 ms | 64 | — ms | 0 | 0 | 0 | 0 | 0.05843 | 0.389 | 5.43% | 34.04% |
| `node0_cores096_clients128_gen0512` | 4424.5 ms | 128 | — ms | 0 | 0 | 0 | 0 | 0.09388 | 0.330 | 8.61% | 43.45% |
| `node0_cores096_clients001_gen0512` | 133.9 ms | 3 | 0.0 ms | 2 | 2 | 2 | 2 | 0.00125 | 0.757 | 0.02% | 16.13% |
| `node0_cores096_clients002_gen0512` | 232.4 ms | 6 | 0.0 ms | 4 | 4 | 4 | 4 | 0.00257 | 0.811 | 0.04% | 15.23% |
| `node0_cores096_clients004_gen0512` | 323.5 ms | 12 | 0.0 ms | 8 | 8 | 8 | 8 | 0.00522 | 0.885 | 0.07% | 12.55% |
| `node0_cores024_clients008_gen0512` | 2156.2 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00861 | 1.025 | 1.49% | 24.52% |
| `node0_cores048_clients008_gen0512` | 1176.1 ms | 16 | 0.0 ms | 8 | 8 | 8 | 8 | 0.00914 | 1.011 | 1.26% | 22.88% |
| `node0_cores072_clients008_gen0512` | 821.3 ms | 16 | 0.0 ms | 8 | 8 | 8 | 8 | 0.00934 | 0.991 | 1.09% | 22.98% |
| `node0_cores096_clients008_gen0512` | 539.7 ms | 16 | 0.0 ms | 8 | 8 | 8 | 8 | 0.01003 | 0.969 | 0.94% | 26.17% |
| `node0_cores096_clients016_gen0512` | 957.7 ms | 32 | 0.0 ms | 16 | 16 | 16 | 16 | 0.01877 | 0.916 | 1.71% | 22.68% |
| `node0_cores096_clients032_gen0512` | 1866.3 ms | 64 | 0.0 ms | 32 | 32 | 32 | 32 | 0.03680 | 0.902 | 2.67% | 17.84% |
| `node0_cores096_clients064_gen0512` | 3280.1 ms | 64 | — ms | 0 | 0 | 0 | 0 | 0.07545 | 0.810 | 3.86% | 14.12% |
| `node0_cores096_clients128_gen0512` | 5947.5 ms | 128 | — ms | 0 | 0 | 0 | 0 | 0.10991 | 0.861 | 5.56% | 11.31% |
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
| `node0_cores096_clients001_gen0512` | 109.0 ms | 2 | 0.0 ms | 1 | 1 | 1 | 1 | 0.00081 | 0.317 | 0.10% | 68.73% |
| `node0_cores096_clients002_gen0512` | 192.8 ms | 4 | 0.0 ms | 2 | 2 | 2 | 2 | 0.00161 | 0.324 | 0.21% | 67.96% |
| `node0_cores096_clients004_gen0512` | 256.3 ms | 8 | 0.0 ms | 4 | 4 | 4 | 4 | 0.00322 | 0.329 | 0.41% | 67.33% |
| `node0_cores024_clients008_gen0512` | 596.1 ms | 16 | 0.0 ms | 8 | 8 | 8 | 8 | 0.00588 | 0.233 | 2.15% | 76.74% |
| `node0_cores048_clients008_gen0512` | 400.5 ms | 16 | 0.0 ms | 8 | 8 | 8 | 8 | 0.00621 | 0.286 | 1.48% | 71.08% |
| `node0_cores072_clients008_gen0512` | 379.9 ms | 16 | 0.0 ms | 8 | 8 | 8 | 8 | 0.00608 | 0.397 | 1.00% | 60.80% |
| `node0_cores096_clients008_gen0512` | 344.6 ms | 16 | 0.0 ms | 8 | 8 | 8 | 8 | 0.00632 | 0.342 | 0.80% | 65.85% |
| `node0_cores096_clients016_gen0512` | 479.1 ms | 32 | 0.0 ms | 16 | 16 | 16 | 16 | 0.01206 | 0.379 | 1.51% | 61.92% |
| `node0_cores096_clients032_gen0512` | 739.6 ms | 64 | 0.1 ms | 32 | 32 | 32 | 32 | 0.02399 | 0.382 | 2.81% | 59.86% |
| `node0_cores096_clients064_gen0512` | 1210.0 ms | 128 | 0.1 ms | 64 | 64 | 64 | 64 | 0.04778 | 0.428 | 4.70% | 32.55% |
| `node0_cores096_clients128_gen0512` | 2000.3 ms | 128 | — ms | 0 | 0 | 0 | 0 | 0.09728 | 0.383 | 7.00% | 41.92% |
| `node0_cores096_clients001_gen0512` | 69.4 ms | 5 | 0.0 ms | 4 | 4 | 4 | 4 | 0.00080 | 0.773 | 0.02% | 18.09% |
| `node0_cores096_clients002_gen0512` | 124.0 ms | 10 | 0.0 ms | 8 | 8 | 8 | 8 | 0.00162 | 0.816 | 0.04% | 17.62% |
| `node0_cores096_clients004_gen0512` | 163.1 ms | 20 | 0.0 ms | 16 | 16 | 16 | 16 | 0.00331 | 0.874 | 0.08% | 14.91% |
| `node0_cores024_clients008_gen0512` | 1074.0 ms | 16 | 0.0 ms | 8 | 8 | 8 | 8 | 0.00581 | 0.980 | 1.40% | 25.27% |
| `node0_cores048_clients008_gen0512` | 584.4 ms | 24 | 0.0 ms | 16 | 16 | 16 | 16 | 0.00604 | 0.969 | 1.15% | 24.03% |
| `node0_cores072_clients008_gen0512` | 418.1 ms | 32 | 0.0 ms | 24 | 24 | 24 | 24 | 0.00639 | 0.959 | 0.97% | 23.07% |
| `node0_cores096_clients008_gen0512` | 257.0 ms | 32 | 0.0 ms | 24 | 24 | 24 | 24 | 0.00633 | 0.942 | 0.83% | 25.58% |
| `node0_cores096_clients016_gen0512` | 430.3 ms | 64 | 0.0 ms | 48 | 48 | 48 | 48 | 0.01276 | 0.890 | 1.49% | 22.74% |
| `node0_cores096_clients032_gen0512` | 836.3 ms | 96 | 0.0 ms | 64 | 64 | 64 | 64 | 0.02433 | 0.871 | 2.36% | 19.90% |
| `node0_cores096_clients064_gen0512` | 1459.3 ms | 128 | 0.1 ms | 64 | 64 | 64 | 64 | 0.04758 | 0.807 | 3.42% | 14.84% |
| `node0_cores096_clients128_gen0512` | 2593.6 ms | 256 | 0.2 ms | 128 | 128 | 128 | 128 | 0.09988 | 0.821 | 4.70% | 14.92% |
| `node0_cores096_clients001_gen0512` | 135.1 ms | 3 | 0.0 ms | 3 | 3 | 3 | 3 | 0.00082 | 0.735 | 0.02% | 6.62% |
| `node0_cores096_clients002_gen0512` | 189.6 ms | 6 | 0.0 ms | 4 | 4 | 4 | 4 | 0.00161 | 0.812 | 0.04% | 6.68% |
| `node0_cores096_clients004_gen0512` | 313.1 ms | 12 | 0.0 ms | 8 | 8 | 8 | 8 | 0.00310 | 0.874 | 0.07% | 6.32% |
| `node0_cores024_clients008_gen0512` | 725.4 ms | 16 | 0.0 ms | 8 | 8 | 8 | 8 | 0.00576 | 1.116 | 2.52% | 6.21% |
| `node0_cores048_clients008_gen0512` | 490.6 ms | 17 | 0.0 ms | 16 | 16 | 16 | 16 | 0.00652 | 0.999 | 1.74% | 6.18% |
| `node0_cores072_clients008_gen0512` | 445.0 ms | 17 | 0.0 ms | 16 | 16 | 16 | 16 | 0.00658 | 0.921 | 1.22% | 5.71% |
| `node0_cores096_clients008_gen0512` | 410.5 ms | 16 | 0.0 ms | 8 | 8 | 8 | 8 | 0.00604 | 0.793 | 0.76% | 4.85% |
| `node0_cores096_clients016_gen0512` | 743.9 ms | 32 | 0.0 ms | 16 | 16 | 16 | 16 | 0.01217 | 0.776 | 1.69% | 5.76% |
| `node0_cores096_clients032_gen0512` | 1244.6 ms | 64 | 0.0 ms | 32 | 32 | 32 | 32 | 0.02315 | 0.670 | 2.55% | 5.44% |
| `node0_cores096_clients064_gen0512` | 2045.6 ms | 64 | — ms | 0 | 0 | 0 | 0 | 0.05128 | 0.664 | 3.66% | 5.14% |
| `node0_cores096_clients128_gen0512` | 3797.2 ms | 128 | — ms | 0 | 0 | 0 | 0 | 0.08255 | 0.593 | 5.69% | 6.35% |
| `node0_cores096_clients001_gen0512` | 108.4 ms | 6 | 0.0 ms | 5 | 5 | 5 | 5 | 0.00049 | 0.506 | 0.06% | 29.16% |
| `node0_cores096_clients002_gen0512` | 178.4 ms | 10 | 0.0 ms | 8 | 8 | 8 | 8 | 0.00099 | 0.451 | 0.10% | 42.07% |
| `node0_cores096_clients004_gen0512` | 218.1 ms | 16 | 0.0 ms | 12 | 12 | 12 | 12 | 0.00195 | 0.395 | 0.15% | 53.95% |
| `node0_cores024_clients008_gen0512` | 317.1 ms | 24 | 0.0 ms | 16 | 16 | 16 | 16 | 0.00395 | 0.271 | 0.75% | 70.33% |
| `node0_cores048_clients008_gen0512` | 268.6 ms | 24 | 0.0 ms | 16 | 16 | 16 | 16 | 0.00399 | 0.369 | 0.55% | 59.66% |
| `node0_cores072_clients008_gen0512` | 253.9 ms | 32 | 0.0 ms | 24 | 24 | 24 | 24 | 0.00392 | 0.385 | 0.40% | 56.24% |
| `node0_cores096_clients008_gen0512` | 255.6 ms | 32 | 0.0 ms | 24 | 24 | 24 | 24 | 0.00394 | 0.412 | 0.30% | 52.04% |
| `node0_cores096_clients016_gen0512` | 312.4 ms | 48 | 0.0 ms | 32 | 32 | 32 | 32 | 0.00733 | 0.377 | 0.49% | 56.33% |
| `node0_cores096_clients032_gen0512` | 391.3 ms | 96 | 0.0 ms | 64 | 64 | 64 | 64 | 0.01524 | 0.396 | 0.90% | 53.34% |
| `node0_cores096_clients064_gen0512` | 594.5 ms | 192 | 0.1 ms | 128 | 128 | 128 | 128 | 0.03100 | 0.470 | 1.80% | 38.59% |
| `node0_cores096_clients128_gen0512` | 928.5 ms | 256 | 0.2 ms | 128 | 128 | 128 | 128 | 0.05705 | 0.492 | 2.83% | 32.73% |
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
| `node0_cores096_clients001_gen0512` | 65.5 ms | 4 | 0.0 ms | 3 | 3 | 3 | 3 | 0.00071 | 0.299 | 0.10% | 68.86% |
| `node0_cores096_clients002_gen0512` | 120.8 ms | 8 | 0.0 ms | 6 | 6 | 6 | 6 | 0.00142 | 0.299 | 0.19% | 69.48% |
| `node0_cores096_clients004_gen0512` | 151.4 ms | 16 | 0.0 ms | 12 | 12 | 12 | 12 | 0.00292 | 0.307 | 0.38% | 68.47% |
| `node0_cores024_clients008_gen0512` | 336.4 ms | 24 | 0.0 ms | 16 | 16 | 16 | 16 | 0.00572 | 0.278 | 1.98% | 71.99% |
| `node0_cores048_clients008_gen0512` | 246.3 ms | 32 | 0.0 ms | 24 | 24 | 24 | 24 | 0.00591 | 0.315 | 1.37% | 67.77% |
| `node0_cores072_clients008_gen0512` | 211.0 ms | 32 | 0.0 ms | 24 | 24 | 24 | 24 | 0.00577 | 0.357 | 0.98% | 63.84% |
| `node0_cores096_clients008_gen0512` | 217.1 ms | 32 | 0.0 ms | 24 | 24 | 24 | 24 | 0.00587 | 0.321 | 0.73% | 66.83% |
| `node0_cores096_clients016_gen0512` | 293.0 ms | 48 | 0.0 ms | 32 | 32 | 32 | 32 | 0.01153 | 0.349 | 1.34% | 63.23% |
| `node0_cores096_clients032_gen0512` | 461.0 ms | 96 | 0.0 ms | 64 | 64 | 64 | 64 | 0.02210 | 0.371 | 2.44% | 59.20% |
| `node0_cores096_clients064_gen0512` | 760.0 ms | 128 | 0.1 ms | 64 | 64 | 64 | 64 | 0.04769 | 0.419 | 4.31% | 33.88% |
| `node0_cores096_clients128_gen0512` | 1210.3 ms | 256 | 0.2 ms | 128 | 128 | 128 | 128 | 0.08443 | 0.419 | 5.82% | 38.44% |
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
| `node0_cores096_clients001_gen0512` | 42.2 ms | 6 | 0.0 ms | 5 | 5 | 5 | 5 | 0.00064 | 0.531 | 0.02% | 49.74% |
| `node0_cores096_clients002_gen0512` | 84.1 ms | 12 | 0.0 ms | 10 | 10 | 10 | 10 | 0.00130 | 0.573 | 0.03% | 46.35% |
| `node0_cores096_clients004_gen0512` | 107.2 ms | 24 | 0.0 ms | 20 | 20 | 20 | 20 | 0.00263 | 0.600 | 0.06% | 44.44% |
| `node0_cores024_clients008_gen0512` | 199.8 ms | 32 | 0.0 ms | 24 | 24 | 24 | 24 | 0.00510 | 0.384 | 1.69% | 60.93% |
| `node0_cores048_clients008_gen0512` | 145.9 ms | 40 | 0.0 ms | 32 | 32 | 32 | 32 | 0.00519 | 0.431 | 1.15% | 56.58% |
| `node0_cores072_clients008_gen0512` | 161.9 ms | 48 | 0.0 ms | 40 | 40 | 40 | 40 | 0.00521 | 0.457 | 0.84% | 53.34% |
| `node0_cores096_clients008_gen0512` | 138.5 ms | 40 | 0.0 ms | 32 | 32 | 32 | 32 | 0.00540 | 0.517 | 0.62% | 48.09% |
| `node0_cores096_clients016_gen0512` | 231.9 ms | 80 | 0.0 ms | 64 | 64 | 64 | 64 | 0.01016 | 0.517 | 1.15% | 47.41% |
| `node0_cores096_clients032_gen0512` | 324.6 ms | 160 | 0.1 ms | 128 | 128 | 128 | 128 | 0.02170 | 0.517 | 2.03% | 45.90% |
| `node0_cores096_clients064_gen0512` | 474.1 ms | 192 | 0.1 ms | 128 | 128 | 128 | 128 | 0.03909 | 0.505 | 2.59% | 30.08% |
| `node0_cores096_clients128_gen0512` | 858.8 ms | 256 | 0.2 ms | 128 | 128 | 128 | 128 | 0.07815 | 0.486 | 3.86% | 28.82% |
| `node0_cores096_clients001_gen0512` | 42.6 ms | 6 | 0.0 ms | 5 | 5 | 5 | 5 | 0.00064 | 0.529 | 0.02% | 49.78% |
| `node0_cores096_clients002_gen0512` | 85.5 ms | 12 | 0.0 ms | 10 | 10 | 10 | 10 | 0.00133 | 0.568 | 0.03% | 46.81% |
| `node0_cores096_clients004_gen0512` | 110.6 ms | 20 | 0.0 ms | 16 | 16 | 16 | 16 | 0.00262 | 0.602 | 0.06% | 44.04% |
| `node0_cores024_clients008_gen0512` | 204.1 ms | 32 | 0.0 ms | 24 | 24 | 24 | 24 | 0.00509 | 0.385 | 1.70% | 61.07% |
| `node0_cores048_clients008_gen0512` | 144.8 ms | 40 | 0.0 ms | 32 | 32 | 32 | 32 | 0.00521 | 0.431 | 1.15% | 56.71% |
| `node0_cores072_clients008_gen0512` | 161.0 ms | 48 | 0.0 ms | 40 | 40 | 40 | 40 | 0.00527 | 0.452 | 0.84% | 53.92% |
| `node0_cores096_clients008_gen0512` | 138.2 ms | 40 | 0.0 ms | 32 | 32 | 32 | 32 | 0.00536 | 0.518 | 0.61% | 48.09% |
| `node0_cores096_clients016_gen0512` | 243.7 ms | 80 | 0.0 ms | 64 | 64 | 64 | 64 | 0.01025 | 0.516 | 1.16% | 47.48% |
| `node0_cores096_clients032_gen0512` | 333.2 ms | 160 | 0.0 ms | 128 | 128 | 128 | 128 | 0.02067 | 0.518 | 2.03% | 45.72% |
| `node0_cores096_clients064_gen0512` | 478.8 ms | 192 | 0.1 ms | 128 | 128 | 128 | 128 | 0.04046 | 0.507 | 2.59% | 30.22% |
| `node0_cores096_clients128_gen0512` | 868.1 ms | 256 | 0.2 ms | 128 | 128 | 128 | 128 | 0.07918 | 0.482 | 3.88% | 29.16% |
| `node0_cores096_clients001_gen0512` | 138.1 ms | 2 | 0.0 ms | 1 | 1 | 1 | 1 | 0.00117 | 0.370 | 0.01% | 66.09% |
| `node0_cores096_clients002_gen0512` | 264.3 ms | 4 | 0.0 ms | 2 | 2 | 2 | 2 | 0.00234 | 0.419 | 0.02% | 62.31% |
| `node0_cores096_clients004_gen0512` | 369.2 ms | 8 | 0.0 ms | 4 | 4 | 4 | 4 | 0.00459 | 0.461 | 0.05% | 59.28% |
| `node0_cores024_clients008_gen0512` | 813.6 ms | 16 | 0.0 ms | 8 | 8 | 8 | 8 | 0.01025 | 0.269 | 2.06% | 71.79% |
| `node0_cores048_clients008_gen0512` | 543.1 ms | 16 | 0.0 ms | 8 | 8 | 8 | 8 | 0.00929 | 0.324 | 1.38% | 66.61% |
| `node0_cores072_clients008_gen0512` | 479.2 ms | 16 | 0.0 ms | 8 | 8 | 8 | 8 | 0.00925 | 0.374 | 0.99% | 62.28% |
| `node0_cores096_clients008_gen0512` | 463.5 ms | 16 | 0.0 ms | 8 | 8 | 8 | 8 | 0.00925 | 0.357 | 0.76% | 63.85% |
| `node0_cores096_clients016_gen0512` | 677.3 ms | 32 | 0.0 ms | 16 | 16 | 16 | 16 | 0.01853 | 0.388 | 1.42% | 60.23% |
| `node0_cores096_clients032_gen0512` | 1271.2 ms | 64 | 0.0 ms | 32 | 32 | 32 | 32 | 0.03764 | 0.395 | 2.60% | 57.33% |
| `node0_cores096_clients064_gen0512` | 1862.8 ms | 64 | — ms | 0 | 0 | 0 | 0 | 0.06880 | 0.427 | 3.39% | 38.68% |
| `node0_cores096_clients128_gen0512` | 3335.0 ms | 128 | — ms | 0 | 0 | 0 | 0 | 0.11121 | 0.409 | 5.18% | 31.09% |
| `node0_cores096_clients001_gen0512` | 44.7 ms | 8 | 0.0 ms | 7 | 7 | 7 | 7 | 0.00066 | 0.814 | 0.02% | 16.20% |
| `node0_cores096_clients002_gen0512` | 81.0 ms | 14 | 0.0 ms | 12 | 12 | 12 | 12 | 0.00129 | 0.846 | 0.04% | 15.61% |
| `node0_cores096_clients004_gen0512` | 105.2 ms | 28 | 0.0 ms | 24 | 24 | 24 | 24 | 0.00269 | 0.893 | 0.08% | 14.22% |
| `node0_cores024_clients008_gen0512` | 612.0 ms | 24 | 0.0 ms | 16 | 16 | 16 | 16 | 0.00500 | 0.968 | 1.32% | 24.83% |
| `node0_cores048_clients008_gen0512` | 394.7 ms | 40 | 0.0 ms | 32 | 32 | 32 | 32 | 0.00522 | 0.921 | 1.02% | 23.69% |
| `node0_cores072_clients008_gen0512` | 235.4 ms | 48 | 0.0 ms | 40 | 40 | 40 | 40 | 0.00495 | 0.921 | 0.89% | 23.53% |
| `node0_cores096_clients008_gen0512` | 152.6 ms | 48 | 0.0 ms | 40 | 40 | 40 | 40 | 0.00514 | 0.938 | 0.70% | 21.92% |
| `node0_cores096_clients016_gen0512` | 279.1 ms | 80 | 0.0 ms | 64 | 64 | 64 | 64 | 0.01059 | 0.881 | 1.24% | 20.85% |
| `node0_cores096_clients032_gen0512` | 464.8 ms | 128 | 0.1 ms | 96 | 96 | 96 | 96 | 0.02059 | 0.857 | 1.96% | 19.34% |
| `node0_cores096_clients064_gen0512` | 803.9 ms | 192 | 0.1 ms | 128 | 128 | 128 | 128 | 0.03962 | 0.793 | 2.88% | 15.02% |
| `node0_cores096_clients128_gen0512` | 1457.3 ms | 256 | 0.2 ms | 128 | 128 | 128 | 128 | 0.07607 | 0.815 | 3.93% | 16.36% |
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
| `node0_cores096_clients001_gen0512` | 66.8 ms | 4 | 0.0 ms | 3 | 3 | 3 | 3 | 0.00063 | 0.313 | 0.10% | 68.66% |
| `node0_cores096_clients002_gen0512` | 120.7 ms | 8 | 0.0 ms | 6 | 6 | 6 | 6 | 0.00124 | 0.311 | 0.20% | 68.38% |
| `node0_cores096_clients004_gen0512` | 154.7 ms | 16 | 0.0 ms | 12 | 12 | 12 | 12 | 0.00251 | 0.320 | 0.39% | 67.57% |
| `node0_cores024_clients008_gen0512` | 332.8 ms | 24 | 0.0 ms | 16 | 16 | 16 | 16 | 0.00500 | 0.282 | 1.98% | 71.82% |
| `node0_cores048_clients008_gen0512` | 231.1 ms | 32 | 0.0 ms | 24 | 24 | 24 | 24 | 0.00519 | 0.315 | 1.39% | 68.04% |
| `node0_cores072_clients008_gen0512` | 218.8 ms | 32 | 0.0 ms | 24 | 24 | 24 | 24 | 0.00505 | 0.348 | 1.01% | 64.72% |
| `node0_cores096_clients008_gen0512` | 201.0 ms | 32 | 0.0 ms | 24 | 24 | 24 | 24 | 0.00517 | 0.335 | 0.75% | 65.74% |
| `node0_cores096_clients016_gen0512` | 294.2 ms | 48 | 0.0 ms | 32 | 32 | 32 | 32 | 0.01042 | 0.374 | 1.35% | 61.36% |
| `node0_cores096_clients032_gen0512` | 435.9 ms | 96 | 0.1 ms | 64 | 64 | 64 | 64 | 0.01980 | 0.424 | 2.38% | 53.94% |
| `node0_cores096_clients064_gen0512` | 730.8 ms | 128 | 0.1 ms | 64 | 64 | 64 | 64 | 0.04151 | 0.470 | 4.06% | 31.07% |
| `node0_cores096_clients128_gen0512` | 1203.2 ms | 256 | 0.2 ms | 128 | 128 | 128 | 128 | 0.07434 | 0.433 | 6.03% | 37.24% |
| `node0_cores096_clients001_gen0512` | 67.8 ms | 4 | 0.0 ms | 3 | 3 | 3 | 3 | 0.00063 | 0.314 | 0.10% | 68.60% |
| `node0_cores096_clients002_gen0512` | 118.3 ms | 8 | 0.0 ms | 6 | 6 | 6 | 6 | 0.00123 | 0.314 | 0.20% | 68.24% |
| `node0_cores096_clients004_gen0512` | 154.2 ms | 16 | 0.0 ms | 12 | 12 | 12 | 12 | 0.00253 | 0.327 | 0.38% | 66.87% |
| `node0_cores024_clients008_gen0512` | 333.6 ms | 24 | 0.0 ms | 16 | 16 | 16 | 16 | 0.00496 | 0.284 | 1.98% | 71.64% |
| `node0_cores048_clients008_gen0512` | 230.6 ms | 32 | 0.0 ms | 24 | 24 | 24 | 24 | 0.00508 | 0.312 | 1.40% | 68.22% |
| `node0_cores072_clients008_gen0512` | 209.0 ms | 32 | 0.0 ms | 24 | 24 | 24 | 24 | 0.00506 | 0.350 | 1.01% | 64.55% |
| `node0_cores096_clients008_gen0512` | 204.7 ms | 32 | 0.0 ms | 24 | 24 | 24 | 24 | 0.00517 | 0.336 | 0.75% | 65.64% |
| `node0_cores096_clients016_gen0512` | 293.8 ms | 48 | 0.0 ms | 32 | 32 | 32 | 32 | 0.01041 | 0.375 | 1.35% | 61.30% |
| `node0_cores096_clients032_gen0512` | 432.8 ms | 96 | 0.1 ms | 64 | 64 | 64 | 64 | 0.01980 | 0.425 | 2.38% | 53.92% |
| `node0_cores096_clients064_gen0512` | 730.6 ms | 128 | 0.1 ms | 64 | 64 | 64 | 64 | 0.04117 | 0.477 | 4.00% | 30.62% |
| `node0_cores096_clients128_gen0512` | 1200.5 ms | 256 | 0.2 ms | 128 | 128 | 128 | 128 | 0.07433 | 0.430 | 6.03% | 37.24% |
| `node0_cores096_clients001_gen0512` | 16.2 ms | 16 | 0.0 ms | 15 | 15 | 15 | 15 | 0.00016 | 0.596 | 0.07% | 40.57% |
| `node0_cores096_clients002_gen0512` | 31.3 ms | 26 | 0.0 ms | 24 | 24 | 24 | 24 | 0.00032 | 0.593 | 0.12% | 34.41% |
| `node0_cores096_clients004_gen0512` | 39.5 ms | 52 | 0.0 ms | 48 | 48 | 48 | 48 | 0.00066 | 0.603 | 0.24% | 33.95% |
| `node0_cores024_clients008_gen0512` | 65.5 ms | 88 | 0.0 ms | 80 | 80 | 80 | 80 | 0.00133 | 0.499 | 1.47% | 50.39% |
| `node0_cores048_clients008_gen0512` | 53.3 ms | 112 | 0.0 ms | 104 | 104 | 104 | 104 | 0.00129 | 0.568 | 0.94% | 42.42% |
| `node0_cores072_clients008_gen0512` | 53.3 ms | 112 | 0.0 ms | 104 | 104 | 104 | 104 | 0.00131 | 0.605 | 0.68% | 38.81% |
| `node0_cores096_clients008_gen0512` | 50.9 ms | 96 | 0.0 ms | 88 | 88 | 88 | 88 | 0.00131 | 0.614 | 0.45% | 32.98% |
| `node0_cores096_clients016_gen0512` | 73.3 ms | 208 | 0.0 ms | 192 | 192 | 192 | 192 | 0.00260 | 0.618 | 0.93% | 36.44% |
| `node0_cores096_clients032_gen0512` | 97.2 ms | 352 | 0.1 ms | 320 | 320 | 320 | 320 | 0.00508 | 0.627 | 1.59% | 33.67% |
| `node0_cores096_clients064_gen0512` | 194.5 ms | 512 | 0.1 ms | 448 | 448 | 448 | 448 | 0.01020 | 0.653 | 2.39% | 19.94% |
| `node0_cores096_clients128_gen0512` | 266.9 ms | 768 | 0.2 ms | 640 | 640 | 640 | 640 | 0.02084 | 0.661 | 3.34% | 16.09% |
| `node0_cores096_clients001_gen0512` | 15.8 ms | 15 | 0.0 ms | 14 | 14 | 14 | 14 | 0.00016 | 0.600 | 0.07% | 40.08% |
| `node0_cores096_clients002_gen0512` | 29.7 ms | 26 | 0.0 ms | 24 | 24 | 24 | 24 | 0.00032 | 0.596 | 0.12% | 34.62% |
| `node0_cores096_clients004_gen0512` | 38.4 ms | 52 | 0.0 ms | 48 | 48 | 48 | 48 | 0.00066 | 0.599 | 0.24% | 34.18% |
| `node0_cores024_clients008_gen0512` | 67.1 ms | 88 | 0.0 ms | 80 | 80 | 80 | 80 | 0.00129 | 0.497 | 1.46% | 50.19% |
| `node0_cores048_clients008_gen0512` | 53.6 ms | 112 | 0.0 ms | 104 | 104 | 104 | 104 | 0.00129 | 0.559 | 0.96% | 43.38% |
| `node0_cores072_clients008_gen0512` | 52.5 ms | 112 | 0.0 ms | 104 | 104 | 104 | 104 | 0.00132 | 0.605 | 0.69% | 39.09% |
| `node0_cores096_clients008_gen0512` | 56.1 ms | 96 | 0.0 ms | 88 | 88 | 88 | 88 | 0.00129 | 0.613 | 0.44% | 32.41% |
| `node0_cores096_clients016_gen0512` | 69.2 ms | 208 | 0.0 ms | 192 | 192 | 192 | 192 | 0.00258 | 0.619 | 0.93% | 36.41% |
| `node0_cores096_clients032_gen0512` | 108.1 ms | 352 | 0.0 ms | 320 | 320 | 320 | 320 | 0.00527 | 0.630 | 1.58% | 33.47% |
| `node0_cores096_clients064_gen0512` | 171.4 ms | 512 | 0.1 ms | 448 | 448 | 448 | 448 | 0.01033 | 0.652 | 2.38% | 19.68% |
| `node0_cores096_clients128_gen0512` | 272.7 ms | 768 | 0.2 ms | 640 | 640 | 640 | 640 | 0.02075 | 0.654 | 3.40% | 16.36% |
| `node0_cores096_clients001_gen0512` | 34.2 ms | 7 | 0.0 ms | 6 | 6 | 6 | 6 | 0.00057 | 0.475 | 0.08% | 52.36% |
| `node0_cores096_clients002_gen0512` | 64.4 ms | 14 | 0.0 ms | 12 | 12 | 12 | 12 | 0.00113 | 0.478 | 0.16% | 52.02% |
| `node0_cores096_clients004_gen0512` | 81.6 ms | 28 | 0.0 ms | 24 | 24 | 24 | 24 | 0.00224 | 0.490 | 0.31% | 50.68% |
| `node0_cores024_clients008_gen0512` | 155.9 ms | 40 | 0.0 ms | 32 | 32 | 32 | 32 | 0.00455 | 0.360 | 1.70% | 62.99% |
| `node0_cores048_clients008_gen0512` | 117.4 ms | 48 | 0.0 ms | 40 | 40 | 40 | 40 | 0.00463 | 0.442 | 1.14% | 55.56% |
| `node0_cores072_clients008_gen0512` | 115.0 ms | 48 | 0.0 ms | 40 | 40 | 40 | 40 | 0.00465 | 0.495 | 0.79% | 49.72% |
| `node0_cores096_clients008_gen0512` | 114.1 ms | 48 | 0.0 ms | 40 | 40 | 40 | 40 | 0.00462 | 0.496 | 0.60% | 49.77% |
| `node0_cores096_clients016_gen0512` | 160.2 ms | 96 | 0.0 ms | 80 | 80 | 80 | 80 | 0.00901 | 0.493 | 1.12% | 49.05% |
| `node0_cores096_clients032_gen0512` | 239.1 ms | 160 | 0.1 ms | 128 | 128 | 128 | 128 | 0.01869 | 0.487 | 1.98% | 47.61% |
| `node0_cores096_clients064_gen0512` | 377.0 ms | 256 | 0.1 ms | 192 | 192 | 192 | 192 | 0.03617 | 0.545 | 2.91% | 28.29% |
| `node0_cores096_clients128_gen0512` | 644.0 ms | 384 | 0.2 ms | 256 | 256 | 256 | 256 | 0.06990 | 0.519 | 4.19% | 26.19% |
| `node0_cores096_clients001_gen0512` | 108.2 ms | 2 | 0.0 ms | 1 | 1 | 1 | 1 | 0.00101 | 0.301 | 0.11% | 70.17% |
| `node0_cores096_clients002_gen0512` | 194.4 ms | 4 | 0.0 ms | 2 | 2 | 2 | 2 | 0.00201 | 0.305 | 0.21% | 69.62% |
| `node0_cores096_clients004_gen0512` | 263.3 ms | 8 | 0.0 ms | 4 | 4 | 4 | 4 | 0.00399 | 0.307 | 0.42% | 69.36% |
| `node0_cores024_clients008_gen0512` | 587.5 ms | 16 | 0.0 ms | 8 | 8 | 8 | 8 | 0.00730 | 0.221 | 2.17% | 77.52% |
| `node0_cores048_clients008_gen0512` | 399.8 ms | 16 | 0.0 ms | 8 | 8 | 8 | 8 | 0.00764 | 0.295 | 1.47% | 70.96% |
| `node0_cores072_clients008_gen0512` | 368.7 ms | 16 | 0.0 ms | 8 | 8 | 8 | 8 | 0.00761 | 0.382 | 1.01% | 62.20% |
| `node0_cores096_clients008_gen0512` | 347.5 ms | 16 | 0.0 ms | 8 | 8 | 8 | 8 | 0.00788 | 0.321 | 0.81% | 67.76% |
| `node0_cores096_clients016_gen0512` | 496.2 ms | 32 | 0.0 ms | 16 | 16 | 16 | 16 | 0.01500 | 0.360 | 1.51% | 63.64% |
| `node0_cores096_clients032_gen0512` | 768.4 ms | 64 | 0.1 ms | 32 | 32 | 32 | 32 | 0.02932 | 0.361 | 2.82% | 61.68% |
| `node0_cores096_clients064_gen0512` | 1244.6 ms | 128 | 0.1 ms | 64 | 64 | 64 | 64 | 0.05974 | 0.393 | 4.82% | 35.19% |
| `node0_cores096_clients128_gen0512` | 2047.2 ms | 128 | — ms | 0 | 0 | 0 | 0 | 0.12055 | 0.356 | 7.10% | 44.48% |
| `node0_cores096_clients001_gen0512` | 51.6 ms | 10 | 0.0 ms | 9 | 9 | 9 | 9 | 0.00020 | 0.739 | 0.05% | 25.70% |
| `node0_cores096_clients002_gen0512` | 90.1 ms | 16 | 0.0 ms | 14 | 14 | 14 | 14 | 0.00040 | 0.767 | 0.08% | 22.28% |
| `node0_cores096_clients004_gen0512` | 111.0 ms | 28 | 0.0 ms | 24 | 24 | 24 | 24 | 0.00082 | 0.820 | 0.13% | 18.59% |
| `node0_cores024_clients008_gen0512` | 252.5 ms | 32 | 0.0 ms | 24 | 24 | 24 | 24 | 0.00159 | 1.020 | 0.74% | 17.79% |
| `node0_cores048_clients008_gen0512` | 174.6 ms | 40 | 0.0 ms | 32 | 32 | 32 | 32 | 0.00162 | 0.960 | 0.52% | 16.24% |
| `node0_cores072_clients008_gen0512` | 146.8 ms | 48 | 0.0 ms | 40 | 40 | 40 | 40 | 0.00160 | 0.892 | 0.41% | 16.64% |
| `node0_cores096_clients008_gen0512` | 143.2 ms | 48 | 0.0 ms | 40 | 40 | 40 | 40 | 0.00162 | 0.833 | 0.31% | 16.48% |
| `node0_cores096_clients016_gen0512` | 187.3 ms | 96 | 0.0 ms | 80 | 80 | 80 | 80 | 0.00321 | 0.746 | 1.12% | 17.12% |
| `node0_cores096_clients032_gen0512` | 266.9 ms | 160 | 0.1 ms | 128 | 128 | 128 | 128 | 0.00632 | 0.757 | 2.08% | 15.63% |
| `node0_cores096_clients064_gen0512` | 412.9 ms | 256 | 0.1 ms | 192 | 192 | 192 | 192 | 0.01260 | 0.725 | 3.21% | 10.09% |
| `node0_cores096_clients128_gen0512` | 690.4 ms | 384 | 0.2 ms | 256 | 256 | 256 | 256 | 0.02462 | 0.716 | 4.60% | 9.41% |
| `node0_cores096_clients001_gen0512` | 76.7 ms | 3 | 0.0 ms | 2 | 2 | 2 | 2 | 0.00020 | 0.328 | 0.09% | 66.83% |
| `node0_cores096_clients002_gen0512` | 129.7 ms | 6 | 0.0 ms | 4 | 4 | 4 | 4 | 0.00039 | 0.332 | 0.19% | 66.27% |
| `node0_cores096_clients004_gen0512` | 157.1 ms | 12 | 0.0 ms | 8 | 8 | 8 | 8 | 0.00078 | 0.341 | 0.37% | 65.09% |
| `node0_cores024_clients008_gen0512` | 394.9 ms | 16 | 0.0 ms | 8 | 8 | 8 | 8 | 0.00159 | 0.290 | 1.94% | 70.71% |
| `node0_cores048_clients008_gen0512` | 261.9 ms | 24 | 0.0 ms | 16 | 16 | 16 | 16 | 0.00153 | 0.334 | 1.37% | 66.22% |
| `node0_cores072_clients008_gen0512` | 261.8 ms | 24 | 0.0 ms | 16 | 16 | 16 | 16 | 0.00156 | 0.353 | 0.97% | 63.97% |
| `node0_cores096_clients008_gen0512` | 236.0 ms | 24 | 0.0 ms | 16 | 16 | 16 | 16 | 0.00156 | 0.350 | 0.72% | 63.95% |
| `node0_cores096_clients016_gen0512` | 292.5 ms | 48 | 0.0 ms | 32 | 32 | 32 | 32 | 0.00301 | 0.384 | 1.35% | 59.91% |
| `node0_cores096_clients032_gen0512` | 535.1 ms | 96 | 0.0 ms | 64 | 64 | 64 | 64 | 0.00624 | 0.409 | 2.53% | 55.54% |
| `node0_cores096_clients064_gen0512` | 838.6 ms | 128 | 0.1 ms | 64 | 64 | 64 | 64 | 0.01238 | 0.449 | 4.58% | 31.86% |
| `node0_cores096_clients128_gen0512` | 1405.2 ms | 256 | 0.2 ms | 128 | 128 | 128 | 128 | 0.02280 | 0.455 | 6.46% | 33.50% |

KV-cache occupancy stays well under 0.1%. The waiting gauge stays at 0 through the finished concurrency points, so TTFT growth is service time inside the batch, not scheduler queue time. Queue-time histograms confirm that only if requests finish; they have not, inside the window.

## FP8 expectations

This node's CPU flags list AMX tile, AMX BF16, and AMX INT8 (`amx_tile`, `amx_bf16`, `amx_int8`). There is no AMX FP8 unit. An FP8 checkpoint therefore does not get FP8 matrix math from AMX, and its weights are converted to a format the CPU kernels handle. Expect `Qwen/Qwen3-14B-FP8` to be no faster than the BF16 `Qwen/Qwen3-14B` row, and possibly slower because of that conversion. Its rows test whether the FP8 path runs on Xeon 6 and what it costs. They are not evidence of an FP8 speedup. The INT8 (`w8a8`) rows are the quantized comparison that uses AMX INT8.

## Caveats

- 19 finished runs have `complete_requests` = 0, so the official complete-request TPOT percentiles in `summary.json` are null. 512 tokens at ~350 ms/token is about three minutes, and the measurement window is 90 seconds. Use observed client TPOT and the server inter-token histogram there.
- 23922 requests have completed inside a measurement window. On those runs the request-level TPOT and decode-time histograms are populated, and they belong in the core-count table.
- Histogram p50/p90/p99 are interpolated inside 100 ms buckets. When almost every sample sits in 300–400 ms, those percentiles collapse toward the middle and the top of that bucket. Quote the mean, and the bucket share, for decode latency.
- Partial rows are mid-window and will be replaced when the attempt writes `summary.json`.
- Several finished attempts record a non-fatal Docker cleanup race (`removal of container ... is already in progress`). The run stays marked done and the controller continues.

## What changes next

This file is rewritten as attempts finish.

