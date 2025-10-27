# Grant Application: TidyGen Substrate POC — Service Verification (Level 2)

Project name: TidyGen Substrate POC — Service Verification
Team / applicant: Vijay B. (solo maintainer, GitHub: https://github.com/vjbollavarapu)
Level requested: 2
Total request: $25,000 USD
Timeline: 8–10 weeks (Milestone 1 + Milestone 2)

Short executive summary
- Deliver a reproducible Substrate POC for trustworthy service verification tailored to field service workflows. Deliverables: hardened ink! contract (service storage + event), backend integration (Django management command + Python SDK), one‑command quickstart (Docker), integration tests, demo video, and docs. Acceptance is verifiable (local quickstart + testnet txs + CI).

Why Polkadot/Kusama
- Substrate/ink! lets us anchor service proofs on a performant interoperable platform. The POC demonstrates how service events are stored on-chain with proof events, enabling cross‑parachain settlement & audit trails.

Milestones (concise, verifiable)

Milestone 1 — POC + Quickstart (4–6 weeks) — $12,500
Deliverables
- contracts/substrate-poc: ink! contract implementing store/get/update/exists + unit tests.
- apps/backend/substrate_poc: deploy_contract.py, submit_service.py and Django management command demo_submit.
- scripts/quickstart.sh + scripts/docker-compose.quickstart.yml: one-command local quickstart that builds, deploys and runs demo (prints extrinsic hash).
- tests/integration/test_substrate_poc_quickstart.py: integration test to run quickstart and assert extrinsic hash format.
- Demo video (2–4 minutes, unlisted).

Acceptance criteria
- Reviewer can run (local, Docker): bash scripts/quickstart.sh --headless and see an extrinsic hash (0x...). OR, run a provided deploy command and demo_submit and obtain a tx hash verifiable on Westend/Subscan or polkadot.js explorer.
- Unit tests pass locally: cargo +nightly test (contract) and pytest for backend test.
- Integration test passes when Docker is available (CI or workflow_dispatch).

Milestone 2 — Integration & Documentation (4 weeks) — $12,500
Deliverables
- Python SDK (packages/py-sdk) and JS SDK (packages/js-sdk) with examples (demo scripts).
- REST API endpoints (simple) for submit/get flows and OpenAPI docs.
- Benchmarks (docs/BENCHMARKS.md): latency & simple throughput tests and cost estimate on Westend.
- A short security checklist + plan for an external mini-audit (AUDIT_BRIEF.md).
- Pilot plan and pilot report template (docs/PILOT_PLAN.md).

Acceptance criteria
- SDK examples run end-to-end against the deployed contract and the REST API is functional (curl examples).
- Benchmarks published with CSV and short analysis.
- Security brief published and an external audit appointment scheduled (or a short external review report attached).
- Documentation and Quickstart allow a reviewer to reproduce the POC in ≤30 minutes (instructions validated).

Team & maintainer
- Solo maintainer: Vijay B. (GitHub: https://github.com/vjbollavarapu). Full‑time on project. Will contract Substrate specialist for pallet/runtime work as needed (budgeted in subsequent milestones).

Open-source & licensing
- Community edition: MIT (repo LICENSE). All grant-scoped code will be open‑sourced.
- Commercial multi‑tenant product will be separate; core grant code remains public.

KYC & legal
- Prepared to complete W3F KYC/KYB and sign the CLA.

Quick verification checklist for reviewers
- Clone repo and checkout the PR branch.
- Build & run (Docker must be running):
  - bash scripts/quickstart.sh --headless
  - Expected: prints extrinsic hash (0x...)
- Alternatively:
  - cd contracts/substrate-poc && cargo +nightly contract build
  - cd apps/backend && python deploy/submit helpers (see README)
  - pytest tests/integration/test_substrate_poc_quickstart.py -q

Notes
- If requested, we will schedule Office Hours for a live walkthrough. Demo video and sample testnet tx hashes are included in the PR.
```