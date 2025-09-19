# DID-Based Access Control User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Wallet Setup](#wallet-setup)
4. [DID Authentication](#did-authentication)
5. [Role Management](#role-management)
6. [Permission System](#permission-system)
7. [Registry Operations](#registry-operations)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)
10. [FAQ](#faq)

## Introduction

The DID-Based Access Control system in TidyGen ERP provides a decentralized approach to identity management and access control. Instead of traditional username/password authentication, users authenticate using their blockchain wallet and a Decentralized Identity (DID).

### Key Benefits

- **Decentralized**: No central authority controls your identity
- **Secure**: Cryptographic signatures ensure authenticity
- **Privacy-Preserving**: Minimal data collection and storage
- **Interoperable**: Works across different systems and platforms
- **Auditable**: All actions are recorded on the blockchain

### Key Concepts

- **DID (Decentralized Identifier)**: A unique identifier that you control
- **Wallet**: Your blockchain wallet (MetaMask, etc.) that holds your private keys
- **Signature**: Cryptographic proof that you own the wallet
- **Role**: A set of permissions assigned to your DID
- **Registry**: On-chain storage for DID documents

## Getting Started

### Prerequisites

1. **Blockchain Wallet**: Install MetaMask or compatible wallet
2. **Ethereum Account**: Have an Ethereum account with some ETH for gas fees
3. **Browser**: Use a modern browser with Web3 support

### Installation Steps

1. **Install MetaMask**
   - Visit [metamask.io](https://metamask.io)
   - Install the browser extension
   - Create a new wallet or import existing one
   - Secure your seed phrase

2. **Connect to TidyGen**
   - Navigate to the TidyGen ERP application
   - Click "Connect Wallet" on the login page
   - Approve the connection in MetaMask

3. **Generate Your DID**
   - Your DID will be automatically generated from your wallet address
   - Format: `did:ethr:0xYourWalletAddress`

## Wallet Setup

### MetaMask Configuration

1. **Network Setup**
   - Ensure you're connected to the correct network
   - For production: Ethereum Mainnet
   - For testing: Goerli Testnet

2. **Account Security**
   - Never share your private key or seed phrase
   - Use hardware wallets for high-value accounts
   - Enable additional security features

3. **Gas Management**
   - Keep some ETH for transaction fees
   - Monitor gas prices for optimal timing
   - Use gas estimation tools

### Alternative Wallets

- **WalletConnect**: For mobile wallets
- **Polkadot.js**: For Polkadot ecosystem
- **Custom Integration**: For enterprise solutions

## DID Authentication

### Authentication Flow

1. **Connect Wallet**
   ```
   Click "Connect Wallet" → Approve in MetaMask → Wallet Connected
   ```

2. **Generate Message**
   ```
   System generates unique message → User reviews message
   ```

3. **Sign Message**
   ```
   Click "Sign Message" → MetaMask prompts for signature → Sign transaction
   ```

4. **Authenticate**
   ```
   System verifies signature → Creates session → Access granted
   ```

### Message Format

Authentication messages follow this format:
```
TidyGen DID Authentication
Timestamp: 1640995200000
Nonce: abc123def456
```

### Session Management

- **Session Duration**: 24 hours (configurable)
- **Auto-Renewal**: Sessions can be extended
- **Logout**: Manual logout or automatic expiration
- **Multiple Sessions**: Support for multiple active sessions

## Role Management

### Available Roles

1. **Administrator**
   - Full system access
   - User management
   - System configuration

2. **Finance Manager**
   - Financial data access
   - Invoice management
   - Payment processing

3. **HR Manager**
   - Employee management
   - Payroll access
   - Performance reviews

4. **Auditor**
   - Read-only access
   - Audit trail viewing
   - Report generation

5. **Field Supervisor**
   - Field operations
   - Team management
   - Schedule oversight

6. **Cleaner**
   - Task management
   - Time tracking
   - Basic reporting

7. **Client**
   - Service requests
   - Invoice viewing
   - Communication

8. **Supplier**
   - Inventory management
   - Order processing
   - Payment tracking

### Role Assignment

1. **Request Role**
   - Contact system administrator
   - Provide justification for role
   - Submit required documentation

2. **Role Approval**
   - Administrator reviews request
   - Assigns appropriate role
   - Sets expiration date (optional)

3. **Role Activation**
   - Role becomes active immediately
   - Permissions are enforced
   - Audit trail is created

### Custom Roles

- **Custom Role Creation**: Administrators can create custom roles
- **Permission Assignment**: Granular permission control
- **Role Templates**: Predefined role templates available

## Permission System

### Permission Categories

1. **Finance**
   - `finance:read` - View financial data
   - `finance:write` - Modify financial data
   - `finance:approve` - Approve financial transactions

2. **Human Resources**
   - `hr:read` - View employee data
   - `hr:write` - Modify employee data
   - `hr:payroll` - Access payroll information

3. **Inventory**
   - `inventory:read` - View inventory data
   - `inventory:write` - Modify inventory data
   - `inventory:order` - Create purchase orders

4. **Scheduling**
   - `scheduling:read` - View schedules
   - `scheduling:write` - Modify schedules
   - `scheduling:assign` - Assign tasks

5. **Analytics**
   - `analytics:read` - View reports
   - `analytics:create` - Create custom reports
   - `analytics:export` - Export data

6. **Administration**
   - `admin:users` - Manage users
   - `admin:system` - System configuration
   - `admin:audit` - View audit logs

### Permission Inheritance

- **Role-Based**: Permissions are inherited from roles
- **Hierarchical**: Higher roles include lower role permissions
- **Explicit**: Permissions can be explicitly granted/denied

### Permission Validation

- **Real-Time**: Permissions checked on each request
- **Caching**: Permission cache for performance
- **Audit**: All permission checks are logged

## Registry Operations

### On-Chain Registry

The DID registry stores DID documents on the blockchain for:

- **Decentralization**: No single point of failure
- **Verification**: Anyone can verify DID authenticity
- **Interoperability**: Works across different systems

### Registry Operations

1. **Register DID**
   ```
   DID created → Registry sync → On-chain storage → Confirmation
   ```

2. **Update DID**
   ```
   DID modified → Registry sync → On-chain update → Confirmation
   ```

3. **Deactivate DID**
   ```
   DID deactivated → Registry sync → On-chain deactivation → Confirmation
   ```

### Registry Status

- **Registered**: DID is stored on-chain
- **Not Registered**: DID exists locally only
- **Deactivated**: DID is deactivated on-chain
- **Unknown**: Registry status unclear

### Gas Costs

Typical gas costs for registry operations:
- **Register DID**: ~150,000 gas
- **Update DID**: ~100,000 gas
- **Deactivate DID**: ~50,000 gas

## Troubleshooting

### Common Issues

#### Wallet Connection Problems

**Problem**: Wallet won't connect
**Solutions**:
- Refresh the page
- Check MetaMask is unlocked
- Verify network connection
- Clear browser cache

**Problem**: Wrong network
**Solutions**:
- Switch to correct network in MetaMask
- Add custom network if needed
- Check network configuration

#### Authentication Issues

**Problem**: Signature verification failed
**Solutions**:
- Ensure you're signing with correct account
- Check message format
- Try generating new message
- Verify wallet is connected

**Problem**: Session expired
**Solutions**:
- Re-authenticate with wallet
- Check system time
- Contact administrator if persistent

#### Registry Issues

**Problem**: Registry sync failed
**Solutions**:
- Check network connection
- Verify sufficient ETH for gas
- Try again during low network congestion
- Contact support if persistent

**Problem**: Transaction pending
**Solutions**:
- Wait for confirmation
- Check transaction on block explorer
- Increase gas price if needed
- Cancel and retry if stuck

### Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| "Wallet not connected" | MetaMask not connected | Connect wallet |
| "Invalid signature" | Signature verification failed | Re-sign message |
| "DID not found" | DID doesn't exist | Create DID first |
| "Insufficient permissions" | Role lacks required permission | Request role upgrade |
| "Session expired" | Authentication session expired | Re-authenticate |
| "Registry unavailable" | On-chain registry not accessible | Try again later |

### Getting Help

1. **Check Documentation**: Review this guide and API docs
2. **Contact Support**: Email support@tidygen.com
3. **Community Forum**: Join our Discord community
4. **GitHub Issues**: Report bugs via GitHub

## Best Practices

### Security

1. **Wallet Security**
   - Use hardware wallets for high-value accounts
   - Never share private keys or seed phrases
   - Enable additional security features
   - Regular security audits

2. **Session Management**
   - Logout when finished
   - Don't share session tokens
   - Use secure networks
   - Monitor active sessions

3. **Permission Management**
   - Follow principle of least privilege
   - Regular permission reviews
   - Immediate revocation when needed
   - Document permission changes

### Performance

1. **Network Optimization**
   - Use appropriate gas prices
   - Batch operations when possible
   - Monitor network congestion
   - Use testnets for development

2. **Caching**
   - Leverage browser caching
   - Use session storage appropriately
   - Clear cache when needed
   - Monitor cache performance

### Compliance

1. **Audit Trail**
   - All actions are logged
   - Regular audit reviews
   - Compliance reporting
   - Data retention policies

2. **Privacy**
   - Minimal data collection
   - User consent for data use
   - Data anonymization
   - GDPR compliance

## FAQ

### General Questions

**Q: What is a DID?**
A: A Decentralized Identifier (DID) is a unique identifier that you control, not a central authority. It's like a digital passport that you own.

**Q: Why use DID instead of username/password?**
A: DIDs provide better security, privacy, and control. You own your identity and can use it across different systems.

**Q: Do I need cryptocurrency to use DID authentication?**
A: You need a small amount of ETH for gas fees when syncing to the registry, but not for basic authentication.

**Q: Can I use multiple wallets?**
A: Yes, each wallet address creates a different DID. You can have multiple DIDs for different purposes.

### Technical Questions

**Q: What happens if I lose my wallet?**
A: If you lose your wallet and don't have the seed phrase, you'll lose access to that DID. Always backup your seed phrase securely.

**Q: Can I change my DID?**
A: Your DID is tied to your wallet address. To change it, you'd need to use a different wallet address.

**Q: How do I sync my DID to the registry?**
A: Use the "Sync to Registry" button in the DID management interface. This will store your DID on the blockchain.

**Q: What if the registry is down?**
A: The system works locally even if the registry is unavailable. Registry sync can be retried later.

### Business Questions

**Q: How do I get a role assigned?**
A: Contact your system administrator to request a role. Provide justification and any required documentation.

**Q: Can I have multiple roles?**
A: Yes, you can have multiple roles simultaneously. Permissions are combined from all active roles.

**Q: How long do roles last?**
A: Roles can be permanent or have expiration dates. Check with your administrator for specific policies.

**Q: What if I need different permissions?**
A: Request a role upgrade or custom role from your administrator. Explain why you need additional permissions.

### Troubleshooting Questions

**Q: Why can't I connect my wallet?**
A: Check that MetaMask is installed, unlocked, and on the correct network. Try refreshing the page.

**Q: Why is my signature invalid?**
A: Ensure you're signing with the correct account and the message hasn't been modified. Try generating a new message.

**Q: Why can't I access certain features?**
A: Check that your role has the required permissions. Contact your administrator if you need access.

**Q: Why is registry sync failing?**
A: Check your network connection, ensure you have sufficient ETH for gas, and try again during low network congestion.

## Conclusion

The DID-Based Access Control system provides a modern, secure, and decentralized approach to identity management in TidyGen ERP. By leveraging blockchain technology and Web3 standards, users have full control over their digital identity while maintaining the security and auditability required for enterprise applications.

For additional support or questions, please refer to the API documentation or contact our support team.
