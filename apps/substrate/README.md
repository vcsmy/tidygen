# TidyGen Substrate Node

A Substrate-based blockchain node for TidyGen ERP system with custom pallets for enterprise resource planning on-chain.

## Features

This Substrate node includes three custom pallets:

- **pallet-tidygen-ledger**: ERP invoice and transaction ledger on-chain
- **pallet-tidygen-did**: Decentralized identity management for users and organizations
- **pallet-tidygen-dao**: On-chain governance for business decision-making

## Prerequisites

- Rust toolchain (stable, nightly for benchmarking)
- Substrate development environment
- Make

### Install Rust

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup default stable
rustup update
rustup update nightly
rustup target add wasm32-unknown-unknown --toolchain nightly
```

## Build

Build the node in release mode:

```bash
make build
```

Or manually:

```bash
cargo build --release
```

## Run

Start a development node:

```bash
make run
```

Or manually:

```bash
./target/release/tidygen-node --dev
```

The node will be available at:
- WebSocket: `ws://127.0.0.1:9944`
- HTTP RPC: `http://127.0.0.1:9933`

## Test

Run all tests:

```bash
make test
```

Or manually:

```bash
cargo test --all
```

## Connect with Polkadot.js Apps

1. Open [Polkadot.js Apps](https://polkadot.js.org/apps/)
2. Click on the network selector (top left)
3. Select "Development" -> "Local Node"
4. Ensure the endpoint is `ws://127.0.0.1:9944`
5. Click "Switch"

## Custom Pallets

### TidyGen Ledger Pallet

Manages on-chain ledger entries for invoices and transactions.

**Extrinsics:**
- `create_ledger_entry`: Create a new ledger entry
- `update_ledger_status`: Update entry status
- `anchor_transaction`: Anchor transaction hash on-chain

**Storage:**
- `LedgerEntries`: Map of entry ID to ledger data
- `TransactionAnchors`: Map of transaction hash to block data

### TidyGen DID Pallet

Decentralized identity management for users and organizations.

**Extrinsics:**
- `create_did`: Create a new DID document
- `update_did`: Update DID document
- `revoke_did`: Revoke a DID
- `add_verification_method`: Add verification method to DID

**Storage:**
- `DIDDocuments`: Map of DID to document data
- `VerificationMethods`: Map of DID to verification methods

### TidyGen DAO Pallet

On-chain governance for business proposals and voting.

**Extrinsics:**
- `create_proposal`: Create a new proposal
- `vote`: Vote on a proposal
- `execute_proposal`: Execute approved proposal
- `close_proposal`: Close a proposal

**Storage:**
- `Proposals`: Map of proposal ID to proposal data
- `Votes`: Map of (proposal ID, voter) to vote data
- `ProposalCount`: Total number of proposals

## Integration with Django Backend

The Django backend in `apps/backend` connects to this Substrate node via:

1. **WebSocket RPC**: `ws://127.0.0.1:9944`
2. **substrate-interface** Python library
3. Ledger service in `apps/backend/apps/ledger/`

## Development

### Adding a New Pallet

1. Create pallet directory: `pallets/new-pallet`
2. Add to workspace members in root `Cargo.toml`
3. Implement pallet in `pallets/new-pallet/src/lib.rs`
4. Add to runtime in `runtime/src/lib.rs`

### Running Benchmarks

```bash
cargo build --release --features runtime-benchmarks
./target/release/tidygen-node benchmark pallet \
    --pallet=pallet_tidygen_ledger \
    --extrinsic='*' \
    --steps=50 \
    --repeat=20 \
    --output=./pallets/tidygen-ledger/src/weights.rs
```

## Architecture

```
apps/substrate/
├── node/              # Node implementation (client, RPC, CLI)
├── runtime/           # Runtime logic and pallet configuration
├── pallets/           # Custom pallets
│   ├── tidygen-ledger/
│   ├── tidygen-did/
│   └── tidygen-dao/
├── Cargo.toml         # Workspace configuration
├── Makefile           # Build automation
└── README.md          # This file
```

## License

Apache-2.0

## Resources

- [Substrate Documentation](https://docs.substrate.io/)
- [Polkadot Documentation](https://wiki.polkadot.network/)
- [TidyGen Documentation](../../README.md)

