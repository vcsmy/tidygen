#!/usr/bin/env bash
# Upload given file(s) as assets to a GitHub release (unlisted) using gh CLI
# Requirements: gh CLI authenticated (gh auth login) and git remote set to origin
#
# Usage:
#   bash scripts/upload_demo_release.sh v0.1.0 "Demo video upload" demo.mp4 demo.cast
#
set -euo pipefail

if [ $# -lt 3 ]; then
  echo "Usage: $0 <tag> <release-name> <file1> [file2 ...]"
  exit 1
fi

TAG="$1"
RELEASE_NAME="$2"
shift 2
FILES=("$@")

# Create a draft release (if exists, reuse)
if gh release view "$TAG" >/dev/null 2>&1; then
  echo "[upload] Release $TAG already exists; updating assets."
else
  echo "[upload] Creating release $TAG"
  gh release create "$TAG" --title "$RELEASE_NAME" --notes "Demo artifacts (auto-upload) - $(date -u +%Y-%m-%d)" || true
fi

for f in "${FILES[@]}"; do
  if [ -f "$f" ]; then
    echo "[upload] Uploading $f to release $TAG..."
    gh release upload "$TAG" "$f" --clobber
  else
    echo "[warning] File not found: $f"
  fi
done

echo "[upload] Done. Release URL:"
gh release view "$TAG" --web