#!/usr/bin/env bash
# scripts/quickstart.sh
# One-command local quickstart: starts a local Substrate node (contracts-enabled),
# builds the ink! contract, deploys it, and runs the Django demo submit to print a tx hash.
# Usage: bash scripts/quickstart.sh [--headless]
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CONTRACT_DIR="$ROOT_DIR/contracts/substrate-poc"
BACKEND_DIR="$ROOT_DIR/apps/backend"
DOCKER_COMPOSE_FILE="$ROOT_DIR/scripts/docker-compose.quickstart.yml"
HEADLESS=false

# parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --headless) HEADLESS=true; shift ;;
    *) shift ;;
  esac
done

echo "[quickstart] Starting quickstart (headless=${HEADLESS})"
echo "[quickstart] 1) Starting substrate node via docker-compose"

docker-compose -f "$DOCKER_COMPOSE_FILE" up -d --build

echo "[quickstart] Waiting for Substrate node to be ready on ws://127.0.0.1:9944 ..."
# wait for node websocket
for i in $(seq 1 60); do
  if nc -z 127.0.0.1 9944 >/dev/null 2>&1; then
    echo "[quickstart] Node is up"
    break
  fi
  echo "[quickstart] waiting... ($i)"
  sleep 1
done

echo "[quickstart] 2) Build ink! contract (this may take a minute)"
cd "$CONTRACT_DIR"
# Try using dockerized builder if cargo-contract isn't available locally
if command -v cargo-contract >/dev/null 2>&1; then
  cargo contract build --release
else
  echo "[quickstart] cargo-contract not found locally, attempting docker builder (may require internet)"
  docker run --rm -v "$CONTRACT_DIR":/code -w /code parity/ink:latest sh -c "cargo contract build --release"
fi

# Ensure compiled contract artifacts exist
METADATA="$CONTRACT_DIR/target/ink/metadata.json"
WASM="$CONTRACT_DIR/target/ink/substrate_poc.wasm"
if [[ ! -f "$METADATA" && ! -f "$CONTRACT_DIR/target/contract/metadata.json" ]]; then
  echo "[quickstart] ERROR: contract metadata not found. Build may have failed."
  exit 1
fi

echo "[quickstart] 3) Deploy contract (using python deploy script)"
cd "$BACKEND_DIR"
python -m pip install -r requirements.txt >/dev/null 2>&1 || true

# deploy contract via the demo deployment script (implement this in apps/backend/substrate_poc/deploy_contract.py)
DEPLOY_SCRIPT="apps/backend/substrate_poc/deploy_contract.py"
if [[ -f "$DEPLOY_SCRIPT" ]]; then
  DEPLOY_OUTPUT=$(python "$DEPLOY_SCRIPT" --wasm "$CONTRACT_DIR/target/ink/substrate_poc.wasm" --metadata "$CONTRACT_DIR/target/ink/metadata.json" --ws ws://127.0.0.1:9944)
  echo "$DEPLOY_OUTPUT"
  # Expect the deploy script to print the deployed contract address in the last line
  CONTRACT_ADDRESS=$(echo "$DEPLOY_OUTPUT" | tail -n1 | tr -d '\r\n')
else
  echo "[quickstart] WARNING: deploy script not found ($DEPLOY_SCRIPT). Please deploy the contract manually and set CONTRACT_ADDRESS."
  CONTRACT_ADDRESS=""
fi

if [[ -z "$CONTRACT_ADDRESS" ]]; then
  echo "[quickstart] ERROR: CONTRACT_ADDRESS not set. Exiting."
  exit 1
fi

echo "[quickstart] 4) Run demo submit to create a service record and print tx hash"
python apps/backend/substrate_poc/submit_service.py --contract "$CONTRACT_ADDRESS" --service-id 1 --payload "demo"

echo "[quickstart] Quickstart finished successfully."
if [[ "$HEADLESS" == "false" ]]; then
  echo "[quickstart] To teardown the local environment, run: docker-compose -f $DOCKER_COMPOSE_FILE down"
fi