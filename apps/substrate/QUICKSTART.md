# TidyGen Substrate - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Run Setup Script

```bash
cd apps/substrate
./setup.sh
```

This will:
- Install/update Rust toolchain
- Clone substrate-node-template
- Configure the workspace
- Build the node (15-30 minutes first time)

### Step 2: Start the Development Node

```bash
make run
```

Or manually:

```bash
./target/release/tidygen-node --dev --tmp
```

You should see:
```
🚀 TidyGen Substrate Node
WebSocket: ws://127.0.0.1:9944
HTTP RPC: http://127.0.0.1:9933
```

### Step 3: Connect with Polkadot.js Apps

1. Open https://polkadot.js.org/apps/
2. Click network selector (top left)
3. Select "Development" → "Local Node"
4. Verify endpoint: `ws://127.0.0.1:9944`
5. Click "Switch"

You're connected! 🎉

## 🔧 Custom Pallets Overview

### TidyGen Ledger

Create a ledger entry:

```javascript
// In Polkadot.js Apps → Developer → Extrinsics
api.tx.tidygenLedger.createLedgerEntry(
  "invoice",           // transaction_type
  "0x1234...",        // data_hash (32 bytes)
  1000000             // amount (optional)
)
```

Query ledger entries:

```javascript
// In Polkadot.js Apps → Developer → Chain State
api.query.tidygenLedger.ledgerEntries(0)  // entry_id
api.query.tidygenLedger.entryCount()
```

### TidyGen DID

Create a DID:

```javascript
// Coming soon - DID pallet implementation
api.tx.tidygenDid.createDid(
  "did:substrate:5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY",
  didDocument
)
```

### TidyGen DAO

Create a proposal:

```javascript
// Coming soon - DAO pallet implementation
api.tx.tidygenDao.createProposal(
  "Approve Q4 Budget",
  proposalDetails,
  votingPeriod
)
```

## 📊 Interacting from Python (Django Backend)

Install substrate-interface:

```bash
pip install substrate-interface
```

Create ledger entry from Python:

```python
from substrateinterface import SubstrateInterface, Keypair

# Connect to node
substrate = SubstrateInterface(
    url="ws://127.0.0.1:9944",
    ss58_format=42
)

# Create keypair
keypair = Keypair.create_from_uri('//Alice')

# Create ledger entry
call = substrate.compose_call(
    call_module='TidygenLedger',
    call_function='create_ledger_entry',
    call_params={
        'transaction_type': 'invoice',
        'data_hash': '0x' + '12' * 32,  # 32 bytes
        'amount': 1000000
    }
)

# Sign and submit
extrinsic = substrate.create_signed_extrinsic(call=call, keypair=keypair)
receipt = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)

print(f"Extrinsic sent: {receipt.extrinsic_hash}")
```

## 🧪 Running Tests

```bash
# All tests
make test

# Specific pallet
make test-ledger
make test-did
make test-dao

# With output
make test-verbose
```

## 🛠️ Development Workflow

### 1. Make Changes to Pallet

Edit `pallets/tidygen-ledger/src/lib.rs`

### 2. Check Compilation

```bash
make check
```

### 3. Run Tests

```bash
cargo test -p pallet-tidygen-ledger
```

### 4. Rebuild

```bash
make build
```

### 5. Restart Node

```bash
make purge  # Clear old data
make run    # Start fresh
```

## 📝 Common Commands

```bash
# Development
make build-dev      # Faster debug build
make run-debug      # Run with debug logging
make watch          # Auto-rebuild on changes

# Testing
make test           # All tests
make test-verbose   # With output
make clippy         # Linter
make fmt            # Format code

# Maintenance
make clean          # Clean artifacts
make purge          # Clear chain data
make update         # Update dependencies

# Documentation
make docs           # Generate docs
```

## 🐛 Troubleshooting

### Build Fails

```bash
# Clean and rebuild
make clean
make build
```

### Node Won't Start

```bash
# Purge old chain data
make purge
make run
```

### Can't Connect from Polkadot.js

- Check node is running: `ps aux | grep tidygen-node`
- Verify WebSocket: `ws://127.0.0.1:9944`
- Check firewall settings
- Try `make run-debug` for detailed logs

### Python Connection Issues

```bash
# Verify node is accessible
curl -H "Content-Type: application/json" \
     -d '{"id":1, "jsonrpc":"2.0", "method": "system_health"}' \
     http://127.0.0.1:9933
```

## 🎓 Learning Resources

- [Substrate Tutorial](https://docs.substrate.io/tutorials/)
- [Pallet Development](https://docs.substrate.io/reference/frame-pallets/)
- [Polkadot.js API](https://polkadot.js.org/docs/)
- [substrate-interface Python](https://github.com/polkascan/py-substrate-interface)

## 📞 Need Help?

- Check [IMPLEMENTATION_STATUS.md](./IMPLEMENTATION_STATUS.md)
- Read [README.md](./README.md)
- Review pallet code in `pallets/*/src/lib.rs`

## 🚀 Next Steps

1. ✅ Get the node running
2. 🔧 Explore custom pallets
3. 🧪 Run tests and experiment
4. 📝 Complete DID and DAO pallets
5. 🔗 Integrate with Django backend
6. 🎯 Deploy to testnet

---

**Happy Building! 🎉**

