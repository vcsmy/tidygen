"""
Django management command to seed the database with comprehensive business data.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from decimal import Decimal
from datetime import date, timedelta
import random

from apps.organizations.models import Organization
from apps.core.models import Role, Permission
from apps.accounts.models import UserProfile
from apps.inventory.models import (
    ProductCategory, Product, StockItem, Warehouse, Supplier, PurchaseOrder, PurchaseOrderItem
)
from apps.finance.models import (
    Account, Invoice, Payment, Budget, FinancialReport
)
from apps.hr.models import (
    Department, Employee, PayrollRecord, Benefit, PerformanceReview, JobPosting, Candidate
)
from apps.projects.models import (
    Client, Project, Resource, TimeEntry, ProjectMilestone
)
from apps.sales.models import (
    Customer, CustomerContact, SalesOrder, SalesOrderItem, SalesInvoice, SalesInvoiceItem, SalesLead, SalesOpportunity
)
from apps.purchasing.models import (
    Vendor, VendorContact, PurchaseRequisition, PurchaseRequisitionItem, PurchaseContract
)
from apps.web3.models import (
    Wallet, BlockchainTransaction, SmartContract, Token, WalletBalance, DeFiPosition, NFT, NFTCollection
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with comprehensive business data for demonstration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing business data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing business data...')
            self.clear_business_data()

        self.stdout.write('Starting to seed database with business data...')
        
        with transaction.atomic():
            # Get or create organization
            try:
                organization = Organization.objects.first()
                if not organization:
                    self.stdout.write(self.style.ERROR('No organization found. Please run seed_demo first.'))
                    return
            except Organization.DoesNotExist:
                self.stdout.write(self.style.ERROR('No organization found. Please run seed_demo first.'))
                return
            
            # Create business data
            self.create_inventory_data(organization)
            self.create_finance_data(organization)
            self.create_hr_data(organization)
            self.create_projects_data(organization)
            self.create_sales_data(organization)
            self.create_purchasing_data(organization)
            self.create_web3_data(organization)
            
        self.stdout.write(
            self.style.SUCCESS('Successfully seeded database with business data!')
        )

    def clear_business_data(self):
        """Clear existing business data."""
        # Clear all business data
        models_to_clear = [
            NFT, NFTCollection, DeFiPosition, WalletBalance, Token, SmartContract, 
            BlockchainTransaction, Wallet, PurchaseContract, PurchaseRequisitionItem,
            PurchaseRequisition, VendorContact, Vendor, SalesOpportunity, SalesLead,
            SalesInvoiceItem, SalesInvoice, SalesOrderItem, SalesOrder, CustomerContact,
            Customer, ProjectMilestone, TimeEntry, Resource, Project, Client,
            Candidate, JobPosting, PerformanceReview, Benefit, PayrollRecord,
            Employee, Department, FinancialReport, Budget, Payment, Invoice,
            Account, PurchaseOrderItem, PurchaseOrder, Supplier, Warehouse,
            StockItem, Product, ProductCategory
        ]
        
        for model in models_to_clear:
            model.objects.all().delete()

    def create_inventory_data(self, organization):
        """Create inventory sample data."""
        self.stdout.write('Creating inventory data...')
        
        # Create categories
        categories_data = [
            ('Electronics', 'Electronic devices and components'),
            ('Office Supplies', 'Office equipment and supplies'),
            ('Software', 'Software licenses and subscriptions'),
            ('Hardware', 'Computer hardware and accessories'),
            ('Furniture', 'Office furniture and fixtures'),
        ]
        
        categories = {}
        for name, description in categories_data:
            category, created = ProductCategory.objects.get_or_create(
                name=name,
                defaults={'description': description, 'organization': organization}
            )
            categories[name] = category

        # Create products
        products_data = [
            ('MacBook Pro 16"', 'LAP-001', 'Electronics', Decimal('1999.99'), Decimal('2499.99'), 25),
            ('Dell XPS 13', 'LAP-002', 'Electronics', Decimal('999.99'), Decimal('1299.99'), 30),
            ('Wireless Mouse', 'MOU-001', 'Hardware', Decimal('25.99'), Decimal('39.99'), 200),
            ('Mechanical Keyboard', 'KEY-001', 'Hardware', Decimal('89.99'), Decimal('129.99'), 100),
            ('Office Chair', 'CHA-001', 'Furniture', Decimal('199.99'), Decimal('299.99'), 25),
            ('Standing Desk', 'DES-001', 'Furniture', Decimal('399.99'), Decimal('599.99'), 15),
            ('Monitor 27"', 'MON-001', 'Electronics', Decimal('299.99'), Decimal('399.99'), 50),
            ('Monitor 24"', 'MON-002', 'Electronics', Decimal('199.99'), Decimal('299.99'), 75),
            ('Software License', 'SW-001', 'Software', Decimal('99.99'), Decimal('149.99'), 1000),
            ('Printer Paper', 'PAP-001', 'Office Supplies', Decimal('4.99'), Decimal('7.99'), 500),
        ]
        
        products = {}
        for name, sku, category_name, cost_price, selling_price, stock in products_data:
            product, created = Product.objects.get_or_create(
                sku=sku,
                defaults={
                    'name': name,
                    'description': f'High-quality {name.lower()} for professional use',
                    'category': categories[category_name],
                    'cost_price': cost_price,
                    'selling_price': selling_price,
                    'current_stock': stock,
                    'min_stock_level': stock // 10,
                    'max_stock_level': stock * 2,
                    'organization': organization
                }
            )
            products[sku] = product

        # Create warehouses
        warehouses_data = [
            ('Main Warehouse', 'San Francisco, CA', 'Primary storage facility', 5000),
            ('East Coast Warehouse', 'New York, NY', 'East coast distribution center', 3000),
            ('West Coast Warehouse', 'Los Angeles, CA', 'West coast distribution center', 4000),
        ]
        
        warehouses = {}
        for name, location, description, capacity in warehouses_data:
            warehouse, created = Warehouse.objects.get_or_create(
                name=name,
                defaults={
                    'location': location,
                    'description': description,
                    'capacity': capacity,
                    'organization': organization
                }
            )
            warehouses[name] = warehouse

        # Create suppliers
        suppliers_data = [
            ('TechSupply Inc', 'orders@techsupply.com', '+1-555-1001', 'Electronics supplier'),
            ('OfficeMax Pro', 'sales@officemax.com', '+1-555-1002', 'Office supplies supplier'),
            ('Furniture World', 'orders@furnitureworld.com', '+1-555-1003', 'Furniture supplier'),
            ('Global Hardware', 'sales@globalhardware.com', '+1-555-1004', 'Hardware supplier'),
        ]
        
        suppliers = {}
        for name, email, phone, description in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                name=name,
                defaults={
                    'contact_person': f'{name} Sales Team',
                    'email': email,
                    'phone': phone,
                    'address': f'123 {name} Street',
                    'city': 'San Francisco',
                    'state': 'CA',
                    'country': 'USA',
                    'postal_code': '94105',
                    'payment_terms': 'net_30',
                    'organization': organization
                }
            )
            suppliers[name] = supplier

    def create_finance_data(self, organization):
        """Create finance sample data."""
        self.stdout.write('Creating finance data...')
        
        # Create accounts
        accounts_data = [
            ('Cash', 'asset', 'Current Assets', Decimal('50000')),
            ('Accounts Receivable', 'asset', 'Current Assets', Decimal('25000')),
            ('Inventory', 'asset', 'Current Assets', Decimal('100000')),
            ('Accounts Payable', 'liability', 'Current Liabilities', Decimal('15000')),
            ('Sales Revenue', 'revenue', 'Revenue', Decimal('0')),
            ('Cost of Goods Sold', 'expense', 'Cost of Sales', Decimal('0')),
            ('Operating Expenses', 'expense', 'Operating Expenses', Decimal('0')),
        ]
        
        for name, account_type, category, balance in accounts_data:
            Account.objects.get_or_create(
                name=name,
                defaults={
                    'account_type': account_type,
                    'category': category,
                    'balance': balance,
                    'organization': organization
                }
            )

        # Create sample invoices
        for i in range(15):
            Invoice.objects.get_or_create(
                invoice_number=f'INV-2024-{i+1:03d}',
                defaults={
                    'customer_name': f'Customer {i+1}',
                    'customer_email': f'customer{i+1}@example.com',
                    'amount': Decimal(str(random.randint(500, 10000))),
                    'status': random.choice(['draft', 'sent', 'paid', 'overdue']),
                    'due_date': date.today() + timedelta(days=random.randint(1, 30)),
                    'organization': organization
                }
            )

        # Create sample payments
        for i in range(10):
            Payment.objects.get_or_create(
                payment_number=f'PAY-2024-{i+1:03d}',
                defaults={
                    'customer_name': f'Customer {i+1}',
                    'amount': Decimal(str(random.randint(500, 5000))),
                    'payment_method': random.choice(['credit_card', 'bank_transfer', 'check', 'cash']),
                    'status': random.choice(['pending', 'completed', 'failed']),
                    'payment_date': date.today() - timedelta(days=random.randint(1, 30)),
                    'organization': organization
                }
            )

    def create_hr_data(self, organization):
        """Create HR sample data."""
        self.stdout.write('Creating HR data...')
        
        # Create departments
        departments_data = [
            ('IT', 'Information Technology'),
            ('Finance', 'Finance and Accounting'),
            ('HR', 'Human Resources'),
            ('Sales', 'Sales and Marketing'),
            ('Operations', 'Operations and Logistics'),
            ('Engineering', 'Software Engineering'),
        ]
        
        departments = {}
        for name, description in departments_data:
            department, created = Department.objects.get_or_create(
                name=name,
                defaults={'description': description, 'organization': organization}
            )
            departments[name] = department

        # Create employees
        employees_data = [
            ('John', 'Doe', 'john.doe@tidygen-demo.com', 'IT', 'Software Engineer', Decimal('75000')),
            ('Jane', 'Smith', 'jane.smith@tidygen-demo.com', 'Finance', 'Accountant', Decimal('65000')),
            ('Mike', 'Johnson', 'mike.johnson@tidygen-demo.com', 'HR', 'HR Specialist', Decimal('60000')),
            ('Sarah', 'Wilson', 'sarah.wilson@tidygen-demo.com', 'Sales', 'Sales Representative', Decimal('70000')),
            ('David', 'Brown', 'david.brown@tidygen-demo.com', 'Operations', 'Operations Manager', Decimal('80000')),
            ('Lisa', 'Davis', 'lisa.davis@tidygen-demo.com', 'Engineering', 'Senior Developer', Decimal('90000')),
            ('Alex', 'Garcia', 'alex.garcia@tidygen-demo.com', 'IT', 'DevOps Engineer', Decimal('85000')),
            ('Emma', 'Martinez', 'emma.martinez@tidygen-demo.com', 'Sales', 'Sales Manager', Decimal('75000')),
        ]
        
        for first_name, last_name, email, dept_name, position, salary in employees_data:
            Employee.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'employee_id': f'EMP-{random.randint(1000, 9999)}',
                    'department': departments[dept_name],
                    'position': position,
                    'salary': salary,
                    'hire_date': date.today() - timedelta(days=random.randint(30, 365)),
                    'status': 'active',
                    'organization': organization
                }
            )

    def create_projects_data(self, organization):
        """Create projects sample data."""
        self.stdout.write('Creating projects data...')
        
        # Create clients
        clients_data = [
            ('Acme Corp', 'contact@acme.com', '+1-555-2001', 'Technology company'),
            ('Global Solutions', 'contact@globalsolutions.com', '+1-555-2002', 'Consulting firm'),
            ('Innovation Labs', 'hello@innovationlabs.com', '+1-555-2003', 'Research and development'),
            ('TechStart Inc', 'info@techstart.com', '+1-555-2004', 'Startup company'),
        ]
        
        clients = {}
        for name, email, phone, description in clients_data:
            client, created = Client.objects.get_or_create(
                name=name,
                defaults={
                    'client_code': f'CLI-{random.randint(1000, 9999)}',
                    'email': email,
                    'phone': phone,
                    'description': description,
                    'status': 'active',
                    'organization': organization
                }
            )
            clients[name] = client

        # Create projects
        projects_data = [
            ('Website Redesign', 'Acme Corp', Decimal('25000'), 'web_development'),
            ('Mobile App Development', 'Global Solutions', Decimal('50000'), 'mobile_development'),
            ('Data Analytics Platform', 'Innovation Labs', Decimal('75000'), 'data_science'),
            ('E-commerce Platform', 'TechStart Inc', Decimal('40000'), 'web_development'),
            ('API Integration', 'Acme Corp', Decimal('15000'), 'api_development'),
        ]
        
        for name, client_name, budget, project_type in projects_data:
            Project.objects.get_or_create(
                name=name,
                defaults={
                    'project_code': f'PRJ-{random.randint(100000, 999999)}',
                    'description': f'Professional {name.lower()} project for {client_name}',
                    'client': clients[client_name],
                    'project_type': project_type,
                    'status': random.choice(['planning', 'in_progress', 'completed']),
                    'priority': random.choice(['low', 'medium', 'high']),
                    'budget': budget,
                    'start_date': date.today() - timedelta(days=random.randint(1, 90)),
                    'planned_end_date': date.today() + timedelta(days=random.randint(30, 180)),
                    'organization': organization
                }
            )

    def create_sales_data(self, organization):
        """Create sales sample data."""
        self.stdout.write('Creating sales data...')
        
        # Create customers
        customers_data = [
            ('TechStart Inc', 'contact@techstart.com', '+1-555-3001', 'business'),
            ('Retail Plus', 'orders@retailplus.com', '+1-555-3002', 'business'),
            ('Individual Customer', 'customer@example.com', '+1-555-3003', 'individual'),
            ('Enterprise Corp', 'sales@enterprise.com', '+1-555-3004', 'business'),
            ('Small Business LLC', 'info@smallbiz.com', '+1-555-3005', 'business'),
        ]
        
        customers = {}
        for name, email, phone, customer_type in customers_data:
            customer, created = Customer.objects.get_or_create(
                name=name,
                defaults={
                    'customer_code': f'CUST-{random.randint(1000, 9999)}',
                    'email': email,
                    'phone': phone,
                    'customer_type': customer_type,
                    'status': 'active',
                    'organization': organization
                }
            )
            customers[name] = customer

        # Create sales orders
        for i in range(10):
            SalesOrder.objects.get_or_create(
                order_number=f'SO-2024-{i+1:03d}',
                defaults={
                    'customer': random.choice(list(customers.values())),
                    'status': random.choice(['draft', 'confirmed', 'shipped', 'delivered']),
                    'total_amount': Decimal(str(random.randint(1000, 15000))),
                    'order_date': date.today() - timedelta(days=random.randint(1, 30)),
                    'organization': organization
                }
            )

        # Create sales leads
        for i in range(8):
            SalesLead.objects.get_or_create(
                lead_number=f'LEAD-2024-{i+1:03d}',
                defaults={
                    'company_name': f'Prospect Company {i+1}',
                    'contact_name': f'Contact Person {i+1}',
                    'email': f'prospect{i+1}@example.com',
                    'phone': f'+1-555-{random.randint(4000, 4999)}',
                    'status': random.choice(['new', 'contacted', 'qualified', 'proposal', 'negotiation', 'closed_won', 'closed_lost']),
                    'source': random.choice(['website', 'referral', 'cold_call', 'email', 'social_media']),
                    'estimated_value': Decimal(str(random.randint(5000, 50000))),
                    'organization': organization
                }
            )

    def create_purchasing_data(self, organization):
        """Create purchasing sample data."""
        self.stdout.write('Creating purchasing data...')
        
        # Create vendors
        vendors_data = [
            ('TechSupply Inc', 'orders@techsupply.com', '+1-555-4001', 'manufacturer'),
            ('OfficeMax Pro', 'purchasing@officemax.com', '+1-555-4002', 'distributor'),
            ('Global Suppliers', 'sales@globalsuppliers.com', '+1-555-4003', 'wholesaler'),
            ('Premium Hardware', 'orders@premiumhardware.com', '+1-555-4004', 'manufacturer'),
        ]
        
        vendors = {}
        for name, email, phone, business_type in vendors_data:
            vendor, created = Vendor.objects.get_or_create(
                name=name,
                defaults={
                    'vendor_code': f'VEND-{random.randint(1000, 9999)}',
                    'email': email,
                    'phone': phone,
                    'business_type': business_type,
                    'status': 'active',
                    'payment_terms': 'net_30',
                    'credit_limit': Decimal(str(random.randint(10000, 100000))),
                    'overall_rating': random.uniform(3.5, 5.0),
                    'organization': organization
                }
            )
            vendors[name] = vendor

        # Create purchase orders
        for i in range(8):
            PurchaseOrder.objects.get_or_create(
                po_number=f'PO-2024-{i+1:03d}',
                defaults={
                    'vendor': random.choice(list(vendors.values())),
                    'status': random.choice(['draft', 'pending_approval', 'approved', 'ordered', 'received']),
                    'total_amount': Decimal(str(random.randint(2000, 20000))),
                    'order_date': date.today() - timedelta(days=random.randint(1, 30)),
                    'expected_delivery_date': date.today() + timedelta(days=random.randint(7, 30)),
                    'organization': organization
                }
            )

        # Create purchase requisitions
        for i in range(6):
            PurchaseRequisition.objects.get_or_create(
                requisition_number=f'PR-2024-{i+1:03d}',
                defaults={
                    'title': f'Purchase Request {i+1}',
                    'description': f'Request for purchasing items for project {i+1}',
                    'status': random.choice(['draft', 'submitted', 'under_review', 'approved', 'converted']),
                    'priority': random.choice(['low', 'medium', 'high']),
                    'required_date': date.today() + timedelta(days=random.randint(7, 30)),
                    'estimated_total': Decimal(str(random.randint(1000, 10000))),
                    'budget_code': f'BUD-{random.randint(100, 999)}',
                    'organization': organization
                }
            )

    def create_web3_data(self, organization):
        """Create Web3 sample data."""
        self.stdout.write('Creating Web3 data...')
        
        # Create wallets
        wallets_data = [
            ('Main Wallet', '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6', 'ethereum'),
            ('Trading Wallet', '0x8ba1f109551bD432803012645Hac136c4c4c4c4c', 'ethereum'),
            ('DeFi Wallet', '0x1234567890123456789012345678901234567890', 'ethereum'),
            ('NFT Wallet', '0xabcdef1234567890abcdef1234567890abcdef12', 'ethereum'),
        ]
        
        wallets = {}
        for name, address, blockchain in wallets_data:
            wallet, created = Wallet.objects.get_or_create(
                address=address,
                defaults={
                    'name': name,
                    'blockchain': blockchain,
                    'wallet_type': 'external',
                    'is_active': True,
                    'organization': organization
                }
            )
            wallets[name] = wallet

        # Create sample transactions
        for i in range(15):
            BlockchainTransaction.objects.get_or_create(
                tx_hash=f'0x{random.randint(1000000000000000000000000000000000000000, 9999999999999999999999999999999999999999)}',
                defaults={
                    'wallet': random.choice(list(wallets.values())),
                    'transaction_type': random.choice(['send', 'receive', 'contract_interaction']),
                    'amount': Decimal(str(random.uniform(0.1, 10.0))),
                    'status': random.choice(['pending', 'confirmed', 'failed']),
                    'gas_used': random.randint(21000, 100000),
                    'gas_price': Decimal(str(random.uniform(20, 100))),
                    'organization': organization
                }
            )

        # Create sample tokens
        tokens_data = [
            ('Ethereum', 'ETH', '0x0000000000000000000000000000000000000000', Decimal('18')),
            ('USD Coin', 'USDC', '0xA0b86a33E6441b8C4C8C0C4C4C4C4C4C4C4C4C4', Decimal('6')),
            ('Chainlink', 'LINK', '0x514910771AF9Ca656af840dff83E8264EcF986CA', Decimal('18')),
        ]
        
        for name, symbol, address, decimals in tokens_data:
            Token.objects.get_or_create(
                symbol=symbol,
                defaults={
                    'name': name,
                    'contract_address': address,
                    'decimals': decimals,
                    'organization': organization
                }
            )
