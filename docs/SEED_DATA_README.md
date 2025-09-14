# 🌱 Database Seed Data

This document explains how to populate the TidyGen ERP system with comprehensive sample data for demonstration and testing purposes.

## 📋 Available Seed Commands

### 1. **Basic Demo Data** (`seed_demo`)
Creates essential demo data including:
- Demo organization
- User roles and permissions
- Admin user and demo users
- Basic user profiles

**Usage:**
```bash
cd apps/backend
python manage.py seed_demo
```

**Demo Users Created:**
- `admin` / `admin123` (Administrator)
- `demo1` / `password123` (Finance Manager)
- `demo2` / `password123` (Sales Manager)
- `demo3` / `password123` (HR Manager)

### 2. **Comprehensive Business Data** (`seed_business_data`)
Creates realistic business data including:
- **Inventory**: Products, categories, warehouses, suppliers
- **Finance**: Accounts, invoices, payments, budgets
- **HR**: Departments, employees, payroll records
- **Projects**: Clients, projects, resources, time entries
- **Sales**: Customers, sales orders, leads, opportunities
- **Purchasing**: Vendors, purchase orders, requisitions
- **Web3**: Wallets, transactions, tokens, smart contracts

**Usage:**
```bash
cd apps/backend
python manage.py seed_business_data
```

### 3. **Full Seed Data** (`seed_data`)
Creates all data including the comprehensive business data above.

**Usage:**
```bash
cd apps/backend
python manage.py seed_data
```

## 🚀 Quick Start

### Option 1: Automated Seeding
```bash
cd apps/backend
python seed_database.py
```

### Option 2: Manual Seeding
```bash
cd apps/backend

# Step 1: Create demo users and organization
python manage.py seed_demo --clear

# Step 2: Create business data
python manage.py seed_business_data --clear
```

### Option 3: Docker Environment
```bash
# Start the system
make dev

# Seed the database
docker-compose exec backend python manage.py seed_demo --clear
docker-compose exec backend python manage.py seed_business_data --clear
```

## 📊 Sample Data Overview

### **Organization**
- **Name**: TidyGen Demo Corp
- **Industry**: Technology
- **Size**: Medium
- **Location**: San Francisco, CA

### **Users & Roles**
- **Admin User**: Full system access
- **Finance Manager**: Finance module access
- **Sales Manager**: Sales module access
- **HR Manager**: HR module access
- **Project Manager**: Projects module access
- **Inventory Manager**: Inventory module access
- **Purchasing Manager**: Purchasing module access
- **Web3 Manager**: Web3 module access

### **Inventory Data**
- **Products**: 10+ products across 5 categories
- **Categories**: Electronics, Office Supplies, Software, Hardware, Furniture
- **Warehouses**: 3 warehouses (Main, East Coast, West Coast)
- **Suppliers**: 4 suppliers with contact information
- **Stock Items**: Realistic stock levels and pricing

### **Finance Data**
- **Accounts**: 7 chart of accounts
- **Invoices**: 15 sample invoices with various statuses
- **Payments**: 10 sample payments
- **Budgets**: Sample budget allocations

### **HR Data**
- **Departments**: 6 departments (IT, Finance, HR, Sales, Operations, Engineering)
- **Employees**: 8 employees with realistic profiles
- **Positions**: Various roles and salary ranges

### **Projects Data**
- **Clients**: 4 client companies
- **Projects**: 5 active projects with budgets and timelines
- **Resources**: Project resources and allocations

### **Sales Data**
- **Customers**: 5 customers (business and individual)
- **Sales Orders**: 10 sales orders with various statuses
- **Sales Leads**: 8 sales leads in different stages

### **Purchasing Data**
- **Vendors**: 4 vendors with performance ratings
- **Purchase Orders**: 8 purchase orders
- **Purchase Requisitions**: 6 requisitions

### **Web3 Data**
- **Wallets**: 4 Ethereum wallets
- **Transactions**: 15 blockchain transactions
- **Tokens**: 3 popular tokens (ETH, USDC, LINK)

## 🔧 Command Options

### Clear Existing Data
Add `--clear` flag to remove existing data before seeding:
```bash
python manage.py seed_demo --clear
python manage.py seed_business_data --clear
```

### Custom Organization Name
```bash
python manage.py seed_demo --organization "My Company Name"
```

## 🎯 Use Cases

### **Demo Presentations**
- Use `seed_demo` for basic user setup
- Use `seed_business_data` for comprehensive business scenarios
- Perfect for showcasing all system features

### **Development Testing**
- Test all modules with realistic data
- Verify CRUD operations
- Test reporting and analytics

### **Training & Onboarding**
- New users can explore with sample data
- Learn system functionality without risk
- Practice with realistic business scenarios

## 📈 Data Relationships

The seed data creates realistic relationships between modules:
- **Sales Orders** → **Customers** → **Invoices** → **Payments**
- **Purchase Orders** → **Vendors** → **Inventory** → **Products**
- **Projects** → **Clients** → **Time Entries** → **Resources**
- **Employees** → **Departments** → **Payroll** → **Benefits**
- **Web3 Wallets** → **Transactions** → **Tokens** → **Smart Contracts**

## 🚨 Important Notes

1. **Production Warning**: Never run seed commands in production
2. **Data Backup**: Always backup before seeding if you have important data
3. **Clear Flag**: Use `--clear` to start fresh, omit to add to existing data
4. **Dependencies**: Run `seed_demo` before `seed_business_data`

## 🔍 Verification

After seeding, verify the data:
```bash
# Check users
python manage.py shell -c "from django.contrib.auth import get_user_model; print(User.objects.count())"

# Check products
python manage.py shell -c "from apps.inventory.models import Product; print(Product.objects.count())"

# Check customers
python manage.py shell -c "from apps.sales.models import Customer; print(Customer.objects.count())"
```

## 🎉 Ready to Demo!

Once seeded, your TidyGen ERP system will have:
- ✅ Realistic business data across all modules
- ✅ Multiple user accounts for different roles
- ✅ Sample transactions and relationships
- ✅ Complete demonstration scenarios
- ✅ Professional presentation-ready data

**Access your demo system at:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- Admin Panel: http://localhost:8000/admin
