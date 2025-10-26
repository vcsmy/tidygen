# TidyGen Substrate POC - Web3-Enabled Service Verification

## Overview
Proof-of-concept for Web3-enabled service verification in the $400B cleaning services industry using ink! smart contracts on Substrate. Addresses trust issues through immutable, transparent service records.

## Quick Verification Checklist

### ✅ Review Requirements
- [ ] **Quickstart Demo**: [Run `bash scripts/quickstart.sh --headless`](https://github.com/tidygen-community/tidygen-community#quick-start)
- [ ] **Demo Video**: [3-minute demo video](https://youtu.be/[VIDEO_ID]) showing complete workflow
- [ ] **Transaction Hash**: Expected pattern `0x[0-9a-f]{64}` (e.g., `0x1234567890abcdef...`)
- [ ] **CI Status**: [GitHub Actions](https://github.com/tidygen-community/tidygen-community/actions) - Unit tests passing
- [ ] **Open Source**: All code will be MIT licensed and open-sourced upon approval

### 🔧 Quick Test (2 minutes)
```bash
git clone https://github.com/tidygen-community/tidygen-community.git
cd tidygen-community
bash scripts/quickstart.sh --headless
cd apps/backend
CONTRACT_ADDR=$(cat /tmp/tidygen_contract_address.txt)
python manage.py demo_submit --contract $CONTRACT_ADDR --service-id 1 --payload "demo"
```

**Expected Output:**
```
Transaction submitted successfully!
Extrinsic hash: 0x1234567890abcdef...
Service ID: 1
Payload: demo
```

## Key Artifacts
- **Smart Contract**: [`contracts/substrate-poc/`](https://github.com/tidygen-community/tidygen-community/tree/main/contracts/substrate-poc)
- **Python Integration**: [`apps/backend/substrate_poc/`](https://github.com/tidygen-community/tidygen-community/tree/main/apps/backend/substrate_poc)
- **Deployment**: [`scripts/quickstart.sh`](https://github.com/tidygen-community/tidygen-community/blob/main/scripts/quickstart.sh)
- **Tests**: [`tests/integration/test_substrate_poc_quickstart.py`](https://github.com/tidygen-community/tidygen-community/blob/main/tests/integration/test_substrate_poc_quickstart.py)

## Team
**Vijay Babu Bollavarapu** - [@vijayababubollavarapu](https://github.com/vijayababubollavarapu)
- 8+ years full-stack, 4+ years Web3 development
- Previous: Enterprise ERP systems, Web3 applications

## Budget
- **Total Request**: $25,000 USD
- **Timeline**: 8 weeks (2 milestones)
- **License**: MIT (open source)

**Ready for Review** ✅
