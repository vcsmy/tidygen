# Comprehensive Demo Data Seeding

This document describes the `seed_comprehensive_demo.py` management command that creates extensive demo data for all portals and modules in the TidyGen ERP Community Edition.

## Overview

The command creates realistic demo data across all modules including:
- **Core**: Users, roles, permissions, organization
- **Freelancers**: Freelancer profiles, skills, availability, reviews
- **Gig Management**: Job categories, gigs, applications, milestones
- **Contractor Payments**: Payment transactions, escrow, disputes
- **Freelancer Web3**: NFT badges, reputation tokens, smart contracts
- **Finance**: Accounts, invoices, payments, budgets
- **HR**: Departments, employees, payroll records
- **Sales**: Clients (individual & corporate), contacts
- **Inventory**: Products, categories, suppliers, stock
- **Purchasing**: Purchase orders, procurement requests
- **Analytics**: KPIs, reports, performance metrics
- **Scheduling**: Resources, appointments, conflicts
- **Field Operations**: Teams, routes, jobs
- **Facility Management**: Facilities, vehicles, equipment
- **Audit Trail**: System events and logs
- **Web3**: Wallets, transactions, smart contracts
- **DID Auth**: Decentralized identity documents

## Usage

### Basic Usage
```bash
# Navigate to backend directory
cd apps/backend

# Run the command with default settings
python manage.py seed_comprehensive_demo

# Clear existing data first (recommended for fresh demo)
python manage.py seed_comprehensive_demo --clear

# Specify custom organization name
python manage.py seed_comprehensive_demo --organization "My Demo Company"
```

### Command Options

- `--clear`: Remove existing data before seeding (keeps superusers)
- `--organization`: Set custom organization name (default: "TidyGen Community Demo")

## Demo Data Created

### Users & Authentication
- **Admin User**: `admin@tidygen.com` / `admin123`
- **Manager User**: `manager@tidygen.com` / `manager123`
- **10 Freelancer Users**: `freelancer1-10@tidygen.com` / `freelancer123`
- **5 Client Users**: `client1-5@tidygen.com` / `client123`

### Business Data Quantities
- **Freelancers**: 10 complete profiles with skills and availability
- **Gig Jobs**: 4 sample jobs across different categories
- **Payment Transactions**: 20 sample transactions
- **Clients**: 4 corporate clients
- **Products**: 9 cleaning supplies and equipment items
- **Purchase Orders**: 5 sample orders
- **Analytics**: 4 KPIs with realistic metrics
- **Audit Events**: 50 system events

### Web3 Integration
- NFT badges for freelancer achievements
- Reputation tokens for performance tracking
- Smart contract agreements for gigs
- Blockchain transaction history
- Wallet connections for users

## Demo Scenarios

The seed data supports these demo scenarios:

1. **Freelancer Onboarding**: Complete freelancer profile creation
2. **Job Posting & Application**: Gig creation and freelancer applications
3. **Payment Processing**: Multiple payment methods and escrow
4. **Performance Tracking**: Reviews, ratings, and reputation tokens
5. **Client Management**: Corporate and individual client handling
6. **Inventory Management**: Product catalog and stock tracking
7. **Financial Reporting**: Invoices, payments, and analytics
8. **Web3 Features**: NFT badges, smart contracts, blockchain transactions

## Customization

To add more demo data or modify existing data:

1. Edit the `seed_comprehensive_demo.py` file
2. Find the relevant data creation method (e.g., `create_freelancers_data`)
3. Add additional entries to the data arrays
4. Run the command with `--clear` to regenerate data

## Troubleshooting

**Import Errors**: Ensure all apps are properly installed and migrated
**Data Conflicts**: Use `--clear` flag to remove existing data first
**Organization Errors**: Only one organization allowed in community edition
**Permission Issues**: Ensure proper database permissions for data creation

## Performance

- Command runs within a database transaction for safety
- Estimated execution time: 30-60 seconds
- Creates ~500+ database records across all modules
- Memory usage: Minimal (data created in batches)
