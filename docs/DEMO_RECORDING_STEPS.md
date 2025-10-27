```markdown
# Record Demo & Upload to GitHub — Quick Guide

Two options:
- Manual (best quality) — use OBS to record screen + audio and upload to YouTube (unlisted) or to GitHub Release.
- Automated (fast) — record terminal session with asciinema, optionally convert to mp4/gif, upload to GitHub Release.

Manual (recommended)
1. Prepare:
   - Start Docker Desktop on your Mac.
   - Ensure contracts/target/ink metadata & .contract exist OR build locally.
2. Recording:
   - Install OBS (https://obsproject.com) and configure a scene with two windows: Terminal and Browser.
   - Terminal: run `bash scripts/quickstart.sh --headless` (or run step-by-step commands).
   - Browser: open polkadot.js/apps -> Connect to `ws://127.0.0.1:9944`.
   - Record 3–4 minutes: intro, quickstart run (or prebuilt artifacts deploy), show extrinsic hash, show the event in polkadot.js.
3. Post-production:
   - Trim video, add captions if needed.
   - Export MP4 (H.264 baseline).
4. Upload:
   - Preferred: Upload to YouTube as Unlisted; paste link into README.md, PR body, and applications file.
   - Alternative: Use `scripts/upload_demo_release.sh <tag> "<title>" demo.mp4` to attach to a GitHub Release.

Automated terminal capture (fast)
1. Record terminal manually:
   - Install asciinema: `brew install asciinema` (macOS)
   - Run: `bash scripts/record_terminal_asciinema.sh --out docs/demo.cast`
   - While recording run: `bash scripts/quickstart.sh --headless`
   - Stop recording (Ctrl-D).
2. Convert:
   - Convert to GIF or MP4 using asciinema2gif or other tools (see asciinema docs).
   - If you cannot convert locally, upload the .cast file as a release asset.
3. Upload:
   - `bash scripts/upload_demo_release.sh v0.1.0 "Demo - quickstart" docs/demo.mp4 docs/demo.cast`

Notes & tips
- For Mac M1/M2, using docker-compose with platform override may be slower — allow extra time.
- For best reproducibility for reviewers, include the terminal log and the exact command lines you used.
- Prefer YouTube for large videos; use GitHub releases for logs and small artifacts.
```