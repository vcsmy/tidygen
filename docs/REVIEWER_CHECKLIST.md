```markdown
Reviewer Quick Verification Checklist (Level 2)

1) Clone & checkout
- git clone https://github.com/vjbollavarapu/tidygen.git
- git checkout feat/substrate-poc

2) Quickstart (preferred)
- Ensure Docker is running.
- bash scripts/quickstart.sh --headless
- Expect output: "Contract deployed at: <address>" and "Extrinsic hash: 0x..."
  - Copy the extrinsic hash and open polkadot.js/apps connected to ws://127.0.0.1:9944 to inspect events.

3) Manual build & run (alternative)
- cd contracts/substrate-poc
- cargo +nightly contract build
- cd apps/backend
- python -m venv venv && source venv/bin/activate
- pip install -r requirements-dev.txt
- python apps/backend/substrate_poc/deploy_contract.py --wasm ../contracts/substrate-poc/target/ink/<contract>.wasm --metadata ../contracts/substrate-poc/target/ink/metadata.json
- python manage.py demo_submit --contract <address> --service-id 1 --payload "demo"

4) Tests
- pytest tests/integration/test_substrate_poc_quickstart.py -q
- Unit tests for contract:
  - cd contracts/substrate-poc
  - cargo +nightly test

5) CI
- .github/workflows/ci.yml runs unit tests on push/PR (integration triggered via workflow_dispatch).

If anything fails, collect the quickstart log (scripts/logs/quickstart-<timestamp>.log) and attach to PR comments.
```