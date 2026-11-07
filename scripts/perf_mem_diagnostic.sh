#!/usr/bin/env bash
# Separate, opt-in PEBS sample profiling pass; NOT run during a regular benchmark.
set -Eeuo pipefail
if (( $# != 3 )); then
  echo 'Usage: sudo bash scripts/perf_mem_diagnostic.sh <CPU_LIST> <OUTPUT_DIR> <DURATION_SECONDS>' >&2
  exit 2
fi
CPUS="$1"
OUT="$2"
SECONDS="$3"
[[ "$SECONDS" =~ ^[0-9]+$ ]] || { echo 'Seconds must be an integer.' >&2; exit 2; }
(( SECONDS > 0 && SECONDS <= 600 )) || { echo 'Allowed seconds: 1..600' >&2; exit 2; }
mkdir -p "$OUT"
perf mem -t load record --ldlat 30 -a -C "$CPUS" \
  -o "$OUT/perf.data" -- sleep "$SECONDS" 2>"$OUT/perf_mem_record.stderr.txt"
perf mem -t load report -i "$OUT/perf.data" -D -x ';' \
  >"$OUT/perf_mem_raw_samples.txt" 2>"$OUT/perf_mem_report.stderr.txt"
perf mem -t load report -i "$OUT/perf.data" --stdio \
  >"$OUT/perf_mem_summary.txt" 2>"$OUT/perf_mem_summary.stderr.txt"
echo "Saved PEBS data and decoded samples under: $OUT"
echo 'Caveat: Intel PEBS use-latency includes queueing and is NOT pure DRAM controller latency.'
