# Service Verification POC - ink! Smart Contract

A minimal proof-of-concept ink! smart contract for storing and retrieving service verification records on Substrate.

## Overview

This contract provides basic functionality to:

- Store service verification data hashes mapped by service ID
- Retrieve stored verification data
- Update existing verification records
- Check if a service verification record exists
- Emit events when data is stored

## Contract Interface

### Storage

- `service_data`: Mapping from `u64` (service_id) → `Vec<u8>` (verification data hash)

### Methods

- `store(service_id: u64, data_hash: Vec<u8>) -> Result<(), Error>` - Store a new verification record
- `get(service_id: u64) -> Option<Vec<u8>>` - Retrieve verification data by service ID
- `update(service_id: u64, data_hash: Vec<u8>) -> Result<(), Error>` - Update existing verification record
- `exists(service_id: u64) -> bool` - Check if a service verification record exists

### Events

- `ServiceStored(service_id: u64, caller: AccountId)` - Emitted when a verification record is stored

## Prerequisites

- Rust toolchain with nightly support
- `cargo-contract` CLI tool
- Substrate Contracts Node (for local testing)

### Installation

```bash
# Install Rust (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# Install cargo-contract
cargo install cargo-contract --force

# Install substrate-contracts-node (for local testing)
cargo install contracts-node --git https://github.com/paritytech/substrate-contracts-node.git --tag latest
```

## Building the Contract

```bash
# Navigate to the contract directory
cd contracts/substrate-poc

# Build the contract
cargo +nightly contract build

# Or alternatively
cargo contract build
```

This will generate:

- `target/ink/service_verification_poc.wasm` - The compiled contract
- `target/ink/service_verification_poc.json` - Contract metadata
- `target/ink/service_verification_poc.contract` - Bundle for deployment

## Running Tests

```bash
# Run unit tests
cargo +nightly test

# Run e2e tests (requires substrate-contracts-node)
cargo +nightly test --features e2e-tests
```

## Local Deployment

### 1. Start Local Substrate Node

```bash
# Start substrate-contracts-node
substrate-contracts-node --dev
```

The node will be available at `ws://127.0.0.1:9944`

### 2. Deploy Contract

Using the [Contracts UI](https://contracts-ui.substrate.io/):

1. Open https://contracts-ui.substrate.io/
2. Connect to `ws://127.0.0.1:9944`
3. Upload the contract bundle (`target/ink/service_verification_poc.contract`)
4. Deploy the contract

### 3. Interact with Contract

Example contract calls:

```javascript
// Store verification data
await contract.tx.store(1, "0x1234567890abcdef");

// Retrieve verification data
const result = await contract.query.get(1);

// Check if service exists
const exists = await contract.query.exists(1);
```

## Contract Usage Example

```rust
// Store a verification record
let service_id = 1u64;
let data_hash = b"verification_data_hash".to_vec();
contract.store(service_id, data_hash)?;

// Retrieve the verification record
let retrieved_data = contract.get(service_id);
assert_eq!(retrieved_data, Some(b"verification_data_hash".to_vec()));

// Update the verification record
let new_data = b"updated_verification_data".to_vec();
contract.update(service_id, new_data)?;

// Check if service exists
let exists = contract.exists(service_id);
assert!(exists);
```

## Error Handling

The contract defines the following error types:

- `ServiceAlreadyExists` - Attempted to store data for an existing service ID
- `ServiceNotFound` - Attempted to update a non-existent service ID
- `InvalidData` - Provided empty or invalid data

## Development Notes

- This is a minimal POC designed for testnet/local development
- The contract uses `Vec<u8>` for data storage (can be changed to `Hash` if needed)
- Events are emitted for all storage operations
- The contract includes comprehensive unit tests
- Gas optimization is not a primary concern in this POC

## File Structure

```text
contracts/substrate-poc/
├── Cargo.toml          # Dependencies and build configuration
├── lib.rs              # Main contract implementation
└── README.md           # This file
```

## Next Steps

For production use, consider:

- Adding access control/authorization
- Implementing data validation
- Adding more sophisticated error handling
- Gas optimization
- Integration with the main TidyGen application
