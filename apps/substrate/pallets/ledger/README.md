# ERP Ledger Pallet

A comprehensive Substrate pallet for managing ERP invoices with SHA256 hashing for Django integration.

## Overview

This pallet provides on-chain invoice management with automatic SHA256 hashing to create verifiable links between blockchain records and Django database entries.

## Features

- ✅ **Invoice Creation**: Create invoices with automatic hash generation
- ✅ **SHA256 Hashing**: Link blockchain invoices with Django records
- ✅ **Client-based Storage**: Invoices organized by client AccountId
- ✅ **Invoice Retrieval**: Query invoices by client or hash
- ✅ **Event Emission**: Track all invoice operations
- ✅ **Comprehensive Tests**: 11 test cases covering all functionality

## Data Structure

### Invoice

```rust
struct Invoice {
    id: u64,                          // Unique invoice ID
    client: AccountId,                // Client account
    amount: Balance,                  // Invoice amount
    metadata: BoundedVec<u8>,         // Invoice details (JSON, invoice number, etc.)
    timestamp: BlockNumber,           // Creation block number
    invoice_hash: [u8; 32],          // SHA256 hash for Django linking
    created_by: AccountId,            // Invoice creator
}
```

## Storage

- `Invoices`: Map of `AccountId => Vec<Invoice>` - All invoices per client
- `InvoiceCount`: Global counter for unique invoice IDs
- `InvoiceByHash`: Map of `Hash => InvoiceId` - Quick hash lookup

## Extrinsics

### create_invoice

Create a new invoice with automatic SHA256 hashing.

```rust
create_invoice(
    origin: OriginFor<T>,
    client: T::AccountId,
    amount: BalanceOf<T>,
    metadata: Vec<u8>
) -> DispatchResult
```

**Parameters:**
- `origin`: Transaction signer (invoice creator)
- `client`: Client account ID
- `amount`: Invoice amount
- `metadata`: Invoice metadata (invoice number, description, JSON data)

**Example:**
```rust
// From Substrate
api.tx.ledger.createInvoice(
    clientAccount,
    1000000,
    "INV-2025-001|Client XYZ|Net 30"
)

// From Python (Django integration)
from substrateinterface import SubstrateInterface, Keypair

substrate = SubstrateInterface(url="ws://127.0.0.1:9944")
keypair = Keypair.create_from_uri('//Alice')

call = substrate.compose_call(
    call_module='Ledger',
    call_function='create_invoice',
    call_params={
        'client': client_account_id,
        'amount': 1000000,
        'metadata': 'INV-2025-001|Client XYZ|Net 30'
    }
)

extrinsic = substrate.create_signed_extrinsic(call=call, keypair=keypair)
receipt = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)
```

### get_invoices

Retrieve all invoices for a specific client (emits event for tracking).

```rust
get_invoices(
    origin: OriginFor<T>,
    client: T::AccountId
) -> DispatchResult
```

**Note:** For actual queries, use RPC calls instead of this extrinsic.

## Events

### InvoiceCreated

Emitted when a new invoice is created.

```rust
InvoiceCreated {
    invoice_id: u64,
    client: AccountId,
    amount: Balance,
    invoice_hash: [u8; 32],
    created_by: AccountId,
}
```

### InvoiceRetrieved

Emitted when invoices are retrieved.

```rust
InvoiceRetrieved {
    client: AccountId,
    count: u32,
}
```

### InvoiceHashStored

Emitted when invoice hash mapping is stored.

```rust
InvoiceHashStored {
    invoice_hash: [u8; 32],
    invoice_id: u64,
}
```

## Helper Functions (for RPC)

### get_invoice_by_hash

Lookup invoice ID by its SHA256 hash.

```rust
pub fn get_invoice_by_hash(hash: [u8; 32]) -> Option<u64>
```

### get_client_invoices

Get all invoices for a client.

```rust
pub fn get_client_invoices(client: &T::AccountId) -> Vec<Invoice<T>>
```

### verify_invoice_hash

Verify invoice hash matches stored data (for Django verification).

```rust
pub fn verify_invoice_hash(client: &T::AccountId, invoice_id: u64) -> bool
```

## SHA256 Hashing for Django Integration

The pallet automatically calculates SHA256 hashes of invoice data to create verifiable links with Django records.

### Hash Calculation

The hash includes:
1. Invoice ID (u64)
2. Client Account ID
3. Amount
4. Metadata
5. Timestamp (Block Number)

### Django Integration Workflow

#### 1. Create Invoice in Django

```python
# Django - apps/backend/apps/finance/views.py
from apps.ledger.services.blockchain_service import SubstrateBlockchainService

# Create invoice in Django
invoice = Invoice.objects.create(
    client=client,
    amount=1000,
    invoice_number="INV-2025-001",
    # ... other fields
)

# Submit to blockchain
blockchain = SubstrateBlockchainService()
metadata = f"{invoice.invoice_number}|{client.name}|{invoice.payment_terms}"

tx_hash = blockchain.create_invoice(
    client_account_id=client.wallet_address,
    amount=invoice.amount * 1000000,  # Convert to smallest unit
    metadata=metadata
)

# Store blockchain reference
invoice.blockchain_tx_hash = tx_hash
invoice.blockchain_anchored = True
invoice.save()
```

#### 2. Verify Invoice from Blockchain

```python
# Django - Verification
def verify_blockchain_invoice(invoice_id):
    invoice = Invoice.objects.get(id=invoice_id)
    blockchain = SubstrateBlockchainService()
    
    # Query blockchain
    result = blockchain.substrate.query(
        module='Ledger',
        storage_function='Invoices',
        params=[invoice.client.wallet_address]
    )
    
    # Find matching invoice by hash
    for chain_invoice in result:
        if chain_invoice['id'] == invoice.blockchain_invoice_id:
            # Verify hash matches
            is_valid = blockchain.verify_invoice_hash(
                client=invoice.client.wallet_address,
                invoice_id=invoice.blockchain_invoice_id
            )
            return is_valid
    
    return False
```

## Tests

The pallet includes 11 comprehensive test cases:

1. ✅ `create_invoice_works` - Basic invoice creation
2. ✅ `create_multiple_invoices_works` - Multiple invoices per client
3. ✅ `multiple_clients_work` - Multiple clients support
4. ✅ `get_invoices_works` - Invoice retrieval
5. ✅ `invoice_hash_is_unique` - Hash uniqueness
6. ✅ `verify_invoice_hash_works` - Hash verification
7. ✅ `metadata_too_long_fails` - Metadata length validation
8. ✅ `invoice_hash_lookup_works` - Hash-based lookup
9. ✅ `events_are_emitted` - Event emission
10. ✅ Additional edge cases

### Running Tests

```bash
# Test this pallet only
cargo test -p pallet-ledger

# Test with output
cargo test -p pallet-ledger -- --nocapture

# Test specific function
cargo test -p pallet-ledger create_invoice_works
```

## Configuration

```rust
impl pallet_ledger::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type Currency = Balances;
    type MaxMetadataLength = ConstU32<1024>;
    type MaxInvoicesPerClient = ConstU32<1000>;
}
```

## Error Handling

- `TooManyInvoices` - Client has reached maximum invoices (1000 default)
- `MetadataTooLong` - Metadata exceeds 1024 bytes
- `InvoiceNotFound` - Invoice ID not found
- `InvalidInvoiceData` - Invoice data validation failed
- `ArithmeticOverflow` - Invoice counter overflow

## Integration Example

### Complete Django-to-Substrate Flow

```python
# apps/backend/apps/ledger/services/blockchain_service.py
from substrateinterface import SubstrateInterface, Keypair
import hashlib

class SubstrateBlockchainService:
    def __init__(self):
        self.substrate = SubstrateInterface(
            url="ws://127.0.0.1:9944",
            ss58_format=42
        )
        self.keypair = Keypair.create_from_uri('//Alice')  # Use actual key
    
    def create_invoice(self, client_account, amount, metadata):
        """Create invoice on Substrate blockchain"""
        call = self.substrate.compose_call(
            call_module='Ledger',
            call_function='create_invoice',
            call_params={
                'client': client_account,
                'amount': amount,
                'metadata': metadata
            }
        )
        
        extrinsic = self.substrate.create_signed_extrinsic(
            call=call,
            keypair=self.keypair
        )
        
        receipt = self.substrate.submit_extrinsic(
            extrinsic,
            wait_for_inclusion=True
        )
        
        return receipt.extrinsic_hash
    
    def get_client_invoices(self, client_account):
        """Get all invoices for a client"""
        result = self.substrate.query(
            module='Ledger',
            storage_function='Invoices',
            params=[client_account]
        )
        return result.value
    
    def verify_invoice_hash(self, client_account, invoice_id):
        """Verify invoice hash on blockchain"""
        # Query and verify
        invoices = self.get_client_invoices(client_account)
        for invoice in invoices:
            if invoice['id'] == invoice_id:
                # Recalculate hash and compare
                calculated_hash = self._calculate_invoice_hash(invoice)
                return calculated_hash == invoice['invoice_hash']
        return False
    
    def _calculate_invoice_hash(self, invoice):
        """Calculate SHA256 hash (same as pallet logic)"""
        data = b''
        data += invoice['id'].to_bytes(8, 'little')
        data += invoice['client'].encode()
        data += str(invoice['amount']).encode()
        data += invoice['metadata'].encode()
        data += str(invoice['timestamp']).encode()
        return hashlib.sha256(data).digest()
```

## Performance Considerations

- **Storage**: Invoices are bounded per client (max 1000)
- **Hashing**: SHA256 calculation is O(n) where n is data size
- **Lookup**: Hash-based lookup is O(1)
- **Iteration**: Getting all client invoices is O(n) where n is invoice count

## License

Apache-2.0

## Resources

- [Substrate Documentation](https://docs.substrate.io/)
- [Django Integration Guide](../../backend/apps/ledger/README.md)
- [TidyGen Documentation](../../../README.md)

