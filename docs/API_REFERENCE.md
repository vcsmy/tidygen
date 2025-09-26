# TidyGen ERP - API Reference

## 🚀 **Overview**

This document provides comprehensive API reference for TidyGen ERP, including all available REST API endpoints, CLI commands, and Web3 integration interfaces. The API follows RESTful principles and provides both traditional HTTP endpoints and Web3 blockchain interactions.

### **Base URLs**
- **Development**: `http://localhost:8000/api/v1/`
- **Staging**: `https://staging-api.tidygen.io/api/v1/`
- **Production**: `https://api.tidygen.io/api/v1/`

### **Authentication**
All API endpoints require authentication using JWT tokens or Web3 wallet signatures.

---

## 🔐 **Authentication Endpoints**

### **JWT Authentication**

#### **Login**
```http
POST /api/v1/auth/login/
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "organization": {
      "id": 1,
      "name": "Acme Cleaning Services"
    }
  }
}
```

#### **Refresh Token**
```http
POST /api/v1/auth/refresh/
```

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### **Logout**
```http
POST /api/v1/auth/logout/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

### **DID Authentication**

#### **Create DID**
```http
POST /api/v1/auth/did/create/
```

**Request Body:**
```json
{
  "user_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
  "signature": "0x1234567890abcdef...",
  "message": "Sign this message to create your DID"
}
```

**Response:**
```json
{
  "did": "did:ethr:0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
  "status": "created",
  "created_at": "2024-01-15T10:00:00Z"
}
```

#### **Verify DID**
```http
POST /api/v1/auth/did/verify/
```

**Request Body:**
```json
{
  "did": "did:ethr:0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
  "signature": "0x1234567890abcdef...",
  "message": "Sign this message to verify your DID"
}
```

**Response:**
```json
{
  "verified": true,
  "user": {
    "id": 1,
    "did": "did:ethr:0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
    "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
  }
}
```

---

## 👥 **User Management Endpoints**

### **Users**

#### **List Users**
```http
GET /api/v1/users/
```

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20)
- `search` (string): Search by name or email
- `role` (string): Filter by role
- `organization` (int): Filter by organization ID

**Response:**
```json
{
  "count": 100,
  "next": "http://api.tidygen.io/api/v1/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "email": "user@example.com",
      "name": "John Doe",
      "role": "admin",
      "organization": {
        "id": 1,
        "name": "Acme Cleaning Services"
      },
      "created_at": "2024-01-15T10:00:00Z",
      "is_active": true
    }
  ]
}
```

#### **Create User**
```http
POST /api/v1/users/
```

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "name": "Jane Smith",
  "password": "securepassword",
  "role": "manager",
  "organization": 1
}
```

**Response:**
```json
{
  "id": 2,
  "email": "newuser@example.com",
  "name": "Jane Smith",
  "role": "manager",
  "organization": {
    "id": 1,
    "name": "Acme Cleaning Services"
  },
  "created_at": "2024-01-15T10:00:00Z",
  "is_active": true
}
```

#### **Get User Details**
```http
GET /api/v1/users/{id}/
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "role": "admin",
  "organization": {
    "id": 1,
    "name": "Acme Cleaning Services"
  },
  "profile": {
    "phone": "+1234567890",
    "address": "123 Main St, City, State",
    "timezone": "UTC"
  },
  "created_at": "2024-01-15T10:00:00Z",
  "last_login": "2024-01-15T09:00:00Z",
  "is_active": true
}
```

#### **Update User**
```http
PUT /api/v1/users/{id}/
```

**Request Body:**
```json
{
  "name": "John Updated",
  "role": "manager",
  "profile": {
    "phone": "+1234567890",
    "address": "456 New St, City, State"
  }
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Updated",
  "role": "manager",
  "organization": {
    "id": 1,
    "name": "Acme Cleaning Services"
  },
  "profile": {
    "phone": "+1234567890",
    "address": "456 New St, City, State",
    "timezone": "UTC"
  },
  "updated_at": "2024-01-15T11:00:00Z"
}
```

#### **Delete User**
```http
DELETE /api/v1/users/{id}/
```

**Response:**
```json
{
  "message": "User deleted successfully"
}
```

---

## 🏢 **Organization Management Endpoints**

### **Organizations**

#### **List Organizations**
```http
GET /api/v1/organizations/
```

**Response:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "name": "Acme Cleaning Services",
      "slug": "acme-cleaning",
      "description": "Professional cleaning services",
      "created_at": "2024-01-15T10:00:00Z",
      "member_count": 25
    }
  ]
}
```

#### **Create Organization**
```http
POST /api/v1/organizations/
```

**Request Body:**
```json
{
  "name": "New Cleaning Company",
  "slug": "new-cleaning",
  "description": "A new cleaning service company"
}
```

**Response:**
```json
{
  "id": 2,
  "name": "New Cleaning Company",
  "slug": "new-cleaning",
  "description": "A new cleaning service company",
  "created_at": "2024-01-15T10:00:00Z",
  "member_count": 1
}
```

#### **Get Organization Members**
```http
GET /api/v1/organizations/{id}/members/
```

**Response:**
```json
{
  "count": 25,
  "results": [
    {
      "id": 1,
      "user": {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com"
      },
      "role": "admin",
      "joined_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

#### **Add Member to Organization**
```http
POST /api/v1/organizations/{id}/members/
```

**Request Body:**
```json
{
  "user_id": 2,
  "role": "member"
}
```

**Response:**
```json
{
  "id": 26,
  "user": {
    "id": 2,
    "name": "Jane Smith",
    "email": "jane@example.com"
  },
  "role": "member",
  "joined_at": "2024-01-15T10:00:00Z"
}
```

---

## ⛓️ **Web3 Integration Endpoints**

### **Wallet Management**

#### **List Wallets**
```http
GET /api/v1/web3/wallets/
```

**Response:**
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "name": "Main Wallet",
      "address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
      "blockchain": "ethereum",
      "wallet_type": "external",
      "is_active": true,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

#### **Add Wallet**
```http
POST /api/v1/web3/wallets/
```

**Request Body:**
```json
{
  "name": "Secondary Wallet",
  "address": "0x8ba1f109551bD432803012645Hac136c",
  "blockchain": "ethereum",
  "wallet_type": "external"
}
```

**Response:**
```json
{
  "id": 2,
  "name": "Secondary Wallet",
  "address": "0x8ba1f109551bD432803012645Hac136c",
  "blockchain": "ethereum",
  "wallet_type": "external",
  "is_active": true,
  "verified": true,
  "created_at": "2024-01-15T10:00:00Z"
}
```

#### **Get Wallet Balance**
```http
GET /api/v1/web3/wallets/{id}/balance/
```

**Response:**
```json
{
  "wallet_id": 1,
  "address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
  "balances": [
    {
      "token": "ETH",
      "balance": "1.5",
      "usd_value": "3000.00"
    },
    {
      "token": "USDC",
      "balance": "1000.00",
      "usd_value": "1000.00"
    }
  ],
  "total_usd_value": "4000.00",
  "last_updated": "2024-01-15T10:00:00Z"
}
```

#### **Sync Wallet**
```http
POST /api/v1/web3/wallets/{id}/sync/
```

**Response:**
```json
{
  "synced": true,
  "transactions_found": 15,
  "last_sync": "2024-01-15T10:00:00Z"
}
```

### **Smart Contract Management**

#### **List Contracts**
```http
GET /api/v1/web3/contracts/
```

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "name": "ServiceContract",
      "address": "0xContractAddress123",
      "type": "service",
      "blockchain": "ethereum",
      "is_verified": true,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

#### **Deploy Contract**
```http
POST /api/v1/web3/contracts/
```

**Request Body:**
```json
{
  "name": "NewServiceContract",
  "type": "service",
  "parameters": {
    "client": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
    "provider": "0x8ba1f109551bD432803012645Hac136c",
    "amount": "100"
  }
}
```

**Response:**
```json
{
  "id": 2,
  "name": "NewServiceContract",
  "address": "0xNewContractAddress456",
  "type": "service",
  "blockchain": "ethereum",
  "tx_hash": "0xTransactionHash789",
  "status": "deployed",
  "created_at": "2024-01-15T10:00:00Z"
}
```

#### **Call Contract Method**
```http
POST /api/v1/web3/contracts/{address}/call/
```

**Request Body:**
```json
{
  "method": "completeService",
  "parameters": [1, "0xCompletionHash123"]
}
```

**Response:**
```json
{
  "result": "success",
  "tx_hash": "0xTransactionHash456",
  "gas_used": 21000,
  "gas_price": "20000000000"
}
```

#### **Get Contract Events**
```http
GET /api/v1/web3/contracts/{address}/events/
```

**Query Parameters:**
- `from_block` (int): Starting block number
- `to_block` (int): Ending block number
- `event_name` (string): Filter by event name

**Response:**
```json
{
  "count": 10,
  "results": [
    {
      "event_name": "ServiceCompleted",
      "block_number": 12345,
      "transaction_hash": "0xTxHash123",
      "log_index": 0,
      "data": {
        "serviceId": 1,
        "provider": "0x8ba1f109551bD432803012645Hac136c"
      },
      "timestamp": "2024-01-15T10:00:00Z"
    }
  ]
}
```

### **Transaction Management**

#### **List Transactions**
```http
GET /api/v1/web3/transactions/
```

**Query Parameters:**
- `wallet` (string): Filter by wallet address
- `status` (string): Filter by status (pending, confirmed, failed)
- `type` (string): Filter by transaction type

**Response:**
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "tx_hash": "0xTransactionHash123",
      "wallet": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
      "transaction_type": "send",
      "amount": "1.0",
      "token": "ETH",
      "status": "confirmed",
      "gas_used": 21000,
      "gas_price": "20000000000",
      "block_number": 12345,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

#### **Create Transaction**
```http
POST /api/v1/web3/transactions/
```

**Request Body:**
```json
{
  "to": "0x8ba1f109551bD432803012645Hac136c",
  "amount": "1.0",
  "token": "ETH",
  "purpose": "service_payment"
}
```

**Response:**
```json
{
  "id": 2,
  "tx_hash": "0xTransactionHash456",
  "status": "pending",
  "created_at": "2024-01-15T10:00:00Z"
}
```

#### **Get Transaction Details**
```http
GET /api/v1/web3/transactions/{tx_hash}/
```

**Response:**
```json
{
  "id": 1,
  "tx_hash": "0xTransactionHash123",
  "wallet": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
  "transaction_type": "send",
  "amount": "1.0",
  "token": "ETH",
  "status": "confirmed",
  "gas_used": 21000,
  "gas_price": "20000000000",
  "block_number": 12345,
  "confirmations": 12,
  "created_at": "2024-01-15T10:00:00Z"
}
```

---

## 🧹 **Service Management Endpoints**

### **Services**

#### **List Services**
```http
GET /api/v1/services/
```

**Query Parameters:**
- `status` (string): Filter by status (scheduled, in_progress, completed, cancelled)
- `client` (string): Filter by client address
- `provider` (string): Filter by provider address
- `service_type` (string): Filter by service type

**Response:**
```json
{
  "count": 20,
  "results": [
    {
      "id": 1,
      "service_id": 1,
      "client": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
      "provider": "0x8ba1f109551bD432803012645Hac136c",
      "service_type": "office_cleaning",
      "status": "scheduled",
      "amount": "100.00",
      "contract_address": "0xContractAddress123",
      "scheduled_time": "2024-01-16T09:00:00Z",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

#### **Create Service**
```http
POST /api/v1/services/
```

**Request Body:**
```json
{
  "client": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
  "provider": "0x8ba1f109551bD432803012645Hac136c",
  "service_type": "office_cleaning",
  "location": "0xLocationHash123",
  "amount": "100.00",
  "scheduled_time": "2024-01-16T09:00:00Z"
}
```

**Response:**
```json
{
  "id": 2,
  "service_id": 2,
  "client": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
  "provider": "0x8ba1f109551bD432803012645Hac136c",
  "service_type": "office_cleaning",
  "status": "scheduled",
  "amount": "100.00",
  "contract_address": "0xNewContractAddress456",
  "scheduled_time": "2024-01-16T09:00:00Z",
  "created_at": "2024-01-15T10:00:00Z"
}
```

#### **Get Service Details**
```http
GET /api/v1/services/{id}/
```

**Response:**
```json
{
  "id": 1,
  "service_id": 1,
  "client": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
  "provider": "0x8ba1f109551bD432803012645Hac136c",
  "service_type": "office_cleaning",
  "status": "in_progress",
  "amount": "100.00",
  "contract_address": "0xContractAddress123",
  "scheduled_time": "2024-01-16T09:00:00Z",
  "started_time": "2024-01-16T09:05:00Z",
  "progress": 50,
  "created_at": "2024-01-15T10:00:00Z"
}
```

#### **Complete Service**
```http
POST /api/v1/services/{id}/complete/
```

**Request Body:**
```json
{
  "completion_hash": "0xCompletionHash123",
  "verification_data": {
    "photos": ["ipfs://PhotoHash1", "ipfs://PhotoHash2"],
    "notes": "Service completed successfully",
    "quality_rating": 5
  }
}
```

**Response:**
```json
{
  "id": 1,
  "status": "completed",
  "completion_hash": "0xCompletionHash123",
  "completed_time": "2024-01-16T10:00:00Z",
  "tx_hash": "0xTransactionHash789",
  "verification_data": {
    "photos": ["ipfs://PhotoHash1", "ipfs://PhotoHash2"],
    "notes": "Service completed successfully",
    "quality_rating": 5
  }
}
```

#### **Verify Service**
```http
POST /api/v1/services/{id}/verify/
```

**Request Body:**
```json
{
  "verified": true,
  "rating": 5,
  "feedback": "Excellent service quality"
}
```

**Response:**
```json
{
  "id": 1,
  "verified": true,
  "rating": 5,
  "feedback": "Excellent service quality",
  "payment_released": true,
  "payment_tx_hash": "0xPaymentTxHash123"
}
```

---

## 📦 **Asset Management Endpoints**

### **Assets**

#### **List Assets**
```http
GET /api/v1/assets/
```

**Response:**
```json
{
  "count": 15,
  "results": [
    {
      "id": 1,
      "name": "Cleaning Equipment Set",
      "description": "Professional cleaning equipment",
      "value": 1000.00,
      "category": "equipment",
      "status": "active",
      "nft_token_id": null,
      "nft_contract_address": null,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

#### **Create Asset**
```http
POST /api/v1/assets/
```

**Request Body:**
```json
{
  "name": "New Cleaning Equipment",
  "description": "Latest model cleaning equipment",
  "value": 1500.00,
  "category": "equipment",
  "metadata": {
    "brand": "Professional Clean",
    "model": "PC-2024",
    "serial_number": "PC2024001"
  }
}
```

**Response:**
```json
{
  "id": 2,
  "name": "New Cleaning Equipment",
  "description": "Latest model cleaning equipment",
  "value": 1500.00,
  "category": "equipment",
  "status": "active",
  "nft_token_id": null,
  "nft_contract_address": null,
  "metadata": {
    "brand": "Professional Clean",
    "model": "PC-2024",
    "serial_number": "PC2024001"
  },
  "created_at": "2024-01-15T10:00:00Z"
}
```

#### **Tokenize Asset**
```http
POST /api/v1/assets/{id}/tokenize/
```

**Request Body:**
```json
{
  "metadata_uri": "ipfs://AssetMetadataHash123"
}
```

**Response:**
```json
{
  "id": 2,
  "nft_token_id": 1,
  "nft_contract_address": "0xNFTContractAddress123",
  "metadata_uri": "ipfs://AssetMetadataHash123",
  "tx_hash": "0xTokenizationTxHash456",
  "status": "tokenized",
  "tokenized_at": "2024-01-15T10:00:00Z"
}
```

#### **Get NFT Details**
```http
GET /api/v1/assets/{id}/nft/
```

**Response:**
```json
{
  "asset_id": 2,
  "token_id": 1,
  "contract_address": "0xNFTContractAddress123",
  "owner": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
  "metadata": {
    "name": "New Cleaning Equipment",
    "description": "Latest model cleaning equipment",
    "image": "ipfs://AssetImageHash123",
    "attributes": [
      {
        "trait_type": "Brand",
        "value": "Professional Clean"
      },
      {
        "trait_type": "Value",
        "value": "1500.00"
      }
    ]
  },
  "created_at": "2024-01-15T10:00:00Z"
}
```

---

## 🚛 **Field Operations Endpoints**

### **Field Teams**

#### **List Field Teams**
```http
GET /api/v1/field-operations/teams/
```

**Response:**
```json
{
  "count": 8,
  "results": [
    {
      "id": 1,
      "name": "Team Alpha",
      "leader": {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com"
      },
      "specialization": "office_cleaning",
      "member_count": 5,
      "status": "active",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

#### **Create Field Team**
```http
POST /api/v1/field-operations/teams/
```

**Request Body:**
```json
{
  "name": "Team Beta",
  "leader_id": 2,
  "specialization": "residential_cleaning",
  "description": "Specialized in residential cleaning services"
}
```

**Response:**
```json
{
  "id": 2,
  "name": "Team Beta",
  "leader": {
    "id": 2,
    "name": "Jane Smith",
    "email": "jane@example.com"
  },
  "specialization": "residential_cleaning",
  "description": "Specialized in residential cleaning services",
  "member_count": 1,
  "status": "active",
  "created_at": "2024-01-15T10:00:00Z"
}
```

#### **Assign Job to Team**
```http
POST /api/v1/field-operations/teams/{id}/assign-job/
```

**Request Body:**
```json
{
  "job_id": 1,
  "priority": "high",
  "assigned_by": 1
}
```

**Response:**
```json
{
  "team_id": 1,
  "job_id": 1,
  "assigned_at": "2024-01-15T10:00:00Z",
  "estimated_completion": "2024-01-15T12:00:00Z",
  "priority": "high"
}
```

### **Service Routes**

#### **List Service Routes**
```http
GET /api/v1/field-operations/routes/
```

**Response:**
```json
{
  "count": 12,
  "results": [
    {
      "id": 1,
      "name": "Downtown Office Route",
      "team": {
        "id": 1,
        "name": "Team Alpha"
      },
      "status": "active",
      "stop_count": 5,
      "estimated_duration": 180,
      "date": "2024-01-16",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

#### **Create Optimized Route**
```http
POST /api/v1/field-operations/routes/
```

**Request Body:**
```json
{
  "stops": [
    {
      "address": "123 Main St, City, State",
      "service_type": "office_cleaning",
      "estimated_duration": 60
    },
    {
      "address": "456 Oak Ave, City, State",
      "service_type": "office_cleaning",
      "estimated_duration": 45
    }
  ],
  "team_id": 1,
  "date": "2024-01-16"
}
```

**Response:**
```json
{
  "id": 2,
  "name": "Optimized Route 2024-01-16",
  "team": {
    "id": 1,
    "name": "Team Alpha"
  },
  "status": "scheduled",
  "optimized_route": [
    {
      "order": 1,
      "address": "123 Main St, City, State",
      "service_type": "office_cleaning",
      "estimated_duration": 60,
      "estimated_arrival": "2024-01-16T09:00:00Z"
    },
    {
      "order": 2,
      "address": "456 Oak Ave, City, State",
      "service_type": "office_cleaning",
      "estimated_duration": 45,
      "estimated_arrival": "2024-01-16T10:00:00Z"
    }
  ],
  "total_estimated_time": 105,
  "created_at": "2024-01-15T10:00:00Z"
}
```

#### **Start Route**
```http
POST /api/v1/field-operations/routes/{id}/start/
```

**Response:**
```json
{
  "route_id": 1,
  "started_at": "2024-01-16T08:30:00Z",
  "status": "in_progress",
  "estimated_completion": "2024-01-16T11:30:00Z"
}
```

#### **Complete Route**
```http
POST /api/v1/field-operations/routes/{id}/complete/
```

**Request Body:**
```json
{
  "completion_data": {
    "actual_duration": 175,
    "stops_completed": 5,
    "issues": [],
    "notes": "Route completed successfully"
  }
}
```

**Response:**
```json
{
  "route_id": 1,
  "completed_at": "2024-01-16T11:25:00Z",
  "status": "completed",
  "total_time": 175,
  "efficiency": 97,
  "stops_completed": 5
}
```

---

## 💻 **CLI Commands**

### **Installation**

```bash
# Install TidyGen CLI
npm install -g @tidygen/cli

# Or using pip
pip install tidygen-cli
```

### **Authentication**

```bash
# Login with email/password
tidygen auth login --email user@example.com --password securepassword

# Login with wallet
tidygen auth login --wallet 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6

# Check authentication status
tidygen auth status
```

### **Service Management**

```bash
# List services
tidygen services list

# Create service
tidygen services create \
  --client 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6 \
  --provider 0x8ba1f109551bD432803012645Hac136c \
  --type office_cleaning \
  --amount 100.00

# Complete service
tidygen services complete --id 1 --hash 0xCompletionHash123

# Verify service
tidygen services verify --id 1 --verified true --rating 5
```

### **Asset Management**

```bash
# List assets
tidygen assets list

# Create asset
tidygen assets create \
  --name "Cleaning Equipment" \
  --description "Professional cleaning equipment" \
  --value 1000.00 \
  --category equipment

# Tokenize asset
tidygen assets tokenize --id 1 --metadata-uri ipfs://MetadataHash123
```

### **Web3 Operations**

```bash
# List wallets
tidygen web3 wallets list

# Add wallet
tidygen web3 wallets add \
  --name "Main Wallet" \
  --address 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6 \
  --blockchain ethereum

# Get wallet balance
tidygen web3 wallets balance --id 1

# Deploy contract
tidygen web3 contracts deploy \
  --name "ServiceContract" \
  --type service \
  --parameters '{"client":"0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6","provider":"0x8ba1f109551bD432803012645Hac136c","amount":"100"}'

# Call contract method
tidygen web3 contracts call \
  --address 0xContractAddress123 \
  --method completeService \
  --parameters '[1,"0xCompletionHash123"]'
```

### **Field Operations**

```bash
# List teams
tidygen field-operations teams list

# Create team
tidygen field-operations teams create \
  --name "Team Alpha" \
  --leader-id 1 \
  --specialization office_cleaning

# List routes
tidygen field-operations routes list

# Create route
tidygen field-operations routes create \
  --stops '[{"address":"123 Main St","service_type":"office_cleaning","duration":60}]' \
  --team-id 1 \
  --date 2024-01-16

# Start route
tidygen field-operations routes start --id 1

# Complete route
tidygen field-operations routes complete --id 1 --duration 175
```

### **Configuration**

```bash
# Set API endpoint
tidygen config set api-endpoint https://api.tidygen.io

# Set default organization
tidygen config set organization 1

# View configuration
tidygen config list

# Reset configuration
tidygen config reset
```

---

## 📊 **Error Handling**

### **Error Response Format**

All API endpoints return errors in the following format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "reason": "Invalid email format"
    }
  },
  "timestamp": "2024-01-15T10:00:00Z",
  "request_id": "req_123456789"
}
```

### **Common Error Codes**

- `AUTHENTICATION_REQUIRED`: Authentication token required
- `INVALID_TOKEN`: Invalid or expired authentication token
- `PERMISSION_DENIED`: Insufficient permissions for operation
- `VALIDATION_ERROR`: Invalid input data
- `RESOURCE_NOT_FOUND`: Requested resource not found
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `BLOCKCHAIN_ERROR`: Blockchain operation failed
- `CONTRACT_ERROR`: Smart contract operation failed

### **HTTP Status Codes**

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

---

## 🔧 **SDK Examples**

### **JavaScript/TypeScript SDK**

```typescript
import { TidyGenClient } from '@tidygen/sdk';

const client = new TidyGenClient({
  apiEndpoint: 'https://api.tidygen.io',
  apiKey: 'your-api-key'
});

// Create service
const service = await client.services.create({
  client: '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6',
  provider: '0x8ba1f109551bD432803012645Hac136c',
  serviceType: 'office_cleaning',
  amount: '100.00'
});

// Complete service
await client.services.complete(service.id, {
  completionHash: '0xCompletionHash123'
});
```

### **Python SDK**

```python
from tidygen import TidyGenClient

client = TidyGenClient(
    api_endpoint='https://api.tidygen.io',
    api_key='your-api-key'
)

# Create service
service = client.services.create({
    'client': '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6',
    'provider': '0x8ba1f109551bD432803012645Hac136c',
    'service_type': 'office_cleaning',
    'amount': '100.00'
})

# Complete service
client.services.complete(service['id'], {
    'completion_hash': '0xCompletionHash123'
})
```

---

This comprehensive API reference provides complete documentation for all TidyGen ERP endpoints, CLI commands, and integration examples. For additional support, please refer to the [Documentation Index](INDEX.md) or contact our support team.
