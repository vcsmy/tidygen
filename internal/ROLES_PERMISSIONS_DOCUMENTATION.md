# TidyGen Community Edition - Roles, Portals & Permissions Documentation

## 📋 Overview

This document provides a comprehensive overview of all roles, portals (modules), and permissions available in the TidyGen Community Edition ERP system. This is a single-tenant system designed for community access and demonstration purposes.

---

## 👥 **ROLES & PERMISSIONS**

### **Available Roles (6 Total)**

| Role Code | Role Name | Description | Primary Use Case |
|-----------|-----------|-------------|------------------|
| `admin` | Administrator | Full system access with all permissions | System administrators, super users |
| `manager` | Manager | Management of freelancers, gigs, and payments | Operations managers, team leads |
| `finance` | Finance Manager | Financial operations and payment management | Finance team, accounting staff |
| `hr` | HR Manager | Human resources and payroll management | HR department, people operations |
| `freelancer` | Freelancer | Limited access for individual contractors | Individual cleaners, contractors |
| `client` | Client | Basic dashboard access for clients | External clients, customers |

---

## 🔐 **PERMISSION SYSTEM**

### **Available Permissions (18 Total)**

| Permission Code | Permission Name | Description |
|-----------------|-----------------|-------------|
| `view_dashboard` | Can view dashboard | Access to main dashboard |
| `manage_users` | Can manage users | User management capabilities |
| `manage_finance` | Can manage finance | Financial operations access |
| `manage_inventory` | Can manage inventory | Inventory management access |
| `manage_hr` | Can manage HR | Human resources management |
| `manage_sales` | Can manage sales | Sales and client management |
| `manage_purchasing` | Can manage purchasing | Procurement and purchasing |
| `manage_web3` | Can manage Web3 | Blockchain and Web3 features |
| `manage_freelancers` | Can manage freelancers | Freelancer management access |
| `manage_gigs` | Can manage gigs | Gig and job management |
| `manage_payments` | Can manage contractor payments | Payment processing access |
| `manage_analytics` | Can view analytics | Analytics and reporting access |
| `manage_scheduling` | Can manage scheduling | Scheduling and calendar management |
| `manage_facilities` | Can manage facilities | Facility management access |
| `manage_payroll` | Can manage payroll | Payroll processing access |
| `view_reports` | Can view reports | Report viewing access |
| `admin_access` | Can access admin panel | Django admin panel access |

---

## 🏢 **PORTALS & MODULES**

### **Core ERP Modules (16 Total)**

| Module | Portal Name | Description | Key Features |
|--------|-------------|-------------|--------------|
| **Core** | System Management | User management, roles, permissions | User accounts, system settings, audit logs |
| **Sales** | Sales & CRM | Client and customer management | Individual/corporate clients, interactions, documents |
| **Finance** | Finance Management | Financial operations and accounting | Invoicing, payments, expenses, budgets |
| **HR** | Human Resources | Employee and workforce management | Employee records, attendance, leave, performance |
| **Inventory** | Inventory Management | Stock and asset management | Product catalog, stock levels, movements |
| **Purchasing** | Procurement | Vendor and purchase management | Vendor management, purchase orders, approvals |
| **Analytics** | Analytics & Reporting | Business intelligence and reporting | KPIs, dashboards, reports, data visualization |
| **Scheduling** | Scheduling & Calendar | Appointment and task scheduling | Calendar management, appointments, resource booking |
| **Facility Management** | Facility Operations | Building and facility management | Maintenance, equipment, space management |
| **Field Operations** | Field Team Management | Mobile workforce management | Field teams, routes, job assignments |
| **Payroll** | Payroll Processing | Employee compensation management | Salary processing, tax calculations, benefits |

### **Freelancer Ecosystem Modules (4 Total)**

| Module | Portal Name | Description | Key Features |
|--------|-------------|-------------|--------------|
| **Freelancers** | Freelancer Management | Individual contractor management | Profile management, skills, availability, reviews |
| **Gig Management** | Job Marketplace | Job posting and assignment platform | Job posting, applications, assignments, milestones |
| **Contractor Payments** | Payment Processing | Freelancer payment management | Multi-method payments, escrow, disputes |
| **Freelancer Web3** | Web3 Integration | Blockchain features for freelancers | NFT badges, smart contracts, reputation tokens |

### **Web3 & Blockchain Modules (3 Total)**

| Module | Portal Name | Description | Key Features |
|--------|-------------|-------------|--------------|
| **Web3** | Blockchain Integration | Core Web3 functionality | Smart contracts, blockchain audit, asset tokenization |
| **Ledger** | Distributed Ledger | Transaction and asset tracking | Multi-currency support, transaction history |
| **DID Auth** | Decentralized Identity | Identity verification and authentication | DID documents, credential management, verification |
| **Wallet** | Digital Wallet | Cryptocurrency and asset management | Wallet connection, transaction management |

### **System Modules (2 Total)**

| Module | Portal Name | Description | Key Features |
|--------|-------------|-------------|--------------|
| **Audit Trail** | System Audit | Activity tracking and compliance | Audit logs, compliance reporting, activity monitoring |
| **Accounts** | Authentication | User authentication and authorization | Login, registration, password management |

---

## 🎯 **ROLE-BASED ACCESS MATRIX**

### **Administrator (`admin`)**
- **Full Access**: All modules and features
- **Permissions**: All 18 permissions
- **Portals**: Complete access to all 25 portals
- **Use Case**: System administrators, super users, technical staff

### **Manager (`manager`)**
- **Primary Focus**: Freelancer ecosystem management
- **Permissions**: 
  - `manage_freelancers` - Freelancer management
  - `manage_gigs` - Gig and job management  
  - `manage_payments` - Contractor payments
  - `view_dashboard` - Dashboard access
  - `view_reports` - Report viewing
- **Portals**: Freelancers, Gig Management, Contractor Payments, Dashboard, Reports
- **Use Case**: Operations managers, team leads, project managers

### **Finance Manager (`finance`)**
- **Primary Focus**: Financial operations
- **Permissions**:
  - `manage_finance` - Financial operations
  - `manage_payments` - Payment processing
  - `view_dashboard` - Dashboard access
  - `view_reports` - Report viewing
- **Portals**: Finance, Contractor Payments, Dashboard, Reports, Analytics
- **Use Case**: Finance team, accounting staff, CFOs

### **HR Manager (`hr`)**
- **Primary Focus**: Human resources and payroll
- **Permissions**:
  - `manage_hr` - HR management
  - `manage_payroll` - Payroll processing
  - `view_dashboard` - Dashboard access
  - `view_reports` - Report viewing
- **Portals**: HR, Payroll, Dashboard, Reports, Analytics
- **Use Case**: HR department, people operations, HR directors

### **Freelancer (`freelancer`)**
- **Primary Focus**: Individual contractor access
- **Permissions**:
  - `view_dashboard` - Limited dashboard access
- **Portals**: Dashboard (limited), Personal profile, Gig applications
- **Use Case**: Individual cleaners, contractors, service providers

### **Client (`client`)**
- **Primary Focus**: External client access
- **Permissions**:
  - `view_dashboard` - Basic dashboard access
- **Portals**: Dashboard (basic), Personal account, Service requests
- **Use Case**: External clients, customers, service recipients

---

## 🚀 **MODULE FEATURES BREAKDOWN**

### **Core ERP Features**

#### **Sales & CRM Portal**
- Individual and corporate client management
- Contact management and interaction tracking
- Document management and file storage
- Client segmentation and tagging
- Sales analytics and reporting
- Lead source tracking

#### **Finance Management Portal**
- Chart of accounts and financial structure
- Invoice creation and management
- Payment processing and tracking
- Expense management and approval workflows
- Budget planning and monitoring
- Financial reporting and analytics

#### **HR Management Portal**
- Employee records and profiles
- Attendance tracking and leave management
- Performance management and reviews
- Training and development tracking
- Document management (contracts, certifications)
- HR analytics and reporting

#### **Inventory Management Portal**
- Product catalog and item management
- Stock level monitoring and alerts
- Inventory movements and transactions
- Supplier and vendor management
- Inventory analytics and reporting
- Asset tracking and depreciation

### **Freelancer Ecosystem Features**

#### **Freelancer Management Portal**
- Freelancer registration and onboarding
- Profile management with skills and certifications
- Availability scheduling and calendar integration
- Document verification and background checks
- Performance tracking and reviews
- Web3 wallet integration

#### **Gig Management Portal**
- Job posting and categorization
- Application management and screening
- Assignment and milestone tracking
- Photo documentation and verification
- In-app messaging system
- Review and rating system

#### **Contractor Payments Portal**
- Multi-method payment processing
- Escrow services and dispute resolution
- Payment scheduling and automation
- Tax calculation and reporting
- Web3 payment integration
- Payment analytics and reporting

### **Web3 & Blockchain Features**

#### **Blockchain Integration Portal**
- Smart contract deployment and management
- Asset tokenization and NFT creation
- Blockchain audit logging
- Multi-currency support
- Decentralized storage integration
- Web3 transaction management

#### **Decentralized Identity Portal**
- DID document creation and management
- Credential verification and validation
- Identity proof and authentication
- Privacy-preserving authentication
- Cross-platform identity management
- Compliance and audit features

---

## 📊 **QUICK REFERENCE**

### **Total System Counts**
- **Roles**: 6 roles
- **Permissions**: 18 permissions  
- **Modules**: 25 modules/portals
- **Core ERP Modules**: 16 modules
- **Freelancer Ecosystem**: 4 modules
- **Web3 & Blockchain**: 3 modules
- **System Modules**: 2 modules

### **Access Levels**
- **Full Access**: Administrator (all 25 portals)
- **Management Access**: Manager, Finance Manager, HR Manager (5-6 portals each)
- **Limited Access**: Freelancer, Client (1-2 portals each)

### **Community Edition Specifics**
- **Architecture**: Single-tenant system
- **Target Users**: Community organizations, small businesses, demo purposes
- **Authentication**: JWT-based with role-based permissions
- **Database**: PostgreSQL with Redis caching
- **Frontend**: React with TypeScript
- **Backend**: Django REST Framework
- **Web3**: Ethereum-compatible blockchain integration

---

## 🔧 **IMPLEMENTATION NOTES**

### **Permission Inheritance**
- All roles inherit `view_dashboard` permission
- Management roles include `view_reports` for analytics access
- Admin role has complete system access
- Freelancer and Client roles have minimal access for security

### **Portal Integration**
- All portals integrate through the main dashboard
- Role-based navigation shows only accessible modules
- Single sign-on across all portals
- Consistent UI/UX across all modules

### **Security Considerations**
- Role-based access control (RBAC) implementation
- API-level permission enforcement
- Frontend route protection based on roles
- Audit logging for all user actions
- Web3 security for blockchain operations

---

*This documentation is current as of the latest Community Edition release. For updates or clarifications, please refer to the system administrators or technical documentation.*
