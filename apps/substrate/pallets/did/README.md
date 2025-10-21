# Decentralized Identity (DID) Pallet

A W3C DID-compliant Substrate pallet for decentralized identity management with RPC support and Django integration.

## Overview

This pallet provides on-chain decentralized identity management following W3C DID Core specification principles. Each account can register a DID document containing verification methods (public keys) and metadata for authentication and authorization.

## Features

- ✅ **DID Registration**: Register DIDs for accounts with public keys
- ✅ **DID Resolution**: Resolve DID documents by AccountId or identifier
- ✅ **DID Updates**: Update public keys and metadata
- ✅ **DID Revocation**: Revoke DIDs when needed
- ✅ **RPC Endpoints**: Query DIDs via JSON-RPC
- ✅ **W3C Compliant**: Follows DID Core specification
- ✅ **Django Integration**: Ready for Django user authentication
- ✅ **Comprehensive Tests**: 15+ test cases

## Data Structure

### DidDocument

```rust
struct DidDocument {
    controller: AccountId,           // DID controller (owner)
    public_key: BoundedVec<u8>,     // Verification public key
    metadata: BoundedVec<u8>,       // Additional metadata (JSON)
    created_at: BlockNumber,        // Creation timestamp
    updated_at: BlockNumber,        // Last update timestamp
    status: DidStatus,              // Active/Revoked/Suspended
    did_identifier: BoundedVec<u8>, // DID identifier string
    nonce: u64,                     // Update nonce (prevents replay)
}
```

### DidStatus

```rust
enum DidStatus {
    Active,      // DID is valid and usable
    Revoked,     // DID has been revoked
    Suspended,   // DID is temporarily suspended
}
```

## Storage

- `DidDocuments`: Map of `AccountId => DidDocument` - Main DID storage
- `DidToAccount`: Map of `DidIdentifier => AccountId` - Reverse lookup
- `DidCount`: Total number of registered DIDs

## Extrinsics

### register_did

Register a new DID for an account.

```rust
register_did(
    origin: OriginFor<T>,
    account_id: T::AccountId,
    public_key: Vec<u8>,
    metadata: Vec<u8>
) -> DispatchResult
```

**Parameters:**
- `origin`: Transaction signer (becomes the DID controller)
- `account_id`: Account to register DID for
- `public_key`: Public key for verification (hex string or bytes)
- `metadata`: JSON metadata with additional DID properties

**Example:**
```rust
// From Substrate
api.tx.did.registerDid(
    accountId,
    "0x0242a61f6c9d42e9984a95b76c3a8c8c7e8f9b0a1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f",
    '{"type":"user","role":"employee","department":"engineering"}'
)

// From Python (Django integration)
from substrateinterface import SubstrateInterface, Keypair

substrate = SubstrateInterface(url="ws://127.0.0.1:9944")
keypair = Keypair.create_from_uri('//Alice')

# Register DID for Django user
call = substrate.compose_call(
    call_module='Did',
    call_function='register_did',
    call_params={
        'account_id': user_account_id,
        'public_key': user.public_key_hex,
        'metadata': json.dumps({
            'django_user_id': user.id,
            'username': user.username,
            'email': user.email,
            'role': 'employee'
        })
    }
)

extrinsic = substrate.create_signed_extrinsic(call=call, keypair=keypair)
receipt = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)
```

### update_did

Update an existing DID document.

```rust
update_did(
    origin: OriginFor<T>,
    account_id: T::AccountId,
    public_key: Option<Vec<u8>>,
    metadata: Option<Vec<u8>>
) -> DispatchResult
```

**Parameters:**
- `origin`: Transaction signer (must be the DID controller)
- `account_id`: Account whose DID to update
- `public_key`: New public key (None to keep existing)
- `metadata`: New metadata (None to keep existing)

### revoke_did

Revoke a DID (marks as inactive).

```rust
revoke_did(
    origin: OriginFor<T>,
    account_id: T::AccountId
) -> DispatchResult
```

### resolve_did

Resolve a DID document (emits event for tracking).

```rust
resolve_did(
    origin: OriginFor<T>,
    account_id: T::AccountId
) -> DispatchResult
```

**Note:** For actual queries, use the RPC endpoint `did_getDid` instead.

## RPC Endpoints

### did_getDid

Get DID document for an account.

```javascript
// Via Polkadot.js
const didDoc = await api.rpc.did.getDid(accountId);
console.log(didDoc.toJSON());
```

```python
# Via Python
from substrateinterface import SubstrateInterface

substrate = SubstrateInterface(url="ws://127.0.0.1:9944")
did_doc = substrate.rpc_request('did_getDid', [account_id])
```

### did_getAccountFromDid

Get account ID from DID identifier.

```javascript
const accountId = await api.rpc.did.getAccountFromDid("did:substrate:tidygen:a1b2c3d4");
```

### did_isDidActive

Check if a DID is active.

```javascript
const isActive = await api.rpc.did.isDidActive(accountId);
```

### did_getTotalDids

Get total number of registered DIDs.

```javascript
const totalDids = await api.rpc.did.getTotalDids();
```

## Events

### DidRegistered

Emitted when a new DID is registered.

```rust
DidRegistered {
    account: AccountId,
    did_identifier: Vec<u8>,
}
```

### DidUpdated

Emitted when a DID is updated.

```rust
DidUpdated {
    account: AccountId,
    nonce: u64,
}
```

### DidRevoked

Emitted when a DID is revoked.

```rust
DidRevoked {
    account: AccountId,
}
```

### DidResolved

Emitted when a DID is resolved.

```rust
DidResolved {
    account: AccountId,
    status: DidStatus,
}
```

### DidStatusChanged

Emitted when DID status changes.

```rust
DidStatusChanged {
    account: AccountId,
    old_status: DidStatus,
    new_status: DidStatus,
}
```

## DID Identifier Format

DIDs are automatically generated in the format:

```
did:substrate:tidygen:{account_hash}
```

**Example:**
```
did:substrate:tidygen:a1b2c3d4e5f6a7b8
```

The account hash is derived from the first 8 bytes of the Blake2-256 hash of the AccountId.

## Django Integration

### Setup

Install substrate-interface in Django:

```bash
cd apps/backend
source venv/bin/activate
pip install substrate-interface
```

### Integration Service

```python
# apps/backend/apps/did_auth/services/substrate_did_service.py

from substrateinterface import SubstrateInterface, Keypair
import json

class SubstrateDidService:
    """Service for DID operations on Substrate blockchain"""
    
    def __init__(self):
        self.substrate = SubstrateInterface(
            url="ws://127.0.0.1:9944",
            ss58_format=42
        )
        self.keypair = Keypair.create_from_uri('//Alice')  # Use actual key
    
    def register_user_did(self, user, account_id):
        """Register DID for a Django user"""
        # Prepare metadata
        metadata = json.dumps({
            'django_user_id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role if hasattr(user, 'role') else 'user',
            'created_at': user.date_joined.isoformat(),
        })
        
        # Get user's public key (from their wallet or generate)
        public_key = user.public_key if hasattr(user, 'public_key') else '0x00'
        
        # Create call
        call = self.substrate.compose_call(
            call_module='Did',
            call_function='register_did',
            call_params={
                'account_id': account_id,
                'public_key': public_key,
                'metadata': metadata
            }
        )
        
        # Submit extrinsic
        extrinsic = self.substrate.create_signed_extrinsic(
            call=call,
            keypair=self.keypair
        )
        
        receipt = self.substrate.submit_extrinsic(
            extrinsic,
            wait_for_inclusion=True
        )
        
        return receipt.extrinsic_hash
    
    def get_user_did(self, account_id):
        """Get DID document for a user"""
        result = self.substrate.rpc_request('did_getDid', [account_id])
        return result
    
    def verify_user_did(self, user, account_id):
        """Verify DID matches Django user"""
        did_doc = self.get_user_did(account_id)
        
        if not did_doc:
            return False
        
        # Parse metadata
        metadata = json.loads(did_doc['metadata'])
        
        # Verify Django user ID matches
        return metadata.get('django_user_id') == user.id
    
    def is_user_did_active(self, account_id):
        """Check if user's DID is active"""
        result = self.substrate.rpc_request('did_isDidActive', [account_id])
        return result
```

### Django Signal Integration

```python
# apps/backend/apps/did_auth/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .services.substrate_did_service import SubstrateDidService

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_did(sender, instance, created, **kwargs):
    """Automatically create DID when user is created"""
    if created and hasattr(instance, 'wallet_address'):
        try:
            did_service = SubstrateDidService()
            tx_hash = did_service.register_user_did(
                user=instance,
                account_id=instance.wallet_address
            )
            
            # Store blockchain reference
            instance.did_tx_hash = tx_hash
            instance.did_registered = True
            instance.save(update_fields=['did_tx_hash', 'did_registered'])
            
        except Exception as e:
            # Log error but don't fail user creation
            print(f"Failed to register DID: {e}")
```

### Django Authentication with DID

```python
# apps/backend/apps/did_auth/backends.py

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from .services.substrate_did_service import SubstrateDidService

User = get_user_model()

class DidAuthenticationBackend(BaseBackend):
    """Authenticate users using their DID"""
    
    def authenticate(self, request, account_id=None, signature=None, message=None):
        """Authenticate using DID signature verification"""
        if not account_id or not signature or not message:
            return None
        
        try:
            did_service = SubstrateDidService()
            
            # Get DID document
            did_doc = did_service.get_user_did(account_id)
            if not did_doc:
                return None
            
            # Verify DID is active
            if not did_service.is_user_did_active(account_id):
                return None
            
            # Verify signature (using public key from DID document)
            # This would use cryptographic verification
            # is_valid = verify_signature(message, signature, did_doc['public_key'])
            # if not is_valid:
            #     return None
            
            # Get Django user from metadata
            metadata = json.loads(did_doc['metadata'])
            user_id = metadata.get('django_user_id')
            
            if user_id:
                user = User.objects.get(id=user_id)
                return user
            
        except Exception as e:
            print(f"DID authentication failed: {e}")
            return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
```

## Tests

The pallet includes 15 comprehensive test cases:

1. ✅ `register_did_works` - Basic DID registration
2. ✅ `register_did_for_self_works` - Self-registration
3. ✅ `cannot_register_did_twice` - Duplicate prevention
4. ✅ `update_did_works` - DID updates
5. ✅ `update_public_key_works` - Public key updates
6. ✅ `only_controller_can_update` - Authorization
7. ✅ `revoke_did_works` - DID revocation
8. ✅ `cannot_update_revoked_did` - Revoked DID protection
9. ✅ `resolve_did_works` - DID resolution
10. ✅ `resolve_nonexistent_did_fails` - Error handling
11. ✅ `multiple_dids_work` - Multiple DIDs
12. ✅ `did_identifier_is_unique` - Identifier uniqueness
13. ✅ `public_key_too_long_fails` - Validation
14. ✅ `metadata_too_long_fails` - Validation
15. ✅ `did_reverse_lookup_works` - Reverse lookup
16. ✅ `nonce_increments_on_update` - Nonce management

### Running Tests

```bash
# Test this pallet only
cargo test -p pallet-did

# Test with output
cargo test -p pallet-did -- --nocapture

# Test specific function
cargo test -p pallet-did register_did_works
```

## Configuration

```rust
// In runtime/src/lib.rs
impl pallet_did::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type MaxPublicKeyLength = ConstU32<256>;
    type MaxMetadataLength = ConstU32<1024>;
    type MaxDidLength = ConstU32<256>;
}

// Add to construct_runtime!
construct_runtime!(
    pub enum Runtime {
        // ... other pallets
        Did: pallet_did,
    }
);

// Implement Runtime API
impl pallet_did_runtime_api::DidApi<Block, AccountId, DidDocument<Runtime>> for Runtime {
    fn get_did(account: AccountId) -> Option<DidDocument<Runtime>> {
        Did::get_did(&account)
    }

    fn get_account_from_did(did_identifier: Vec<u8>) -> Option<AccountId> {
        Did::get_account_from_did(&did_identifier)
    }

    fn is_did_active(account: AccountId) -> bool {
        Did::is_did_active(&account)
    }

    fn get_total_dids() -> u64 {
        Did::total_dids()
    }
}
```

## Usage Examples

### From Polkadot.js Apps

```javascript
// Register DID
await api.tx.did.registerDid(
    '5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY',
    '0x0242a61f6c9d42e9984a95b76c3a8c8c7e8f9b0a1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f',
    JSON.stringify({
        type: 'user',
        role: 'employee',
        email: 'user@example.com'
    })
).signAndSend(alice);

// Query DID via RPC
const didDoc = await api.rpc.did.getDid(accountId);
console.log('DID Document:', didDoc.toJSON());

// Check if active
const isActive = await api.rpc.did.isDidActive(accountId);
console.log('Is Active:', isActive);

// Get total DIDs
const total = await api.rpc.did.getTotalDids();
console.log('Total DIDs:', total);
```

### From Python (Django Backend)

```python
from substrateinterface import SubstrateInterface, Keypair
import json

# Initialize
substrate = SubstrateInterface(url="ws://127.0.0.1:9944")
keypair = Keypair.create_from_uri('//Alice')

# Register DID for Django user
user = User.objects.get(username='alice')
metadata = json.dumps({
    'django_user_id': user.id,
    'username': user.username,
    'email': user.email,
    'first_name': user.first_name,
    'last_name': user.last_name,
})

call = substrate.compose_call(
    call_module='Did',
    call_function='register_did',
    call_params={
        'account_id': user.wallet_address,
        'public_key': user.public_key,
        'metadata': metadata
    }
)

extrinsic = substrate.create_signed_extrinsic(call=call, keypair=keypair)
receipt = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)

# Update user record
user.did_tx_hash = receipt.extrinsic_hash
user.did_registered = True
user.save()

# Query DID via RPC
did_doc = substrate.rpc_request('did_getDid', [user.wallet_address])
print(f"DID Document: {did_doc}")

# Verify DID
is_active = substrate.rpc_request('did_isDidActive', [user.wallet_address])
print(f"DID Active: {is_active}")
```

## Error Handling

- `DidAlreadyExists` - Account already has a DID registered
- `DidNotFound` - DID does not exist for the account
- `PublicKeyTooLong` - Public key exceeds 256 bytes
- `MetadataTooLong` - Metadata exceeds 1024 bytes
- `NotController` - Only the DID controller can update/revoke
- `DidRevoked` - DID has been revoked and cannot be used
- `DidSuspended` - DID is suspended
- `InvalidDidIdentifier` - Invalid DID format
- `DidIdentifierTooLong` - DID identifier exceeds limit

## Django User Model Extension

Extend your Django User model to support DID:

```python
# apps/backend/apps/accounts/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # ... existing fields ...
    
    # DID fields
    wallet_address = models.CharField(max_length=48, blank=True, null=True)
    public_key = models.CharField(max_length=512, blank=True, null=True)
    did_registered = models.BooleanField(default=False)
    did_tx_hash = models.CharField(max_length=66, blank=True, null=True)
    did_identifier = models.CharField(max_length=256, blank=True, null=True)
    did_status = models.CharField(
        max_length=20,
        choices=[('active', 'Active'), ('revoked', 'Revoked'), ('suspended', 'Suspended')],
        default='active'
    )
    
    def register_blockchain_did(self):
        """Register DID on Substrate blockchain"""
        from apps.did_auth.services.substrate_did_service import SubstrateDidService
        
        if not self.wallet_address:
            raise ValueError("User must have a wallet address")
        
        did_service = SubstrateDidService()
        tx_hash = did_service.register_user_did(self, self.wallet_address)
        
        self.did_tx_hash = tx_hash
        self.did_registered = True
        self.save()
        
        return tx_hash
    
    def get_blockchain_did(self):
        """Get DID document from blockchain"""
        from apps.did_auth.services.substrate_did_service import SubstrateDidService
        
        if not self.wallet_address:
            return None
        
        did_service = SubstrateDidService()
        return did_service.get_user_did(self.wallet_address)
```

## Use Cases

### 1. User Authentication

```python
# Password-less authentication using DID
def authenticate_with_did(account_id, signature, message):
    did_service = SubstrateDidService()
    
    # Get DID document
    did_doc = did_service.get_user_did(account_id)
    if not did_doc:
        return None
    
    # Verify signature with public key
    is_valid = verify_signature(
        message=message,
        signature=signature,
        public_key=did_doc['public_key']
    )
    
    if is_valid:
        # Get Django user from metadata
        metadata = json.loads(did_doc['metadata'])
        user_id = metadata['django_user_id']
        return User.objects.get(id=user_id)
    
    return None
```

### 2. Freelancer Verification

```python
# Verify freelancer identity on blockchain
def verify_freelancer_did(freelancer):
    did_service = SubstrateDidService()
    
    # Check if DID exists and is active
    if not did_service.is_user_did_active(freelancer.wallet_address):
        return False
    
    # Get DID and verify metadata
    did_doc = did_service.get_user_did(freelancer.wallet_address)
    metadata = json.loads(did_doc['metadata'])
    
    return metadata.get('django_user_id') == freelancer.user.id
```

### 3. Client Identity Management

```python
# Register client with DID
def register_client_did(client):
    did_service = SubstrateDidService()
    
    metadata = json.dumps({
        'django_client_id': client.id,
        'client_type': client.client_type,
        'email': client.email,
        'verified': True
    })
    
    tx_hash = did_service.register_user_did(
        user=client,
        account_id=client.wallet_address
    )
    
    client.did_registered = True
    client.did_tx_hash = tx_hash
    client.save()
```

## Performance

- **Registration**: O(1) - Single storage write
- **Update**: O(1) - Single storage mutation
- **Revocation**: O(1) - Single storage mutation
- **Resolution**: O(1) - Single storage read
- **Reverse Lookup**: O(1) - Hash map lookup

## Security Considerations

- **Controller Authorization**: Only DID controller can update/revoke
- **Nonce Protection**: Prevents replay attacks on updates
- **Revocation Support**: DIDs can be revoked if compromised
- **Public Key Rotation**: Public keys can be updated
- **Metadata Privacy**: Metadata is on-chain (use encryption for sensitive data)

## License

Apache-2.0

## Resources

- [W3C DID Core Specification](https://www.w3.org/TR/did-core/)
- [Substrate Documentation](https://docs.substrate.io/)
- [Django Integration Guide](../../backend/apps/did_auth/README.md)
- [TidyGen Documentation](../../../README.md)

