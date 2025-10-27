# Audit Brief — TidyGen Service Verification + Escrow

Purpose
- Provide an audit scope and quick-entry guide for a security reviewer (contract & integration focus).
- Target: Level‑2 grant deliverable review (ink! contract + backend integration).

Repositories / paths (primary)
- Contract: `contracts/escrow-sla/` (lib.rs, Cargo.toml)
- Contract (baseline POC): `contracts/substrate-poc/` (lib.rs, Cargo.toml)
- Backend integration: `apps/backend/substrate_poc/` (deploy_contract.py, submit_service.py)
- Quickstart & CI: `scripts/quickstart.sh`, `scripts/docker-compose.quickstart.yml`, `.github/workflows/ci.yml`

Scope (recommended)
1. Core contract functionality (high priority)
   - store(), get(), update(), exists()
   - deposit_escrow(), release_escrow(), open_dispute(), resolve_dispute_release()
2. Funds flow & escrow handling
   - Verify transfer logic, balance accounting, overflow/underflow, and error handling.
3. Event emission & replayability
   - Ensure events are emitted correctly and contain sufficient data for off-chain indexing.
4. Access control & authorization
   - Owner-only functions and intended future governance paths.
5. Integration & scripts
   - deploy_contract.py and submit_service.py — key handling, signing, and error paths.
6. CI / automation
   - Reproducible build, artifact checks, and protected secrets.

Threat model highlights
- Theft of escrow funds via reentrancy or logic bug.
- Incorrect balance accounting leading to double-pay or loss.
- Unauthorized release of funds (insufficient RBAC).
- Malformed inputs causing panic/unexpected state.
- Backend scripts leaking secrets or signing with insecure keys.

Test vectors (examples to provide)
- Create service_id = 1; deposit escrow = 100; release_escrow to provider -> confirm balance zero and event.
- Attempt release_escrow when dispute open -> should fail.
- Attempt duplicate store(service_id) -> should return ServiceAlreadyExists.
- Submit large payloads and empty payloads (boundary tests).
- Simulate failing transfer (mock env error) and verify contract state remains consistent.

Files & artifacts to provide to auditor
- Compiled contract artifacts: `target/ink/*.contract`, `metadata.json`.
- Example quickstart logs with tx hashes and events.
- A small set of test keys & test accounts for dev chain (e.g., //Alice) and instructions to reproduce.
- CI run logs if available.

Deliverables expected from auditor
- A short report (markdown) enumerating:
  - Critical / High / Medium / Low findings with reproduction steps.
  - Recommended fixes and estimated effort.
  - Confirmation of test vectors run and results.
  - Any suggestions for on-chain governance / multisig designs.

Contact & access
- Maintainer: Vijay B. — vijay@tidygen-erp.com
- Repo: https://github.com/vjbollavarapu/tidygen
- Provide a reproducible quickstart link and sample tx hashes so auditor can focus.

Notes for auditor
- The POC uses ink! payable flows for escrow in `escrow-sla`. For payer safety, use testnet tokens only (Westend).
- Recommend focusing on escrow transfer and dispute logic for the first round. Subsequent iterations can include more formal verification for economic-critical paths.
```