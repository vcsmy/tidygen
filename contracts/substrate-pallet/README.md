# pallet-service-verification (FRAME v2) - scaffold

This is a scaffold for a Substrate runtime pallet that stores service verification data and supports an escrow mechanism.

Quick start
1. Add the pallet to a local node runtime (e.g., a development node runtime).
2. Build the node and run with `--dev`.
3. Interact using polkadot.js Apps or runtime RPC.

Notes
- This scaffold uses `ensure_root` for escrow release — replace with governance/multisig or on-chain voting for production.
- The pallet includes:
  - Storage: ServiceData, Escrow
  - Extrinsics: store, deposit_escrow, release_escrow
  - Events: ServiceStored, EscrowDeposited, EscrowReleased

Next steps to move toward production
- Add pallet weights and benchmarking (use `frame-benchmarking`).
- Implement access control (roles or pallet-specific permissions).
- Add offchain worker or indexing for notifications.
- Integrate with XCM for cross-chain forwarding of verification events.
```