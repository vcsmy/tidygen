#!/usr/bin/env bash
# Robust builder script for contracts/substrate-poc
# Usage: bash scripts/build_contract.sh [--clean]
set -euo pipefail

CLEAN=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --clean) CLEAN=true; shift ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

CONTRACT_DIR="contracts/substrate-poc"

if [ "$CLEAN" = true ]; then
  echo "[build] Cleaning previous target/ink..."
  rm -rf "$CONTRACT_DIR/target/ink" || true
fi

if [ ! -d "$CONTRACT_DIR" ]; then
  echo "[error] Contract dir not found: $CONTRACT_DIR"
  exit 1
fi

cd "$CONTRACT_DIR"

if command -v cargo-contract >/dev/null 2>&1; then
  echo "[build] Using local cargo-contract..."
  cargo +nightly contract build
else
  echo "[build] Using dockerized builder..."
  docker run --rm -v "$(pwd)":/code -w /code paritytech/ink-ci-linux:latest \
    sh -c "cargo +nightly contract build"
fi

echo "[build] Checking artifacts..."
if [ -d "target/ink" ]; then
  ls -la target/ink
  echo "[build] Build artifacts produced in target/ink"
else
  echo "[error] Build did not produce target/ink"
  exit 1
fi