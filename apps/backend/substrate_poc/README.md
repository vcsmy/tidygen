# Substrate POC Python Demo

A Python demo script for submitting service verification records to the ink! smart contract deployed on a local Substrate node.

## Overview

This demo script demonstrates how to interact with the service verification ink! contract using Python and the `py-substrate-interface` library. It allows you to submit service verification records by providing a service ID and payload, which gets hashed and stored on-chain.

## Prerequisites

### 1. Python Dependencies

Install the required Python packages:

```bash
pip install substrate-interface
```

### 2. Substrate Node

Make sure you have a local Substrate node running:

```bash
# Start substrate-contracts-node
substrate-contracts-node --dev
```

The node should be available at `ws://127.0.0.1:9944`

### 3. Deployed Contract

Deploy the service verification contract and note the contract address. You can use the [Contracts UI](https://contracts-ui.substrate.io/) to deploy the contract.

## Environment Variables

The script supports the following environment variables:

- `SUBSTRATE_WS` - Substrate WebSocket URL (default: `ws://127.0.0.1:9944`)
- `SUBSTRATE_SENDER_SEED` - Sender account seed (default: `//Alice` for local testing)

## Usage

### Basic Usage

```bash
python submit_service.py --contract <CONTRACT_ADDRESS> --service-id <SERVICE_ID> --payload "<PAYLOAD>"
```

### Example Commands

```bash
# Submit a service verification record
python submit_service.py --contract 5F... --service-id 1 --payload "demo"

# Use custom Substrate endpoint
python submit_service.py --contract 5F... --service-id 2 --payload "test data" --substrate-ws ws://localhost:9944

# Use custom sender account
python submit_service.py --contract 5F... --service-id 3 --payload "verification" --sender-seed "//Bob"
```

### Command Line Arguments

- `--contract` (required): Contract address (e.g., 5F...)
- `--service-id` (required): Service ID (integer)
- `--payload` (required): Payload string to hash and store
- `--substrate-ws` (optional): Substrate WebSocket URL
- `--sender-seed` (optional): Sender account seed

## How It Works

1. **Connection**: Connects to the local Substrate node via WebSocket
2. **Metadata Loading**: Loads the contract metadata from the compiled contract bundle
3. **Keypair Creation**: Creates a keypair from the provided seed
4. **Hash Computation**: Computes SHA256 hash of the provided payload
5. **Contract Call**: Calls the `store` method on the contract with service_id and data_hash
6. **Transaction Submission**: Submits the transaction and waits for inclusion
7. **Result**: Prints the extrinsic hash and transaction details

## Output

The script outputs:
- Transaction hash (extrinsic hash)
- Service ID
- Original payload
- Computed data hash (hex)

Example output:
```
Transaction submitted successfully!
Extrinsic hash: 0x1234567890abcdef...
Service ID: 1
Payload: demo
Data hash: a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3
```

## Error Handling

The script handles common errors:
- Missing contract metadata file
- Connection issues with Substrate node
- Transaction failures
- Invalid contract addresses

## File Structure

```text
apps/backend/substrate_poc/
├── submit_service.py    # Main demo script
└── README.md           # This documentation
```

## Integration with Contract

This script works with the service verification ink! contract located at `contracts/substrate-poc/`. The contract must be compiled and deployed before using this script.

The script expects the contract metadata to be available at:

`contracts/substrate-poc/target/ink/metadata.json`

## Development Notes

- This is a demo script for local testing
- Uses `//Alice` as the default sender for convenience
- The script computes SHA256 hash of the payload before storing
- Transaction waits for inclusion before returning
- Designed to work with the minimal ink! contract POC

## Troubleshooting

### Contract Metadata Not Found
Make sure the contract is compiled:
```bash
cd contracts/substrate-poc
cargo +nightly contract build
```

### Connection Issues
Verify the Substrate node is running:
```bash
# Check if node is running
curl -H "Content-Type: application/json" -d '{"id":1, "jsonrpc":"2.0", "method": "system_health"}' http://127.0.0.1:9944
```

### Transaction Failures
- Check if the contract address is correct
- Verify the sender account has sufficient balance
- Ensure the service ID doesn't already exist (if using the same contract instance)
