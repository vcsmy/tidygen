#!/usr/bin/env bash
# Download contract artifacts from a GitHub Release into contracts/*/target/ink
# Usage:
#   GITHUB_TOKEN=<PAT or GITHUB_TOKEN> bash scripts/download_release_artifacts.sh v0.1.0
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <tag> [owner repo]"
  echo "Example: GITHUB_TOKEN=xxx $0 v0.1.0"
  exit 1
fi

TAG="$1"
OWNER="${2:-vcsmy}"
REPO="${3:-tidygen}"
API="https://api.github.com/repos/${OWNER}/${REPO}/releases/tags/${TAG}"
AUTH_HEADER="Authorization: token ${GITHUB_TOKEN:-}"

echo "[info] Querying release $OWNER/$REPO:$TAG"
assets_json=$(curl -s -H "$AUTH_HEADER" "$API")
if [ -z "$assets_json" ]; then
  echo "[error] Release not found or API failed"
  exit 2
fi

mkdir -p contracts/substrate-poc/target/ink contracts/escrow-sla/target/ink

# download each asset
echo "$assets_json" | jq -r '.assets[] | "\(.name) \(.browser_download_url)"' | while read -r name url; do
  echo "[info] Downloading $name"
  curl -L -H "$AUTH_HEADER" -o "/tmp/$name" "$url"
  # place into correct target folder based on name patterns
  if echo "$name" | grep -q substrate-poc; then
    mv "/tmp/$name" "contracts/substrate-poc/target/ink/$name"
  elif echo "$name" | grep -q escrow-sla; then
    mv "/tmp/$name" "contracts/escrow-sla/target/ink/$name"
  elif echo "$name" | grep -i metadata || echo "$name" | grep -i .contract; then
    # attempt to place heuristically
    if echo "$name" | grep -q service_verification_poc; then
      mv "/tmp/$name" "contracts/substrate-poc/target/ink/$name"
    else
      mv "/tmp/$name" "contracts/escrow-sla/target/ink/$name" || true
    fi
  else
    # fallback to artifacts root
    mv "/tmp/$name" "artifacts/$name"
  fi
done

echo "[info] Download complete. Listing target/ink:"
ls -la contracts/*/target/ink || true