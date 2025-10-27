# Service Verification + Escrow (ink!) - POC

This contract extends the Service Verification POC with a simple escrow and dispute primitive.

Features
- Store / get / update service verification data (hash).
- Deposit escrow (payable) for a service id.
- Release escrow to recipient by contract owner if no dispute exists.
- Open dispute to block automatic release.
- Resolve dispute via owner (or external governance later).

Build (local)
```bash
# Ensure Rust + nightly + cargo-contract are installed
cd contracts/escrow-sla
cargo +nightly contract build
```

Artifacts
- `target/ink/` contains `.wasm`, `metadata.json`, and `.contract` bundle.

Local quickstart
- Use repository quickstart script at `scripts/quickstart.sh` — it will build and deploy this contract if configured to use the escrow contract path.
- Alternatively deploy with `apps/backend/substrate_poc/deploy_contract.py`

Testing
- Unit tests: `cargo +nightly test`
- Run e2e (ink_e2e) with a contracts node if you want to exercise payable flows.

Notes & next steps
- Current dispute resolution is owner-driven — consider upgrading to multisig, DAO arbitration, or on-chain vote for production.
- For Level‑2 application keep payments on testnets (Westend). Do not use real funds in examples.
```