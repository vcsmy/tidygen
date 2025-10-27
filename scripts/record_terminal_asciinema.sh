#!/usr/bin/env bash
# Record a quick terminal demo of the quickstart using asciinema
# Requirements: asciinema (https://asciinema.org), ffmpeg (optional for mp4)
#
# Usage:
#   bash scripts/record_terminal_asciinema.sh --out demo.cast --mp4 demo.mp4
#
set -euo pipefail

OUT_CAST="demo.cast"
OUT_MP4=""
DURATION_LIMIT=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --out) OUT_CAST="$2"; shift 2 ;;
    --mp4) OUT_MP4="$2"; shift 2 ;;
    --limit) DURATION_LIMIT="$2"; shift 2 ;;
    -h|--help) echo "Usage: $0 [--out <cast>] [--mp4 <mp4>] [--limit <seconds>]"; exit 0 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

echo "[record] Starting asciinema recording to $OUT_CAST"
echo "When recording starts, run: bash scripts/quickstart.sh --headless"
echo "Press Ctrl-D when finished recording."

# Start recording (interactive)
asciinema rec "$OUT_CAST"

if [ -n "$OUT_MP4" ]; then
  if ! command -v asciinema2gif >/dev/null 2>&1 && ! command -v svg-term >/dev/null 2>&1; then
    echo "[warning] asciinema2gif/svg-term not installed. Attempting ffmpeg conversion via asciinema.org (requires upload)."
  fi
  # Option 1: convert using asciinema.org (upload) - warns user
  echo "[info] To convert locally to mp4, consider installing svg-term or asciinema2gif."
  echo "[info] If you want, upload to asciinema.org and then use asciinema2gif or download a PNG sequence and convert with ffmpeg."
fi

echo "[record] Recording saved to $OUT_CAST"