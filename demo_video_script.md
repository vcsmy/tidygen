# TidyGen Substrate POC Demo Video Script

**Duration:** ~3-4 minutes  
**Target:** W3F Grant Application Demo  
**Focus:** End-to-end service verification workflow  

## Pre-Recording Setup

### Terminal Setup
- Open 3 terminal windows:
  1. **Main Terminal**: For running commands
  2. **Docker Terminal**: For monitoring Docker containers
  3. **Browser**: For block explorer

### Browser Setup
- Open Subscan Westend: https://westend.subscan.io/
- Keep it ready in a tab

---

## Demo Script

### [0:00] Introduction
**Script:** "Welcome to the TidyGen Substrate POC demo. I'll show you how we've built a Web3-enabled service verification system using ink! smart contracts on Substrate. This addresses trust issues in the $400+ billion cleaning services industry."

**Visual:** Show project structure briefly
```bash
ls -la
```

### [0:15] Show Project Structure
**Script:** "Here's our project structure with the ink! contract, Python integration, and deployment scripts."

**Commands:**
```bash
tree -L 3 -I 'node_modules|venv|__pycache__|.git'
```

### [0:30] Build the Smart Contract
**Script:** "First, let's build our ink! smart contract for service verification."

**Commands:**
```bash
cd contracts/substrate-poc
cargo +nightly contract build
```

**Expected Output:** Show successful compilation with generated files
```bash
ls -la target/ink/
```

### [0:45] Start Quickstart Script
**Script:** "Now I'll run our automated quickstart script that starts a local Substrate node, deploys the contract, and sets up the integration."

**Commands:**
```bash
cd ../..
bash scripts/quickstart.sh --headless
```

**Note:** This will take 2-3 minutes. Show progress and explain what's happening:
- "Starting Substrate node with Docker..."
- "Building and deploying the contract..."
- "Setting up Python environment..."

### [2:30] Show Contract Deployment
**Script:** "The contract has been deployed! Let me show you the contract address."

**Commands:**
```bash
echo "Contract Address: $(cat /tmp/tidygen_contract_address.txt)"
```

**Visual:** Copy the contract address to clipboard and show it clearly

### [2:45] Run Demo Submission
**Script:** "Now let's submit a service verification record using our Django management command."

**Commands:**
```bash
cd apps/backend
CONTRACT_ADDR=$(cat /tmp/tidygen_contract_address.txt)
python manage.py demo_submit --contract $CONTRACT_ADDR --service-id 1 --payload "Cleaning service completed for Office Building A"
```

**Expected Output:** Show the transaction hash and copy it

### [3:00] Show Transaction Details
**Script:** "Perfect! We got a transaction hash. Let me show you this transaction on the block explorer."

**Commands:**
```bash
echo "Transaction Hash: [COPY THE HASH FROM OUTPUT]"
```

**Browser Action:**
1. Go to https://westend.subscan.io/
2. Paste the transaction hash in the search box
3. Show the transaction details
4. Point out the contract interaction and events

### [3:15] Show Contract Events
**Script:** "Here you can see the ServiceStored event emitted by our contract, proving that the service verification record was successfully stored on-chain."

**Visual:** Scroll through the transaction details showing:
- Contract address
- Method called (store)
- Events emitted
- Gas used

### [3:30] Wrap Up
**Script:** "This demonstrates how traditional ERP systems can be enhanced with Web3 capabilities. The service verification is now immutable, transparent, and verifiable by anyone. This is just the beginning of our vision for Web3-enabled enterprise systems."

**Commands:**
```bash
echo "Demo completed successfully!"
echo "Contract: $CONTRACT_ADDR"
echo "Transaction: [HASH]"
```

---

## Exact Commands for Recording

### Terminal 1 (Main Commands)
```bash
# Show project structure
tree -L 3 -I 'node_modules|venv|__pycache__|.git'

# Build contract
cd contracts/substrate-poc
cargo +nightly contract build
ls -la target/ink/

# Run quickstart
cd ../..
bash scripts/quickstart.sh --headless

# Show contract address
echo "Contract Address: $(cat /tmp/tidygen_contract_address.txt)"

# Run demo
cd apps/backend
CONTRACT_ADDR=$(cat /tmp/tidygen_contract_address.txt)
python manage.py demo_submit --contract $CONTRACT_ADDR --service-id 1 --payload "Cleaning service completed for Office Building A"

# Show transaction hash
echo "Transaction completed! Check the output above for the hash."
```

### Terminal 2 (Docker Monitoring)
```bash
# Monitor Docker containers
docker ps
docker logs tidygen-substrate-node --tail 20
```

### Terminal 3 (Browser Commands)
```bash
# Open browser to Subscan
open https://westend.subscan.io/
# Or for Linux:
# xdg-open https://westend.subscan.io/
```

---

## Recording Tips

### Screen Layout
- **Left Side (60%)**: Main terminal with commands
- **Right Side (40%)**: Browser with block explorer
- **Bottom**: Small terminal showing Docker logs

### Key Points to Emphasize
1. **Speed**: Quick deployment and testing
2. **Integration**: Seamless Django integration
3. **Transparency**: On-chain verification
4. **Usability**: Simple commands for complex operations

### Backup Plans
- If quickstart fails, show the manual steps
- If browser doesn't open, use curl to check transaction
- If contract deployment fails, show the error and retry

### Post-Recording
- Save the contract address and transaction hash
- Take screenshots of the block explorer
- Note any issues for the final video

---

## Expected Outputs

### Contract Address Format
```
Contract Address: 5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY
```

### Transaction Hash Format
```
Transaction submitted successfully!
Extrinsic hash: 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
Service ID: 1
Payload: Cleaning service completed for Office Building A
Data hash: a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3
```

### Block Explorer Verification
- Transaction shows contract interaction
- ServiceStored event is visible
- Method called: `store`
- Parameters: service_id=1, data_hash=[hash]

---

## Troubleshooting Commands

### If Quickstart Fails
```bash
# Check Docker
docker ps
docker-compose -f scripts/docker-compose.quickstart.yml down
bash scripts/quickstart.sh --headless
```

### If Contract Build Fails
```bash
# Check Rust installation
rustup show
cargo --version

# Try alternative build
cd contracts/substrate-poc
cargo +nightly contract build --release
```

### If Python Command Fails
```bash
# Check Python environment
cd apps/backend
python --version
pip list | grep substrate

# Install missing dependencies
pip install substrate-interface
```

### If Transaction Not Found
```bash
# Check if node is running
curl -H "Content-Type: application/json" -d '{"id":1, "jsonrpc":"2.0", "method": "system_health"}' http://127.0.0.1:9944

# Wait a bit and try again
sleep 10
```

---

**Total Recording Time:** 3-4 minutes  
**Preparation Time:** 5-10 minutes  
**Retake Buffer:** 2-3 attempts recommended
