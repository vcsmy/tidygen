# TidyGen Backend Services - Substrate Integration

## Overview

This module provides Django integration with the TidyGen Substrate blockchain node through Python services.

## SubstrateClient

A comprehensive Python client for interacting with Substrate pallets from Django.

### Features

- ✅ **Invoice Management**: Create and query invoices on-chain
- ✅ **DID Management**: Register and query decentralized identities  
- ✅ **DAO Governance**: Create proposals and cast votes
- ✅ **Retry Logic**: Automatic retry on connection failures
- ✅ **Error Handling**: Comprehensive exception handling
- ✅ **Connection Pooling**: Persistent WebSocket connection
- ✅ **Context Manager**: Automatic resource cleanup

## Installation

```bash
cd apps/backend
source venv/bin/activate
pip install substrate-interface
```

The package is now included in `requirements.txt`.

## Configuration

### Environment Variables

Add to your Django settings or `.env`:

```python
# Substrate Node Connection
SUBSTRATE_WS_URL = "ws://127.0.0.1:9944"
SUBSTRATE_SS58_FORMAT = 42
SUBSTRATE_KEYPAIR_URI = "//Alice"  # Default signing key
```

### Django Settings

```python
# backend/settings/base.py

SUBSTRATE_CONFIG = {
    'URL': env('SUBSTRATE_WS_URL', default='ws://127.0.0.1:9944'),
    'SS58_FORMAT': env.int('SUBSTRATE_SS58_FORMAT', default=42),
    'KEYPAIR_URI': env('SUBSTRATE_KEYPAIR_URI', default='//Alice'),
    'MAX_RETRIES': 3,
    'RETRY_DELAY': 1.0,
}
```

## Usage

### Basic Usage

```python
from services.substrate_client import SubstrateClient

# Initialize client
client = SubstrateClient(keypair_uri='//Alice')

# Get chain info
info = client.get_chain_info()
print(f"Connected to: {info['chain']}")

# Close when done
client.close()
```

### Context Manager

```python
from services.substrate_client import SubstrateClient

# Automatic connection cleanup
with SubstrateClient(keypair_uri='//Alice') as client:
    info = client.get_chain_info()
    print(f"Block: {info['block_number']}")
```

## Methods

### Invoice Management (pallet-ledger)

#### record_invoice()

Create an invoice on the blockchain.

```python
from services.substrate_client import SubstrateClient
from substrateinterface import Keypair

client = SubstrateClient()
alice = Keypair.create_from_uri('//Alice')

tx_hash, receipt = client.record_invoice(
    user_id=1,
    invoice_hash="invoice_hash_from_django",
    client_account="5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY",
    amount=1000000,  # Amount in smallest unit
    metadata="INV-2025-001|Client XYZ|Net 30",
    keypair=alice
)

print(f"Invoice recorded: {tx_hash}")
```

#### get_invoices()

Retrieve all invoices for an account.

```python
invoices = client.get_invoices("5GrwvaEF...")

for invoice in invoices:
    print(f"Invoice {invoice['id']}: ${invoice['amount']}")
    print(f"  Metadata: {invoice['metadata']}")
    print(f"  Hash: {invoice['invoice_hash']}")
```

#### get_invoice_by_hash()

Lookup invoice by SHA256 hash.

```python
invoice_id = client.get_invoice_by_hash("a1b2c3d4...")
print(f"Invoice ID: {invoice_id}")
```

### DID Management (pallet-did)

#### register_did()

Register a decentralized identity.

```python
tx_hash, receipt = client.register_did(
    user_id=1,
    account_id="5GrwvaEF...",
    public_key="0x04a1b2c3...",
    metadata={
        'username': 'alice',
        'email': 'alice@example.com',
        'role': 'employee'
    },
    keypair=alice_keypair
)

print(f"DID registered: {tx_hash}")
```

#### get_did()

Get DID document via RPC.

```python
did_doc = client.get_did("5GrwvaEF...")

if did_doc:
    print(f"Controller: {did_doc['controller']}")
    print(f"Status: {did_doc['status']}")
    print(f"Public Key: {did_doc['public_key']}")
    print(f"Metadata: {did_doc['metadata']}")
```

#### is_did_active()

Check if DID is active.

```python
is_active = client.is_did_active("5GrwvaEF...")
print(f"DID Active: {is_active}")
```

#### update_did()

Update DID document.

```python
tx_hash, receipt = client.update_did(
    account_id="5GrwvaEF...",
    public_key="0x04newkey...",  # Optional
    metadata={'updated': True},   # Optional
    keypair=alice_keypair
)
```

### DAO Governance (pallet-dao)

#### create_proposal()

Create a governance proposal.

```python
tx_hash, receipt = client.create_proposal(
    title="Approve Q4 Budget",
    description="Allocate $50,000 for Q4 operations",
    voting_period=100,  # 100 blocks
    keypair=alice_keypair
)

print(f"Proposal created: {tx_hash}")
```

#### vote_on_proposal()

Vote on a proposal.

```python
# Vote in favor
tx_hash, receipt = client.vote_on_proposal(
    proposal_id=0,
    in_favor=True,
    keypair=bob_keypair
)

# Vote against
tx_hash, receipt = client.vote_on_proposal(
    proposal_id=0,
    in_favor=False,
    keypair=charlie_keypair
)
```

#### get_proposal()

Query proposal details.

```python
proposal = client.get_proposal(proposal_id=0)

print(f"Title: {proposal['title']}")
print(f"Status: {proposal['status']}")
print(f"Votes: {proposal['votes_for']} for, {proposal['votes_against']} against")
print(f"Total: {proposal['total_votes']}")
```

#### execute_proposal()

Execute an approved proposal.

```python
tx_hash, receipt = client.execute_proposal(
    proposal_id=0,
    keypair=alice_keypair
)

print(f"Proposal executed: {tx_hash}")
```

## Django Integration Examples

### Invoice Creation Signal

```python
# apps/backend/apps/finance/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from services.substrate_client import SubstrateClient
from .models import Invoice

@receiver(post_save, sender=Invoice)
def anchor_invoice_to_blockchain(sender, instance, created, **kwargs):
    """Automatically anchor invoices to blockchain"""
    if created:
        try:
            client = SubstrateClient()
            
            # Get client wallet address
            client_wallet = instance.client.wallet_address
            if not client_wallet:
                return
            
            # Create invoice on blockchain
            tx_hash, receipt = client.record_invoice(
                user_id=instance.created_by.id if instance.created_by else 0,
                invoice_hash=instance.calculate_hash(),
                client_account=client_wallet,
                amount=int(instance.total_amount * 1000000),  # Convert to smallest unit
                metadata=f"{instance.invoice_number}|{instance.client.name}|{instance.payment_terms}"
            )
            
            # Update invoice with blockchain reference
            instance.blockchain_tx_hash = tx_hash
            instance.blockchain_anchored = True
            instance.save(update_fields=['blockchain_tx_hash', 'blockchain_anchored'])
            
            client.close()
            
        except Exception as e:
            logger.error(f"Failed to anchor invoice to blockchain: {e}")
```

### User DID Registration

```python
# apps/backend/apps/accounts/views.py

from rest_framework.decorators import action
from rest_framework.response import Response
from services.substrate_client import SubstrateClient

class UserViewSet(viewsets.ModelViewSet):
    
    @action(detail=True, methods=['post'])
    def register_blockchain_did(self, request, pk=None):
        """Register user's DID on blockchain"""
        user = self.get_object()
        
        if not user.wallet_address:
            return Response(
                {'error': 'User must have wallet address'},
                status=400
            )
        
        try:
            client = SubstrateClient()
            
            tx_hash, receipt = client.register_did(
                user_id=user.id,
                account_id=user.wallet_address,
                public_key=user.public_key or "0x04" + "00" * 32,
                metadata={
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            )
            
            # Update user
            user.did_registered = True
            user.did_tx_hash = tx_hash
            user.save()
            
            client.close()
            
            return Response({
                'success': True,
                'tx_hash': tx_hash,
                'block_hash': receipt['block_hash']
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=500
            )
```

### DAO Proposal Management

```python
# apps/backend/apps/web3/views.py

from rest_framework import viewsets
from services.substrate_client import SubstrateClient

class ProposalViewSet(viewsets.ModelViewSet):
    
    def create(self, request):
        """Create DAO proposal on blockchain"""
        title = request.data.get('title')
        description = request.data.get('description')
        voting_period = request.data.get('voting_period', 100)
        
        try:
            client = SubstrateClient()
            
            tx_hash, receipt = client.create_proposal(
                title=title,
                description=description,
                voting_period=voting_period
            )
            
            # Create Django record
            proposal = Proposal.objects.create(
                title=title,
                description=description,
                created_by=request.user,
                blockchain_tx_hash=tx_hash,
                voting_period_blocks=voting_period
            )
            
            client.close()
            
            return Response({
                'id': proposal.id,
                'tx_hash': tx_hash,
                'status': 'active'
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        """Vote on proposal"""
        proposal = self.get_object()
        in_favor = request.data.get('in_favor', True)
        
        try:
            client = SubstrateClient()
            
            # User's keypair (in production, get from secure storage)
            user_keypair = Keypair.create_from_uri(f'//{request.user.username}')
            
            tx_hash, receipt = client.vote_on_proposal(
                proposal_id=proposal.blockchain_proposal_id,
                in_favor=in_favor,
                keypair=user_keypair
            )
            
            # Record vote in Django
            Vote.objects.create(
                proposal=proposal,
                user=request.user,
                in_favor=in_favor,
                blockchain_tx_hash=tx_hash
            )
            
            # Sync proposal data from blockchain
            blockchain_proposal = client.get_proposal(proposal.blockchain_proposal_id)
            proposal.votes_for = blockchain_proposal['votes_for']
            proposal.votes_against = blockchain_proposal['votes_against']
            proposal.save()
            
            client.close()
            
            return Response({
                'tx_hash': tx_hash,
                'in_favor': in_favor
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)
```

## Testing

### Run Integration Tests

```bash
# Ensure Substrate node is running
cd apps/substrate
make run

# In another terminal, run tests
cd apps/backend
source venv/bin/activate
python services/test_substrate_client.py
```

### Individual Test Methods

```python
from services.test_substrate_client import *

# Test connection
test_connection()

# Test invoice
test_create_invoice()
test_get_invoices()

# Test DID
test_register_did()
test_get_did()

# Test DAO
test_create_dao_proposal()
test_vote_on_proposal()

# Complete workflow
test_comprehensive_workflow()
```

### Expected Output

```
==================================================================
 TidyGen Substrate Client - Integration Tests
==================================================================

TEST 1: Connection Test
✅ Connected to chain: tidygen-node
✅ Block number: 42
✅ Version: 1.0.0

TEST 2: Create Invoice
✅ Invoice created!
   Transaction Hash: 0x1234...
   Block Hash: 0x5678...
   Finalized: True

...

TEST SUMMARY
✅ PASS - Connection
✅ PASS - Create Invoice
✅ PASS - Get Invoices
✅ PASS - Register DID
✅ PASS - Get DID via RPC
✅ PASS - Create DAO Proposal
✅ PASS - Vote on Proposal
✅ PASS - Comprehensive Workflow

Results: 8/8 tests passed

🎉 All tests passed! Django-Substrate integration is working!
```

## Error Handling

### Connection Errors

```python
from services.substrate_client import SubstrateClient, SubstrateConnectionError

try:
    client = SubstrateClient(url="ws://invalid:9944")
except SubstrateConnectionError as e:
    print(f"Connection failed: {e}")
```

### Transaction Errors

```python
from services.substrate_client import SubstrateTransactionError

try:
    tx_hash, receipt = client.record_invoice(...)
except SubstrateTransactionError as e:
    print(f"Transaction failed: {e}")
```

### Retry Logic

The client automatically retries failed operations (default: 3 attempts with 1s delay):

```python
# Configure retry behavior
client = SubstrateClient(
    max_retries=5,
    retry_delay=2.0
)
```

## Advanced Usage

### Custom Keypairs

```python
from substrateinterface import Keypair

# From mnemonic
keypair = Keypair.create_from_mnemonic('your mnemonic phrase here')

# From URI
keypair = Keypair.create_from_uri('//Alice')

# Use with client
client.record_invoice(..., keypair=keypair)
```

### Batch Operations

```python
client = SubstrateClient()

# Create multiple invoices
invoices_data = [
    {'user_id': 1, 'client': 'Bob', 'amount': 1000},
    {'user_id': 2, 'client': 'Charlie', 'amount': 2000},
    {'user_id': 3, 'client': 'Dave', 'amount': 3000},
]

for data in invoices_data:
    tx_hash, _ = client.record_invoice(
        user_id=data['user_id'],
        invoice_hash=f"hash_{data['user_id']}",
        client_account=data['client'],
        amount=data['amount'],
        metadata=f"Invoice for user {data['user_id']}"
    )
    print(f"Created: {tx_hash}")

client.close()
```

### Query Chain State

```python
# Get current block
block_number = client.get_block_number()

# Get chain info
info = client.get_chain_info()
print(f"Chain: {info['chain']}")
print(f"Version: {info['version']}")
print(f"Block: {info['block_number']}")
```

## Django Management Command

Create a management command to sync blockchain data:

```python
# apps/backend/apps/ledger/management/commands/sync_blockchain.py

from django.core.management.base import BaseCommand
from services.substrate_client import SubstrateClient
from apps.finance.models import Invoice

class Command(BaseCommand):
    help = 'Sync invoices with blockchain'
    
    def handle(self, *args, **options):
        client = SubstrateClient()
        
        # Get all invoices that need blockchain anchoring
        invoices = Invoice.objects.filter(blockchain_anchored=False)
        
        for invoice in invoices:
            try:
                if not invoice.client.wallet_address:
                    continue
                
                tx_hash, _ = client.record_invoice(
                    user_id=invoice.created_by.id,
                    invoice_hash=invoice.calculate_hash(),
                    client_account=invoice.client.wallet_address,
                    amount=int(invoice.total_amount * 1000000),
                    metadata=f"{invoice.invoice_number}|{invoice.client.name}"
                )
                
                invoice.blockchain_tx_hash = tx_hash
                invoice.blockchain_anchored = True
                invoice.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f"Invoice {invoice.id} anchored: {tx_hash}")
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to anchor invoice {invoice.id}: {e}")
                )
        
        client.close()
        self.stdout.write(self.style.SUCCESS("Blockchain sync complete!"))
```

Run with:
```bash
python manage.py sync_blockchain
```

## API Reference

### SubstrateClient Class

```python
class SubstrateClient:
    def __init__(
        url: str = "ws://127.0.0.1:9944",
        ss58_format: int = 42,
        type_registry_preset: str = 'substrate-node-template',
        max_retries: int = 3,
        retry_delay: float = 1.0,
        keypair_uri: Optional[str] = None
    )
```

### Methods

| Method | Pallet | Type | Description |
|--------|--------|------|-------------|
| `record_invoice()` | Ledger | Write | Create invoice on-chain |
| `get_invoices()` | Ledger | Read | Query invoices |
| `get_invoice_by_hash()` | Ledger | Read | Lookup by hash |
| `register_did()` | Did | Write | Register DID |
| `get_did()` | Did | Read (RPC) | Query DID document |
| `is_did_active()` | Did | Read (RPC) | Check DID status |
| `update_did()` | Did | Write | Update DID |
| `create_proposal()` | Dao | Write | Create proposal |
| `vote_on_proposal()` | Dao | Write | Cast vote |
| `get_proposal()` | Dao | Read | Query proposal |
| `execute_proposal()` | Dao | Write | Execute proposal |

### Utility Methods

| Method | Description |
|--------|-------------|
| `get_block_number()` | Get current block number |
| `get_chain_info()` | Get chain information |
| `create_keypair()` | Create keypair from URI |
| `calculate_invoice_hash()` | Calculate invoice SHA256 hash |
| `close()` | Close connection |

## Performance Considerations

- **Connection Pooling**: Reuses WebSocket connection
- **Retry Logic**: Automatic retry on transient failures
- **Timeout Handling**: Configurable timeouts
- **Resource Cleanup**: Automatic connection closing

## Security Best Practices

1. **Keypair Management**: Store private keys securely
2. **Environment Variables**: Use env vars for sensitive config
3. **Error Logging**: Log errors without exposing secrets
4. **Connection Security**: Use WSS (wss://) in production
5. **Access Control**: Restrict who can sign transactions

## Troubleshooting

### Connection Refused

```bash
# Ensure Substrate node is running
cd apps/substrate
make run
```

### Import Errors

```bash
# Reinstall substrate-interface
pip install --upgrade substrate-interface
```

### Transaction Failures

```python
# Check logs
import logging
logging.basicConfig(level=logging.DEBUG)
```

## License

Apache-2.0

## Resources

- [substrate-interface Documentation](https://github.com/polkascan/py-substrate-interface)
- [Substrate Documentation](https://docs.substrate.io/)
- [TidyGen Substrate Pallets](../../substrate/README.md)

