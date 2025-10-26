# Demo Commands Quick Reference

## Pre-Recording Setup
```bash
# Open 3 terminals + browser
# Terminal 1: Main commands
# Terminal 2: Docker monitoring  
# Terminal 3: Browser (https://westend.subscan.io/)
```

## Demo Sequence (3-4 minutes)

### 1. Show Project Structure [0:15]
```bash
tree -L 3 -I 'node_modules|venv|__pycache__|.git'
```

### 2. Build Contract [0:30]
```bash
cd contracts/substrate-poc
cargo +nightly contract build
ls -la target/ink/
```

### 3. Run Quickstart [0:45]
```bash
cd ../..
bash scripts/quickstart.sh --headless
# Wait 2-3 minutes, show progress
```

### 4. Show Contract Address [2:30]
```bash
echo "Contract Address: $(cat /tmp/tidygen_contract_address.txt)"
# Copy address to clipboard
```

### 5. Submit Service Record [2:45]
```bash
cd apps/backend
CONTRACT_ADDR=$(cat /tmp/tidygen_contract_address.txt)
python manage.py demo_submit --contract $CONTRACT_ADDR --service-id 1 --payload "Cleaning service completed for Office Building A"
# Copy transaction hash from output
```

### 6. Show on Block Explorer [3:00]
- Go to https://westend.subscan.io/
- Paste transaction hash
- Show contract interaction and events

## Key Talking Points

- **Problem**: $400B cleaning industry trust issues
- **Solution**: Immutable service verification on Substrate
- **Speed**: Quick deployment and testing
- **Integration**: Seamless Django integration
- **Transparency**: On-chain verification

## Expected Outputs

**Contract Address:**
```
5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY
```

**Transaction Hash:**
```
0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
```

**Success Message:**
```
Transaction submitted successfully!
Extrinsic hash: 0x...
Service ID: 1
Payload: Cleaning service completed for Office Building A
Data hash: a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3
```

## Troubleshooting

**If quickstart fails:**
```bash
docker-compose -f scripts/docker-compose.quickstart.yml down
bash scripts/quickstart.sh --headless
```

**If Python fails:**
```bash
cd apps/backend
pip install substrate-interface
```

**If transaction not found:**
```bash
curl -H "Content-Type: application/json" -d '{"id":1, "jsonrpc":"2.0", "method": "system_health"}' http://127.0.0.1:9944
```
