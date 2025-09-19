# DID-Based Access Control API Documentation

## Overview

The DID-Based Access Control system provides a comprehensive API for managing Decentralized Identities (DIDs), roles, permissions, and authentication in TidyGen ERP. This system leverages Web3 technologies and W3C DID standards.

## Base URL

```
/api/v1/did-auth/
```

## Authentication

The DID system supports multiple authentication methods:

1. **DID-based Authentication**: Using wallet signatures
2. **Traditional JWT**: For admin operations
3. **Session-based**: For DID sessions

## Endpoints

### DID Documents

#### List DID Documents
```http
GET /api/v1/did-auth/documents/
```

**Query Parameters:**
- `did`: Filter by DID string
- `status`: Filter by status (active, deactivated, revoked)
- `user`: Filter by user ID
- `search`: Search in DID, document, controller, username, email
- `ordering`: Order by created_at, updated_at, status

**Response:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "did": "did:ethr:0x1234567890abcdef",
      "user": 1,
      "user_username": "john_doe",
      "user_email": "john@example.com",
      "document": {
        "@context": ["https://www.w3.org/ns/did/v1"],
        "id": "did:ethr:0x1234567890abcdef",
        "verificationMethod": [...]
      },
      "controller": "did:ethr:0x1234567890abcdef",
      "status": "active",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "deactivated_at": null,
      "on_chain_registry_status": "registered",
      "metadata": {}
    }
  ]
}
```

#### Create DID Document
```http
POST /api/v1/did-auth/documents/
```

**Request Body:**
```json
{
  "did": "did:ethr:0x1234567890abcdef",
  "document": {
    "@context": ["https://www.w3.org/ns/did/v1"],
    "id": "did:ethr:0x1234567890abcdef",
    "verificationMethod": [
      {
        "id": "did:ethr:0x1234567890abcdef#key-1",
        "type": "EcdsaSecp256k1RecoveryMethod2020",
        "controller": "did:ethr:0x1234567890abcdef",
        "publicKeyMultibase": "zQ3shZc2QzApp2oymGvQbzP8eKheVshBHbU4ZYjeXqwSKEn6N"
      }
    ],
    "authentication": ["did:ethr:0x1234567890abcdef#key-1"],
    "assertionMethod": ["did:ethr:0x1234567890abcdef#key-1"]
  },
  "controller": "did:ethr:0x1234567890abcdef",
  "user": 1
}
```

#### Resolve DID
```http
POST /api/v1/did-auth/documents/resolve/
```

**Request Body:**
```json
{
  "did": "did:ethr:0x1234567890abcdef"
}
```

#### Verify Signature
```http
POST /api/v1/did-auth/documents/verify-signature/
```

**Request Body:**
```json
{
  "did": "did:ethr:0x1234567890abcdef",
  "signature": "0x1234567890abcdef...",
  "message": "Hello, World!"
}
```

#### Sync to Registry
```http
POST /api/v1/did-auth/documents/{id}/sync-to-registry/
```

**Response:**
```json
{
  "status": "synced",
  "did": "did:ethr:0x1234567890abcdef",
  "tx_hash": "0xabcdef1234567890...",
  "block_number": 12345678,
  "gas_used": 150000
}
```

#### Sync from Registry
```http
POST /api/v1/did-auth/documents/sync-from-registry/
```

**Request Body:**
```json
{
  "did": "did:ethr:0x1234567890abcdef"
}
```

#### Deactivate on Registry
```http
POST /api/v1/did-auth/documents/{id}/deactivate-on-registry/
```

#### Get Registry Status
```http
GET /api/v1/did-auth/documents/registry-status/?did=did:ethr:0x1234567890abcdef
```

#### Get Network Info
```http
GET /api/v1/did-auth/documents/network-info/
```

### DID Roles

#### List DID Roles
```http
GET /api/v1/did-auth/roles/
```

**Query Parameters:**
- `role_name`: Filter by role name
- `is_active`: Filter by active status
- `did`: Filter by DID ID
- `search`: Search in DID, role_name, custom_role_name
- `ordering`: Order by granted_at

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "did": {
        "id": 1,
        "did": "did:ethr:0x1234567890abcdef",
        "status": "active"
      },
      "role_name": "admin",
      "custom_role_name": "",
      "permissions": ["finance:read", "finance:write", "hr:read", "hr:write"],
      "granted_by": "did:system:admin",
      "granted_at": "2024-01-01T00:00:00Z",
      "expires_at": null,
      "is_active": true,
      "metadata": {}
    }
  ]
}
```

#### Assign Role
```http
POST /api/v1/did-auth/roles/assign-role/
```

**Request Body:**
```json
{
  "did": "did:ethr:0x1234567890abcdef",
  "role_name": "finance_manager",
  "custom_role_name": "",
  "permissions": ["finance:read", "finance:write", "inventory:read"],
  "expires_at": "2024-12-31T23:59:59Z"
}
```

### DID Credentials

#### List DID Credentials
```http
GET /api/v1/did-auth/credentials/
```

**Query Parameters:**
- `credential_type`: Filter by credential type
- `issuer`: Filter by issuer DID
- `revoked`: Filter by revoked status
- `search`: Search in DID, credential_type, issuer
- `ordering`: Order by issued_at

#### Issue Credential
```http
POST /api/v1/did-auth/credentials/issue/
```

**Request Body:**
```json
{
  "did": "did:ethr:0x1234567890abcdef",
  "credential_type": "employment",
  "credential_data": {
    "@context": ["https://www.w3.org/2018/credentials/v1"],
    "type": ["VerifiableCredential", "EmploymentCredential"],
    "credentialSubject": {
      "id": "did:ethr:0x1234567890abcdef",
      "position": "Finance Manager",
      "department": "Finance",
      "startDate": "2024-01-01"
    }
  },
  "issuer": "did:system:hr",
  "expires_at": "2025-01-01T00:00:00Z"
}
```

#### Verify Credential
```http
POST /api/v1/did-auth/credentials/{id}/verify/
```

#### Revoke Credential
```http
POST /api/v1/did-auth/credentials/{id}/revoke/
```

### DID Sessions

#### List DID Sessions
```http
GET /api/v1/did-auth/sessions/
```

**Query Parameters:**
- `is_active`: Filter by active status
- `did`: Filter by DID ID
- `search`: Search in DID, session_token
- `ordering`: Order by created_at, last_activity

#### Login with DID
```http
POST /api/v1/did-auth/sessions/login/
```

**Request Body:**
```json
{
  "did": "did:ethr:0x1234567890abcdef",
  "signature": "0x1234567890abcdef...",
  "message": "TidyGen DID Authentication\nTimestamp: 1640995200000\nNonce: abc123",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0..."
}
```

**Response:**
```json
{
  "status": "authenticated",
  "session": {
    "id": 1,
    "session_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "created_at": "2024-01-01T00:00:00Z",
    "expires_at": "2024-01-02T00:00:00Z",
    "last_activity": "2024-01-01T00:00:00Z",
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "is_active": true,
    "did": {
      "id": 1,
      "did": "did:ethr:0x1234567890abcdef",
      "status": "active"
    }
  }
}
```

#### Logout
```http
POST /api/v1/did-auth/sessions/logout/
```

**Request Body:**
```json
{
  "session_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### DID Permissions

#### List DID Permissions
```http
GET /api/v1/did-auth/permissions/
```

**Query Parameters:**
- `category`: Filter by permission category
- `is_active`: Filter by active status
- `search`: Search in name, display_name, description, resource, action
- `ordering`: Order by category, name

**Response:**
```json
{
  "count": 20,
  "results": [
    {
      "id": 1,
      "name": "finance_read",
      "display_name": "Read Finance Data",
      "description": "Permission to read financial data and reports",
      "category": "finance",
      "resource": "finance",
      "action": "read",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "metadata": {}
    }
  ]
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "error": "Invalid request data",
  "details": {
    "field_name": ["This field is required."]
  }
}
```

### 401 Unauthorized
```json
{
  "error": "Authentication required",
  "message": "Invalid or missing authentication credentials"
}
```

### 403 Forbidden
```json
{
  "error": "Permission denied",
  "message": "You don't have permission to perform this action"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found",
  "message": "The requested resource does not exist"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Authentication endpoints**: 5 requests per minute per IP
- **Registry sync endpoints**: 10 requests per minute per user
- **General endpoints**: 100 requests per minute per user

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Web3 Integration

### Supported Networks

- **Ethereum Mainnet**: Production environment
- **Ethereum Goerli**: Test environment
- **Polygon**: Alternative network
- **Local Development**: Hardhat/Ganache

### Registry Contract

The system integrates with on-chain DID registries:

- **Contract Address**: Configurable via settings
- **ABI**: Standard DID registry interface
- **Gas Optimization**: Batch operations supported

### Wallet Integration

Supported wallet types:

- **MetaMask**: Browser extension
- **WalletConnect**: Mobile wallets
- **Polkadot.js**: Polkadot ecosystem
- **Custom**: Programmatic access

## Security Considerations

### Signature Verification

- **Message Format**: Standardized authentication messages
- **Nonce**: Random nonce to prevent replay attacks
- **Timestamp**: Time-based validation
- **Domain Binding**: Domain-specific signatures

### Session Management

- **JWT Tokens**: Secure session tokens
- **Expiration**: Configurable session timeouts
- **Refresh**: Token refresh mechanism
- **Revocation**: Immediate session termination

### Access Control

- **Role-Based**: Hierarchical permission system
- **Resource-Based**: Fine-grained permissions
- **Time-Based**: Expiring permissions
- **Audit Trail**: Complete access logging

## Examples

### Complete Authentication Flow

1. **Connect Wallet**
```javascript
const accounts = await ethereum.request({ method: 'eth_requestAccounts' });
const address = accounts[0];
```

2. **Generate DID**
```javascript
const did = `did:ethr:${address}`;
```

3. **Create Message**
```javascript
const message = `TidyGen DID Authentication\nTimestamp: ${Date.now()}\nNonce: ${Math.random().toString(36).substring(7)}`;
```

4. **Sign Message**
```javascript
const signature = await ethereum.request({
  method: 'personal_sign',
  params: [message, address],
});
```

5. **Authenticate**
```javascript
const response = await fetch('/api/v1/did-auth/sessions/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ did, signature, message }),
});
```

### Assign Role to DID

```javascript
const response = await fetch('/api/v1/did-auth/roles/assign-role/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    did: 'did:ethr:0x1234567890abcdef',
    role_name: 'finance_manager',
    permissions: ['finance:read', 'finance:write'],
    expires_at: '2024-12-31T23:59:59Z'
  }),
});
```

### Sync DID to Registry

```javascript
const response = await fetch('/api/v1/did-auth/documents/1/sync-to-registry/', {
  method: 'POST',
});
const result = await response.json();
console.log('Transaction Hash:', result.tx_hash);
```

## Management Commands

### Initialize DID System
```bash
python manage.py init_did_system --create-sample-did --assign-sample-roles
```

### Sync Registry
```bash
python manage.py sync_did_registry --action=network-info
python manage.py sync_did_registry --action=sync-all --batch-size=5
python manage.py sync_did_registry --action=sync-to-registry --did=did:ethr:0x1234567890abcdef
```

## Configuration

### Environment Variables

```bash
# Web3 Configuration
WEB3_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
WEB3_PRIVATE_KEY=your_private_key_here
DID_REGISTRY_ADDRESS=0x1234567890abcdef1234567890abcdef12345678

# DID Configuration
DID_DEFAULT_EXPIRY_HOURS=24
DID_SESSION_TIMEOUT_HOURS=8
DID_AUTO_SYNC_REGISTRY=true
```

### Django Settings

```python
# settings/base.py
WEB3_CONFIG = {
    'RPC_URL': 'https://mainnet.infura.io/v3/YOUR_PROJECT_ID',
    'PRIVATE_KEY': 'your_private_key_here',
    'DID_REGISTRY_ADDRESS': '0x1234567890abcdef1234567890abcdef12345678',
}

DID_CONFIG = {
    'DEFAULT_EXPIRY_HOURS': 24,
    'SESSION_TIMEOUT_HOURS': 8,
    'AUTO_SYNC_REGISTRY': True,
}
```

## Testing

### Unit Tests
```bash
python manage.py test apps.did_auth.tests
```

### API Tests
```bash
python manage.py test apps.did_auth.tests.DIDAPITest
```

### Integration Tests
```bash
python manage.py test apps.did_auth.tests.DIDIntegrationTest
```

## Monitoring and Logging

### Audit Events

All DID operations are logged to the audit trail:

- `did_created`: DID document created
- `did_updated`: DID document updated
- `did_deactivated`: DID deactivated
- `role_assigned`: Role assigned to DID
- `role_revoked`: Role revoked from DID
- `credential_issued`: Credential issued
- `credential_revoked`: Credential revoked
- `session_created`: DID session created
- `session_terminated`: DID session terminated

### Metrics

Key metrics tracked:

- **DID Creation Rate**: DIDs created per day
- **Authentication Success Rate**: Successful authentications
- **Registry Sync Success Rate**: Successful registry operations
- **Session Duration**: Average session length
- **Permission Usage**: Most used permissions

## Troubleshooting

### Common Issues

1. **Wallet Connection Failed**
   - Ensure MetaMask is installed and unlocked
   - Check network configuration
   - Verify RPC URL is accessible

2. **Signature Verification Failed**
   - Verify message format matches expected format
   - Check signature is from correct address
   - Ensure DID matches wallet address

3. **Registry Sync Failed**
   - Check Web3 connection
   - Verify contract address and ABI
   - Ensure sufficient gas for transaction

4. **Permission Denied**
   - Verify user has required role
   - Check role is active and not expired
   - Ensure role has required permissions

### Debug Mode

Enable debug logging:

```python
LOGGING = {
    'loggers': {
        'apps.did_auth': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

## Support

For technical support and questions:

- **Documentation**: Check this API documentation
- **Issues**: Report bugs via GitHub issues
- **Community**: Join our Discord community
- **Email**: support@tidygen.com
