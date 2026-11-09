# vLLM decode latency report

Live notes for plan `5226854cadfd` on the Xeon 6972P node-0 benchmark. Updated 2026-11-09 14:02:56 UTC.

## Snapshot

Controller is not running. Progress 66/66 successful runs.

Decode latency here is the time between generated tokens. The server series that records every token is `vllm:inter_token_latency_seconds`. The client series is the per-request mean TPOT, `(last token time − first token time) / (tokens − 1)`. Those two agree. vLLM's request-level `request_time_per_output_token_seconds` and `request_decode_time_seconds` update only when a request finishes. At ~350 ms/token a 512-token request cannot finish inside the 90-second window, so those histograms stay empty. They fill once the step is short enough that 512 tokens fit in the window.

Across 144 finished runs, server inter-token latency averages **9.0–1973.8 ms**. Relative spread versus the fastest finished run is 21876.4%. Per-token time is no longer a single band.

## Decode latency by run

Means are `histogram_sum / histogram_count` over samples that arrived between `measurement_start` and `measurement_window_end`. The Prometheus buckets are 100 ms wide in this region, so a reported p50 near 350 ms only means the median bucket is 300–400 ms. The mean is the precise number. Client TPOT is the median of per-request mean token gaps, including requests that the 90-second window truncates.

| Model | Sweep | Cores | Clients | Gen | Status | Server ITL mean | ITL bucket | Client TPOT median | Client TTFT median | Tokens/s | Running | Waiting |
|---|---|---:|---:|---:|---|---:|---|---:|---:|---:|---:|---:|
| `Qwen/Qwen2.5-0.5B-Instruct` | baseline | 96 | 8 | 512 | done | 364.9 ms | 99.9% in 300–400 ms | 364.8 ms | 930.7 ms | 21.79 | 7.9 | 0.0 |
| `Qwen/Qwen2.5-0.5B-Instruct` | concurrency | 96 | 1 | 512 | done | 378.4 ms | 100.0% in 300–400 ms | 378.2 ms | 388.3 ms | 2.63 | 1.0 | 0.0 |
| `Qwen/Qwen2.5-0.5B-Instruct` | concurrency | 96 | 2 | 512 | done | 355.8 ms | 100.0% in 300–400 ms | 355.8 ms | 576.1 ms | 5.59 | 2.0 | 0.0 |
| `Qwen/Qwen2.5-0.5B-Instruct` | concurrency | 96 | 4 | 512 | done | 346.8 ms | 99.9% in 300–400 ms | 346.8 ms | 825.9 ms | 11.48 | 4.0 | 0.0 |
| `Qwen/Qwen2.5-0.5B-Instruct` | concurrency | 96 | 16 | 512 | done | 367.1 ms | 100.0% in 300–400 ms | 367.0 ms | 1178.3 ms | 43.03 | 15.7 | 0.0 |
| `Qwen/Qwen2.5-0.5B-Instruct` | concurrency | 96 | 32 | 512 | done | 381.9 ms | 100.0% in 300–400 ms | 380.9 ms | 1537.0 ms | 82.50 | 31.3 | 0.0 |
| `Qwen/Qwen2.5-0.5B-Instruct` | concurrency | 96 | 64 | 512 | done | 436.4 ms | 99.5% in 400–500 ms | 435.6 ms | 2352.7 ms | 143.70 | 62.0 | 0.0 |
| `Qwen/Qwen2.5-0.5B-Instruct` | concurrency | 96 | 128 | 512 | done | 511.3 ms | 87.5% in 500–750 ms | 511.4 ms | 3735.2 ms | 240.37 | 122.3 | 0.0 |
| `Qwen/Qwen2.5-0.5B-Instruct` | cores | 24 | 8 | 512 | done | 118.3 ms | 99.8% in 100–150 ms | 117.6 ms | 357.4 ms | 67.27 | 7.8 | 0.0 |
| `Qwen/Qwen2.5-0.5B-Instruct` | cores | 48 | 8 | 512 | done | 147.9 ms | 83.3% in 100–150 ms | 147.1 ms | 520.5 ms | 53.61 | 7.8 | 0.0 |
| `Qwen/Qwen2.5-0.5B-Instruct` | cores | 72 | 8 | 512 | done | 202.6 ms | 60.6% in 200–300 ms | 202.6 ms | 667.5 ms | 39.21 | 7.9 | 0.0 |
| `Qwen/Qwen2.5-0.5B-Instruct` | output_tokens | 96 | 8 | 128 | done | 352.1 ms | 99.9% in 300–400 ms | 352.6 ms | 908.2 ms | 22.41 | 7.8 | 0.0 |
| `Qwen/Qwen2.5-0.5B-Instruct` | output_tokens | 96 | 8 | 2048 | done | 357.2 ms | 99.9% in 300–400 ms | 357.3 ms | 922.7 ms | 22.23 | 7.9 | 0.0 |
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
| `Qwen/Qwen3-1.7B` | baseline | 96 | 8 | 512 | done | 553.2 ms | 99.9% in 500–750 ms | 553.1 ms | 1924.7 ms | 14.23 | 7.8 | 0.0 |
| `Qwen/Qwen3-1.7B` | concurrency | 96 | 1 | 512 | done | 561.9 ms | 100.0% in 500–750 ms | 561.6 ms | 663.5 ms | 1.77 | 1.0 | 0.0 |
| `Qwen/Qwen3-1.7B` | concurrency | 96 | 2 | 512 | done | 547.2 ms | 100.0% in 500–750 ms | 547.2 ms | 979.8 ms | 3.63 | 2.0 | 0.0 |
| `Qwen/Qwen3-1.7B` | concurrency | 96 | 4 | 512 | done | 542.2 ms | 99.8% in 500–750 ms | 541.6 ms | 1507.1 ms | 7.30 | 3.9 | 0.0 |
| `Qwen/Qwen3-1.7B` | concurrency | 96 | 16 | 512 | done | 611.6 ms | 99.9% in 500–750 ms | 610.6 ms | 2732.0 ms | 25.63 | 15.5 | 0.0 |
| `Qwen/Qwen3-1.7B` | concurrency | 96 | 32 | 512 | done | 692.9 ms | 99.8% in 500–750 ms | 690.7 ms | 4116.0 ms | 44.52 | 30.4 | 0.0 |
| `Qwen/Qwen3-1.7B` | concurrency | 96 | 64 | 512 | done | 826.7 ms | 100.0% in 750–1000 ms | 829.3 ms | 6772.3 ms | 71.83 | 59.1 | 0.0 |
| `Qwen/Qwen3-1.7B` | concurrency | 96 | 128 | 512 | done | 1117.5 ms | 100.0% in 1000–2500 ms | 1119.8 ms | 15204.0 ms | 95.30 | 106.6 | 0.0 |
| `Qwen/Qwen3-1.7B` | cores | 24 | 8 | 512 | done | 334.7 ms | 100.0% in 300–400 ms | 335.2 ms | 1268.7 ms | 23.66 | 7.8 | 0.0 |
| `Qwen/Qwen3-1.7B` | cores | 48 | 8 | 512 | done | 378.7 ms | 99.6% in 300–400 ms | 379.5 ms | 1094.8 ms | 20.89 | 7.8 | 0.0 |
| `Qwen/Qwen3-1.7B` | cores | 72 | 8 | 512 | done | 418.3 ms | 100.0% in 400–500 ms | 418.9 ms | 1215.0 ms | 18.93 | 7.8 | 0.0 |
| `Qwen/Qwen3-1.7B` | output_tokens | 96 | 8 | 128 | done | 552.3 ms | 99.8% in 500–750 ms | 551.3 ms | 1887.4 ms | 14.06 | 7.7 | 0.0 |
| `Qwen/Qwen3-1.7B` | output_tokens | 96 | 8 | 2048 | done | 552.5 ms | 99.9% in 500–750 ms | 552.5 ms | 1909.1 ms | 14.23 | 7.8 | 0.0 |
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
| `Qwen/Qwen3-4B` | baseline | 96 | 8 | 512 | done | 967.0 ms | 99.7% in 750–1000 ms | 964.1 ms | 3556.7 ms | 8.02 | 7.7 | 0.0 |
| `Qwen/Qwen3-4B` | concurrency | 96 | 1 | 512 | done | 978.6 ms | 100.0% in 750–1000 ms | 978.4 ms | 1096.8 ms | 1.01 | 1.0 | 0.0 |
| `Qwen/Qwen3-4B` | concurrency | 96 | 2 | 512 | done | 946.3 ms | 100.0% in 750–1000 ms | 946.3 ms | 1396.9 ms | 2.09 | 2.0 | 0.0 |
| `Qwen/Qwen3-4B` | concurrency | 96 | 4 | 512 | done | 950.0 ms | 99.7% in 750–1000 ms | 948.3 ms | 2696.0 ms | 4.14 | 3.9 | 0.0 |
| `Qwen/Qwen3-4B` | concurrency | 96 | 16 | 512 | done | 1013.4 ms | 99.9% in 1000–2500 ms | 1011.1 ms | 5725.1 ms | 14.94 | 15.0 | 0.0 |
| `Qwen/Qwen3-4B` | concurrency | 96 | 32 | 512 | done | 1140.1 ms | 100.0% in 1000–2500 ms | 1138.0 ms | 9191.6 ms | 25.61 | 28.8 | 0.0 |
| `Qwen/Qwen3-4B` | concurrency | 96 | 64 | 512 | done | 1463.6 ms | 100.0% in 1000–2500 ms | 1460.2 ms | 15703.4 ms | 36.28 | 53.4 | 0.0 |
| `Qwen/Qwen3-4B` | concurrency | 96 | 128 | 512 | done | 1973.8 ms | 99.8% in 1000–2500 ms | 1927.5 ms | 31387.2 ms | 44.17 | 87.4 | 0.0 |
| `Qwen/Qwen3-4B` | cores | 24 | 8 | 512 | done | 721.1 ms | 99.9% in 500–750 ms | 720.0 ms | 3107.1 ms | 10.77 | 7.7 | 0.0 |
| `Qwen/Qwen3-4B` | cores | 48 | 8 | 512 | done | 772.5 ms | 99.9% in 750–1000 ms | 771.1 ms | 3343.2 ms | 10.06 | 7.7 | 0.0 |
| `Qwen/Qwen3-4B` | cores | 72 | 8 | 512 | done | 856.1 ms | 99.9% in 750–1000 ms | 854.8 ms | 3441.3 ms | 9.08 | 7.7 | 0.0 |
| `Qwen/Qwen3-4B` | output_tokens | 96 | 8 | 128 | done | 970.7 ms | 99.9% in 750–1000 ms | 969.3 ms | 3745.4 ms | 8.01 | 7.7 | 0.0 |
| `Qwen/Qwen3-4B` | output_tokens | 96 | 8 | 2048 | done | 967.8 ms | 99.9% in 750–1000 ms | 965.7 ms | 3751.2 ms | 8.01 | 7.7 | 0.0 |
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
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | baseline | 96 | 8 | 512 | done | 311.7 ms | 99.0% in 300–400 ms | 311.6 ms | 704.4 ms | 25.51 | 7.9 | 0.0 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | concurrency | 96 | 1 | 512 | done | 254.4 ms | 100.0% in 200–300 ms | 254.4 ms | 335.3 ms | 3.92 | 1.0 | 0.0 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | concurrency | 96 | 2 | 512 | done | 312.5 ms | 87.7% in 300–400 ms | 313.1 ms | 516.2 ms | 6.37 | 2.0 | 0.0 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | concurrency | 96 | 4 | 512 | done | 322.5 ms | 99.9% in 300–400 ms | 322.1 ms | 795.3 ms | 12.32 | 4.0 | 0.0 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | concurrency | 96 | 16 | 512 | done | 310.7 ms | 100.0% in 300–400 ms | 310.8 ms | 1335.6 ms | 50.86 | 15.7 | 0.0 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | concurrency | 96 | 32 | 512 | done | 342.5 ms | 100.0% in 300–400 ms | 343.3 ms | 2025.8 ms | 91.39 | 30.9 | 0.0 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | concurrency | 96 | 64 | 512 | done | 436.7 ms | 100.0% in 400–500 ms | 438.3 ms | 3392.6 ms | 141.52 | 61.2 | 0.0 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | concurrency | 96 | 128 | 512 | done | 567.5 ms | 100.0% in 500–750 ms | 569.7 ms | 6237.4 ms | 210.50 | 119.4 | 0.0 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | cores | 24 | 8 | 512 | done | 150.9 ms | 55.0% in 150–200 ms | 150.0 ms | 604.1 ms | 52.54 | 7.8 | 0.0 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | cores | 48 | 8 | 512 | done | 178.6 ms | 100.0% in 150–200 ms | 178.6 ms | 714.6 ms | 44.54 | 7.9 | 0.0 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | cores | 72 | 8 | 512 | done | 216.3 ms | 100.0% in 200–300 ms | 216.6 ms | 845.3 ms | 36.72 | 7.9 | 0.0 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | output_tokens | 96 | 8 | 128 | done | 313.4 ms | 98.8% in 300–400 ms | 312.9 ms | 1005.1 ms | 24.90 | 7.7 | 0.0 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | output_tokens | 96 | 8 | 2048 | done | 310.1 ms | 98.6% in 300–400 ms | 309.7 ms | 1019.0 ms | 25.61 | 7.8 | 0.0 |
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
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | baseline | 96 | 8 | 512 | done | 614.4 ms | 99.9% in 500–750 ms | 614.0 ms | 2271.5 ms | 12.72 | 7.8 | 0.0 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | concurrency | 96 | 1 | 512 | done | 519.8 ms | 100.0% in 500–750 ms | 519.7 ms | 670.1 ms | 1.91 | 1.0 | 0.0 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | concurrency | 96 | 2 | 512 | done | 588.0 ms | 99.7% in 500–750 ms | 588.2 ms | 1055.5 ms | 3.37 | 2.0 | 0.0 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | concurrency | 96 | 4 | 512 | done | 641.7 ms | 99.8% in 500–750 ms | 641.2 ms | 1698.9 ms | 6.14 | 3.9 | 0.0 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | concurrency | 96 | 16 | 512 | done | 628.6 ms | 100.0% in 500–750 ms | 628.7 ms | 3121.3 ms | 24.72 | 15.3 | 0.0 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | concurrency | 96 | 32 | 512 | done | 706.6 ms | 100.0% in 500–750 ms | 707.1 ms | 4775.1 ms | 43.03 | 30.2 | 0.0 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | concurrency | 96 | 64 | 512 | done | 963.2 ms | 100.0% in 750–1000 ms | 963.8 ms | 8174.4 ms | 61.17 | 58.3 | 0.0 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | concurrency | 96 | 128 | 512 | done | 1252.3 ms | 100.0% in 1000–2500 ms | 1252.2 ms | 16689.5 ms | 83.92 | 106.3 | 0.0 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | cores | 24 | 8 | 512 | done | 354.9 ms | 99.9% in 300–400 ms | 355.5 ms | 1512.0 ms | 22.23 | 7.8 | 0.0 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | cores | 48 | 8 | 512 | done | 405.6 ms | 80.0% in 400–500 ms | 406.0 ms | 1677.1 ms | 19.39 | 7.8 | 0.0 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | cores | 72 | 8 | 512 | done | 467.0 ms | 98.9% in 400–500 ms | 467.0 ms | 1930.0 ms | 16.81 | 7.8 | 0.0 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | output_tokens | 96 | 8 | 128 | done | 606.6 ms | 99.8% in 500–750 ms | 606.0 ms | 2242.7 ms | 12.72 | 7.6 | 0.0 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | output_tokens | 96 | 8 | 2048 | done | 604.7 ms | 99.9% in 500–750 ms | 604.3 ms | 2236.6 ms | 12.99 | 7.8 | 0.0 |
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
| `ibm-granite/granite-3.2-2b-instruct` | baseline | 96 | 8 | 512 | done | 785.7 ms | 99.9% in 750–1000 ms | 784.8 ms | 2962.4 ms | 9.88 | 7.8 | 0.0 |
| `ibm-granite/granite-3.2-2b-instruct` | concurrency | 96 | 1 | 512 | done | 822.2 ms | 100.0% in 750–1000 ms | 821.8 ms | 904.9 ms | 1.21 | 1.0 | 0.0 |
| `ibm-granite/granite-3.2-2b-instruct` | concurrency | 96 | 2 | 512 | done | 762.6 ms | 100.0% in 750–1000 ms | 762.5 ms | 1387.0 ms | 2.59 | 2.0 | 0.0 |
| `ibm-granite/granite-3.2-2b-instruct` | concurrency | 96 | 4 | 512 | done | 767.4 ms | 99.6% in 750–1000 ms | 767.4 ms | 1641.9 ms | 5.13 | 3.9 | 0.0 |
| `ibm-granite/granite-3.2-2b-instruct` | concurrency | 96 | 16 | 512 | done | 827.9 ms | 99.9% in 750–1000 ms | 826.9 ms | 4099.7 ms | 18.50 | 15.2 | 0.0 |
| `ibm-granite/granite-3.2-2b-instruct` | concurrency | 96 | 32 | 512 | done | 927.8 ms | 100.0% in 750–1000 ms | 927.0 ms | 6213.7 ms | 32.37 | 29.6 | 0.0 |
| `ibm-granite/granite-3.2-2b-instruct` | concurrency | 96 | 64 | 512 | done | 1119.1 ms | 100.0% in 1000–2500 ms | 1118.3 ms | 11077.7 ms | 50.50 | 56.3 | 0.0 |
| `ibm-granite/granite-3.2-2b-instruct` | concurrency | 96 | 128 | 512 | done | 1473.1 ms | 99.8% in 1000–2500 ms | 1441.4 ms | 21681.1 ms | 68.40 | 99.9 | 0.0 |
| `ibm-granite/granite-3.2-2b-instruct` | cores | 24 | 8 | 512 | done | 479.2 ms | 100.0% in 400–500 ms | 479.8 ms | 1542.6 ms | 16.44 | 7.8 | 0.0 |
| `ibm-granite/granite-3.2-2b-instruct` | cores | 48 | 8 | 512 | done | 551.1 ms | 99.9% in 500–750 ms | 550.8 ms | 2086.1 ms | 14.23 | 7.8 | 0.0 |
| `ibm-granite/granite-3.2-2b-instruct` | cores | 72 | 8 | 512 | done | 622.1 ms | 99.9% in 500–750 ms | 621.5 ms | 2348.5 ms | 12.63 | 7.8 | 0.0 |
| `ibm-granite/granite-3.2-2b-instruct` | output_tokens | 96 | 8 | 128 | done | 785.7 ms | 99.9% in 750–1000 ms | 784.8 ms | 2940.4 ms | 9.88 | 7.8 | 0.0 |
| `ibm-granite/granite-3.2-2b-instruct` | output_tokens | 96 | 8 | 2048 | done | 784.7 ms | 99.7% in 750–1000 ms | 782.4 ms | 2793.8 ms | 9.99 | 7.8 | 0.0 |
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
| `node0_cores096_clients001_gen0512` | 378.4 ms | 235 | 350.0 ms | 390.0 ms | 378.2 ms | 378.2 ms | 378.2 ms | 0 |
| `node0_cores096_clients001_gen0512` | 9.9 ms | 9028 | 6.5 ms | 18.4 ms | 9.7 ms | 9.9 ms | 10.0 ms | 18 |
| `node0_cores096_clients002_gen0512` | 355.8 ms | 501 | 350.0 ms | 390.0 ms | 355.8 ms | 355.8 ms | 355.9 ms | 0 |
| `node0_cores096_clients002_gen0512` | 17.2 ms | 10357 | 17.5 ms | 23.5 ms | 17.1 ms | 17.2 ms | 17.3 ms | 22 |
| `node0_cores096_clients004_gen0512` | 346.8 ms | 1025 | 350.0 ms | 390.1 ms | 346.8 ms | 346.8 ms | 347.2 ms | 0 |
| `node0_cores096_clients004_gen0512` | 17.9 ms | 19881 | 17.5 ms | 23.6 ms | 17.8 ms | 17.9 ms | 18.0 ms | 40 |
| `node0_cores024_clients008_gen0512` | 118.3 ms | 6022 | 125.0 ms | 145.1 ms | 115.6 ms | 117.6 ms | 119.6 ms | 8 |
| `node0_cores024_clients008_gen0512` | 11.6 ms | 61489 | 17.5 ms | 23.5 ms | 11.5 ms | 11.5 ms | 11.7 ms | 128 |
| `node0_cores048_clients008_gen0512` | 147.9 ms | 4793 | 130.0 ms | 170.1 ms | 144.4 ms | 147.1 ms | 148.4 ms | 8 |
| `node0_cores048_clients008_gen0512` | 23.0 ms | 30954 | 17.8 ms | 24.1 ms | 22.8 ms | 23.1 ms | 23.2 ms | 64 |
| `node0_cores072_clients008_gen0512` | 202.6 ms | 3513 | 217.5 ms | 283.5 ms | 202.6 ms | 202.6 ms | 202.6 ms | 0 |
| `node0_cores072_clients008_gen0512` | 32.9 ms | 21715 | 37.5 ms | 47.5 ms | 32.7 ms | 32.9 ms | 33.1 ms | 40 |
| `node0_cores096_clients008_gen0128` | 352.1 ms | 1993 | 350.1 ms | 390.1 ms | 350.7 ms | 352.6 ms | 353.1 ms | 16 |
| `node0_cores096_clients008_gen0512` | 364.9 ms | 1945 | 350.0 ms | 390.0 ms | 364.8 ms | 364.8 ms | 364.8 ms | 0 |
| `node0_cores096_clients008_gen0512` | 20.0 ms | 35700 | 17.8 ms | 24.0 ms | 18.4 ms | 18.7 ms | 25.0 ms | 72 |
| `node0_cores096_clients008_gen2048` | 357.2 ms | 1985 | 350.0 ms | 390.0 ms | 357.3 ms | 357.3 ms | 357.3 ms | 0 |
| `node0_cores096_clients016_gen0512` | 367.1 ms | 3857 | 350.0 ms | 390.0 ms | 367.0 ms | 367.0 ms | 367.0 ms | 0 |
| `node0_cores096_clients016_gen0512` | 20.0 ms | 71313 | 17.6 ms | 23.8 ms | 19.7 ms | 19.9 ms | 20.4 ms | 144 |
| `node0_cores096_clients032_gen0512` | 381.9 ms | 7361 | 350.0 ms | 390.0 ms | 380.9 ms | 380.9 ms | 380.9 ms | 0 |
| `node0_cores096_clients032_gen0512` | 21.7 ms | 131169 | 17.7 ms | 23.9 ms | 21.5 ms | 21.6 ms | 21.8 ms | 256 |
| `node0_cores096_clients064_gen0512` | 436.4 ms | 12805 | 449.8 ms | 490.0 ms | 435.6 ms | 435.6 ms | 435.6 ms | 0 |
| `node0_cores096_clients064_gen0512` | 29.2 ms | 194945 | 37.5 ms | 47.5 ms | 29.0 ms | 29.2 ms | 29.3 ms | 384 |
| `node0_cores096_clients128_gen0512` | 511.3 ms | 21505 | 607.1 ms | 721.4 ms | 511.4 ms | 511.4 ms | 511.4 ms | 0 |
| `node0_cores096_clients128_gen0512` | 33.8 ms | 334465 | 37.5 ms | 47.5 ms | 33.4 ms | 33.9 ms | 34.0 ms | 640 |
| `node0_cores096_clients001_gen0512` | 561.9 ms | 158 | 625.0 ms | 725.0 ms | 561.6 ms | 561.6 ms | 561.6 ms | 0 |
| `node0_cores096_clients001_gen0512` | 17.2 ms | 5192 | 17.5 ms | 23.5 ms | 17.1 ms | 17.2 ms | 17.3 ms | 11 |
| `node0_cores096_clients002_gen0512` | 547.2 ms | 325 | 625.0 ms | 725.0 ms | 546.9 ms | 547.2 ms | 547.5 ms | 0 |
| `node0_cores096_clients002_gen0512` | 20.6 ms | 8651 | 17.7 ms | 23.8 ms | 20.5 ms | 20.6 ms | 20.8 ms | 18 |
| `node0_cores096_clients004_gen0512` | 542.2 ms | 653 | 625.2 ms | 725.3 ms | 541.6 ms | 541.6 ms | 543.3 ms | 0 |
| `node0_cores096_clients004_gen0512` | 21.2 ms | 16801 | 17.7 ms | 23.9 ms | 21.1 ms | 21.2 ms | 21.4 ms | 32 |
| `node0_cores024_clients008_gen0512` | 334.7 ms | 2113 | 350.0 ms | 390.0 ms | 335.2 ms | 335.2 ms | 335.2 ms | 0 |
| `node0_cores024_clients008_gen0512` | 24.4 ms | 29201 | 18.7 ms | 32.4 ms | 24.1 ms | 24.4 ms | 24.4 ms | 56 |
| `node0_cores048_clients008_gen0512` | 378.7 ms | 1872 | 350.2 ms | 390.4 ms | 379.5 ms | 379.5 ms | 379.5 ms | 0 |
| `node0_cores048_clients008_gen0512` | 19.3 ms | 36792 | 17.5 ms | 23.5 ms | 19.3 ms | 19.3 ms | 19.4 ms | 72 |
| `node0_cores072_clients008_gen0512` | 418.3 ms | 1688 | 450.0 ms | 490.0 ms | 418.9 ms | 418.9 ms | 418.9 ms | 0 |
| `node0_cores072_clients008_gen0512` | 18.0 ms | 39530 | 17.5 ms | 23.5 ms | 17.9 ms | 18.0 ms | 18.1 ms | 80 |
| `node0_cores096_clients008_gen0128` | 552.3 ms | 1249 | 625.2 ms | 725.4 ms | 550.6 ms | 551.3 ms | 556.7 ms | 8 |
| `node0_cores096_clients008_gen0512` | 553.2 ms | 1273 | 625.1 ms | 725.2 ms | 553.1 ms | 553.1 ms | 553.1 ms | 0 |
| `node0_cores096_clients008_gen0512` | 22.5 ms | 31601 | 17.9 ms | 24.2 ms | 22.4 ms | 22.5 ms | 22.8 ms | 64 |
| `node0_cores096_clients008_gen2048` | 552.5 ms | 1273 | 625.1 ms | 725.2 ms | 552.5 ms | 552.5 ms | 552.5 ms | 0 |
| `node0_cores096_clients016_gen0512` | 611.6 ms | 2291 | 625.2 ms | 725.3 ms | 610.6 ms | 610.6 ms | 618.5 ms | 0 |
| `node0_cores096_clients016_gen0512` | 21.9 ms | 64769 | 17.8 ms | 24.1 ms | 21.7 ms | 22.0 ms | 22.2 ms | 128 |
| `node0_cores096_clients032_gen0512` | 692.9 ms | 3975 | 625.2 ms | 725.4 ms | 690.7 ms | 690.7 ms | 706.7 ms | 0 |
| `node0_cores096_clients032_gen0512` | 28.6 ms | 99073 | 36.6 ms | 47.4 ms | 27.5 ms | 28.5 ms | 28.8 ms | 192 |
| `node0_cores096_clients064_gen0512` | 826.7 ms | 6401 | 875.0 ms | 975.0 ms | 829.3 ms | 829.3 ms | 829.3 ms | 0 |
| `node0_cores096_clients064_gen0512` | 37.6 ms | 150148 | 37.7 ms | 47.9 ms | 36.8 ms | 37.2 ms | 43.6 ms | 256 |
| `node0_cores096_clients128_gen0512` | 1117.5 ms | 8449 | 1750.1 ms | 2350.2 ms | 1119.8 ms | 1119.8 ms | 1119.8 ms | 0 |
| `node0_cores096_clients128_gen0512` | 57.4 ms | 196481 | 59.4 ms | 72.1 ms | 49.3 ms | 57.4 ms | 57.5 ms | 384 |
| `node0_cores096_clients001_gen0512` | 978.6 ms | 90 | 875.0 ms | 975.0 ms | 978.4 ms | 978.4 ms | 978.4 ms | 0 |
| `node0_cores096_clients001_gen0512` | 33.1 ms | 2703 | 37.5 ms | 47.5 ms | 32.9 ms | 33.1 ms | 33.2 ms | 5 |
| `node0_cores096_clients002_gen0512` | 946.3 ms | 186 | 875.0 ms | 975.0 ms | 946.3 ms | 946.3 ms | 946.3 ms | 0 |
| `node0_cores096_clients002_gen0512` | 33.1 ms | 5397 | 37.5 ms | 47.5 ms | 33.0 ms | 33.1 ms | 33.1 ms | 10 |
| `node0_cores096_clients004_gen0512` | 950.0 ms | 365 | 875.3 ms | 975.6 ms | 948.3 ms | 948.3 ms | 954.8 ms | 0 |
| `node0_cores096_clients004_gen0512` | 34.0 ms | 10481 | 37.5 ms | 47.5 ms | 33.7 ms | 33.9 ms | 34.2 ms | 20 |
| `node0_cores024_clients008_gen0512` | 721.1 ms | 961 | 625.1 ms | 725.2 ms | 720.0 ms | 720.0 ms | 720.0 ms | 0 |
| `node0_cores024_clients008_gen0512` | 48.6 ms | 14642 | 38.3 ms | 49.0 ms | 48.5 ms | 48.6 ms | 48.9 ms | 24 |
| `node0_cores048_clients008_gen0512` | 772.5 ms | 889 | 875.1 ms | 975.3 ms | 771.1 ms | 771.1 ms | 771.1 ms | 0 |
| `node0_cores048_clients008_gen0512` | 36.0 ms | 19746 | 37.5 ms | 47.5 ms | 35.9 ms | 36.1 ms | 36.2 ms | 40 |
| `node0_cores072_clients008_gen0512` | 856.1 ms | 809 | 875.2 ms | 975.3 ms | 854.8 ms | 854.8 ms | 854.8 ms | 0 |
| `node0_cores072_clients008_gen0512` | 38.4 ms | 18530 | 37.5 ms | 47.6 ms | 38.3 ms | 38.4 ms | 38.5 ms | 32 |
| `node0_cores096_clients008_gen0128` | 970.7 ms | 705 | 875.2 ms | 975.3 ms | 969.3 ms | 969.3 ms | 969.3 ms | 0 |
| `node0_cores096_clients008_gen0512` | 967.0 ms | 714 | 875.4 ms | 975.6 ms | 964.1 ms | 964.1 ms | 976.2 ms | 0 |
| `node0_cores096_clients008_gen0512` | 35.6 ms | 19985 | 37.5 ms | 47.5 ms | 35.5 ms | 35.6 ms | 35.8 ms | 40 |
| `node0_cores096_clients008_gen2048` | 967.8 ms | 713 | 875.2 ms | 975.3 ms | 965.7 ms | 965.7 ms | 965.7 ms | 0 |
| `node0_cores096_clients016_gen0512` | 1013.4 ms | 1329 | 1750.6 ms | 2351.0 ms | 1011.1 ms | 1011.1 ms | 1011.1 ms | 0 |
| `node0_cores096_clients016_gen0512` | 38.0 ms | 37361 | 37.5 ms | 47.5 ms | 37.9 ms | 38.1 ms | 38.3 ms | 64 |
| `node0_cores096_clients032_gen0512` | 1140.1 ms | 2241 | 1750.3 ms | 2350.6 ms | 1138.0 ms | 1138.0 ms | 1138.0 ms | 0 |
| `node0_cores096_clients032_gen0512` | 43.3 ms | 65313 | 37.8 ms | 48.1 ms | 40.7 ms | 43.1 ms | 43.6 ms | 128 |
| `node0_cores096_clients064_gen0512` | 1463.6 ms | 3201 | 1750.2 ms | 2350.4 ms | 1460.2 ms | 1460.2 ms | 1460.2 ms | 0 |
| `node0_cores096_clients064_gen0512` | 66.8 ms | 84484 | 63.1 ms | 73.6 ms | 65.6 ms | 67.1 ms | 68.2 ms | 128 |
| `node0_cores096_clients128_gen0512` | 1973.8 ms | 3847 | 1751.4 ms | 2352.5 ms | 1927.4 ms | 1927.5 ms | 1927.5 ms | 0 |
| `node0_cores096_clients128_gen0512` | 92.6 ms | 121603 | 91.0 ms | 127.4 ms | 93.3 ms | 93.6 ms | 93.6 ms | 256 |
| `node0_cores096_clients001_gen0512` | 254.4 ms | 349 | 250.0 ms | 290.0 ms | 254.4 ms | 254.4 ms | 254.4 ms | 0 |
| `node0_cores096_clients001_gen0512` | 9.0 ms | 9950 | 5.5 ms | 9.9 ms | 8.8 ms | 9.0 ms | 9.1 ms | 20 |
| `node0_cores096_clients002_gen0512` | 312.5 ms | 571 | 343.0 ms | 388.6 ms | 313.0 ms | 313.1 ms | 313.2 ms | 0 |
| `node0_cores096_clients002_gen0512` | 9.7 ms | 18455 | 6.3 ms | 17.6 ms | 9.6 ms | 9.7 ms | 9.7 ms | 38 |
| `node0_cores096_clients004_gen0512` | 322.5 ms | 1105 | 350.0 ms | 390.1 ms | 322.1 ms | 322.1 ms | 322.5 ms | 0 |
| `node0_cores096_clients004_gen0512` | 10.2 ms | 34997 | 7.3 ms | 20.3 ms | 10.0 ms | 10.2 ms | 10.3 ms | 72 |
| `node0_cores024_clients008_gen0512` | 150.9 ms | 4665 | 154.6 ms | 191.0 ms | 146.3 ms | 150.0 ms | 151.5 ms | 8 |
| `node0_cores024_clients008_gen0512` | 12.7 ms | 56169 | 17.5 ms | 23.5 ms | 12.6 ms | 12.7 ms | 12.7 ms | 112 |
| `node0_cores048_clients008_gen0512` | 178.6 ms | 4001 | 175.0 ms | 195.0 ms | 178.6 ms | 178.6 ms | 178.6 ms | 8 |
| `node0_cores048_clients008_gen0512` | 10.5 ms | 67777 | 17.4 ms | 23.5 ms | 10.4 ms | 10.5 ms | 10.6 ms | 136 |
| `node0_cores072_clients008_gen0512` | 216.3 ms | 3297 | 250.0 ms | 290.0 ms | 216.6 ms | 216.6 ms | 216.6 ms | 0 |
| `node0_cores072_clients008_gen0512` | 10.7 ms | 66754 | 17.5 ms | 23.5 ms | 10.6 ms | 10.6 ms | 10.8 ms | 136 |
| `node0_cores096_clients008_gen0128` | 313.4 ms | 2217 | 349.5 ms | 390.0 ms | 312.6 ms | 312.9 ms | 315.4 ms | 16 |
| `node0_cores096_clients008_gen0512` | 311.7 ms | 2288 | 349.5 ms | 389.9 ms | 311.6 ms | 311.6 ms | 311.6 ms | 0 |
| `node0_cores096_clients008_gen0512` | 10.6 ms | 67211 | 15.0 ms | 23.0 ms | 10.4 ms | 10.5 ms | 10.7 ms | 136 |
| `node0_cores096_clients008_gen2048` | 310.1 ms | 2289 | 349.3 ms | 389.9 ms | 309.7 ms | 309.7 ms | 309.7 ms | 0 |
| `node0_cores096_clients016_gen0512` | 310.7 ms | 4561 | 350.0 ms | 390.0 ms | 310.8 ms | 310.8 ms | 310.8 ms | 0 |
| `node0_cores096_clients016_gen0512` | 11.8 ms | 120241 | 17.5 ms | 23.5 ms | 11.7 ms | 11.8 ms | 12.0 ms | 240 |
| `node0_cores096_clients032_gen0512` | 342.5 ms | 8193 | 350.0 ms | 390.0 ms | 343.3 ms | 343.3 ms | 343.3 ms | 0 |
| `node0_cores096_clients032_gen0512` | 13.9 ms | 203009 | 17.5 ms | 23.5 ms | 13.9 ms | 14.0 ms | 14.0 ms | 416 |
| `node0_cores096_clients064_gen0512` | 436.7 ms | 12545 | 450.0 ms | 490.0 ms | 438.3 ms | 438.3 ms | 438.3 ms | 0 |
| `node0_cores096_clients064_gen0512` | 19.7 ms | 287745 | 17.6 ms | 23.8 ms | 19.5 ms | 19.7 ms | 20.5 ms | 576 |
| `node0_cores096_clients128_gen0512` | 567.5 ms | 18817 | 625.0 ms | 725.0 ms | 569.7 ms | 569.7 ms | 569.7 ms | 0 |
| `node0_cores096_clients128_gen0512` | 28.8 ms | 392448 | 36.5 ms | 47.3 ms | 27.3 ms | 28.9 ms | 29.0 ms | 768 |
| `node0_cores096_clients001_gen0512` | 519.8 ms | 171 | 625.0 ms | 725.0 ms | 519.7 ms | 519.7 ms | 519.7 ms | 0 |
| `node0_cores096_clients001_gen0512` | 17.6 ms | 5074 | 17.5 ms | 23.6 ms | 17.5 ms | 17.6 ms | 17.8 ms | 10 |
| `node0_cores096_clients002_gen0512` | 588.0 ms | 301 | 625.4 ms | 725.8 ms | 587.6 ms | 588.2 ms | 588.9 ms | 0 |
| `node0_cores096_clients002_gen0512` | 18.4 ms | 9709 | 17.6 ms | 23.6 ms | 18.2 ms | 18.4 ms | 18.5 ms | 20 |
| `node0_cores096_clients004_gen0512` | 641.7 ms | 549 | 625.2 ms | 725.4 ms | 641.2 ms | 641.2 ms | 643.7 ms | 0 |
| `node0_cores096_clients004_gen0512` | 19.2 ms | 18513 | 17.6 ms | 23.7 ms | 19.0 ms | 19.2 ms | 19.5 ms | 36 |
| `node0_cores024_clients008_gen0512` | 354.9 ms | 1985 | 350.0 ms | 390.0 ms | 355.5 ms | 355.5 ms | 355.5 ms | 0 |
| `node0_cores024_clients008_gen0512` | 25.6 ms | 27762 | 32.8 ms | 46.6 ms | 25.5 ms | 25.6 ms | 25.8 ms | 56 |
| `node0_cores048_clients008_gen0512` | 405.6 ms | 1721 | 437.5 ms | 487.6 ms | 406.0 ms | 406.0 ms | 406.0 ms | 0 |
| `node0_cores048_clients008_gen0512` | 20.6 ms | 34547 | 17.6 ms | 23.6 ms | 20.5 ms | 20.6 ms | 20.7 ms | 72 |
| `node0_cores072_clients008_gen0512` | 467.0 ms | 1505 | 450.6 ms | 491.0 ms | 467.0 ms | 467.0 ms | 467.0 ms | 0 |
| `node0_cores072_clients008_gen0512` | 20.2 ms | 35107 | 17.5 ms | 23.5 ms | 20.2 ms | 20.2 ms | 20.4 ms | 72 |
| `node0_cores096_clients008_gen0128` | 606.6 ms | 1121 | 625.2 ms | 725.4 ms | 604.7 ms | 606.0 ms | 612.1 ms | 8 |
| `node0_cores096_clients008_gen0512` | 614.4 ms | 1129 | 625.1 ms | 725.2 ms | 614.0 ms | 614.0 ms | 614.0 ms | 0 |
| `node0_cores096_clients008_gen0512` | 20.1 ms | 35322 | 17.7 ms | 23.8 ms | 20.0 ms | 20.2 ms | 20.3 ms | 72 |
| `node0_cores096_clients008_gen2048` | 604.7 ms | 1153 | 625.1 ms | 725.2 ms | 604.3 ms | 604.3 ms | 604.3 ms | 0 |
| `node0_cores096_clients016_gen0512` | 628.6 ms | 2177 | 625.1 ms | 725.1 ms | 628.7 ms | 628.7 ms | 628.7 ms | 0 |
| `node0_cores096_clients016_gen0512` | 22.3 ms | 63634 | 17.9 ms | 24.3 ms | 22.0 ms | 22.3 ms | 22.6 ms | 128 |
| `node0_cores096_clients032_gen0512` | 706.6 ms | 3809 | 625.0 ms | 725.1 ms | 707.1 ms | 707.1 ms | 707.1 ms | 0 |
| `node0_cores096_clients032_gen0512` | 26.3 ms | 107809 | 31.4 ms | 46.3 ms | 26.2 ms | 26.3 ms | 26.7 ms | 224 |
| `node0_cores096_clients064_gen0512` | 963.2 ms | 5377 | 875.0 ms | 975.0 ms | 963.8 ms | 963.8 ms | 963.8 ms | 0 |
| `node0_cores096_clients064_gen0512` | 49.8 ms | 113857 | 47.7 ms | 69.5 ms | 49.0 ms | 50.1 ms | 50.4 ms | 192 |
| `node0_cores096_clients128_gen0512` | 1252.3 ms | 7425 | 1750.1 ms | 2350.2 ms | 1252.2 ms | 1252.2 ms | 1252.2 ms | 0 |
| `node0_cores096_clients128_gen0512` | 65.9 ms | 171523 | 63.9 ms | 74.9 ms | 65.4 ms | 66.7 ms | 67.0 ms | 256 |
| `node0_cores096_clients001_gen0512` | 822.2 ms | 107 | 875.0 ms | 975.0 ms | 821.8 ms | 821.8 ms | 821.8 ms | 0 |
| `node0_cores096_clients001_gen0512` | 24.0 ms | 3725 | 19.4 ms | 37.8 ms | 23.9 ms | 24.0 ms | 24.1 ms | 7 |
| `node0_cores096_clients002_gen0512` | 762.6 ms | 231 | 875.0 ms | 975.0 ms | 761.7 ms | 762.5 ms | 763.3 ms | 0 |
| `node0_cores096_clients002_gen0512` | 29.3 ms | 6091 | 37.5 ms | 47.5 ms | 29.2 ms | 29.3 ms | 29.5 ms | 12 |
| `node0_cores096_clients004_gen0512` | 767.4 ms | 458 | 875.5 ms | 976.0 ms | 766.0 ms | 767.4 ms | 768.7 ms | 0 |
| `node0_cores096_clients004_gen0512` | 29.3 ms | 12153 | 37.5 ms | 47.5 ms | 29.1 ms | 29.3 ms | 29.6 ms | 24 |
| `node0_cores024_clients008_gen0512` | 479.2 ms | 1464 | 450.0 ms | 490.0 ms | 479.8 ms | 479.8 ms | 479.8 ms | 0 |
| `node0_cores024_clients008_gen0512` | 34.1 ms | 20809 | 37.5 ms | 47.5 ms | 33.9 ms | 34.1 ms | 34.2 ms | 40 |
| `node0_cores048_clients008_gen0512` | 551.1 ms | 1273 | 625.1 ms | 725.2 ms | 550.8 ms | 550.8 ms | 550.8 ms | 0 |
| `node0_cores048_clients008_gen0512` | 26.9 ms | 26458 | 37.5 ms | 47.5 ms | 26.8 ms | 26.9 ms | 27.0 ms | 56 |
| `node0_cores072_clients008_gen0512` | 622.1 ms | 1121 | 625.1 ms | 725.2 ms | 621.5 ms | 621.5 ms | 621.5 ms | 0 |
| `node0_cores072_clients008_gen0512` | 25.5 ms | 27881 | 30.5 ms | 46.1 ms | 25.3 ms | 25.5 ms | 25.7 ms | 56 |
| `node0_cores096_clients008_gen0128` | 785.7 ms | 881 | 875.1 ms | 975.3 ms | 784.8 ms | 784.8 ms | 784.8 ms | 0 |
| `node0_cores096_clients008_gen0512` | 785.7 ms | 881 | 875.1 ms | 975.3 ms | 784.8 ms | 784.8 ms | 784.8 ms | 0 |
| `node0_cores096_clients008_gen0512` | 30.7 ms | 23163 | 37.5 ms | 47.5 ms | 30.6 ms | 30.8 ms | 31.0 ms | 48 |
| `node0_cores096_clients008_gen2048` | 784.7 ms | 891 | 875.4 ms | 975.8 ms | 782.4 ms | 782.4 ms | 788.7 ms | 0 |
| `node0_cores096_clients016_gen0512` | 827.9 ms | 1649 | 875.1 ms | 975.1 ms | 826.9 ms | 826.9 ms | 826.9 ms | 0 |
| `node0_cores096_clients016_gen0512` | 28.8 ms | 49217 | 37.5 ms | 47.5 ms | 28.5 ms | 28.7 ms | 29.2 ms | 96 |
| `node0_cores096_clients032_gen0512` | 927.8 ms | 2881 | 875.0 ms | 975.1 ms | 927.0 ms | 927.0 ms | 927.0 ms | 0 |
| `node0_cores096_clients032_gen0512` | 33.2 ms | 85122 | 37.5 ms | 47.5 ms | 32.4 ms | 33.3 ms | 33.7 ms | 160 |
| `node0_cores096_clients064_gen0512` | 1119.1 ms | 4481 | 1750.2 ms | 2350.3 ms | 1118.2 ms | 1118.3 ms | 1118.3 ms | 0 |
| `node0_cores096_clients064_gen0512` | 46.0 ms | 122502 | 38.7 ms | 49.7 ms | 46.0 ms | 46.3 ms | 46.4 ms | 256 |
| `node0_cores096_clients128_gen0512` | 1473.1 ms | 5900 | 1751.5 ms | 2352.8 ms | 1441.4 ms | 1441.4 ms | 1441.5 ms | 0 |
| `node0_cores096_clients128_gen0512` | 66.4 ms | 169473 | 63.2 ms | 73.8 ms | 65.8 ms | 66.9 ms | 67.3 ms | 256 |

## Trend

On `Qwen/Qwen2.5-0.5B-Instruct`, 96 cores, 512 generated tokens, one client produces one token every **378.4 ms** (2.63 tokens/s).

| Clients | ITL mean | ITL vs 1-client | Tokens/s | Tokens/s vs linear | TTFT median | Mean running | Mean waiting | Step batch (iteration tokens) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 378.4 ms | 1.00× | 2.63 | 100.00% | 388.3 ms | 1.0 | 0.0 | 1.14 |
| 1 | 9.9 ms | 0.03× | 100.90 | 3831.65% | 24.1 ms | 1.0 | 0.0 | 1.06 |
| 2 | 355.8 ms | 0.94× | 5.59 | 106.12% | 576.1 ms | 2.0 | 0.0 | 2.25 |
| 2 | 17.2 ms | 0.05× | 115.77 | 2198.10% | 41.0 ms | 2.0 | 0.0 | 2.13 |
| 4 | 346.8 ms | 0.92× | 11.48 | 108.97% | 825.9 ms | 4.0 | 0.0 | 4.48 |
| 4 | 17.9 ms | 0.05× | 222.10 | 2108.54% | 45.2 ms | 3.9 | 0.0 | 4.25 |
| 8 | 364.9 ms | 0.96× | 21.79 | 103.43% | 930.7 ms | 7.9 | 0.0 | 9.02 |
| 8 | 20.0 ms | 0.05× | 399.07 | 1894.30% | 54.6 ms | 7.9 | 0.0 | 8.50 |
| 16 | 367.1 ms | 0.97× | 43.03 | 102.14% | 1178.3 ms | 15.7 | 0.0 | 18.05 |
| 16 | 20.0 ms | 0.05× | 796.81 | 1891.17% | 65.4 ms | 15.8 | 0.0 | 17.00 |
| 32 | 381.9 ms | 1.01× | 82.50 | 97.90% | 1537.0 ms | 31.3 | 0.0 | 36.28 |
| 32 | 21.7 ms | 0.06× | 1465.97 | 1739.68% | 87.7 ms | 31.6 | 0.0 | 34.17 |
| 64 | 436.4 ms | 1.15× | 143.70 | 85.27% | 2352.7 ms | 62.0 | 0.0 | 73.85 |
| 64 | 29.2 ms | 0.08× | 2176.01 | 1291.15% | 124.6 ms | 61.2 | 0.0 | 67.89 |
| 128 | 511.3 ms | 1.35× | 240.37 | 71.31% | 3735.2 ms | 122.3 | 0.0 | 151.35 |
| 128 | 33.8 ms | 0.09× | 3734.77 | 1108.02% | 189.1 ms | 123.7 | 0.0 | 137.07 |

The scheduler keeps every client in the running set and the waiting set at zero, so the extra delay is not a queue. `iteration_tokens_total` grows almost one-for-one with concurrency: each engine step decodes the whole batch, and every request in that run sees the same TPOT.

Through 128 clients the step stays flat at 9.9–381.9 ms, and tokens/s stay near the 1-client line.
The step then lengthens: 64 clients at 436.4 ms (85.27% of linear, 143.70 tokens/s); 128 clients at 511.3 ms (71.31% of linear, 240.37 tokens/s). On these points OpenMP warning #124 is present, so the extra threads were piled onto CPU 0.

Time to first token rises with concurrency on the 96-core runs. Client TTFT median goes from 388.3 ms at 1 client to 189.1 ms at 128 clients. Server `time_to_first_token_seconds` matches that rise. Waiting requests stay at zero, so this is batch service time. On these 96-core points the request-finish histograms stay empty, because a request does not complete inside the window.

## Core count, same 8 clients

8 clients, 512 generated tokens. Compared inside one model.

| Model | Cores | ITL mean | Client TPOT | Tokens/s | Complete requests | Request TPOT mean | Decode time mean | Server TTFT |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `Qwen/Qwen2.5-0.5B-Instruct` | 24 | 118.3 ms | 117.6 ms | 67.27 | 8 | 119.5 ms | 61.1 s | 330.6 ms |
| `Qwen/Qwen2.5-0.5B-Instruct` | 24 | 11.6 ms | 11.5 ms | 687.39 | 128 | 11.6 ms | 5909.6 ms | 43.5 ms |
| `Qwen/Qwen2.5-0.5B-Instruct` | 48 | 147.9 ms | 147.1 ms | 53.61 | 8 | 148.4 ms | 75.8 s | 494.5 ms |
| `Qwen/Qwen2.5-0.5B-Instruct` | 48 | 23.0 ms | 23.1 ms | 345.36 | 64 | 23.0 ms | 11.8 s | 74.9 ms |
| `Qwen/Qwen2.5-0.5B-Instruct` | 72 | 202.6 ms | 202.6 ms | 39.21 | 0 | — | — | 607.5 ms |
| `Qwen/Qwen2.5-0.5B-Instruct` | 72 | 32.9 ms | 32.9 ms | 242.26 | 40 | 32.9 ms | 16.8 s | 93.3 ms |
| `Qwen/Qwen2.5-0.5B-Instruct` | 96 | 364.9 ms | 364.8 ms | 21.79 | 0 | — | — | 855.8 ms |
| `Qwen/Qwen2.5-0.5B-Instruct` | 96 | 20.0 ms | 18.7 ms | 399.07 | 72 | 20.1 ms | 10.3 s | 56.4 ms |
| `Qwen/Qwen3-1.7B` | 24 | 334.7 ms | 335.2 ms | 23.66 | 0 | — | — | 1153.9 ms |
| `Qwen/Qwen3-1.7B` | 24 | 24.4 ms | 24.4 ms | 326.32 | 56 | 24.4 ms | 12.5 s | 96.0 ms |
| `Qwen/Qwen3-1.7B` | 48 | 378.7 ms | 379.5 ms | 20.89 | 0 | — | — | 1088.4 ms |
| `Qwen/Qwen3-1.7B` | 48 | 19.3 ms | 19.3 ms | 410.69 | 72 | 19.3 ms | 9881.0 ms | 81.2 ms |
| `Qwen/Qwen3-1.7B` | 72 | 418.3 ms | 418.9 ms | 18.93 | 0 | — | — | 1208.7 ms |
| `Qwen/Qwen3-1.7B` | 72 | 18.0 ms | 18.0 ms | 441.44 | 80 | 18.0 ms | 9192.3 ms | 90.0 ms |
| `Qwen/Qwen3-1.7B` | 96 | 553.2 ms | 553.1 ms | 14.23 | 0 | — | — | 1759.1 ms |
| `Qwen/Qwen3-1.7B` | 96 | 22.5 ms | 22.5 ms | 352.90 | 64 | 22.5 ms | 11.5 s | 77.3 ms |
| `Qwen/Qwen3-4B` | 24 | 721.1 ms | 720.0 ms | 10.77 | 0 | — | — | 2818.4 ms |
| `Qwen/Qwen3-4B` | 24 | 48.6 ms | 48.6 ms | 163.58 | 24 | 48.7 ms | 24.9 s | 189.2 ms |
| `Qwen/Qwen3-4B` | 48 | 772.5 ms | 771.1 ms | 10.06 | 0 | — | — | 3031.7 ms |
| `Qwen/Qwen3-4B` | 48 | 36.0 ms | 36.1 ms | 220.56 | 40 | 36.1 ms | 18.4 s | 149.3 ms |
| `Qwen/Qwen3-4B` | 72 | 856.1 ms | 854.8 ms | 9.08 | 0 | — | — | 3128.5 ms |
| `Qwen/Qwen3-4B` | 72 | 38.4 ms | 38.4 ms | 206.96 | 32 | 38.4 ms | 19.6 s | 150.5 ms |
| `Qwen/Qwen3-4B` | 96 | 967.0 ms | 964.1 ms | 8.02 | 0 | — | — | 3013.6 ms |
| `Qwen/Qwen3-4B` | 96 | 35.6 ms | 35.6 ms | 223.21 | 40 | 35.6 ms | 18.2 s | 141.4 ms |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | 24 | 150.9 ms | 150.0 ms | 52.54 | 8 | 151.5 ms | 77.4 s | 567.4 ms |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | 24 | 12.7 ms | 12.7 ms | 627.57 | 112 | 12.7 ms | 6474.1 ms | 51.7 ms |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | 48 | 178.6 ms | 178.6 ms | 44.54 | 8 | — | — | 646.8 ms |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | 48 | 10.5 ms | 10.5 ms | 757.17 | 136 | 10.5 ms | 5365.6 ms | 41.0 ms |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | 72 | 216.3 ms | 216.6 ms | 36.72 | 0 | — | — | 765.1 ms |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | 72 | 10.7 ms | 10.6 ms | 745.71 | 136 | 10.7 ms | 5443.6 ms | 45.5 ms |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | 96 | 311.7 ms | 311.6 ms | 25.51 | 0 | — | — | 697.7 ms |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | 96 | 10.6 ms | 10.5 ms | 750.88 | 136 | 10.6 ms | 5408.4 ms | 43.4 ms |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | 24 | 354.9 ms | 355.5 ms | 22.23 | 0 | — | — | 1368.2 ms |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | 24 | 25.6 ms | 25.6 ms | 310.16 | 56 | 25.6 ms | 13.1 s | 107.9 ms |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | 48 | 405.6 ms | 406.0 ms | 19.39 | 0 | — | — | 1520.3 ms |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | 48 | 20.6 ms | 20.6 ms | 385.90 | 72 | 20.6 ms | 10.5 s | 84.7 ms |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | 72 | 467.0 ms | 467.0 ms | 16.81 | 0 | — | — | 1748.9 ms |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | 72 | 20.2 ms | 20.2 ms | 392.30 | 72 | 20.3 ms | 10.4 s | 94.5 ms |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | 96 | 614.4 ms | 614.0 ms | 12.72 | 0 | — | — | 2066.3 ms |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | 96 | 20.1 ms | 20.2 ms | 394.51 | 72 | 20.1 ms | 10.3 s | 98.7 ms |
| `ibm-granite/granite-3.2-2b-instruct` | 24 | 479.2 ms | 479.8 ms | 16.44 | 0 | — | — | 1537.2 ms |
| `ibm-granite/granite-3.2-2b-instruct` | 24 | 34.1 ms | 34.1 ms | 232.63 | 40 | 34.1 ms | 17.4 s | 139.4 ms |
| `ibm-granite/granite-3.2-2b-instruct` | 48 | 551.1 ms | 550.8 ms | 14.23 | 0 | — | — | 1899.7 ms |
| `ibm-granite/granite-3.2-2b-instruct` | 48 | 26.9 ms | 26.9 ms | 295.58 | 56 | 26.9 ms | 13.7 s | 112.6 ms |
| `ibm-granite/granite-3.2-2b-instruct` | 72 | 622.1 ms | 621.5 ms | 12.63 | 0 | — | — | 2138.2 ms |
| `ibm-granite/granite-3.2-2b-instruct` | 72 | 25.5 ms | 25.5 ms | 311.57 | 56 | 25.5 ms | 13.0 s | 110.7 ms |
| `ibm-granite/granite-3.2-2b-instruct` | 96 | 785.7 ms | 784.8 ms | 9.88 | 0 | — | — | 2700.4 ms |
| `ibm-granite/granite-3.2-2b-instruct` | 96 | 30.7 ms | 30.8 ms | 258.88 | 48 | 30.7 ms | 15.7 s | 101.6 ms |

For `Qwen/Qwen2.5-0.5B-Instruct`, 24 cores finished at 11.6 ms/token and 687.39 tokens/s. 128 requests completed inside the 90-second window. 96 cores at the same concurrency was 364.9 ms/token and 21.79 tokens/s. OpenMP warning #124 is present, so the worker mask collapsed onto CPU 0.

For `Qwen/Qwen3-1.7B`, 72 cores finished at 18.0 ms/token and 441.44 tokens/s. 80 requests completed inside the 90-second window. 96 cores at the same concurrency was 553.2 ms/token and 14.23 tokens/s. OpenMP warning #124 is present, so the worker mask collapsed onto CPU 0.

For `Qwen/Qwen3-4B`, 96 cores finished at 35.6 ms/token and 223.21 tokens/s. 40 requests completed inside the 90-second window. 96 cores at the same concurrency was 967.0 ms/token and 8.02 tokens/s. OpenMP warning #124 is present, so the worker mask collapsed onto CPU 0.

For `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8`, 48 cores finished at 10.5 ms/token and 757.17 tokens/s. 136 requests completed inside the 90-second window. 96 cores at the same concurrency was 311.7 ms/token and 25.51 tokens/s. OpenMP warning #124 is present, so the worker mask collapsed onto CPU 0.

For `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8`, 96 cores finished at 20.1 ms/token and 394.51 tokens/s. 72 requests completed inside the 90-second window. 96 cores at the same concurrency was 614.4 ms/token and 12.72 tokens/s. OpenMP warning #124 is present, so the worker mask collapsed onto CPU 0.

For `ibm-granite/granite-3.2-2b-instruct`, 72 cores finished at 25.5 ms/token and 311.57 tokens/s. 56 requests completed inside the 90-second window. 96 cores at the same concurrency was 785.7 ms/token and 9.88 tokens/s. OpenMP warning #124 is present, so the worker mask collapsed onto CPU 0.

## Thread pinning

81 attempts logged OpenMP warning #124, ignoring OS proc IDs up to 95 (`node0_cores096_clients001_gen0512`). Those workers did not keep one thread per core.

This 0.5B path is manual BF16, not a Xeon 6 recipe. AMX-busy time across finished runs is 0.02%–17.54% of counted cycles. It rises with batch size and is still a small slice of the step. IPC stays near 0.15–0.88.

Reported DRAM bandwidth in `system.csv` is about 0.0002 GB/s. A 0.5B BF16 model is about 1 GB of weights, larger than this socket's share of the 960 MiB L3, so a real decode should move on the order of gigabytes per second. The IMC CAS counts are tens of events per 100 ms interval. Treat the bandwidth column as not yet measuring this workload. It is not evidence that decode is cache-resident.

## Other vLLM series

| Config | Server TTFT mean | TTFT n | Queue mean | Prefill n | Decode-time n | Request TPOT n | E2E n | KV cache mean | IPC | AMX busy | L3 stall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `node0_cores096_clients001_gen0512` | 384.3 ms | 1 | — ms | 0 | 0 | 0 | 0 | 0.00004 | 0.553 | 0.06% | 24.18% |
| `node0_cores096_clients001_gen0512` | 22.8 ms | 18 | 0.0 ms | 17 | 17 | 17 | 17 | 0.00006 | 0.883 | 0.03% | 10.45% |
| `node0_cores096_clients002_gen0512` | 574.3 ms | 2 | — ms | 0 | 0 | 0 | 0 | 0.00008 | 0.556 | 0.14% | 25.14% |
| `node0_cores096_clients002_gen0512` | 38.3 ms | 22 | 0.0 ms | 20 | 20 | 20 | 20 | 0.00012 | 0.695 | 0.04% | 5.72% |
| `node0_cores096_clients004_gen0512` | 706.2 ms | 4 | — ms | 0 | 0 | 0 | 0 | 0.00016 | 0.572 | 0.28% | 24.56% |
| `node0_cores096_clients004_gen0512` | 46.4 ms | 40 | 0.0 ms | 36 | 36 | 36 | 36 | 0.00024 | 0.692 | 0.07% | 5.68% |
| `node0_cores024_clients008_gen0512` | 330.6 ms | 16 | 0.0 ms | 8 | 8 | 8 | 8 | 0.00043 | 0.452 | 1.74% | 61.81% |
| `node0_cores024_clients008_gen0512` | 43.5 ms | 128 | 0.0 ms | 120 | 120 | 120 | 120 | 0.00048 | 0.717 | 0.85% | 25.60% |
| `node0_cores048_clients008_gen0512` | 494.5 ms | 16 | 0.0 ms | 8 | 8 | 8 | 8 | 0.00044 | 0.599 | 1.40% | 44.70% |
| `node0_cores048_clients008_gen0512` | 74.9 ms | 64 | 0.0 ms | 56 | 56 | 56 | 56 | 0.00048 | 0.693 | 0.22% | 16.55% |
| `node0_cores072_clients008_gen0512` | 607.5 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00045 | 0.611 | 0.99% | 35.00% |
| `node0_cores072_clients008_gen0512` | 93.3 ms | 48 | 0.0 ms | 40 | 40 | 40 | 40 | 0.00048 | 0.674 | 0.10% | 9.48% |
| `node0_cores096_clients008_gen0128` | 864.8 ms | 16 | 0.0 ms | 8 | 8 | 8 | 8 | 0.00022 | 0.572 | 0.60% | 22.77% |
| `node0_cores096_clients008_gen0512` | 855.8 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00031 | 0.557 | 0.53% | 22.45% |
| `node0_cores096_clients008_gen0512` | 56.4 ms | 72 | 0.0 ms | 64 | 64 | 64 | 64 | 0.00050 | 0.716 | 0.13% | 5.50% |
| `node0_cores096_clients008_gen2048` | 848.8 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00031 | 0.565 | 0.55% | 22.83% |
| `node0_cores096_clients016_gen0512` | 1120.2 ms | 16 | — ms | 0 | 0 | 0 | 0 | 0.00060 | 0.563 | 1.06% | 22.97% |
| `node0_cores096_clients016_gen0512` | 65.4 ms | 144 | 0.0 ms | 128 | 128 | 128 | 128 | 0.00098 | 0.699 | 0.26% | 6.07% |
| `node0_cores096_clients032_gen0512` | 1481.7 ms | 32 | — ms | 0 | 0 | 0 | 0 | 0.00116 | 0.569 | 2.04% | 23.91% |
| `node0_cores096_clients032_gen0512` | 84.9 ms | 288 | 0.1 ms | 256 | 256 | 256 | 256 | 0.00202 | 0.712 | 0.48% | 6.90% |
| `node0_cores096_clients064_gen0512` | 2183.0 ms | 64 | — ms | 0 | 0 | 0 | 0 | 0.00215 | 0.561 | 3.59% | 14.32% |
| `node0_cores096_clients064_gen0512` | 120.5 ms | 384 | 0.1 ms | 320 | 320 | 320 | 320 | 0.00379 | 0.697 | 0.72% | 4.55% |
| `node0_cores096_clients128_gen0512` | 3660.0 ms | 128 | — ms | 0 | 0 | 0 | 0 | 0.00400 | 0.598 | 6.49% | 16.48% |
| `node0_cores096_clients128_gen0512` | 171.9 ms | 768 | 0.2 ms | 640 | 640 | 640 | 640 | 0.00768 | 0.752 | 1.33% | 6.19% |
| `node0_cores096_clients001_gen0512` | 658.2 ms | 1 | — ms | 0 | 0 | 0 | 0 | 0.00029 | 0.511 | 0.16% | 45.48% |
| `node0_cores096_clients001_gen0512` | 25.8 ms | 11 | 0.0 ms | 10 | 10 | 10 | 10 | 0.00057 | 0.576 | 0.07% | 41.67% |
| `node0_cores096_clients002_gen0512` | 974.6 ms | 2 | — ms | 0 | 0 | 0 | 0 | 0.00059 | 0.496 | 0.33% | 46.43% |
| `node0_cores096_clients002_gen0512` | 46.0 ms | 18 | 0.0 ms | 16 | 16 | 16 | 16 | 0.00116 | 0.571 | 0.11% | 35.74% |
| `node0_cores096_clients004_gen0512` | 1289.8 ms | 4 | — ms | 0 | 0 | 0 | 0 | 0.00118 | 0.503 | 0.67% | 46.16% |
| `node0_cores096_clients004_gen0512` | 57.3 ms | 36 | 0.0 ms | 32 | 32 | 32 | 32 | 0.00226 | 0.576 | 0.22% | 35.42% |
| `node0_cores024_clients008_gen0512` | 1153.9 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00302 | 0.210 | 2.21% | 78.12% |
| `node0_cores024_clients008_gen0512` | 96.0 ms | 64 | 0.0 ms | 56 | 56 | 56 | 56 | 0.00456 | 0.477 | 1.42% | 51.90% |
| `node0_cores048_clients008_gen0512` | 1088.4 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00274 | 0.314 | 1.96% | 68.87% |
| `node0_cores048_clients008_gen0512` | 81.2 ms | 72 | 0.0 ms | 72 | 72 | 72 | 72 | 0.00455 | 0.534 | 0.91% | 45.14% |
| `node0_cores072_clients008_gen0512` | 1208.7 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00260 | 0.349 | 1.77% | 61.04% |
| `node0_cores072_clients008_gen0512` | 90.0 ms | 80 | 0.0 ms | 72 | 72 | 72 | 72 | 0.00456 | 0.574 | 0.68% | 41.63% |
| `node0_cores096_clients008_gen0128` | 1770.5 ms | 16 | 0.0 ms | 8 | 8 | 8 | 8 | 0.00196 | 0.500 | 1.48% | 44.46% |
| `node0_cores096_clients008_gen0512` | 1759.1 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00234 | 0.503 | 1.32% | 45.53% |
| `node0_cores096_clients008_gen0512` | 77.3 ms | 64 | 0.0 ms | 56 | 56 | 56 | 56 | 0.00462 | 0.574 | 0.41% | 35.19% |
| `node0_cores096_clients008_gen2048` | 1746.6 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00234 | 0.500 | 1.32% | 45.55% |
| `node0_cores096_clients016_gen0512` | 2374.8 ms | 16 | — ms | 0 | 0 | 0 | 0 | 0.00442 | 0.496 | 2.42% | 43.09% |
| `node0_cores096_clients016_gen0512` | 104.9 ms | 128 | 0.0 ms | 112 | 112 | 112 | 112 | 0.00945 | 0.568 | 0.85% | 40.27% |
| `node0_cores096_clients032_gen0512` | 3472.1 ms | 32 | — ms | 0 | 0 | 0 | 0 | 0.00798 | 0.481 | 4.33% | 41.56% |
| `node0_cores096_clients032_gen0512` | 160.2 ms | 224 | 0.1 ms | 192 | 192 | 192 | 192 | 0.01869 | 0.587 | 1.30% | 34.20% |
| `node0_cores096_clients064_gen0512` | 6639.0 ms | 64 | — ms | 0 | 0 | 0 | 0 | 0.01324 | 0.492 | 7.38% | 24.03% |
| `node0_cores096_clients064_gen0512` | 268.0 ms | 320 | 0.1 ms | 256 | 256 | 256 | 256 | 0.03755 | 0.584 | 2.08% | 25.95% |
| `node0_cores096_clients128_gen0512` | 15036.3 ms | 128 | — ms | 0 | 0 | 0 | 0 | 0.02277 | 0.417 | 11.28% | 29.27% |
| `node0_cores096_clients128_gen0512` | 386.5 ms | 512 | 0.2 ms | 384 | 384 | 384 | 384 | 0.07689 | 0.547 | 2.90% | 29.87% |
| `node0_cores096_clients001_gen0512` | 1092.0 ms | 1 | — ms | 0 | 0 | 0 | 0 | 0.00027 | 0.386 | 0.25% | 59.54% |
| `node0_cores096_clients001_gen0512` | 41.2 ms | 6 | 0.0 ms | 5 | 5 | 5 | 5 | 0.00073 | 0.496 | 0.08% | 50.50% |
| `node0_cores096_clients002_gen0512` | 1391.7 ms | 2 | — ms | 0 | 0 | 0 | 0 | 0.00054 | 0.366 | 0.52% | 60.51% |
| `node0_cores096_clients002_gen0512` | 77.5 ms | 12 | 0.0 ms | 10 | 10 | 10 | 10 | 0.00144 | 0.479 | 0.17% | 52.02% |
| `node0_cores096_clients004_gen0512` | 2290.0 ms | 4 | — ms | 0 | 0 | 0 | 0 | 0.00107 | 0.368 | 1.02% | 60.40% |
| `node0_cores096_clients004_gen0512` | 101.2 ms | 24 | 0.0 ms | 20 | 20 | 20 | 20 | 0.00292 | 0.488 | 0.33% | 51.09% |
| `node0_cores024_clients008_gen0512` | 2818.4 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00253 | 0.148 | 2.68% | 83.14% |
| `node0_cores024_clients008_gen0512` | 189.2 ms | 32 | 0.0 ms | 24 | 24 | 24 | 24 | 0.00567 | 0.384 | 1.68% | 61.66% |
| `node0_cores048_clients008_gen0512` | 3031.7 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00238 | 0.203 | 2.51% | 77.09% |
| `node0_cores048_clients008_gen0512` | 149.3 ms | 40 | 0.0 ms | 32 | 32 | 32 | 32 | 0.00583 | 0.441 | 1.15% | 55.35% |
| `node0_cores072_clients008_gen0512` | 3128.5 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00221 | 0.266 | 2.26% | 69.25% |
| `node0_cores072_clients008_gen0512` | 150.5 ms | 40 | 0.0 ms | 32 | 32 | 32 | 32 | 0.00567 | 0.494 | 0.76% | 48.73% |
| `node0_cores096_clients008_gen0128` | 3408.0 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00211 | 0.369 | 1.95% | 58.21% |
| `node0_cores096_clients008_gen0512` | 3013.6 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00211 | 0.372 | 2.01% | 59.16% |
| `node0_cores096_clients008_gen0512` | 141.4 ms | 40 | 0.0 ms | 32 | 32 | 32 | 32 | 0.00591 | 0.494 | 0.61% | 50.31% |
| `node0_cores096_clients008_gen2048` | 3415.1 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00211 | 0.363 | 1.95% | 57.85% |
| `node0_cores096_clients016_gen0512` | 5428.2 ms | 16 | — ms | 0 | 0 | 0 | 0 | 0.00412 | 0.362 | 3.81% | 57.61% |
| `node0_cores096_clients016_gen0512` | 197.7 ms | 80 | 0.0 ms | 64 | 64 | 64 | 64 | 0.01163 | 0.494 | 1.16% | 49.51% |
| `node0_cores096_clients032_gen0512` | 8920.1 ms | 32 | — ms | 0 | 0 | 0 | 0 | 0.00793 | 0.346 | 6.82% | 56.54% |
| `node0_cores096_clients032_gen0512` | 301.4 ms | 128 | 0.1 ms | 96 | 96 | 96 | 96 | 0.02423 | 0.485 | 2.03% | 47.82% |
| `node0_cores096_clients064_gen0512` | 15436.5 ms | 64 | — ms | 0 | 0 | 0 | 0 | 0.01466 | 0.391 | 11.52% | 30.20% |
| `node0_cores096_clients064_gen0512` | 488.2 ms | 192 | 0.1 ms | 128 | 128 | 128 | 128 | 0.04554 | 0.544 | 2.88% | 27.91% |
| `node0_cores096_clients128_gen0512` | 29748.8 ms | 128 | — ms | 0 | 0 | 0 | 0 | 0.02402 | 0.362 | 17.54% | 24.57% |
| `node0_cores096_clients128_gen0512` | 803.5 ms | 256 | 0.2 ms | 128 | 128 | 128 | 128 | 0.09344 | 0.520 | 4.21% | 26.25% |
| `node0_cores096_clients001_gen0512` | 331.8 ms | 1 | — ms | 0 | 0 | 0 | 0 | 0.00013 | 0.574 | 0.06% | 39.06% |
| `node0_cores096_clients001_gen0512` | 13.9 ms | 20 | 0.0 ms | 19 | 19 | 19 | 19 | 0.00017 | 0.810 | 0.02% | 21.93% |
| `node0_cores096_clients002_gen0512` | 514.5 ms | 2 | — ms | 0 | 0 | 0 | 0 | 0.00023 | 0.598 | 0.09% | 32.71% |
| `node0_cores096_clients002_gen0512` | 24.9 ms | 38 | 0.0 ms | 36 | 36 | 36 | 36 | 0.00032 | 0.816 | 0.04% | 20.95% |
| `node0_cores096_clients004_gen0512` | 674.6 ms | 4 | — ms | 0 | 0 | 0 | 0 | 0.00044 | 0.623 | 0.19% | 33.52% |
| `node0_cores096_clients004_gen0512` | 31.8 ms | 72 | 0.0 ms | 68 | 68 | 68 | 68 | 0.00066 | 0.825 | 0.08% | 20.47% |
| `node0_cores024_clients008_gen0512` | 567.4 ms | 16 | 0.0 ms | 8 | 8 | 8 | 8 | 0.00121 | 0.318 | 2.11% | 69.73% |
| `node0_cores024_clients008_gen0512` | 51.7 ms | 112 | 0.0 ms | 104 | 104 | 104 | 104 | 0.00127 | 0.618 | 1.17% | 38.16% |
| `node0_cores048_clients008_gen0512` | 646.8 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00131 | 0.425 | 1.72% | 58.87% |
| `node0_cores048_clients008_gen0512` | 41.0 ms | 136 | 0.0 ms | 128 | 128 | 128 | 128 | 0.00131 | 0.713 | 0.72% | 28.47% |
| `node0_cores072_clients008_gen0512` | 765.1 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00115 | 0.477 | 1.40% | 48.74% |
| `node0_cores072_clients008_gen0512` | 45.5 ms | 136 | 0.0 ms | 128 | 128 | 128 | 128 | 0.00128 | 0.775 | 0.49% | 22.53% |
| `node0_cores096_clients008_gen0128` | 949.0 ms | 24 | 0.0 ms | 16 | 16 | 16 | 16 | 0.00057 | 0.559 | 1.05% | 34.30% |
| `node0_cores096_clients008_gen0512` | 697.7 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00091 | 0.560 | 0.94% | 34.52% |
| `node0_cores096_clients008_gen0512` | 43.4 ms | 136 | 0.0 ms | 128 | 128 | 128 | 128 | 0.00132 | 0.786 | 0.37% | 21.35% |
| `node0_cores096_clients008_gen2048` | 928.3 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00090 | 0.566 | 0.95% | 34.57% |
| `node0_cores096_clients016_gen0512` | 1266.3 ms | 16 | — ms | 0 | 0 | 0 | 0 | 0.00179 | 0.579 | 1.87% | 35.73% |
| `node0_cores096_clients016_gen0512` | 56.6 ms | 240 | 0.0 ms | 224 | 224 | 224 | 224 | 0.00262 | 0.788 | 0.67% | 21.01% |
| `node0_cores096_clients032_gen0512` | 1947.3 ms | 32 | — ms | 0 | 0 | 0 | 0 | 0.00332 | 0.564 | 3.42% | 37.25% |
| `node0_cores096_clients032_gen0512` | 81.3 ms | 416 | 0.1 ms | 384 | 384 | 384 | 384 | 0.00527 | 0.780 | 1.13% | 21.07% |
| `node0_cores096_clients064_gen0512` | 3314.9 ms | 64 | — ms | 0 | 0 | 0 | 0 | 0.00566 | 0.537 | 5.48% | 28.22% |
| `node0_cores096_clients064_gen0512` | 123.6 ms | 576 | 0.1 ms | 512 | 512 | 512 | 512 | 0.01081 | 0.752 | 1.70% | 15.77% |
| `node0_cores096_clients128_gen0512` | 6117.4 ms | 128 | — ms | 0 | 0 | 0 | 0 | 0.00992 | 0.534 | 8.77% | 25.37% |
| `node0_cores096_clients128_gen0512` | 195.9 ms | 768 | 0.2 ms | 768 | 768 | 768 | 768 | 0.02153 | 0.746 | 2.35% | 15.78% |
| `node0_cores096_clients001_gen0512` | 668.5 ms | 1 | — ms | 0 | 0 | 0 | 0 | 0.00030 | 0.528 | 0.06% | 45.39% |
| `node0_cores096_clients001_gen0512` | 24.1 ms | 10 | 0.0 ms | 9 | 9 | 9 | 9 | 0.00058 | 0.606 | 0.02% | 41.01% |
| `node0_cores096_clients002_gen0512` | 1053.9 ms | 2 | — ms | 0 | 0 | 0 | 0 | 0.00057 | 0.605 | 0.11% | 41.26% |
| `node0_cores096_clients002_gen0512` | 47.0 ms | 20 | 0.0 ms | 18 | 18 | 18 | 18 | 0.00115 | 0.636 | 0.04% | 38.43% |
| `node0_cores096_clients004_gen0512` | 1438.6 ms | 4 | — ms | 0 | 0 | 0 | 0 | 0.00109 | 0.612 | 0.21% | 41.42% |
| `node0_cores096_clients004_gen0512` | 64.2 ms | 40 | 0.0 ms | 36 | 36 | 36 | 36 | 0.00226 | 0.656 | 0.07% | 36.72% |
| `node0_cores024_clients008_gen0512` | 1368.2 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00288 | 0.238 | 2.21% | 76.40% |
| `node0_cores024_clients008_gen0512` | 107.9 ms | 56 | 0.0 ms | 48 | 48 | 48 | 48 | 0.00463 | 0.481 | 1.42% | 51.23% |
| `node0_cores048_clients008_gen0512` | 1520.3 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00260 | 0.328 | 1.92% | 66.64% |
| `node0_cores048_clients008_gen0512` | 84.7 ms | 72 | 0.0 ms | 64 | 64 | 64 | 64 | 0.00462 | 0.557 | 0.90% | 43.42% |
| `node0_cores072_clients008_gen0512` | 1748.9 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00249 | 0.386 | 1.67% | 58.05% |
| `node0_cores072_clients008_gen0512` | 94.5 ms | 72 | 0.0 ms | 64 | 64 | 64 | 64 | 0.00454 | 0.636 | 0.63% | 35.82% |
| `node0_cores096_clients008_gen0128` | 2083.6 ms | 16 | 0.0 ms | 8 | 8 | 8 | 8 | 0.00196 | 0.510 | 1.45% | 43.78% |
| `node0_cores096_clients008_gen0512` | 2066.3 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00219 | 0.510 | 1.26% | 43.38% |
| `node0_cores096_clients008_gen0512` | 98.7 ms | 72 | 0.0 ms | 64 | 64 | 64 | 64 | 0.00457 | 0.596 | 0.49% | 39.04% |
| `node0_cores096_clients008_gen2048` | 2036.1 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00221 | 0.512 | 1.28% | 44.12% |
| `node0_cores096_clients016_gen0512` | 2959.9 ms | 16 | — ms | 0 | 0 | 0 | 0 | 0.00427 | 0.507 | 2.46% | 43.84% |
| `node0_cores096_clients016_gen0512` | 134.6 ms | 128 | 0.0 ms | 112 | 112 | 112 | 112 | 0.00916 | 0.594 | 0.88% | 38.68% |
| `node0_cores096_clients032_gen0512` | 4628.1 ms | 32 | — ms | 0 | 0 | 0 | 0 | 0.00777 | 0.484 | 4.40% | 44.21% |
| `node0_cores096_clients032_gen0512` | 157.3 ms | 224 | 0.1 ms | 192 | 192 | 192 | 192 | 0.01854 | 0.585 | 1.49% | 38.13% |
| `node0_cores096_clients064_gen0512` | 8025.1 ms | 64 | — ms | 0 | 0 | 0 | 0 | 0.01246 | 0.436 | 6.79% | 39.81% |
| `node0_cores096_clients064_gen0512` | 278.0 ms | 256 | 0.1 ms | 192 | 192 | 192 | 192 | 0.03586 | 0.568 | 1.75% | 24.06% |
| `node0_cores096_clients128_gen0512` | 16519.0 ms | 128 | — ms | 0 | 0 | 0 | 0 | 0.02272 | 0.430 | 10.70% | 32.20% |
| `node0_cores096_clients128_gen0512` | 429.3 ms | 384 | 0.2 ms | 256 | 256 | 256 | 256 | 0.07143 | 0.534 | 2.65% | 25.46% |
| `node0_cores096_clients001_gen0512` | 903.5 ms | 1 | — ms | 0 | 0 | 0 | 0 | 0.00017 | 0.514 | 0.18% | 45.89% |
| `node0_cores096_clients001_gen0512` | 31.2 ms | 8 | 0.0 ms | 7 | 7 | 7 | 7 | 0.00041 | 0.548 | 0.07% | 44.55% |
| `node0_cores096_clients002_gen0512` | 1382.4 ms | 2 | — ms | 0 | 0 | 0 | 0 | 0.00035 | 0.481 | 0.38% | 48.36% |
| `node0_cores096_clients002_gen0512` | 55.4 ms | 12 | 0.0 ms | 10 | 10 | 10 | 10 | 0.00081 | 0.553 | 0.12% | 36.29% |
| `node0_cores096_clients004_gen0512` | 1636.9 ms | 4 | — ms | 0 | 0 | 0 | 0 | 0.00069 | 0.483 | 0.77% | 47.78% |
| `node0_cores096_clients004_gen0512` | 80.0 ms | 24 | 0.0 ms | 20 | 20 | 20 | 20 | 0.00157 | 0.553 | 0.24% | 36.71% |
| `node0_cores024_clients008_gen0512` | 1537.2 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00176 | 0.206 | 2.42% | 78.31% |
| `node0_cores024_clients008_gen0512` | 139.4 ms | 48 | 0.0 ms | 40 | 40 | 40 | 40 | 0.00323 | 0.459 | 1.53% | 53.95% |
| `node0_cores048_clients008_gen0512` | 1899.7 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00166 | 0.306 | 2.12% | 69.24% |
| `node0_cores048_clients008_gen0512` | 112.6 ms | 56 | 0.0 ms | 48 | 48 | 48 | 48 | 0.00323 | 0.511 | 0.98% | 47.16% |
| `node0_cores072_clients008_gen0512` | 2138.2 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00156 | 0.352 | 1.88% | 59.94% |
| `node0_cores072_clients008_gen0512` | 110.7 ms | 56 | 0.0 ms | 48 | 48 | 48 | 48 | 0.00334 | 0.558 | 0.71% | 42.71% |
| `node0_cores096_clients008_gen0128` | 2682.8 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00133 | 0.476 | 1.50% | 46.49% |
| `node0_cores096_clients008_gen0512` | 2700.4 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00133 | 0.480 | 1.50% | 46.53% |
| `node0_cores096_clients008_gen0512` | 101.6 ms | 48 | 0.0 ms | 40 | 40 | 40 | 40 | 0.00323 | 0.564 | 0.45% | 35.89% |
| `node0_cores096_clients008_gen2048` | 2203.8 ms | 8 | — ms | 0 | 0 | 0 | 0 | 0.00134 | 0.479 | 1.50% | 46.35% |
| `node0_cores096_clients016_gen0512` | 3892.7 ms | 16 | — ms | 0 | 0 | 0 | 0 | 0.00248 | 0.491 | 2.86% | 45.02% |
| `node0_cores096_clients016_gen0512` | 141.6 ms | 112 | 0.0 ms | 96 | 96 | 96 | 96 | 0.00654 | 0.563 | 0.97% | 40.82% |
| `node0_cores096_clients032_gen0512` | 6028.9 ms | 32 | — ms | 0 | 0 | 0 | 0 | 0.00451 | 0.471 | 5.13% | 44.73% |
| `node0_cores096_clients032_gen0512` | 215.0 ms | 192 | 0.1 ms | 160 | 160 | 160 | 160 | 0.01332 | 0.572 | 1.68% | 37.64% |
| `node0_cores096_clients064_gen0512` | 10885.7 ms | 64 | — ms | 0 | 0 | 0 | 0 | 0.00859 | 0.491 | 9.07% | 24.20% |
| `node0_cores096_clients064_gen0512` | 389.1 ms | 256 | 0.1 ms | 192 | 192 | 192 | 192 | 0.02520 | 0.588 | 2.57% | 24.79% |
| `node0_cores096_clients128_gen0512` | 19866.7 ms | 128 | — ms | 0 | 0 | 0 | 0 | 0.01525 | 0.447 | 14.35% | 21.64% |
| `node0_cores096_clients128_gen0512` | 582.4 ms | 384 | 0.2 ms | 256 | 256 | 256 | 256 | 0.05080 | 0.566 | 3.73% | 20.49% |

KV-cache occupancy stays well under 0.1%. The waiting gauge stays at 0 through the finished concurrency points, so TTFT growth is service time inside the batch, not scheduler queue time. Queue-time histograms confirm that only if requests finish; they have not, inside the window.

## Caveats

- 70 finished runs have `complete_requests` = 0, so the official complete-request TPOT percentiles in `summary.json` are null. 512 tokens at ~350 ms/token is about three minutes, and the measurement window is 90 seconds. Use observed client TPOT and the server inter-token histogram there.
- 8727 requests have completed inside a measurement window. On those runs the request-level TPOT and decode-time histograms are populated, and they belong in the core-count table.
- Histogram p50/p90/p99 are interpolated inside 100 ms buckets. When almost every sample sits in 300–400 ms, those percentiles collapse toward the middle and the top of that bucket. Quote the mean, and the bucket share, for decode latency.
- Partial rows are mid-window and will be replaced when the attempt writes `summary.json`.
- Several finished attempts record a non-fatal Docker cleanup race (`removal of container ... is already in progress`). The run stays marked done and the controller continues.

## What changes next

This file is rewritten as attempts finish.

