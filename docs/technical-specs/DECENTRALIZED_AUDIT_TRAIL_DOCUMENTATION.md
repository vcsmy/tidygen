# Decentralized Audit Trail Documentation

## Overview

The Decentralized Audit Trail system provides tamper-proof logging for compliance and transparency in the TidyGen ERP system. It captures all critical financial and system events, generates cryptographic hashes, and optionally stores them on-chain or in IPFS for maximum security and verifiability.

## Features

### Core Functionality
- **Event Capture**: Automatically captures all critical system events
- **Cryptographic Hashing**: Uses SHA256 and Keccak256 for data integrity
- **Merkle Tree Verification**: Batch verification of multiple events
- **On-Chain Storage**: Optional blockchain anchoring for maximum security
- **IPFS Integration**: Decentralized storage for event data
- **CLI Verification**: Command-line tool for integrity checking
- **Admin Interface**: Django admin for monitoring and management

### Event Types
- Financial Events: Invoice creation/updates, payment processing
- User Events: Login/logout, permission changes
- System Events: Data updates, configuration changes
- Contract Events: Smart contract interactions
- Asset Events: Asset transfers, tokenization

## Architecture

### Models

#### AuditEvent
The core model that stores all audit events:

```python
class AuditEvent(models.Model):
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    object_type = models.CharField(max_length=100)
    object_id = models.CharField(max_length=255)
    data = models.JSONField()
    hash = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    on_chain_tx_hash = models.CharField(max_length=66, blank=True)
    on_chain_block_number = models.BigIntegerField(blank=True, null=True)
    ipfs_hash = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Services

#### HashService
Generates cryptographic hashes for event data:
- SHA256 hashing for standard events
- Keccak256 hashing for blockchain compatibility
- Consistent hash generation for the same data

#### MerkleService
Creates and manages Merkle trees for batch verification:
- Builds Merkle trees from event hashes
- Generates Merkle proofs for individual events
- Verifies event integrity against Merkle roots

#### BlockchainService
Handles on-chain storage of event hashes:
- Connects to Ethereum networks
- Anchors event hashes in smart contracts
- Tracks transaction hashes and block numbers

#### IPFSService
Manages decentralized storage of event data:
- Stores event data on IPFS
- Returns Content Identifiers (CIDs)
- Enables decentralized data access

#### AuditService
High-level orchestration service:
- Coordinates all audit operations
- Manages event lifecycle
- Provides integrity checking

## API Endpoints

### Audit Events
- `GET /api/v1/audit-trail/events/` - List all audit events
- `POST /api/v1/audit-trail/events/` - Create new audit event
- `GET /api/v1/audit-trail/events/{id}/` - Get specific event
- `POST /api/v1/audit-trail/events/verify/` - Verify event integrity
- `POST /api/v1/audit-trail/events/batch_operation/` - Batch operations
- `GET /api/v1/audit-trail/events/stats/` - Get audit statistics
- `GET /api/v1/audit-trail/events/integrity_check/` - System integrity check

### Event Actions
- `POST /api/v1/audit-trail/events/{id}/anchor_on_chain/` - Anchor event on-chain
- `POST /api/v1/audit-trail/events/{id}/store_ipfs/` - Store event on IPFS

## Usage Examples

### Creating an Audit Event

```python
from apps.audit_trail.services import AuditService

audit_service = AuditService()

event = audit_service.log_event(
    event_type='invoice_created',
    actor=user,
    entity_type='Invoice',
    entity_id='123',
    event_data={'amount': 1000.00, 'currency': 'USD'}
)
```

### Verifying Event Integrity

```python
# Verify single event
is_valid = audit_service.verify_event(event)

# Verify with Merkle proof
is_valid = audit_service.verify_event(
    event, 
    merkle_proof=['hash1', 'hash2'], 
    merkle_root='root_hash'
)
```

### Batch Operations

```python
# Create Merkle tree for multiple events
merkle_data = audit_service.generate_merkle_tree(events)

# Anchor multiple events on-chain
for event in events:
    tx_hash = audit_service.anchor_event_on_chain(event)
```

## CLI Commands

### Verify Audit Integrity

```bash
# Verify all events
python manage.py verify_audit_integrity

# Verify specific event
python manage.py verify_audit_integrity --event-id 123

# Verify events by type
python manage.py verify_audit_integrity --event-type invoice_created

# Export failed verifications
python manage.py verify_audit_integrity --export-failed failed_events.json

# Verbose output
python manage.py verify_audit_integrity --verbose
```

## Configuration

### Environment Variables

```bash
# Blockchain Configuration
ETHEREUM_RPC_URL=http://localhost:8545
ETHEREUM_PRIVATE_KEY=your_private_key
AUDIT_CONTRACT_ADDRESS=0x...

# IPFS Configuration
IPFS_GATEWAY_URL=https://ipfs.io/ipfs/
IPFS_API_URL=http://localhost:5001

# Audit Configuration
AUDIT_HASH_ALGORITHM=sha256  # or keccak256
AUDIT_BATCH_SIZE=100
AUDIT_RETENTION_DAYS=365
```

### Django Settings

```python
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ... other apps
    'apps.audit_trail',
]

# Audit Trail Settings
AUDIT_TRAIL = {
    'ENABLED': True,
    'HASH_ALGORITHM': 'sha256',
    'BATCH_SIZE': 100,
    'RETENTION_DAYS': 365,
    'ON_CHAIN_ENABLED': True,
    'IPFS_ENABLED': True,
}
```

## Security Considerations

### Data Integrity
- All events are cryptographically hashed
- Hashes are immutable once generated
- Merkle trees enable efficient batch verification
- On-chain storage provides tamper-proof anchoring

### Privacy
- Event data can be stored on IPFS for privacy
- Only hashes are stored on-chain by default
- Sensitive data can be encrypted before storage

### Access Control
- API endpoints require authentication
- Admin interface has read-only access
- CLI commands require appropriate permissions

## Monitoring and Maintenance

### Health Checks
- Regular integrity verification
- Monitor on-chain transaction status
- Check IPFS availability
- Verify hash consistency

### Performance Optimization
- Batch operations for multiple events
- Async processing for on-chain operations
- Caching for frequently accessed data
- Database indexing for efficient queries

### Backup and Recovery
- Regular database backups
- IPFS data replication
- On-chain data is immutable
- Export functionality for compliance

## Compliance Features

### Audit Requirements
- Immutable event logs
- Cryptographic proof of integrity
- Timestamp verification
- User attribution
- Data retention policies

### Reporting
- Event statistics and analytics
- Integrity verification reports
- Compliance dashboards
- Export capabilities

## Troubleshooting

### Common Issues

1. **Hash Verification Failures**
   - Check data consistency
   - Verify hash algorithm
   - Review event creation process

2. **On-Chain Connection Issues**
   - Verify RPC URL
   - Check network connectivity
   - Validate contract address

3. **IPFS Storage Problems**
   - Check IPFS node status
   - Verify gateway configuration
   - Review storage limits

### Debug Commands

```bash
# Check system status
python manage.py verify_audit_integrity --verbose

# Test blockchain connection
python manage.py shell
>>> from apps.audit_trail.services import BlockchainService
>>> service = BlockchainService('ethereum')
>>> service.test_connection()

# Test IPFS connection
>>> from apps.audit_trail.services import IPFSService
>>> service = IPFSService()
>>> service.test_connection()
```

## Future Enhancements

### Planned Features
- Multi-chain support (Polkadot, Solana)
- Advanced analytics and reporting
- Automated compliance checking
- Integration with external audit systems
- Real-time monitoring and alerting

### Scalability Improvements
- Sharding for large datasets
- Distributed verification
- Optimized Merkle tree algorithms
- Enhanced caching strategies

## Support and Contributing

### Documentation
- API documentation: `/api/docs/`
- Admin interface: `/admin/audit_trail/`
- CLI help: `python manage.py verify_audit_integrity --help`

### Testing
- Unit tests: `python manage.py test apps.audit_trail`
- Integration tests: `python manage.py test apps.audit_trail.tests`
- CLI tests: Manual verification commands

### Contributing
- Follow Django best practices
- Add tests for new features
- Update documentation
- Follow security guidelines
