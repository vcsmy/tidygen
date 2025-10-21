# TidyGen Community Edition - System Architecture

## 📋 **Table of Contents**

1. [Overview](#overview)
2. [System Components](#system-components)
3. [Architecture Layers](#architecture-layers)
4. [Data Flow](#data-flow)
5. [Use Cases](#use-cases)
6. [Integration Points](#integration-points)
7. [Security Architecture](#security-architecture)
8. [Deployment Architecture](#deployment-architecture)

---

## 1. Overview

### **Hybrid Web2 + Web3 Design**

TidyGen Community Edition implements a **hybrid architecture** that combines traditional Web2 technologies (Django REST API, PostgreSQL database) with cutting-edge Web3 blockchain capabilities (Substrate pallets, Polkadot.js). This approach provides:

- ✅ **Best of Both Worlds**: Fast, familiar Web2 UX with Web3 transparency and immutability
- ✅ **Gradual Adoption**: Users can leverage blockchain features without abandoning existing workflows
- ✅ **Data Sovereignty**: Critical data anchored on-chain, operational data in traditional database
- ✅ **Scalability**: High-performance database for queries, blockchain for verification
- ✅ **Interoperability**: Seamless integration between centralized and decentralized layers

### **Design Philosophy**

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  Traditional ERP Functionality (Web2)                   │
│  ├─ Fast queries and reporting                         │
│  ├─ Complex business logic                             │
│  ├─ User-friendly interfaces                           │
│  └─ Familiar authentication                            │
│                                                         │
│                         +                               │
│                                                         │
│  Blockchain Enhancements (Web3)                         │
│  ├─ Immutable audit trails                             │
│  ├─ Decentralized identity                             │
│  ├─ DAO governance                                     │
│  └─ Cryptographic verification                         │
│                                                         │
│                         =                               │
│                                                         │
│  Next-Generation ERP System                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 2. System Components

### **Component Stack**

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[React 18 + TypeScript]
        B[Tailwind CSS + Shadcn/ui]
        C[Polkadot.js Extension]
        D[React Query + Axios]
    end
    
    subgraph "Backend Layer"
        E[Django 4.2 + DRF]
        F[PostgreSQL Database]
        G[Redis Cache]
        H[Celery Workers]
        I[Python Substrate Client]
    end
    
    subgraph "Blockchain Layer"
        J[Substrate Node]
        K[pallet-ledger]
        L[pallet-did]
        M[pallet-dao]
    end
    
    A --> E
    A --> C
    C --> J
    E --> I
    I --> J
    E --> F
    E --> G
    E --> H
```

### **2.1 Frontend: React + TypeScript**

**Technology Stack:**
- React 18 with TypeScript
- Vite for build tooling
- Tailwind CSS for styling
- Shadcn/ui component library
- React Query for state management
- Polkadot.js for blockchain interaction

**Key Features:**
- Single Page Application (SPA)
- Server-side rendering ready
- Real-time updates via WebSocket
- Responsive design
- Progressive Web App (PWA) capable

**Web3 Integration:**
- Polkadot.js extension connection
- Wallet management UI
- Transaction signing
- Blockchain state queries

### **2.2 Backend: Django REST Framework**

**Technology Stack:**
- Django 4.2
- Django REST Framework (DRF)
- PostgreSQL for relational data
- Redis for caching and sessions
- Celery for async tasks
- JWT authentication

**Key Features:**
- RESTful API design
- Role-based access control (RBAC)
- Comprehensive business logic
- 25 ERP modules
- API documentation (Swagger/OpenAPI)

**Web3 Integration:**
- Python substrate-interface library
- Automatic blockchain anchoring
- DID-based authentication
- DAO proposal synchronization

### **2.3 Blockchain: Substrate Runtime**

**Technology Stack:**
- Substrate FRAME
- Rust 2021 edition
- WebAssembly runtime
- RocksDB for chain storage

**Custom Pallets:**
1. **pallet-ledger**: Invoice and transaction ledger
2. **pallet-did**: Decentralized identity management
3. **pallet-dao**: On-chain governance

**Consensus:**
- Development: Instant finality (dev mode)
- Production: Aura + GRANDPA (or parachain)

---

## 3. Architecture Layers

### **Three-Tier Architecture**

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  PRESENTATION LAYER (Frontend)                      │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │   React UI  │  │ Polkadot.js  │  │  Wallet   │ │
│  │   Components│  │  Extension   │  │ Extension │ │
│  └──────┬──────┘  └───────┬──────┘  └─────┬─────┘ │
│         │                 │                │       │
└─────────┼─────────────────┼────────────────┼───────┘
          │                 │                │
          │                 │                │
┌─────────┼─────────────────┼────────────────┼───────┐
│         │                 │                │       │
│  APPLICATION LAYER (Backend)                │       │
│  ┌──────▼──────┐  ┌───────▼────────┐      │       │
│  │   Django    │  │   Substrate    │      │       │
│  │ REST API    │  │     Client     │      │       │
│  └──────┬──────┘  └───────┬────────┘      │       │
│         │                 │                │       │
│  ┌──────▼──────┐  ┌───────▼────────┐      │       │
│  │ PostgreSQL  │  │   WebSocket    │      │       │
│  │   Database  │  │   RPC Client   │      │       │
│  └─────────────┘  └───────┬────────┘      │       │
│                            │                │       │
└────────────────────────────┼────────────────┼───────┘
                             │                │
                             │                │
┌────────────────────────────┼────────────────┼───────┐
│                            │                │       │
│  BLOCKCHAIN LAYER (Substrate)               │       │
│                     ┌──────▼────────┐       │       │
│                     │   Substrate   │◄──────┘       │
│                     │     Node      │               │
│                     └──────┬────────┘               │
│                            │                        │
│         ┌──────────────────┼──────────────────┐     │
│         │                  │                  │     │
│  ┌──────▼──────┐  ┌────────▼────┐  ┌────────▼────┐│
│  │   Ledger    │  │     DID     │  │     DAO     ││
│  │   Pallet    │  │   Pallet    │  │   Pallet    ││
│  └─────────────┘  └─────────────┘  └─────────────┘│
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │         On-Chain Storage (RocksDB)          │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 4. Data Flow

### **4.1 Dual Data Flow Architecture**

TidyGen implements two distinct data flow patterns:

#### **Flow 1: React → Django → Substrate (Backend-Initiated)**

```mermaid
sequenceDiagram
    participant User
    participant React
    participant Django
    participant SubstrateClient
    participant Substrate
    participant Database

    User->>React: Create Invoice
    React->>Django: POST /api/v1/finance/invoices
    Django->>Database: Save Invoice
    Database-->>Django: Invoice Saved (ID: 123)
    Django->>SubstrateClient: record_invoice()
    SubstrateClient->>Substrate: create_invoice() signed extrinsic
    Substrate-->>SubstrateClient: tx_hash: 0xabc...
    SubstrateClient-->>Django: Receipt
    Django->>Database: Update invoice.blockchain_tx_hash
    Django-->>React: Invoice created + blockchain anchored
    React-->>User: Success notification
```

**Use Cases:**
- Automatic blockchain anchoring
  - Batch operations
- System-initiated transactions
- Background synchronization

#### **Flow 2: React → Polkadot.js → Substrate (User-Initiated)**

```mermaid
sequenceDiagram
    participant User
    participant React
    participant PolkadotExt as Polkadot.js Extension
    participant Substrate
    participant Django
    participant Database

    User->>React: Submit Invoice to Blockchain
    React->>PolkadotExt: Request signature
    PolkadotExt->>User: Approve transaction?
    User->>PolkadotExt: Approve
    PolkadotExt->>Substrate: Signed create_invoice() extrinsic
    Substrate-->>PolkadotExt: tx_hash: 0xdef...
    PolkadotExt-->>React: Transaction confirmed
    React->>Django: POST /api/v1/invoices/sync-blockchain
    Django->>Substrate: Query invoice data
    Substrate-->>Django: Invoice details
    Django->>Database: Save/update invoice
    React-->>User: Invoice on blockchain + synced
```

**Use Cases:**
- User-controlled transactions
- Governance voting
- DID registration
- Direct blockchain interaction

### **4.2 Data Synchronization Strategy**

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  Django Database (Source of Truth for Operations)   │
│  ┌─────────────────────────────────────────────┐   │
│  │  • User accounts and authentication         │   │
│  │  • Business logic and workflows             │   │
│  │  │  • Complex queries and reporting          │   │
│  │  • Soft deletions and history               │   │
│  └────────────┬────────────────────────────────┘   │
│               │                                     │
│               │ Selective Anchoring                 │
│               │                                     │
│               ▼                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │  Blockchain Reference Fields                │   │
│  │  • blockchain_tx_hash                       │   │
│  │  • blockchain_anchored (boolean)            │   │
│  │  • blockchain_block_number                  │   │
│  └────────────┬────────────────────────────────┘   │
│               │                                     │
└───────────────┼─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│                                                     │
│  Substrate Blockchain (Source of Truth for Audit)   │
│  ┌─────────────────────────────────────────────┐   │
│  │  • Immutable audit trail                    │   │
│  │  • Cryptographic verification               │   │
│  │  • Decentralized identity                   │   │
│  │  • Governance decisions                     │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 5. Use Cases

### **Use Case 1: Invoice Creation and Blockchain Anchoring**

#### **Scenario**
A finance manager creates an invoice for a client, and the system automatically anchors it to the blockchain for tamper-proof verification.

#### **Complete Flow**

```mermaid
sequenceDiagram
    autonumber
    participant FM as Finance Manager
    participant UI as React Frontend
    participant API as Django REST API
    participant DB as PostgreSQL
    participant SC as Substrate Client
    participant Chain as Substrate Chain
    participant Ledger as pallet-ledger

    FM->>UI: Fill invoice form (client, amount, terms)
    UI->>API: POST /api/v1/finance/invoices/<br/>{client_id, amount, items, terms}
    
    API->>API: Validate data & permissions
    API->>DB: BEGIN TRANSACTION
    
    Note over API,DB: Step 1: Save to Database
    API->>DB: INSERT INTO invoices<br/>(client_id, amount, invoice_number)
    DB-->>API: Invoice ID: 12345
    
    Note over API,Chain: Step 2: Calculate Hash
    API->>API: hash = SHA256(invoice_data)
    
    Note over API,Chain: Step 3: Anchor to Blockchain
    API->>SC: record_invoice(invoice_id, hash, client_wallet, amount)
    SC->>Chain: WebSocket: create_invoice extrinsic
    Chain->>Ledger: Store invoice entry
    Ledger->>Ledger: Calculate on-chain hash
    Ledger-->>Chain: InvoiceCreated event
    Chain-->>SC: tx_hash: 0xabc123...
    
    Note over API,DB: Step 4: Update Database with Blockchain Reference
    SC-->>API: Success + tx_hash
    API->>DB: UPDATE invoices SET<br/>blockchain_tx_hash='0xabc...',<br/>blockchain_anchored=true<br/>WHERE id=12345
    DB-->>API: Updated
    
    API->>DB: COMMIT TRANSACTION
    API-->>UI: Invoice created<br/>{id: 12345, tx_hash: 0xabc...}
    UI-->>FM: Success: "Invoice INV-2025-12345<br/>anchored to blockchain"
```

#### **Data Storage**

**In PostgreSQL:**
```sql
invoices (
    id: 12345,
    client_id: 456,
    amount: 1000.00,
    invoice_number: "INV-2025-12345",
    created_at: "2025-10-22 00:00:00",
    blockchain_tx_hash: "0xabc123...",
    blockchain_anchored: true,
    -- other business fields
)
```

**On Substrate Blockchain:**
```rust
Invoice {
    id: 0,
    client: 5GrwvaEF...,
    amount: 1000000000,  // Smallest unit
    metadata: "INV-2025-12345|Client XYZ|Net 30",
    timestamp: 42,  // Block number
    invoice_hash: [a1, b2, c3, ...],  // SHA256
    created_by: 5FHneW...
}
```

#### **Verification Process**

```mermaid
graph LR
    A[User requests verification] --> B[Django retrieves invoice]
    B --> C[Calculate hash from DB data]
    C --> D[Query blockchain for invoice]
    D --> E[Compare hashes]
    E --> F{Hashes match?}
    F -->|Yes| G[✅ Verified: Data unchanged]
    F -->|No| H[❌ Warning: Data tampered]
```

**Benefits:**
- ✅ **Immutability**: Invoice cannot be altered without detection
- ✅ **Transparency**: Anyone can verify the invoice on-chain
- ✅ **Audit Trail**: Complete history preserved on blockchain
- ✅ **Trust**: No need to trust the database

---

### **Use Case 2: User Authentication with Decentralized Identity**

#### **Scenario**
A user registers with the system and gets a decentralized identity (DID) for password-less authentication.

#### **Registration Flow**

```mermaid
sequenceDiagram
    participant User
    participant React
    participant PolkadotExt as Polkadot.js
    participant Django
    participant DB as PostgreSQL
    participant Substrate
    participant DID as pallet-did

    User->>React: Register Account
    React->>Django: POST /api/v1/auth/register
    Django->>DB: Create user record
    DB-->>Django: User ID: 789
    
    Note over React,Substrate: User-Initiated DID Registration
    User->>React: Click "Register DID"
    React->>PolkadotExt: Connect wallet
    PolkadotExt-->>React: Account: 5GHjk...
    
    React->>PolkadotExt: Sign registerDid() extrinsic
    PolkadotExt->>User: Confirm transaction?
    User->>PolkadotExt: Approve
    
    PolkadotExt->>Substrate: registerDid(account, pubkey, metadata)
    Substrate->>DID: Store DID document
    DID-->>Substrate: DidRegistered event
    Substrate-->>PolkadotExt: tx_hash: 0xdef456
    
    PolkadotExt-->>React: DID registered
    React->>Django: POST /api/v1/users/sync-did
    Django->>DB: UPDATE users SET<br/>did_registered=true,<br/>wallet_address='5GHjk...'
    Django-->>React: User updated
    React-->>User: DID registered successfully
```

#### **Authentication Flow (Password-less)**

```mermaid
sequenceDiagram
    participant User
    participant React
    participant PolkadotExt as Polkadot.js
    participant Django
    participant Substrate
    participant DID as pallet-did

    User->>React: Click "Login with DID"
    React->>PolkadotExt: Request accounts
    PolkadotExt-->>React: Accounts: [5GHjk...]
    User->>React: Select account
    
    React->>React: Generate random message
    React->>PolkadotExt: Sign message
    PolkadotExt->>User: Sign message?
    User->>PolkadotExt: Approve
    PolkadotExt-->>React: Signature: 0xsig...
    
    React->>Django: POST /api/v1/auth/did-login<br/>{account, message, signature}
    Django->>Substrate: RPC: did_getDid(account)
    Substrate->>DID: Query DID document
    DID-->>Substrate: DidDocument {pubkey, metadata}
    Substrate-->>Django: DID document
    
    Django->>Django: Verify signature with pubkey
    Django->>Django: Extract user_id from metadata
    Django->>Django: Create JWT token
    Django-->>React: {token, user}
    React-->>User: Logged in successfully
```

---

### **Use Case 3: DAO Governance for Budget Approval**

#### **Scenario**
The finance team creates a proposal to approve Q4 budget, and stakeholders vote on it democratically.

#### **Complete Governance Flow**

```mermaid
sequenceDiagram
    participant CFO
    participant React
    participant PolkadotExt
    participant Substrate
    participant DAO as pallet-dao
    participant Team as Team Members
    participant Django

    Note over CFO,DAO: Phase 1: Proposal Creation
    CFO->>React: Create proposal form
    React->>PolkadotExt: Sign createProposal()
    PolkadotExt->>Substrate: createProposal(title, desc, period)
    Substrate->>DAO: Store proposal ID: 0
    DAO-->>Substrate: ProposalCreated event
    Substrate-->>React: Proposal created
    
    Note over Team,DAO: Phase 2: Voting Period
    Team->>React: View proposals
    React->>Substrate: Query proposals
    Substrate->>DAO: Get proposal 0
    DAO-->>React: Proposal details
    
    Team->>React: Vote Yes/No
    React->>PolkadotExt: Sign vote() extrinsic
    PolkadotExt->>Substrate: vote(proposal_id: 0, in_favor: true)
    Substrate->>DAO: Record vote
    DAO->>DAO: votes_for++
    DAO-->>Substrate: VoteCast event
    
    Note over CFO,DAO: Phase 3: Voting Ends
    React->>Substrate: closeProposal(0)
    Substrate->>DAO: Finalize voting
    DAO->>DAO: votes_for > votes_against?
    DAO->>DAO: status = Approved
    DAO-->>Substrate: ProposalApproved event
    
    Note over CFO,Django: Phase 4: Execution
    CFO->>React: Execute proposal
    React->>PolkadotExt: Sign executeProposal()
    PolkadotExt->>Substrate: executeProposal(0)
    Substrate->>DAO: Execute
    DAO-->>Substrate: ProposalExecuted event
    
    React->>Django: Sync proposal execution
    Django->>Django: Implement budget allocation
    Django-->>React: Budget applied
    React-->>CFO: Proposal executed successfully
```

---

## 6. Integration Points

### **6.1 Frontend-Backend Integration**

```
React Components → Django REST API
───────────────────────────────────

Authentication:
  POST /api/v1/auth/login
  POST /api/v1/auth/did-login  ✨ DID-based

Invoice Management:
  GET  /api/v1/finance/invoices
  POST /api/v1/finance/invoices
  POST /api/v1/finance/invoices/{id}/anchor  ✨ Blockchain

DAO Governance:
  GET  /api/v1/web3/proposals
  POST /api/v1/web3/proposals
  POST /api/v1/web3/proposals/{id}/vote
  POST /api/v1/web3/proposals/{id}/sync  ✨ Blockchain sync
```

### **6.2 Backend-Blockchain Integration**

```python
# Django → Substrate (via Python client)

from services.substrate_client import SubstrateClient

# Create client
client = SubstrateClient(keypair_uri='//Alice')

# Submit transaction
tx_hash, receipt = client.record_invoice(
    user_id=user.id,
    invoice_hash=invoice.calculate_hash(),
    client_account=client.wallet_address,
    amount=int(invoice.amount * 1000000),
    metadata=f"{invoice.number}|{client.name}"
)

# Query data
invoices = client.get_invoices(account_id)
did_doc = client.get_did(account_id)
proposal = client.get_proposal(proposal_id)
```

### **6.3 Frontend-Blockchain Integration**

```typescript
// React → Substrate (via Polkadot.js)

import { submitInvoice, connectWallet } from '../web3';

// Connect wallet
const accounts = await connectWallet();

// Submit transaction
const result = await submitInvoice(
  {
    client: clientAddress,
    amount: 1000000,
    metadata: 'INV-2025-001'
  },
  accounts[0]
);

// Query blockchain
const invoices = await queryInvoices(accountId);
const didDoc = await queryDID(accountId);
const proposal = await queryProposal(proposalId);
```

---

## 7. Security Architecture

### **7.1 Multi-Layer Security**

```
┌─────────────────────────────────────────────────────┐
│  Layer 1: Network Security                          │
│  ├─ HTTPS/WSS in production                        │
│  ├─ CORS configuration                             │
│  ├─ Rate limiting                                  │
│  └─ DDoS protection                                │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  Layer 2: Application Security                      │
│  ├─ JWT authentication                             │
│  ├─ Role-based access control (RBAC)               │
│  ├─ Input validation                               │
│  └─ SQL injection prevention                       │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  Layer 3: Blockchain Security                       │
│  ├─ Cryptographic signatures                       │
│  ├─ On-chain access control                        │
│  ├─ Immutable audit logs                           │
│  └─ DID-based authentication                       │
└─────────────────────────────────────────────────────┘
```

### **7.2 Authentication Flow**

```mermaid
graph TD
    A[User Login] --> B{Auth Method}
    
    B -->|Traditional| C[Username + Password]
    C --> D[Django Auth]
    D --> E[JWT Token]
    
    B -->|Web3| F[Wallet Signature]
    F --> G[Verify with DID Pubkey]
    G --> H[DID Metadata → User]
    H --> E
    
    E --> I[Access Granted]
    
    I --> J[API Requests]
    J --> K{Permission Check}
    K -->|Authorized| L[Resource Access]
    K -->|Denied| M[403 Forbidden]
```

---

## 8. Deployment Architecture

### **8.1 Development Environment**

```
┌─────────────────────────────────────────────────────┐
│  Developer Machine                                   │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │   Frontend   │  │   Backend    │  │ Substrate │ │
│  │              │  │              │  │   Node    │ │
│  │ localhost    │  │ localhost    │  │ localhost │ │
│  │   :5173      │  │   :8002      │  │   :9944   │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐                 │
│  │  PostgreSQL  │  │    Redis     │                 │
│  │    :5432     │  │    :6379     │                 │
│  └──────────────┘  └──────────────┘                 │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### **8.2 Production Architecture (Docker)**

```mermaid
graph TB
    subgraph "Internet"
        Users[Users/Clients]
    end
    
    subgraph "Load Balancer"
        LB[Nginx/Traefik]
    end
    
    subgraph "Frontend Tier"
        F1[React App 1]
        F2[React App 2]
        F3[React App N]
    end
    
    subgraph "Backend Tier"
        B1[Django API 1]
        B2[Django API 2]
        B3[Django API N]
    end
    
    subgraph "Data Tier"
        DB[(PostgreSQL<br/>Primary)]
        DBR[(PostgreSQL<br/>Replica)]
        Redis[(Redis<br/>Cache)]
    end
    
    subgraph "Blockchain Tier"
        S1[Substrate<br/>Validator 1]
        S2[Substrate<br/>Validator 2]
        S3[Substrate<br/>Validator 3]
    end
    
    subgraph "Worker Tier"
        W1[Celery Worker 1]
        W2[Celery Worker 2]
    end
    
    Users --> LB
    LB --> F1 & F2 & F3
    F1 & F2 & F3 --> B1 & B2 & B3
    B1 & B2 & B3 --> DB
    B1 & B2 & B3 --> Redis
    B1 & B2 & B3 --> S1 & S2 & S3
    DB --> DBR
    W1 & W2 --> DB
    W1 & W2 --> S1 & S2 & S3
```

### **8.3 Technology Stack Summary**

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | React 18 + TypeScript | User interface |
| **Styling** | Tailwind CSS + Shadcn/ui | Modern UI components |
| **State** | React Query + Zustand | State management |
| **Web3** | Polkadot.js API | Blockchain interaction |
| **Backend** | Django 4.2 + DRF | Business logic & API |
| **Database** | PostgreSQL 15 | Relational data |
| **Cache** | Redis 7 | Session & caching |
| **Tasks** | Celery + RabbitMQ | Async processing |
| **Blockchain** | Substrate (Rust) | On-chain logic |
| **Pallets** | FRAME pallets | Custom business logic |
| **Storage** | RocksDB | Blockchain state |
| **Network** | WebSocket + HTTP | Communication |

---

## 9. System Architecture Diagram

### **Complete System Overview**

```mermaid
graph TB
    subgraph "User Layer"
        U1[Web Browser]
        U2[Polkadot.js Extension]
        U3[Mobile App - Future]
    end
    
    subgraph "Frontend Layer - React + TypeScript"
        direction LR
        F1[UI Components]
        F2[Web3 Utils]
        F3[API Client]
        F4[State Management]
        
        F1 --> F2
        F1 --> F3
        F1 --> F4
    end
    
    subgraph "API Gateway"
        G1[Nginx Reverse Proxy]
        G2[Rate Limiting]
        G3[SSL/TLS]
    end
    
    subgraph "Backend Layer - Django"
        direction LR
        B1[REST API<br/>25 Modules]
        B2[Business Logic]
        B3[Substrate Client]
        B4[Celery Workers]
        
        B1 --> B2
        B2 --> B3
        B2 --> B4
    end
    
    subgraph "Data Layer"
        D1[(PostgreSQL<br/>Operational Data)]
        D2[(Redis<br/>Cache & Sessions)]
        D3[File Storage<br/>IPFS/S3]
    end
    
    subgraph "Blockchain Layer - Substrate"
        direction TB
        S1[Substrate Node Runtime]
        S2[pallet-ledger<br/>Invoices]
        S3[pallet-did<br/>Identity]
        S4[pallet-dao<br/>Governance]
        S5[(RocksDB<br/>Chain State)]
        
        S1 --> S2 & S3 & S4
        S2 & S3 & S4 --> S5
    end
    
    U1 & U2 --> F1
    F3 --> G1
    F2 --> S1
    G1 --> B1
    B2 --> D1 & D2 & D3
    B3 --> S1
    B4 --> S1
    
    style S2 fill:#90EE90
    style S3 fill:#87CEEB
    style S4 fill:#FFD700
    style B3 fill:#FFA07A
    style F2 fill:#DDA0DD
```

---

## 10. Data Flow Patterns

### **Pattern 1: Write to Database, Anchor to Blockchain**

```
User Action
    │
    ▼
Django Creates Record
    │
    ├─► PostgreSQL: Full data
    │
    └─► Substrate: Hash + key fields
            │
            └─► Immutable audit trail
```

**Example:** Invoices, Contracts, Payroll

### **Pattern 2: Write to Blockchain, Sync to Database**

```
User Action (Web3)
    │
    ▼
Polkadot.js Transaction
    │
    ▼
Substrate Pallet
    │
    ├─► On-chain storage
    │
    └─► Event emission
            │
            ▼
        Django Listens
            │
            ▼
        Database Sync
```

**Example:** DAO Voting, DID Registration

### **Pattern 3: Query Both Layers**

```
User Request
    │
    ├─► Django: Business data
    │       │
    │       └─► Quick response
    │
    └─► Substrate: Verification
            │
            └─► Proof of authenticity
```

**Example:** Invoice Verification, DID Lookup

---

## 11. Performance Optimization

### **11.1 Caching Strategy**

```
┌─────────────────────────────────────────┐
│  Level 1: Browser Cache                 │
│  • Static assets (24 hours)             │
│  • API responses (React Query, 5 min)   │
└─────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  Level 2: Redis Cache                   │
│  • Session data                         │
│  • Frequently accessed data             │
│  • Blockchain query results (1 min)     │
└─────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  Level 3: Database Query Cache          │
│  • PostgreSQL query result cache        │
└─────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  Level 4: Blockchain State              │
│  • On-chain immutable data              │
│  • No cache (always query for proof)    │
└─────────────────────────────────────────┘
```

### **11.2 Scalability Approach**

| Component | Scaling Strategy |
|-----------|------------------|
| Frontend | CDN + Static hosting (Vercel/Netlify) |
| Django API | Horizontal scaling (multiple instances) |
| PostgreSQL | Read replicas + connection pooling |
| Redis | Redis Cluster for high availability |
| Substrate | Validator set or parachain deployment |
| Celery | Auto-scaling worker pool |

---

## 12. Future Enhancements

### **Phase 2: Parachain Deployment**

```mermaid
graph TB
    subgraph "Polkadot Relay Chain"
        R[Relay Chain Validators]
    end
    
    subgraph "TidyGen Parachain"
        P1[Collator 1]
        P2[Collator 2]
        P3[Collator 3]
        
        P1 & P2 & P3 --> Pallets
        
        subgraph Pallets
            PL[pallet-ledger]
            PD[pallet-did]
            PA[pallet-dao]
        end
    end
    
    subgraph "Other Parachains"
        O1[Acala - DeFi]
        O2[Moonbeam - EVM]
    end
    
    P1 & P2 & P3 <--> R
    Pallets <-.-> O1 & O2
    
    style Pallets fill:#FFD700
```

### **Roadmap**

- **Q1 2026**: Parachain deployment on testnet
- **Q2 2026**: XCM integration with other parachains
- **Q3 2026**: Mainnet parachain launch
- **Q4 2026**: Cross-chain asset management

---

## 13. Key Architectural Decisions

### **Why Hybrid (Web2 + Web3)?**

| Aspect | Web2 (Django) | Web3 (Substrate) |
|--------|---------------|------------------|
| **Speed** | Very fast | Slower (block time) |
| **Cost** | Low | Gas fees |
| **Queryability** | Excellent | Limited |
| **Immutability** | No | Yes |
| **Trust** | Trust provider | Trustless |
| **Privacy** | Controllable | Public |

**Decision**: Use Web2 for operations, Web3 for verification

### **Why Substrate?**

- ✅ Modular pallet architecture
- ✅ Rust safety and performance
- ✅ Polkadot ecosystem integration
- ✅ Customizable consensus
- ✅ Built-in governance
- ✅ Interoperability (XCM)

### **Why Django?**

- ✅ Mature ORM for complex queries
- ✅ Admin interface for management
- ✅ Rich ecosystem of packages
- ✅ Strong security features
- ✅ Excellent documentation
- ✅ Python for substrate-interface

### **Why React + Polkadot.js?**

- ✅ Component-based architecture
- ✅ TypeScript for type safety
- ✅ Official Polkadot library
- ✅ Active development
- ✅ Large ecosystem
- ✅ Excellent wallet integration

---

## 14. API Endpoints

### **REST API (Django)**

```
Authentication:
  POST   /api/v1/auth/login
  POST   /api/v1/auth/register
  POST   /api/v1/auth/did-login              ✨ Web3
  POST   /api/v1/auth/refresh

Finance:
  GET    /api/v1/finance/invoices
  POST   /api/v1/finance/invoices
  GET    /api/v1/finance/invoices/{id}
  POST   /api/v1/finance/invoices/{id}/anchor ✨ Blockchain

Blockchain:
  POST   /api/v1/blockchain/invoices
  GET    /api/v1/blockchain/invoices/{hash}
  POST   /api/v1/blockchain/did/register
  GET    /api/v1/blockchain/did/{account}

DAO:
  GET    /api/v1/dao/proposals
  POST   /api/v1/dao/proposals
  POST   /api/v1/dao/proposals/{id}/vote
  POST   /api/v1/dao/proposals/{id}/execute
  POST   /api/v1/dao/proposals/{id}/sync        ✨ Blockchain sync
```

### **RPC API (Substrate)**

```
Chain Queries:
  system_chain()
  system_version()
  chain_getBlock()
  chain_getBlockHash()

Ledger Pallet:
  ledger.invoices(AccountId)              → Vec<Invoice>
  ledger.invoiceByHash(Hash)              → Option<InvoiceId>
  ledger.invoiceCount()                   → u64

DID Pallet:
  did_getDid(AccountId)                   → Option<DidDocument>  ✨ RPC
  did_isDidActive(AccountId)              → bool                 ✨ RPC
  did_getAccountFromDid(String)           → Option<AccountId>    ✨ RPC
  did_getTotalDids()                      → u64                  ✨ RPC
  did.didDocuments(AccountId)             → Option<DidDocument>

DAO Pallet:
  dao.proposals(ProposalId)               → Option<Proposal>
  dao.votes(ProposalId, AccountId)        → Option<bool>
  dao.proposalCount()                     → u64
```

---

## 15. Monitoring and Observability

### **Monitoring Stack**

```
┌─────────────────────────────────────────┐
│  Application Metrics                    │
│  ├─ Django: Request rate, errors       │
│  ├─ Substrate: Block time, finality    │
│  └─ Celery: Task queue length          │
└─────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  Logging                                │
│  ├─ Django: Application logs           │
│  ├─ Substrate: Node logs               │
│  └─ Nginx: Access logs                 │
└─────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  Blockchain Monitoring                  │
│  ├─ Block production rate               │
│  ├─ Transaction throughput              │
│  ├─ Pallet-specific metrics             │
│  └─ Network health                      │
└─────────────────────────────────────────┘
```

---

## 16. Conclusion

### **Architecture Strengths**

✅ **Hybrid Design**: Best of Web2 and Web3  
✅ **Modular**: Easy to extend and maintain  
✅ **Scalable**: Horizontal scaling for all layers  
✅ **Secure**: Multi-layer security approach  
✅ **Performant**: Optimized data flow  
✅ **Developer-Friendly**: Clear separation of concerns  
✅ **Production-Ready**: Tested and documented  

### **Key Innovations**

1. **Selective Blockchain Anchoring**: Only critical data goes on-chain
2. **Dual Data Flow**: Backend and user-initiated transactions
3. **DID Authentication**: Password-less login with blockchain identity
4. **DAO Governance**: Democratic business decision-making
5. **Hybrid Storage**: Fast queries + immutable verification

### **Suitable For**

- Small to medium businesses (SMBs)
- Community organizations
- Freelancer platforms
- Organizations requiring audit trails
- Web3-forward enterprises
- Grant-funded open-source projects

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **DID** | Decentralized Identifier - W3C standard for self-sovereign identity |
| **DAO** | Decentralized Autonomous Organization - On-chain governance |
| **Extrinsic** | Substrate transaction (like Ethereum transaction) |
| **Pallet** | Substrate module (like smart contract) |
| **RPC** | Remote Procedure Call - Query interface |
| **FRAME** | Framework for Runtime Aggregation of Modularized Entities |
| **XCM** | Cross-Consensus Messaging - Polkadot interoperability protocol |

## Appendix B: References

- [Substrate Documentation](https://docs.substrate.io/)
- [Polkadot Documentation](https://wiki.polkadot.network/)
- [Django Documentation](https://docs.djangoproject.com/)
- [Polkadot.js Documentation](https://polkadot.js.org/docs/)
- [W3C DID Specification](https://www.w3.org/TR/did-core/)

---

**Document Version**: 1.0  
**Last Updated**: October 2025  
**Status**: Production Architecture

*This architecture powers TidyGen Community Edition - a next-generation ERP system combining traditional enterprise software with blockchain innovation.*
