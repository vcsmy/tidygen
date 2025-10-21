# Smart Contract Demo

This document provides instructions for running a sample job verification → payment flow once smart contracts are integrated.

## Prerequisites

- MetaMask wallet installed and configured
- Testnet tokens (ETH, MATIC, or DOT) for gas fees
- TidyGen ERP application running locally
- Smart contracts deployed to testnet

## Demo Flow

### 1. Service Creation
```bash
# Create a new cleaning service
curl -X POST http://localhost:8000/api/services/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
    "provider": "0x8ba1f109551bD432803012645Hac136c",
    "service_type": "office_cleaning",
    "location": "0x1234567890abcdef",
    "amount": "100"
  }'
```

### 2. Smart Contract Deployment
```javascript
// Deploy service contract
const serviceContract = await deployServiceContract({
  client: "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
  provider: "0x8ba1f109551bD432803012645Hac136c",
  amount: "100000000000000000000", // 100 tokens in wei
  serviceType: "office_cleaning"
});
```

### 3. Service Verification
```javascript
// Provider marks service as completed
await serviceContract.markServiceCompleted({
  from: providerAddress,
  gas: 200000
});

// Client verifies service completion
const isCompleted = await serviceContract.isServiceCompleted();
console.log("Service completed:", isCompleted);
```

### 4. Automated Payment
```javascript
// Payment is automatically released upon verification
const paymentTx = await serviceContract.releasePayment({
  from: clientAddress,
  gas: 150000
});

console.log("Payment released:", paymentTx.transactionHash);
```

### 5. On-Chain Verification
```javascript
// Verify payment on blockchain
const paymentEvent = await serviceContract.getPastEvents('PaymentReleased', {
  fromBlock: 0,
  toBlock: 'latest'
});

console.log("Payment events:", paymentEvent);
```

## Expected Results

- ✅ Service contract deployed successfully
- ✅ Service marked as completed by provider
- ✅ Client verification completed
- ✅ Payment automatically released
- ✅ Transaction recorded on blockchain
- ✅ Audit trail created in TidyGen ERP

## Troubleshooting

### Common Issues
- **Gas estimation failed**: Increase gas limit or check network congestion
- **Transaction reverted**: Verify contract state and parameters
- **MetaMask connection**: Ensure wallet is connected to correct network
- **Insufficient funds**: Check wallet balance for gas fees

### Support
For issues with smart contract integration, please:
1. Check the [TidyGen ERP Documentation](../docs/)
2. Review [Web3 Technical Implementation](../docs/WEB3_TECHNICAL_IMPLEMENTATION.md)
3. Open an issue on [GitHub](https://github.com/tidygen-community/tidygen-community/issues)

## Next Steps

Once the demo is working:
1. Deploy to mainnet
2. Integrate with production TidyGen ERP
3. Add additional smart contract features
4. Implement cross-chain functionality
5. Add governance mechanisms

---

**Note**: This demo is for development and testing purposes only. Do not use mainnet tokens for testing.
