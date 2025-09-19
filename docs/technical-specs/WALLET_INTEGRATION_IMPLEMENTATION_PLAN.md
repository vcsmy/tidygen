# Wallet Integration Implementation Plan

## 🎯 **Overview**

This document outlines the complete implementation plan for integrating wallet-based authentication into TidyGen ERP using MetaMask and Polkadot.js. This feature will replace traditional email/password login with wallet signature verification, enabling Web3-native user authentication and transaction signing.

## 📋 **Implementation Goals**

### **Primary Objectives**
1. **Wallet Authentication**: Replace email/password with wallet signature verification
2. **Multi-Chain Support**: Support both EVM (MetaMask) and Substrate (Polkadot.js) chains
3. **Transaction Signing**: Enable wallet-based transaction signing for ERP operations
4. **Permission System**: Use wallet addresses for access control and permissions
5. **Fallback Support**: Maintain traditional login for admin panel
6. **User Experience**: Seamless wallet connection and authentication flow

### **Technical Requirements**
- MetaMask integration for Ethereum-compatible chains
- Polkadot.js integration for Substrate chains
- Django backend for wallet authentication
- React frontend components for wallet connection
- Signature verification and validation
- Multi-chain wallet management
- Transaction signing workflows

---

## 🏗️ **Architecture Overview**

### **System Components**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend        │    │   Blockchain    │
│                 │    │                  │    │                 │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
│ │   MetaMask  │ │───▶│ │   Wallet     │ │───▶│ │   Ethereum  │ │
│ │   Provider  │ │    │ │   Auth       │ │    │ │   Network   │ │
│ └─────────────┘ │    │ └──────────────┘ │    │ └─────────────┘ │
│                 │    │                  │    │                 │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
│ │ Polkadot.js │ │───▶│ │   Signature  │ │───▶│ │   Substrate │ │
│ │   Provider  │ │    │ │   Verifier   │ │    │ │   Network   │ │
│ └─────────────┘ │    │ └──────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### **Authentication Flow**

1. **Wallet Connection**: User connects wallet (MetaMask/Polkadot.js)
2. **Signature Request**: Backend requests signature for authentication
3. **Signature Verification**: Backend verifies signature against wallet address
4. **JWT Generation**: Generate JWT token for authenticated session
5. **Permission Mapping**: Map wallet address to user permissions
6. **Session Management**: Maintain authenticated session with wallet context

---

## 📁 **File Structure**

```
apps/backend/
├── apps/
│   └── wallet/                    # New Django app
│       ├── __init__.py
│       ├── apps.py
│       ├── models.py              # Wallet models
│       ├── serializers.py         # API serializers
│       ├── views.py               # REST API views
│       ├── services/              # Business logic
│       │   ├── __init__.py
│       │   ├── metamask_service.py
│       │   ├── polkadot_service.py
│       │   ├── signature_service.py
│       │   └── wallet_service.py
│       ├── management/
│       │   └── commands/
│       │       └── sync_wallets.py
│       ├── migrations/
│       ├── tests/
│       │   ├── test_models.py
│       │   ├── test_services.py
│       │   └── test_views.py
│       └── urls.py
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── wallet/
│       │   │   ├── WalletConnect.tsx
│       │   │   ├── MetaMaskButton.tsx
│       │   │   ├── PolkadotButton.tsx
│       │   │   ├── WalletSelector.tsx
│       │   │   └── TransactionSigner.tsx
│       │   └── auth/
│       │       ├── WalletLogin.tsx
│       │       ├── SignatureRequest.tsx
│       │       └── AuthProvider.tsx
│       ├── hooks/
│       │   ├── useWallet.ts
│       │   ├── useMetaMask.ts
│       │   ├── usePolkadot.ts
│       │   └── useSignature.ts
│       ├── services/
│       │   ├── walletService.ts
│       │   ├── metamaskService.ts
│       │   ├── polkadotService.ts
│       │   └── authService.ts
│       └── types/
│           ├── wallet.ts
│           └── auth.ts
└── requirements.txt               # Updated dependencies
```

---

## 🔧 **Implementation Phases**

### **Phase 1: Backend Wallet Models & Services**
- [ ] Create `apps/wallet` Django app
- [ ] Define wallet models and relationships
- [ ] Implement signature verification services
- [ ] Create MetaMask integration service
- [ ] Create Polkadot.js integration service
- [ ] Add database migrations

### **Phase 2: Authentication API**
- [ ] Create wallet authentication endpoints
- [ ] Implement signature verification
- [ ] Add JWT token generation
- [ ] Create wallet management endpoints
- [ ] Add permission mapping
- [ ] Implement session management

### **Phase 3: Frontend Wallet Components**
- [ ] Create wallet connection components
- [ ] Implement MetaMask integration
- [ ] Implement Polkadot.js integration
- [ ] Create signature request UI
- [ ] Add wallet selector component
- [ ] Implement transaction signing UI

### **Phase 4: Integration & Testing**
- [ ] Integrate with existing authentication
- [ ] Add comprehensive test coverage
- [ ] Implement error handling
- [ ] Add loading states and UX
- [ ] Create documentation
- [ ] Add fallback mechanisms

---

## 🛠️ **Technical Specifications**

### **Django Models**

#### **Wallet**
```python
class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    address = models.CharField(max_length=100, unique=True)
    wallet_type = models.CharField(max_length=20)  # metamask, polkadot
    chain_id = models.CharField(max_length=50)     # network identifier
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now=True)
```

#### **WalletSignature**
```python
class WalletSignature(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    message = models.TextField()
    signature = models.TextField()
    nonce = models.CharField(max_length=100)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
```

#### **WalletPermission**
```python
class WalletPermission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    permission_type = models.CharField(max_length=50)
    resource = models.CharField(max_length=100)
    granted = models.BooleanField(default=True)
    granted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
```

### **API Endpoints**

#### **Authentication Endpoints**
- `POST /api/v1/wallet/connect/` - Connect wallet and request signature
- `POST /api/v1/wallet/verify/` - Verify signature and authenticate
- `POST /api/v1/wallet/disconnect/` - Disconnect wallet
- `GET /api/v1/wallet/status/` - Get wallet connection status

#### **Wallet Management**
- `GET /api/v1/wallet/list/` - List user wallets
- `POST /api/v1/wallet/add/` - Add new wallet
- `PUT /api/v1/wallet/{id}/` - Update wallet settings
- `DELETE /api/v1/wallet/{id}/` - Remove wallet

#### **Transaction Signing**
- `POST /api/v1/wallet/sign/` - Request transaction signature
- `GET /api/v1/wallet/sign/{id}/status/` - Get signing status
- `POST /api/v1/wallet/sign/{id}/confirm/` - Confirm signature

### **Frontend Components**

#### **WalletConnect Component**
```typescript
interface WalletConnectProps {
  onConnect: (wallet: WalletInfo) => void;
  onDisconnect: () => void;
  supportedWallets: WalletType[];
}

const WalletConnect: React.FC<WalletConnectProps> = ({
  onConnect,
  onDisconnect,
  supportedWallets
}) => {
  // Wallet connection logic
};
```

#### **TransactionSigner Component**
```typescript
interface TransactionSignerProps {
  transaction: TransactionData;
  wallet: WalletInfo;
  onSigned: (signature: string) => void;
  onError: (error: string) => void;
}

const TransactionSigner: React.FC<TransactionSignerProps> = ({
  transaction,
  wallet,
  onSigned,
  onError
}) => {
  // Transaction signing logic
};
```

---

## 🔒 **Security Considerations**

### **Signature Verification**
- Verify signature against wallet address
- Use nonce to prevent replay attacks
- Implement signature expiration
- Validate message format and content

### **Wallet Security**
- Store only wallet addresses, never private keys
- Implement rate limiting for signature requests
- Add IP-based restrictions for sensitive operations
- Log all wallet authentication attempts

### **Permission Management**
- Map wallet addresses to user roles
- Implement granular permissions
- Support multi-wallet users
- Enable wallet-based access control

---

## 📊 **User Experience Flow**

### **Initial Wallet Connection**
1. User clicks "Connect Wallet" button
2. Wallet selector shows available options (MetaMask, Polkadot.js)
3. User selects wallet type
4. Browser prompts for wallet connection
5. User approves connection
6. System requests signature for authentication
7. User signs authentication message
8. Backend verifies signature and creates session

### **Transaction Signing**
1. User initiates transaction (e.g., approve payment)
2. System shows transaction details
3. User clicks "Sign Transaction"
4. Wallet prompts for signature
5. User reviews and signs transaction
6. System submits signed transaction
7. Transaction is processed and confirmed

### **Multi-Wallet Management**
1. User can connect multiple wallets
2. Set primary wallet for default operations
3. Switch between wallets for different operations
4. Manage wallet permissions and access levels

---

## 🧪 **Testing Strategy**

### **Backend Tests**
- Signature verification accuracy
- Wallet model validation
- API endpoint functionality
- Permission system testing
- Error handling scenarios

### **Frontend Tests**
- Wallet connection flows
- Component rendering and interaction
- Error state handling
- Loading state management
- Cross-browser compatibility

### **Integration Tests**
- End-to-end authentication flow
- Transaction signing workflows
- Multi-wallet scenarios
- Network switching
- Error recovery

---

## 📈 **Performance Optimization**

### **Caching Strategy**
- Cache wallet verification results
- Store signature nonces temporarily
- Implement session caching
- Use Redis for session management

### **Network Optimization**
- Batch signature requests
- Implement connection pooling
- Add retry logic for network failures
- Optimize API response times

---

## 🚀 **Deployment Considerations**

### **Environment Configuration**
- Configure supported networks
- Set up wallet provider endpoints
- Configure signature message templates
- Set nonce expiration times

### **Monitoring & Logging**
- Log all wallet connections
- Monitor signature verification success rates
- Track transaction signing metrics
- Alert on authentication failures

---

## 📚 **Documentation Requirements**

### **User Documentation**
- Wallet connection guide
- Transaction signing tutorial
- Troubleshooting common issues
- Multi-wallet management guide

### **Developer Documentation**
- API reference
- Component usage examples
- Integration guidelines
- Security best practices

---

**This implementation plan provides a comprehensive roadmap for integrating wallet-based authentication into TidyGen ERP, enabling Web3-native user experience while maintaining security and usability.**
