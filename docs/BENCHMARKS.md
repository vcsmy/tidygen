# TidyGen Benchmarks

This document describes simple benchmarking procedures for the Service Verification contract POC.

Goals
- Measure latency of a single store() transaction (local node).
- Measure throughput for N concurrent store() actions (local node).
- Measure gas/weight usage per store() call.

Quick local benchmark (single-threaded)
1. Build and deploy the contract (see contracts/substrate-poc/README.md).
2. Use the Python demo in packages/py-sdk/examples/demo.py to submit a series of requests and measure elapsed time.

Example script (bash)
```bash
#!/usr/bin/env bash
set -euo pipefail
CONTRACT_ADDR="$1"
RUNS=50
START=$(date +%s%3N)
for i in $(seq 1 $RUNS); do
  python packages/py-sdk/examples/demo.py "$CONTRACT_ADDR" "$i" "payload-$i" >/dev/null
done
END=$(date +%s%3N)
ELAPSED_MS=$((END-START))
echo "Submitted $RUNS txs in ${ELAPSED_MS} ms (avg $(echo "$ELAPSED_MS / $RUNS" | bc -l) ms per tx)"
```

Concurrent throughput (simple)
- Use GNU parallel or a small Node/Python script to run multiple submitters in parallel.
- Record average success rate, failure rate and time to completion.

Gas/Weight analysis
- Extract contract event data or the returned extrinsic details from the node to estimate gas/weight per call.
- Use these numbers to estimate on-chain costs on Westend/Kusama.

Reporting
- Save raw outputs to `benchmarks/` and produce a small CSV:
  - timestamp, run_id, tx_hash, elapsed_ms, gas_limit, weight_estimate

Notes
- These are informal benchmarks for capacity planning. For production, run tests on a larger, more realistic environment and use dedicated benchmarking tools (k6, locust, or custom load generator).
```