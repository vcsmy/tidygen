"""
Django management command to seed the database with sample data for demonstration.
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
    help = 'Seed the database with comprehensive sample data for demonstration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )
        parser.add_argument(
            '--organization',
            type=str,
            default='TidyGen Corp',
            help='Organization name for the seed data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()

        self.stdout.write('Starting to seed database with sample data...')
        
        with transaction.atomic():
            # Create organization
            organization = self.create_organization(options['organization'])
            
            # Create core data
            self.create_roles_and_permissions(organization)
            admin_user = self.create_users(organization)
            
            # Create business data
            self.create_inventory_data(organization, admin_user)
            self.create_finance_data(organization, admin_user)
            self.create_hr_data(organization, admin_user)
            self.create_projects_data(organization, admin_user)
            self.create_sales_data(organization, admin_user)
            self.create_purchasing_data(organization, admin_user)
            self.create_web3_data(organization, admin_user)
            
        self.stdout.write(
            self.style.SUCCESS('Successfully seeded database with sample data!')
        )
        self.stdout.write(f'Admin user: admin / admin123')
        self.stdout.write(f'Organization: {organization.name}')

    def clear_data(self):
        """Clear existing data (except superusers)."""
        # Clear all data except superusers
        models_to_clear = [
            NFT, NFTCollection, DeFiPosition, WalletBalance, Token, SmartContract, 
            BlockchainTransaction, Wallet, PurchaseContract, PurchaseRequisitionItem,
            PurchaseRequisition, VendorContact, Vendor, SalesOpportunity, SalesLead,
            SalesInvoiceItem, SalesInvoice, SalesOrderItem, SalesOrder, CustomerContact,
            Customer, ProjectMilestone, TimeEntry, Resource, Project, Client,
            Candidate, JobPosting, PerformanceReview, Benefit, PayrollRecord,
            Employee, Department, FinancialReport, Budget, Payment, Invoice,
            Account, PurchaseOrderItem, PurchaseOrder, Supplier, Warehouse,
            StockItem, Product, ProductCategory, UserProfile, Permission, Role
        ]
        
        for model in models_to_clear:
            model.objects.all().delete()
        
        # Clear non-superuser users
        User.objects.filter(is_superuser=False).delete()
        Organization.objects.all().delete()

    def create_organization(self, org_name):
        """Create the main organization."""
        organization, created = Organization.objects.get_or_create(
            name=org_name,
            defaults={
                'slug': org_name.lower().replace(' ', '-'),
                'description': f'{org_name} - Enterprise Resource Planning System',
                'industry': 'Technology',
                'size': 'medium',
                'website': 'https://tidygen.com',
                'phone': '+1-555-0123',
                'email': 'info@tidygen.com',
                'address': '123 Business Street',
                'city': 'San Francisco',
                'state': 'CA',
                'country': 'USA',
                'postal_code': '94105'
            }
        )
        return organization

    def create_roles_and_permissions(self, organization):
        """Create roles and permissions."""
        # Create permissions
        permissions_data = [
            ('view_dashboard', 'Can view dashboard'),
            ('manage_users', 'Can manage users'),
            ('manage_finance', 'Can manage finance'),
            ('manage_inventory', 'Can manage inventory'),
            ('manage_hr', 'Can manage HR'),
            ('manage_projects', 'Can manage projects'),
            ('manage_sales', 'Can manage sales'),
            ('manage_purchasing', 'Can manage purchasing'),
            ('manage_web3', 'Can manage Web3'),
            ('view_reports', 'Can view reports'),
            ('admin_access', 'Can access admin panel'),
        ]
        
        permissions = {}
        for codename, name in permissions_data:
            perm, created = Permission.objects.get_or_create(
                codename=codename,
                defaults={'name': name, 'organization': organization}
            )
            permissions[codename] = perm

        # Create roles
        roles_data = [
            ('admin', 'Administrator', ['admin_access', 'manage_users', 'view_dashboard', 'view_reports']),
            ('finance', 'Finance Manager', ['manage_finance', 'view_dashboard', 'view_reports']),
            ('inventory', 'Inventory Manager', ['manage_inventory', 'view_dashboard', 'view_reports']),
            ('hr', 'HR Manager', ['manage_hr', 'view_dashboard', 'view_reports']),
            ('projects', 'Project Manager', ['manage_projects', 'view_dashboard', 'view_reports']),
            ('sales', 'Sales Manager', ['manage_sales', 'view_dashboard', 'view_reports']),
            ('purchasing', 'Purchasing Manager', ['manage_purchasing', 'view_dashboard', 'view_reports']),
            ('web3', 'Web3 Manager', ['manage_web3', 'view_dashboard', 'view_reports']),
            ('employee', 'Employee', ['view_dashboard']),
        ]
        
        for role_code, role_name, perm_codenames in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_code,
                defaults={'display_name': role_name, 'organization': organization}
            )
            if created:
                role.permissions.set([permissions[codename] for codename in perm_codenames])

    def create_users(self, organization):
        """Create sample users."""
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@tidygen.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_active': True,
                'organization': organization
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            
            # Create user profile
            UserProfile.objects.create(
                user=admin_user,
                organization=organization,
                phone='+1-555-0001',
                department='IT',
                position='System Administrator',
                hire_date=date.today() - timedelta(days=365)
            )

        # Create other sample users
        users_data = [
            ('john.doe', 'john.doe@tidygen.com', 'John', 'Doe', 'finance', 'Finance Manager'),
            ('jane.smith', 'jane.smith@tidygen.com', 'Jane', 'Smith', 'inventory', 'Inventory Manager'),
            ('mike.johnson', 'mike.johnson@tidygen.com', 'Mike', 'Johnson', 'hr', 'HR Manager'),
            ('sarah.wilson', 'sarah.wilson@tidygen.com', 'Sarah', 'Wilson', 'projects', 'Project Manager'),
            ('david.brown', 'david.brown@tidygen.com', 'David', 'Brown', 'sales', 'Sales Manager'),
            ('lisa.davis', 'lisa.davis@tidygen.com', 'Lisa', 'Davis', 'purchasing', 'Purchasing Manager'),
            ('alex.garcia', 'alex.garcia@tidygen.com', 'Alex', 'Garcia', 'web3', 'Web3 Manager'),
        ]
        
        for username, email, first_name, last_name, role_name, position in users_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_active': True,
                    'organization': organization
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                
                # Create user profile
                UserProfile.objects.create(
                    user=user,
                    organization=organization,
                    phone=f'+1-555-{random.randint(1000, 9999)}',
                    department=position.split()[0],
                    position=position,
                    hire_date=date.today() - timedelta(days=random.randint(30, 365))
                )

        return admin_user

    def create_inventory_data(self, organization, admin_user):
        """Create inventory sample data."""
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
            ('Laptop Pro 15"', 'LAP-001', 'Electronics', Decimal('1299.99'), Decimal('1599.99'), 50),
            ('Wireless Mouse', 'MOU-001', 'Hardware', Decimal('25.99'), Decimal('39.99'), 200),
            ('Office Chair', 'CHA-001', 'Furniture', Decimal('199.99'), Decimal('299.99'), 25),
            ('Monitor 24"', 'MON-001', 'Electronics', Decimal('199.99'), Decimal('299.99'), 75),
            ('Keyboard Mechanical', 'KEY-001', 'Hardware', Decimal('89.99'), Decimal('129.99'), 100),
            ('Desk Lamp', 'LAM-001', 'Furniture', Decimal('49.99'), Decimal('79.99'), 60),
            ('Software License', 'SW-001', 'Software', Decimal('99.99'), Decimal('149.99'), 1000),
            ('Printer Paper', 'PAP-001', 'Office Supplies', Decimal('4.99'), Decimal('7.99'), 500),
        ]
        
        products = {}
        for name, sku, category_name, cost_price, selling_price, stock in products_data:
            product, created = Product.objects.get_or_create(
                sku=sku,
                defaults={
                    'name': name,
                    'description': f'High-quality {name.lower()}',
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
            ('Main Warehouse', 'San Francisco, CA', 'Primary storage facility'),
            ('East Coast Warehouse', 'New York, NY', 'East coast distribution center'),
            ('West Coast Warehouse', 'Los Angeles, CA', 'West coast distribution center'),
        ]
        
        warehouses = {}
        for name, location, description in warehouses_data:
            warehouse, created = Warehouse.objects.get_or_create(
                name=name,
                defaults={
                    'location': location,
                    'description': description,
                    'capacity': random.randint(1000, 5000),
                    'organization': organization
                }
            )
            warehouses[name] = warehouse

        # Create suppliers
        suppliers_data = [
            ('TechSupply Inc', 'techsupply@example.com', '+1-555-1001', 'Electronics supplier'),
            ('OfficeMax Pro', 'sales@officemax.com', '+1-555-1002', 'Office supplies supplier'),
            ('Furniture World', 'orders@furnitureworld.com', '+1-555-1003', 'Furniture supplier'),
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

    def create_finance_data(self, organization, admin_user):
        """Create finance sample data."""
        # Create accounts
        accounts_data = [
            ('Cash', 'asset', 'Current Assets'),
            ('Accounts Receivable', 'asset', 'Current Assets'),
            ('Inventory', 'asset', 'Current Assets'),
            ('Accounts Payable', 'liability', 'Current Liabilities'),
            ('Sales Revenue', 'revenue', 'Revenue'),
            ('Cost of Goods Sold', 'expense', 'Cost of Sales'),
            ('Operating Expenses', 'expense', 'Operating Expenses'),
        ]
        
        for name, account_type, category in accounts_data:
            Account.objects.get_or_create(
                name=name,
                defaults={
                    'account_type': account_type,
                    'category': category,
                    'balance': Decimal(str(random.randint(1000, 100000))),
                    'organization': organization
                }
            )

        # Create sample invoices
        for i in range(10):
            Invoice.objects.get_or_create(
                invoice_number=f'INV-2024-{i+1:03d}',
                defaults={
                    'customer_name': f'Customer {i+1}',
                    'customer_email': f'customer{i+1}@example.com',
                    'amount': Decimal(str(random.randint(100, 5000))),
                    'status': random.choice(['draft', 'sent', 'paid', 'overdue']),
                    'due_date': date.today() + timedelta(days=random.randint(1, 30)),
                    'organization': organization,
                    'created_by': admin_user
                }
            )

    def create_hr_data(self, organization, admin_user):
        """Create HR sample data."""
        # Create departments
        departments_data = [
            ('IT', 'Information Technology'),
            ('Finance', 'Finance and Accounting'),
            ('HR', 'Human Resources'),
            ('Sales', 'Sales and Marketing'),
            ('Operations', 'Operations and Logistics'),
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
            ('John', 'Doe', 'john.doe@tidygen.com', 'IT', 'Software Engineer', Decimal('75000')),
            ('Jane', 'Smith', 'jane.smith@tidygen.com', 'Finance', 'Accountant', Decimal('65000')),
            ('Mike', 'Johnson', 'mike.johnson@tidygen.com', 'HR', 'HR Specialist', Decimal('60000')),
            ('Sarah', 'Wilson', 'sarah.wilson@tidygen.com', 'Sales', 'Sales Representative', Decimal('70000')),
            ('David', 'Brown', 'david.brown@tidygen.com', 'Operations', 'Operations Manager', Decimal('80000')),
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

    def create_projects_data(self, organization, admin_user):
        """Create projects sample data."""
        # Create clients
        clients_data = [
            ('Acme Corp', 'acme@example.com', '+1-555-2001', 'Technology company'),
            ('Global Solutions', 'contact@globalsolutions.com', '+1-555-2002', 'Consulting firm'),
            ('Innovation Labs', 'hello@innovationlabs.com', '+1-555-2003', 'Research and development'),
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
        ]
        
        for name, client_name, budget, project_type in projects_data:
            Project.objects.get_or_create(
                name=name,
                defaults={
                    'project_code': f'PRJ-{random.randint(100000, 999999)}',
                    'description': f'Professional {name.lower()} project',
                    'client': clients[client_name],
                    'project_type': project_type,
                    'status': random.choice(['planning', 'in_progress', 'completed']),
                    'priority': random.choice(['low', 'medium', 'high']),
                    'budget': budget,
                    'start_date': date.today() - timedelta(days=random.randint(1, 90)),
                    'planned_end_date': date.today() + timedelta(days=random.randint(30, 180)),
                    'project_manager': admin_user,
                    'organization': organization
                }
            )

    def create_sales_data(self, organization, admin_user):
        """Create sales sample data."""
        # Create customers
        customers_data = [
            ('TechStart Inc', 'contact@techstart.com', '+1-555-3001', 'business'),
            ('Retail Plus', 'orders@retailplus.com', '+1-555-3002', 'business'),
            ('Individual Customer', 'customer@example.com', '+1-555-3003', 'individual'),
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
        for i in range(5):
            SalesOrder.objects.get_or_create(
                order_number=f'SO-2024-{i+1:03d}',
                defaults={
                    'customer': random.choice(list(customers.values())),
                    'status': random.choice(['draft', 'confirmed', 'shipped', 'delivered']),
                    'total_amount': Decimal(str(random.randint(500, 5000))),
                    'order_date': date.today() - timedelta(days=random.randint(1, 30)),
                    'organization': organization,
                    'created_by': admin_user
                }
            )

    def create_purchasing_data(self, organization, admin_user):
        """Create purchasing sample data."""
        # Create vendors
        vendors_data = [
            ('TechSupply Inc', 'orders@techsupply.com', '+1-555-4001', 'manufacturer'),
            ('OfficeMax Pro', 'purchasing@officemax.com', '+1-555-4002', 'distributor'),
            ('Global Suppliers', 'sales@globalsuppliers.com', '+1-555-4003', 'wholesaler'),
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
                    'overall_rating': random.uniform(3.0, 5.0),
                    'organization': organization
                }
            )
            vendors[name] = vendor

        # Create purchase orders
        for i in range(5):
            PurchaseOrder.objects.get_or_create(
                po_number=f'PO-2024-{i+1:03d}',
                defaults={
                    'vendor': random.choice(list(vendors.values())),
                    'status': random.choice(['draft', 'pending_approval', 'approved', 'ordered']),
                    'total_amount': Decimal(str(random.randint(1000, 10000))),
                    'order_date': date.today() - timedelta(days=random.randint(1, 30)),
                    'expected_delivery_date': date.today() + timedelta(days=random.randint(7, 30)),
                    'organization': organization,
                    'requested_by': admin_user
                }
            )

    def create_web3_data(self, organization, admin_user):
        """Create Web3 sample data."""
        # Create wallets
        wallets_data = [
            ('Main Wallet', '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6', 'ethereum'),
            ('Trading Wallet', '0x8ba1f109551bD432803012645Hac136c4c4c4c4c', 'ethereum'),
            ('DeFi Wallet', '0x1234567890123456789012345678901234567890', 'ethereum'),
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
                    'organization': organization,
                    'created_by': admin_user
                }
            )
            wallets[name] = wallet

        # Create sample transactions
        for i in range(10):
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
