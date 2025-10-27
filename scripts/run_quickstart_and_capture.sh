#!/usr/bin/env bash
set -euo pipefail

LOGDIR="logs"
mkdir -p "$LOGDIR"
TS=$(date +%Y%m%d-%H%M%S)
LOGFILE="$LOGDIR/quickstart-$TS.log"

echo "[run] Running quickstart (headless) and capturing logs to $LOGFILE"
if bash scripts/quickstart.sh --headless >"$LOGFILE" 2>&1; then
  echo "[run] Quickstart completed. Searching for extrinsic hash in $LOGFILE"
  HASH=$(grep -o -E "0x[0-9a-fA-F]{64}" "$LOGFILE" | head -n1 || true)
  if [ -n "$HASH" ]; then
    echo "[run] Found extrinsic hash: $HASH"
    echo "$HASH"
    exit 0
  else
    echo "[run] No extrinsic hash found in logs. Tail of log:"
    tail -n 200 "$LOGFILE"
    exit 2
  fi
else
  echo "[run] Quickstart failed. See $LOGFILE"
  tail -n 200 "$LOGFILE"
  exit 1
fi