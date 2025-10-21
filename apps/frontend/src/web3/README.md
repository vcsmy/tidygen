# TidyGen Web3 Frontend Integration

## Overview

Complete React/TypeScript integration with TidyGen Substrate blockchain using Polkadot.js.

## Features

- ✅ **Wallet Connection**: Connect to Polkadot.js browser extension
- ✅ **Account Management**: List and select user accounts
- ✅ **Invoice Submission**: Create invoices on blockchain
- ✅ **DID Registration**: Register decentralized identities
- ✅ **DAO Governance**: Create proposals and vote
- ✅ **Real-time Updates**: Subscribe to new blocks
- ✅ **UI Components**: Pre-built Tailwind components

## Installation

Packages are already installed:

```bash
npm install @polkadot/api @polkadot/extension-dapp @polkadot/util @polkadot/util-crypto
```

## Configuration

### Environment Variables

Create `.env.local` or use `.env.example`:

```env
# Substrate Blockchain Configuration
VITE_WS_ENDPOINT=ws://127.0.0.1:9944
VITE_APP_NAME=TidyGen ERP
```

## Core Utilities

### polkadotWallet.ts

Wallet connection and management utilities.

#### connectWallet()

```typescript
import { connectWallet } from '../web3/polkadotWallet';

const accounts = await connectWallet();
console.log(`Connected ${accounts.length} accounts`);
```

#### getAccounts()

```typescript
import { getAccounts } from '../web3/polkadotWallet';

const accounts = getAccounts();
accounts.forEach(account => {
  console.log(account.meta.name, account.address);
});
```

#### initializeApi()

```typescript
import { initializeApi } from '../web3/polkadotWallet';

const api = await initializeApi();
const chain = await api.rpc.system.chain();
```

### substrateTransactions.ts

Blockchain transaction utilities.

#### submitInvoice()

```typescript
import { submitInvoice } from '../web3/substrateTransactions';

const result = await submitInvoice(
  {
    client: '5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY',
    amount: 1000000,
    metadata: 'INV-2025-001|Client XYZ|Net 30'
  },
  account
);

if (result.success) {
  console.log('Invoice created:', result.txHash);
}
```

#### registerDID()

```typescript
import { registerDID } from '../web3/substrateTransactions';

const result = await registerDID(
  {
    accountId: account.address,
    publicKey: '0x04a1b2c3...',
    metadata: JSON.stringify({ email: 'user@example.com' })
  },
  account
);
```

#### createProposal()

```typescript
import { createProposal } from '../web3/substrateTransactions';

const result = await createProposal(
  {
    title: 'Approve Q4 Budget',
    description: 'Allocate $50,000 for Q4 operations',
    votingPeriod: 100
  },
  account
);
```

#### voteOnProposal()

```typescript
import { voteOnProposal } from '../web3/substrateTransactions';

// Vote yes
const result = await voteOnProposal(0, true, account);

// Vote no
const result = await voteOnProposal(0, false, account);
```

## UI Components

### WalletConnectButton

Pre-built button component for wallet connection.

```tsx
import { WalletConnectButton } from '../components/web3';

function MyComponent() {
  const handleAccountSelect = (account) => {
    console.log('Selected:', account.address);
  };

  return (
    <WalletConnectButton onAccountSelect={handleAccountSelect} />
  );
}
```

**Features:**
- Connects to Polkadot.js extension
- Shows connected accounts
- Account selection dropdown
- Disconnect option
- Responsive design

### InvoiceForm

Form component for creating blockchain invoices.

```tsx
import { InvoiceForm } from '../components/web3';

function MyComponent() {
  const handleSuccess = (txHash) => {
    console.log('Invoice submitted:', txHash);
  };

  return (
    <InvoiceForm
      selectedAccount={selectedAccount}
      onSuccess={handleSuccess}
    />
  );
}
```

**Features:**
- Client address input
- Amount input
- Invoice number
- Description textarea
- Blockchain submission
- Success/error handling

### DAOProposal

Component for DAO governance.

```tsx
import { DAOProposal } from '../components/web3';

function MyComponent() {
  return <DAOProposal selectedAccount={selectedAccount} />;
}
```

**Features:**
- Create proposal tab
- Vote on proposals tab
- Voting progress bars
- Status badges
- Real-time updates

## Demo Page

### BlockchainDemo

Complete demo page using all components.

```tsx
import { BlockchainDemo } from '../pages/BlockchainDemo';

// In your routes
<Route path="/blockchain-demo" element={<BlockchainDemo />} />
```

**Features:**
- Wallet connection
- Chain information display
- Invoice creation form
- DAO governance interface
- Live block number
- Connection status alerts

## Usage Examples

### Complete Workflow

```typescript
import {
  connectWallet,
  submitInvoice,
  registerDID,
  createProposal,
  voteOnProposal,
} from '../web3';

// 1. Connect wallet
const accounts = await connectWallet();
const account = accounts[0];

// 2. Submit invoice
const invoiceResult = await submitInvoice(
  {
    client: clientAddress,
    amount: 1000000,
    metadata: 'INV-2025-001|Client|Net 30'
  },
  account
);

// 3. Register DID
const didResult = await registerDID(
  {
    accountId: account.address,
    publicKey: '0x04...',
    metadata: JSON.stringify({ email: 'user@example.com' })
  },
  account
);

// 4. Create DAO proposal
const proposalResult = await createProposal(
  {
    title: 'Approve Invoice',
    description: 'Approve invoice INV-2025-001',
    votingPeriod: 100
  },
  account
);

// 5. Vote on proposal
const voteResult = await voteOnProposal(0, true, account);

console.log('All transactions completed successfully!');
```

### Query Blockchain State

```typescript
import { queryInvoices, queryDID, queryProposal } from '../web3';

// Query invoices
const invoices = await queryInvoices(accountAddress);
invoices.forEach(inv => {
  console.log(`Invoice ${inv.id}: ${inv.amount}`);
});

// Query DID via RPC
const didDoc = await queryDID(accountAddress);
console.log('DID Status:', didDoc.status);

// Query proposal
const proposal = await queryProposal(0);
console.log('Votes:', proposal.votesFor, 'for,', proposal.votesAgainst, 'against');
```

### Subscribe to Events

```typescript
import { subscribeToNewBlocks } from '../web3/polkadotWallet';

// Subscribe to new blocks
const unsubscribe = await subscribeToNewBlocks((blockNumber) => {
  console.log('New block:', blockNumber);
});

// Unsubscribe when done
unsubscribe();
```

## Integration with Django Backend

### Sync Blockchain Data

```typescript
// After blockchain transaction, sync with Django
async function createAndSyncInvoice(invoiceData) {
  // 1. Submit to blockchain
  const blockchainResult = await submitInvoice(invoiceData, account);
  
  if (!blockchainResult.success) {
    throw new Error('Blockchain submission failed');
  }
  
  // 2. Save to Django database
  const response = await fetch('/api/v1/finance/invoices/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ...invoiceData,
      blockchain_tx_hash: blockchainResult.txHash,
      blockchain_anchored: true,
    })
  });
  
  if (!response.ok) {
    throw new Error('Django save failed');
  }
  
  return await response.json();
}
```

## Troubleshooting

### Polkadot.js Extension Not Found

**Error:** "Polkadot.js extension not found"

**Solution:**
1. Install from https://polkadot.js.org/extension/
2. Create an account in the extension
3. Refresh the page

### Connection Failed

**Error:** "Substrate connection failed"

**Solution:**
1. Ensure Substrate node is running:
   ```bash
   cd apps/substrate
   make run
   ```
2. Verify endpoint: `ws://127.0.0.1:9944`
3. Check firewall settings

### Transaction Failed

**Error:** "Transaction failed"

**Solutions:**
- Ensure account has sufficient balance
- Check if account has permissions
- Verify pallet is correctly configured in runtime
- Check browser console for detailed errors

## Best Practices

### 1. Error Handling

```typescript
try {
  const result = await submitInvoice(data, account);
  
  if (!result.success) {
    toast.error('Transaction failed', {
      description: result.error
    });
    return;
  }
  
  toast.success('Success!');
} catch (error) {
  console.error('Error:', error);
  toast.error('Unexpected error');
}
```

### 2. Loading States

```typescript
const [isSubmitting, setIsSubmitting] = useState(false);

const handleSubmit = async () => {
  setIsSubmitting(true);
  try {
    await submitInvoice(...);
  } finally {
    setIsSubmitting(false);
  }
};
```

### 3. Account Validation

```typescript
if (!selectedAccount) {
  toast.error('Please connect your wallet first');
  return;
}
```

## TypeScript Types

```typescript
// Account type
import type { InjectedAccountWithMeta } from '@polkadot/extension-dapp/types';

// Transaction result
interface TransactionResult {
  success: boolean;
  txHash?: string;
  blockHash?: string;
  error?: string;
  events?: any[];
}

// Invoice data
interface InvoiceData {
  client: string;
  amount: number;
  metadata: string;
}

// DID data
interface DIDData {
  accountId: string;
  publicKey: string;
  metadata: string;
}

// Proposal data
interface ProposalData {
  title: string;
  description: string;
  votingPeriod?: number;
}
```

## File Structure

```
src/web3/
├── index.ts                      # Central exports
├── polkadotWallet.ts            # Wallet utilities
├── substrateTransactions.ts      # Transaction utilities
└── README.md                     # This file

src/components/web3/
├── index.ts                      # Component exports
├── WalletConnectButton.tsx      # Wallet connect UI
├── InvoiceForm.tsx              # Invoice creation UI
└── DAOProposal.tsx              # DAO governance UI

src/pages/
└── BlockchainDemo.tsx           # Complete demo page
```

## Running the Demo

### 1. Start Substrate Node

```bash
cd apps/substrate
make run
```

### 2. Start Django Backend

```bash
cd apps/backend
source venv/bin/activate
python manage.py runserver 0.0.0.0:8002
```

### 3. Start Frontend

```bash
cd apps/frontend
npm run dev
```

### 4. Access Demo

Navigate to: `http://localhost:5173/blockchain-demo`

### 5. Connect Wallet

Click "Connect Wallet" and authorize Polkadot.js extension

### 6. Interact

- Create invoices
- Register DIDs
- Create proposals
- Vote on proposals

## License

Apache-2.0

## Resources

- [Polkadot.js API](https://polkadot.js.org/docs/api/)
- [Polkadot.js Extension](https://polkadot.js.org/docs/extension/)
- [Substrate Documentation](https://docs.substrate.io/)

