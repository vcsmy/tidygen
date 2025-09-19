# Smart Contract Ledger Integration Guide

## 🎯 **Overview**

This guide provides comprehensive instructions for integrating the Smart Contract Ledger functionality into TidyGen ERP. The ledger system enables tamper-proof logging of all financial transactions to blockchain networks, providing enhanced transparency and audit capabilities.

## 📋 **Table of Contents**

1. [Quick Start](#1-quick-start)
2. [Installation & Setup](#2-installation--setup)
3. [Configuration](#3-configuration)
4. [API Usage](#4-api-usage)
5. [Smart Contract Deployment](#5-smart-contract-deployment)
6. [Integration Examples](#6-integration-examples)
7. [Testing](#7-testing)
8. [Troubleshooting](#8-troubleshooting)
9. [Best Practices](#9-best-practices)

---

## 1. Quick Start

### **Basic Integration**

```python
# 1. Import the transaction service
from apps.ledger.services import TransactionService

# 2. Create a transaction service instance
transaction_service = TransactionService(organization_id="your-org-id")

# 3. Log a transaction to the blockchain
ledger_transaction = transaction_service.create_transaction(
    transaction_type="invoice",
    source_module="finance",
    source_id="INV-001",
    transaction_data={
        "amount": 1000.00,
        "currency": "USD",
        "description": "Invoice payment"
    },
    organization_id="your-org-id"
)

# 4. Submit to blockchain
success = transaction_service.submit_transaction(ledger_transaction)
```

### **REST API Usage**

```bash
# Push a transaction to the ledger
curl -X POST http://localhost:8000/api/v1/ledger/push/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "transaction_type": "invoice",
    "source_module": "finance",
    "source_id": "INV-001",
    "transaction_data": {
      "amount": 1000.00,
      "currency": "USD",
      "description": "Invoice payment"
    }
  }'
```

---

## 2. Installation & Setup

### **Dependencies**

Add the following dependencies to your `requirements.txt`:

```txt
# Blockchain integration
web3>=6.0.0
substrate-interface>=1.7.0

# Additional dependencies (if not already present)
cryptography>=3.4.8
pycryptodome>=3.15.0
```

### **Installation Steps**

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run database migrations:**
   ```bash
   python manage.py migrate ledger
   ```

3. **Create superuser (if needed):**
   ```bash
   python manage.py createsuperuser
   ```

4. **Collect static files:**
   ```bash
   python manage.py collectstatic
   ```

### **Environment Variables**

Add the following environment variables to your `.env` file:

```env
# Blockchain Configuration
LEDGER_AUTO_LOG_ENABLED=true
BLOCKCHAIN_NETWORK=ethereum
RPC_ENDPOINT=http://localhost:8545
CONTRACT_ADDRESS=0x...
PRIVATE_KEY=your-private-key

# Optional: Gas settings
GAS_LIMIT=1000000
GAS_PRICE=20000000000

# Optional: Batch settings
BATCH_SIZE=10
BATCH_TIMEOUT=300
```

---

## 3. Configuration

### **Django Settings**

The ledger app is automatically configured when added to `INSTALLED_APPS`. No additional settings are required.

### **Ledger Configuration**

Create a ledger configuration for your organization:

```python
from apps.ledger.models import LedgerConfiguration

config = LedgerConfiguration.objects.create(
    organization=your_organization,
    blockchain_network='ethereum',
    rpc_endpoint='http://localhost:8545',
    contract_address='0x...',
    batch_size=10,
    batch_timeout=300,
    retry_attempts=3,
    gas_limit=1000000,
    auto_confirm=True,
    is_active=True
)
```

### **Smart Contract Configuration**

1. **Deploy the smart contract:**
   ```bash
   cd smart_contracts/ledger
   npm install
   npx hardhat compile
   npx hardhat run scripts/deploy.js --network localhost
   ```

2. **Update configuration with contract address:**
   ```python
   config.contract_address = "0x..."  # From deployment output
   config.save()
   ```

---

## 4. API Usage

### **Core Endpoints**

#### **Push Transaction**
```http
POST /api/v1/ledger/push/
Content-Type: application/json
Authorization: Bearer <token>

{
  "transaction_type": "invoice",
  "source_module": "finance", 
  "source_id": "INV-001",
  "transaction_data": {
    "amount": 1000.00,
    "currency": "USD",
    "description": "Invoice payment"
  }
}
```

**Response:**
```json
{
  "id": "uuid",
  "hash": "sha256_hash",
  "blockchain_hash": "0x...",
  "status": "pending",
  "message": "Transaction logged successfully",
  "created_at": "2025-01-XX"
}
```

#### **Verify Transaction**
```http
GET /api/v1/ledger/verify/{transaction_id}/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "transaction_id": "uuid",
  "hash_valid": true,
  "blockchain_confirmed": true,
  "blockchain_hash": "0x...",
  "block_number": 12345,
  "verification_timestamp": "2025-01-XX"
}
```

#### **Get Audit Trail**
```http
GET /api/v1/ledger/audit/?start_date=2025-01-01&end_date=2025-01-31&limit=100
Authorization: Bearer <token>
```

**Response:**
```json
{
  "transactions": [...],
  "total_count": 150,
  "has_next": true,
  "has_previous": false,
  "next_offset": 100,
  "previous_offset": null
}
```

### **Transaction Management**

#### **Submit Transaction**
```http
POST /api/v1/ledger/transactions/{id}/submit/
Authorization: Bearer <token>
```

#### **Confirm Transaction**
```http
POST /api/v1/ledger/transactions/{id}/confirm/
Content-Type: application/json
Authorization: Bearer <token>

{
  "block_number": 12345,
  "transaction_index": 0,
  "gas_used": 21000,
  "gas_price": 20000000000
}
```

#### **Get Transaction Details**
```http
GET /api/v1/ledger/transactions/{id}/
Authorization: Bearer <token>
```

### **Batch Operations**

#### **Create Batch**
```http
POST /api/v1/ledger/batches/
Content-Type: application/json
Authorization: Bearer <token>

{
  "transaction_ids": ["uuid1", "uuid2", "uuid3"]
}
```

#### **Submit Batch**
```http
POST /api/v1/ledger/batches/{id}/submit/
Authorization: Bearer <token>
```

---

## 5. Smart Contract Deployment

### **Local Development**

1. **Start local blockchain:**
   ```bash
   npx hardhat node
   ```

2. **Deploy contract:**
   ```bash
   npx hardhat run scripts/deploy.js --network localhost
   ```

3. **Test contract:**
   ```bash
   npx hardhat test
   ```

### **Testnet Deployment**

1. **Configure network:**
   ```bash
   # Add your private key to .env
   echo "PRIVATE_KEY=your-private-key" >> .env
   echo "SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_KEY" >> .env
   ```

2. **Deploy to Sepolia:**
   ```bash
   npx hardhat run scripts/deploy.js --network sepolia
   ```

3. **Verify contract:**
   ```bash
   npx hardhat verify --network sepolia <contract-address>
   ```

### **Mainnet Deployment**

1. **Configure mainnet:**
   ```bash
   echo "MAINNET_RPC_URL=https://mainnet.infura.io/v3/YOUR_KEY" >> .env
   echo "ETHERSCAN_API_KEY=your-etherscan-key" >> .env
   ```

2. **Deploy to mainnet:**
   ```bash
   npx hardhat run scripts/deploy.js --network mainnet
   ```

3. **Verify contract:**
   ```bash
   npx hardhat verify --network mainnet <contract-address>
   ```

---

## 6. Integration Examples

### **Automatic Transaction Logging**

The ledger system automatically logs transactions from other ERP modules using Django signals:

```python
# In your finance app models.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Invoice

@receiver(post_save, sender=Invoice)
def log_invoice_to_ledger(sender, instance, created, **kwargs):
    """Automatically log invoice to blockchain ledger."""
    if created:
        from apps.ledger.services import TransactionService
        
        transaction_service = TransactionService(
            organization_id=str(instance.organization.id)
        )
        
        transaction_service.create_transaction(
            transaction_type="invoice",
            source_module="finance",
            source_id=str(instance.id),
            transaction_data={
                "amount": float(instance.total_amount),
                "currency": instance.currency,
                "description": f"Invoice {instance.invoice_number}",
                "invoice_number": instance.invoice_number,
                "client_name": instance.client.name,
                "due_date": instance.due_date.isoformat() if instance.due_date else None,
                "status": instance.status
            },
            organization_id=str(instance.organization.id)
        )
```

### **Manual Transaction Logging**

```python
from apps.ledger.services import TransactionService

def log_custom_transaction(organization_id, transaction_data):
    """Log a custom transaction to the ledger."""
    transaction_service = TransactionService(organization_id=organization_id)
    
    ledger_transaction = transaction_service.create_transaction(
        transaction_type="custom",
        source_module="custom_module",
        source_id="CUSTOM-001",
        transaction_data=transaction_data,
        organization_id=organization_id
    )
    
    # Submit to blockchain
    success = transaction_service.submit_transaction(ledger_transaction)
    
    if success:
        print(f"Transaction logged successfully: {ledger_transaction.id}")
    else:
        print(f"Failed to log transaction: {ledger_transaction.id}")
    
    return ledger_transaction
```

### **Batch Transaction Processing**

```python
def process_batch_transactions(organization_id, transactions_data):
    """Process multiple transactions in a batch."""
    transaction_service = TransactionService(organization_id=organization_id)
    
    # Create individual transactions
    transaction_ids = []
    for data in transactions_data:
        ledger_transaction = transaction_service.create_transaction(
            transaction_type=data["type"],
            source_module=data["module"],
            source_id=data["id"],
            transaction_data=data["data"],
            organization_id=organization_id
        )
        transaction_ids.append(str(ledger_transaction.id))
    
    # Create and submit batch
    batch = transaction_service.create_batch(
        transaction_ids=transaction_ids,
        organization_id=organization_id
    )
    
    success = transaction_service.submit_batch(batch)
    
    return batch, success
```

### **Transaction Verification**

```python
def verify_transaction_integrity(transaction_id):
    """Verify a transaction's integrity."""
    from apps.ledger.models import LedgerTransaction
    
    try:
        ledger_transaction = LedgerTransaction.objects.get(id=transaction_id)
        transaction_service = TransactionService(
            organization_id=str(ledger_transaction.organization.id)
        )
        
        verification_result = transaction_service.verify_transaction(
            ledger_transaction=ledger_transaction,
            verify_hash=True,
            verify_blockchain=True
        )
        
        return verification_result
    except LedgerTransaction.DoesNotExist:
        return {"error": "Transaction not found"}
```

---

## 7. Testing

### **Unit Tests**

```python
# tests/test_ledger.py
from django.test import TestCase
from apps.ledger.services import TransactionService
from apps.ledger.models import LedgerTransaction

class LedgerTestCase(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name="Test Org")
        self.transaction_service = TransactionService(
            organization_id=str(self.organization.id)
        )
    
    def test_create_transaction(self):
        """Test transaction creation."""
        transaction = self.transaction_service.create_transaction(
            transaction_type="invoice",
            source_module="finance",
            source_id="TEST-001",
            transaction_data={
                "amount": 100.00,
                "currency": "USD",
                "description": "Test invoice"
            },
            organization_id=str(self.organization.id)
        )
        
        self.assertIsNotNone(transaction.id)
        self.assertEqual(transaction.transaction_type, "invoice")
        self.assertEqual(transaction.status, "pending")
    
    def test_transaction_hash_generation(self):
        """Test transaction hash generation."""
        transaction = self.transaction_service.create_transaction(
            transaction_type="invoice",
            source_module="finance",
            source_id="TEST-002",
            transaction_data={
                "amount": 200.00,
                "currency": "USD",
                "description": "Test invoice 2"
            },
            organization_id=str(self.organization.id)
        )
        
        self.assertIsNotNone(transaction.hash)
        self.assertEqual(len(transaction.hash), 64)  # SHA256 hash length
```

### **Integration Tests**

```python
# tests/test_integration.py
import requests
from django.test import TestCase

class LedgerAPITestCase(TestCase):
    def setUp(self):
        self.base_url = "http://localhost:8000/api/v1/ledger"
        self.auth_token = "your-jwt-token"
        self.headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_push_transaction(self):
        """Test pushing a transaction via API."""
        data = {
            "transaction_type": "invoice",
            "source_module": "finance",
            "source_id": "API-TEST-001",
            "transaction_data": {
                "amount": 500.00,
                "currency": "USD",
                "description": "API test invoice"
            }
        }
        
        response = requests.post(
            f"{self.base_url}/push/",
            json=data,
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.json())
        self.assertIn("hash", response.json())
```

### **Smart Contract Tests**

```bash
# Run smart contract tests
cd smart_contracts/ledger
npx hardhat test

# Run with coverage
npx hardhat coverage

# Run gas report
REPORT_GAS=true npx hardhat test
```

---

## 8. Troubleshooting

### **Common Issues**

#### **1. Transaction Submission Fails**

**Problem:** Transactions fail to submit to blockchain.

**Solutions:**
- Check RPC endpoint connectivity
- Verify contract address is correct
- Ensure sufficient gas limit
- Check private key permissions

```python
# Debug connection
from apps.ledger.services import BlockchainService

service = BlockchainService(network='ethereum', rpc_endpoint='your-rpc')
print(f"Connected: {service.is_connected()}")
```

#### **2. Hash Verification Fails**

**Problem:** Transaction hash verification returns false.

**Solutions:**
- Ensure transaction data hasn't been modified
- Check organization ID consistency
- Verify hash generation algorithm

```python
# Debug hash verification
transaction = LedgerTransaction.objects.get(id='your-id')
print(f"Hash valid: {transaction.verify_hash()}")
print(f"Expected hash: {transaction.hash}")
```

#### **3. Batch Processing Issues**

**Problem:** Batch transactions fail to process.

**Solutions:**
- Check batch size limits
- Verify all transactions are in pending status
- Ensure sufficient gas for batch operation

```python
# Debug batch
batch = LedgerBatch.objects.get(id='your-batch-id')
print(f"Transaction count: {batch.transaction_count}")
print(f"Status: {batch.status}")
```

### **Logging and Monitoring**

Enable detailed logging:

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'ledger.log',
        },
    },
    'loggers': {
        'apps.ledger': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### **Performance Optimization**

1. **Use batch processing for multiple transactions**
2. **Implement connection pooling for RPC calls**
3. **Cache blockchain state for verification**
4. **Use async processing for non-critical operations**

```python
# Async transaction processing
import asyncio
from asgiref.sync import sync_to_async

async def process_transactions_async(transactions):
    """Process transactions asynchronously."""
    tasks = []
    for transaction in transactions:
        task = sync_to_async(transaction_service.submit_transaction)(transaction)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

---

## 9. Best Practices

### **Security**

1. **Never expose private keys in code**
2. **Use environment variables for sensitive data**
3. **Implement proper access controls**
4. **Regular security audits**

### **Performance**

1. **Batch transactions when possible**
2. **Use appropriate gas limits**
3. **Implement retry logic with exponential backoff**
4. **Monitor blockchain network status**

### **Reliability**

1. **Implement comprehensive error handling**
2. **Use database transactions for consistency**
3. **Implement health checks**
4. **Monitor transaction status**

### **Maintenance**

1. **Regular contract updates**
2. **Monitor gas costs**
3. **Keep dependencies updated**
4. **Document all changes**

---

## 📚 **Additional Resources**

- [Smart Contract Ledger Implementation Plan](./SMART_CONTRACT_LEDGER_IMPLEMENTATION_PLAN.md)
- [API Documentation](../api-documentation/API_ENDPOINTS_SUMMARY.md)
- [Web3 Integration Guide](../web3/WEB3_TECHNICAL_IMPLEMENTATION.md)
- [Testing Documentation](../testing/README.md)

---

**This integration guide provides everything needed to successfully implement the Smart Contract Ledger functionality in TidyGen ERP. For additional support, refer to the troubleshooting section or contact the development team.**
