```markdown
# Audit Request: TidyGen — Service Verification & Escrow Contracts

Purpose
- Request a focused security review of the escrow/dispute contract and build/deployment scripts used in the TidyGen Substrate POC.

Repository
- https://github.com/vcsmy/tidygen (branch: dev)

Scope (high priority)
1. contracts/escrow-sla/lib.rs
   - funds flow, escrow accounting, transfer logic, dispute handling, event emission.
2. contracts/substrate-poc (store/get minimal contract)
   - data anchoring correctness and event integrity.
3. CI build & release workflow (.github/workflows/build-and-release.yml)
   - artifact integrity, checksum generation, release process.
4. deploy scripts: apps/backend/substrate_poc/deploy_contract.py
   - transaction composition, error handling and private key usage.

Test vectors (required)
- Upload and instantiate the escrow contract, deposit escrow, open dispute, attempt release (should be blocked), resolve_dispute_release and confirm transfer.
- Stress test: repeated deposit + partial release flows.
- Boundary tests: zero‑value deposit, duplicate store attempts, malformed data hash sizes.

Deliverables requested
- Short report (markdown) listing critical, high, medium, low findings.
- Repro steps for each finding and recommended fixes.
- If critical issues are found, suggested mitigation steps (e.g., freeze multisig, disable release).
- Confirmation of test vectors executed and result.

Contact & access
- Maintainer: Vijay B. (vijay@tidygen-erp.com)
- Quickstart: `bash scripts/quickstart.sh --no-build` (needs release artifacts in contracts/*/target/ink or run CI to build).
- Note: All contracts are on test/dev network; do not use real funds.

Suggested auditor timeline: 1–2 weeks (initial report), 1 week re-review after fixes.
