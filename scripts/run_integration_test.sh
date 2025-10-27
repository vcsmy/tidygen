#!/usr/bin/env bash
set -euo pipefail
HELP=false
NO_BUILD=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-build) NO_BUILD=true; shift ;;
    -h|--help) HELP=true; shift ;;
    *) echo "Unknown arg $1"; exit 1 ;;
  esac
done

if [ "$HELP" = true ]; then
  echo "Usage: $0 [--no-build]"
  exit 0
fi

if [ "$NO_BUILD" = false ]; then
  bash scripts/build_contract.sh
fi

bash scripts/run_quickstart_and_capture.sh
pytest tests/integration/test_substrate_poc_quickstart.py -q