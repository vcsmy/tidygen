#!/usr/bin/env bash
# Install a cargo-contract version compatible with ink! v4 (or a pinned version)
# Usage:
#   bash scripts/install_cargo_contract.sh             # installs default pinned version
#   bash scripts/install_cargo_contract.sh 0.16.0      # installs a specific version
#
# Notes:
# - Requires Rust toolchain (rustup) installed.
# - This script will ensure the nightly toolchain and wasm target are installed.
# - It attempts to install a cargo-contract compatible with the repo's ink! version. Adjust version if needed.

set -euo pipefail

DEFAULT_VERSION="0.16.0"   # recommended for ink! v4 POC; change to match your ink! / cargo-contract compatibility
CARGO_CONTRACT_VERSION="${1:-$DEFAULT_VERSION}"

echo "[install] Installing cargo-contract (version: ${CARGO_CONTRACT_VERSION})"

# ensure rustup exists
if ! command -v rustup >/dev/null 2>&1; then
  echo "[error] rustup not found. Please install Rust toolchain from https://rustup.rs/"
  exit 1
fi

# install nightly toolchain
echo "[install] Ensuring nightly toolchain is installed..."
rustup toolchain install nightly || true
rustup target add wasm32-unknown-unknown --toolchain nightly || true

# install cargo-contract with pinned version
if command -v cargo-contract >/dev/null 2>&1; then
  CURRENT="$(cargo-contract --version 2>/dev/null || true)"
  echo "[install] cargo-contract already installed: ${CURRENT}"
fi

echo "[install] Installing cargo-contract v${CARGO_CONTRACT_VERSION}..."
cargo install cargo-contract --version "${CARGO_CONTRACT_VERSION}" --force

echo "[install] cargo-contract installed:"
cargo-contract --version || true

echo "[install] Done. You can now build contracts with:"
echo "  cd contracts/substrate-poc"
echo "  cargo +nightly contract build"

# End of script