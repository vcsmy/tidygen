"""
Comprehensive seed data management command for TidyGen ERP Community Demo.
Creates extensive sample data for all portals and modules to showcase the application.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from decimal import Decimal
from datetime import date, timedelta, datetime
import random
import uuid

# Core imports
from apps.core.models import Role, Permission, Organization, SystemSettings

# Auth and user imports
from apps.accounts.models import UserProfile

# Business modules
from apps.inventory.models import (
    ProductCategory, Product, StockMovement, Supplier, PurchaseOrder, PurchaseOrderItem
)
from apps.finance.models import (
    Account, Invoice, Payment, Budget, FinancialReport, Customer as FinanceCustomer, Vendor as FinanceVendor
)
from apps.hr.models import (
    Department, Employee, Payroll, PayrollPeriod, PerformanceReview, Training, Document, Position
)
from apps.sales.models import (
    Client, IndividualClient, CorporateClient, ClientContact
)
from apps.purchasing.models import (
    PurchaseOrder, PurchaseOrderItem, ProcurementRequest, PurchaseReceipt
)

# New Community Edition modules
from apps.freelancers.models import (
    Freelancer, FreelancerDocument, FreelancerAvailability, FreelancerSkill, 
    FreelancerSkillAssignment, FreelancerReview
)
from apps.gig_management.models import (
    GigCategory, GigJob, GigApplication, JobMilestone, JobPhoto, JobMessage, JobReview
)
from apps.contractor_payments.models import (
    ContractorPayment, PaymentMethod, EscrowAccount, PaymentSchedule, DisputeResolution
)
from apps.freelancer_web3.models import (
    FreelancerNFTBadge, FreelancerReputationToken, FreelancerSmartContract, FreelancerWeb3Transaction
)

# Additional modules
from apps.analytics.models import KPI, Report, ReportTemplate, AnalyticsCache
from apps.audit_trail.models import AuditEvent
from apps.facility_management.models import Facility, Vehicle, Equipment
from apps.field_operations.models import (
    FieldTeam, TeamMember, ServiceRoute, RouteStop, FieldJob, JobEquipment, DispatchLog
)
from apps.payroll.models import (
    PayrollConfiguration, PayrollComponent, EmployeePayrollProfile, PayrollRun,
    TaxYear, PayrollReport, PayrollIntegration
)
from apps.scheduling.models import (
    ScheduleTemplate, Resource, Team, TeamMember, Appointment, ScheduleConflict,
    ScheduleRule, ScheduleNotification, ScheduleAnalytics
)
from apps.ledger.models import LedgerTransaction, LedgerBatch, LedgerEvent, LedgerConfiguration
from apps.wallet.models import Wallet, WalletSignature
from apps.did_auth.models import DIDDocument, DIDCredential, DIDSession
from apps.web3.models import (
    Wallet as Web3Wallet, BlockchainTransaction, SmartContract, Token, WalletBalance as Web3WalletBalance
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with comprehensive demo data for all portals and modules'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )
        parser.add_argument(
            '--organization',
            type=str,
            default='TidyGen Community Demo',
            help='Organization name for the demo',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()

        self.stdout.write('Starting comprehensive demo data seeding...')
        
        with transaction.atomic():
            # Create organization
            organization = self.create_organization(options['organization'])
            
            # Create core data
            self.create_roles_and_permissions(organization)
            users_data = self.create_users(organization)
            
            # Create all module data
            self.create_inventory_data(organization, users_data['admin'])
            self.create_finance_data(organization, users_data['admin'])
            self.create_hr_data(organization, users_data['admin'])
            self.create_sales_data(organization, users_data['admin'])
            self.create_purchasing_data(organization, users_data['admin'])
            self.create_freelancers_data(organization, users_data)
            self.create_gig_management_data(organization, users_data)
            self.create_contractor_payments_data(organization, users_data)
            self.create_freelancer_web3_data(organization, users_data)
            self.create_analytics_data(organization, users_data['admin'])
            self.create_audit_trail_data(organization, users_data)
            self.create_facility_management_data(organization, users_data['admin'])
            self.create_field_operations_data(organization, users_data)
            self.create_payroll_data(organization, users_data)
            self.create_scheduling_data(organization, users_data)
            self.create_ledger_data(organization, users_data['admin'])
            self.create_wallet_data(organization, users_data)
            self.create_did_auth_data(organization, users_data)
            
        self.stdout.write(
            self.style.SUCCESS('Successfully seeded database with comprehensive demo data!')
        )
        self.stdout.write(f'Admin user: admin / admin123')
        self.stdout.write(f'Manager user: manager@tidygen.com / manager123')
        self.stdout.write(f'Freelancer users: freelancer1-5@tidygen.com / freelancer123')
        self.stdout.write(f'Organization: {organization.name}')

    def clear_data(self):
        """Clear existing data (except superusers)."""
        # Clear all models in reverse dependency order
        models_to_clear = [
            # Community Edition modules first
            FreelancerWeb3Transaction, FreelancerSmartContract, FreelancerReputationToken, FreelancerNFTBadge,
            DisputeResolution, PaymentSchedule, EscrowAccount, ContractorPayment, PaymentMethod,
            JobReview, JobMessage, JobPhoto, JobMilestone, GigApplication, GigJob, GigCategory,
            FreelancerReview, FreelancerSkillAssignment, FreelancerSkill, 
            FreelancerAvailability, FreelancerDocument, Freelancer,
            
            # Other modules
            ScheduleAnalytics, ScheduleNotification, ScheduleRule, ScheduleConflict,
            Appointment, TeamMember, Team, Resource, ScheduleTemplate,
            PayrollIntegration, PayrollReport, TaxYear, PayrollRun, EmployeePayrollProfile,
            PayrollComponent, PayrollConfiguration,
            DispatchLog, JobEquipment, FieldJob, RouteStop, ServiceRoute, FieldTeam,
            Equipment, Vehicle, Facility,
            DIDSession, DIDCredential, DIDDocument,
            WalletSignature, Wallet,
            LedgerConfiguration, LedgerEvent, LedgerBatch, LedgerTransaction,
            AnalyticsCache, ReportTemplate, Report, KPI,
            AuditEvent,
            
            # Core business modules
            Web3WalletBalance, Token, SmartContract, BlockchainTransaction, Web3Wallet,
            PurchaseOrderItem, PurchaseOrder, ProcurementRequest, PurchaseReceipt,
            ClientContact, CorporateClient, IndividualClient, Client,
            Document, Training, PerformanceReview, Payroll, PayrollPeriod,
            Employee, Department, Position, FinancialReport, Budget, Payment, Invoice, Account,
            FinanceCustomer, FinanceVendor, Supplier, StockMovement, Product, ProductCategory, UserProfile, Permission, Role
        ]
        
        for model in models_to_clear:
            try:
                model.objects.all().delete()
            except Exception as e:
                self.stdout.write(f'Warning: Could not clear {model.__name__}: {e}')
        
        # Clear non-superuser users and organization
        User.objects.filter(is_superuser=False).delete()
        Organization.objects.all().delete()

    def create_organization(self, org_name):
        """Create the demo organization."""
        organization, created = Organization.objects.get_or_create(
            name=org_name,
            defaults={
                'description': f'{org_name} - Comprehensive ERP Demo Platform',
                'industry': 'Cleaning Services',
                'size': '1000+',
                'website': 'https://tidygen.com',
                'phone': '+1-555-0123',
                'email': 'demo@tidygen.com',
                'address_line1': '456 Demo Street',
                'city': 'San Francisco',
                'state': 'CA',
                'country': 'USA',
                'postal_code': '94105'
            }
        )
        return organization

    def create_roles_and_permissions(self, organization):
        """Create comprehensive roles and permissions."""
        permissions_data = [
            ('view_dashboard', 'Can view dashboard'),
            ('manage_users', 'Can manage users'),
            ('manage_finance', 'Can manage finance'),
            ('manage_inventory', 'Can manage inventory'),
            ('manage_hr', 'Can manage HR'),
            ('manage_sales', 'Can manage sales'),
            ('manage_purchasing', 'Can manage purchasing'),
            ('manage_web3', 'Can manage Web3'),
            ('manage_freelancers', 'Can manage freelancers'),
            ('manage_gigs', 'Can manage gigs'),
            ('manage_payments', 'Can manage contractor payments'),
            ('manage_analytics', 'Can view analytics'),
            ('manage_scheduling', 'Can manage scheduling'),
            ('manage_facilities', 'Can manage facilities'),
            ('manage_payroll', 'Can manage payroll'),
            ('view_reports', 'Can view reports'),
            ('admin_access', 'Can access admin panel'),
        ]
        
        permissions = {}
        for codename, name in permissions_data:
            perm, created = Permission.objects.get_or_create(
                codename=codename,
                defaults={'name': name}
            )
            permissions[codename] = perm

        # Create comprehensive roles
        roles_data = [
            ('admin', 'Administrator', ['admin_access', 'manage_users', 'view_dashboard', 'view_reports']),
            ('manager', 'Manager', ['manage_freelancers', 'manage_gigs', 'manage_payments', 'view_dashboard', 'view_reports']),
            ('finance', 'Finance Manager', ['manage_finance', 'manage_payments', 'view_dashboard', 'view_reports']),
            ('hr', 'HR Manager', ['manage_hr', 'manage_payroll', 'view_dashboard', 'view_reports']),
            ('freelancer', 'Freelancer', ['view_dashboard']),
            ('client', 'Client', ['view_dashboard']),
        ]
        
        for role_code, role_name, perm_codenames in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_code,
                defaults={'description': role_name}
            )
            if created:
                role.permissions.set([permissions[codename] for codename in perm_codenames if codename in permissions])

    def create_users(self, organization):
        """Create comprehensive user base."""
        users_data = {}
        
        # Admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@tidygen.com',
                'first_name': 'System',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
        users_data['admin'] = admin_user

        # Manager user
        manager_user, created = User.objects.get_or_create(
            username='manager',
            defaults={
                'email': 'manager@tidygen.com',
                'first_name': 'Demo',
                'last_name': 'Manager',
                'is_staff': True,
                'is_active': True,
            }
        )
        if created:
            manager_user.set_password('manager123')
            manager_user.save()
        users_data['manager'] = manager_user

        # Create demo freelancers
        for i in range(1, 11):
            freelancer_user, created = User.objects.get_or_create(
                username=f'freelancer{i}',
                defaults={
                    'email': f'freelancer{i}@tidygen.com',
                    'first_name': f'Freelancer{i}',
                    'last_name': 'Cleaner',
                    'is_active': True,
                }
            )
            if created:
                freelancer_user.set_password('freelancer123')
                freelancer_user.save()
            users_data[f'freelancer{i}'] = freelancer_user

        # Create demo clients
        for i in range(1, 6):
            client_user, created = User.objects.get_or_create(
                username=f'client{i}',
                defaults={
                    'email': f'client{i}@tidygen.com',
                    'first_name': f'Client{i}',
                    'last_name': 'Customer',
                    'is_active': True,
                }
            )
            if created:
                client_user.set_password('client123')
                client_user.save()
            users_data[f'client{i}'] = client_user

        return users_data

    def create_inventory_data(self, organization, admin_user):
        """Create extensive inventory data."""
        # Product categories for cleaning business
        categories_data = [
            ('Cleaning Supplies', 'All cleaning products and supplies'),
            ('Equipment', 'Cleaning equipment and tools'),
            ('Safety Gear', 'Safety equipment and protective gear'),
            ('Office Supplies', 'General office supplies'),
            ('Maintenance', 'Building and equipment maintenance items'),
        ]
        
        categories = {}
        for name, description in categories_data:
            category, created = ProductCategory.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            categories[name] = category

        # Extensive product catalog
        products_data = [
            ('All-Purpose Cleaner', 'CLN-001', 'Cleaning Supplies', Decimal('8.99'), Decimal('12.99'), 150),
            ('Disinfectant Spray', 'CLN-002', 'Cleaning Supplies', Decimal('12.99'), Decimal('18.99'), 100),
            ('Microfiber Cloths', 'CLN-003', 'Cleaning Supplies', Decimal('15.99'), Decimal('24.99'), 200),
            ('Vacuum Cleaner', 'EQP-001', 'Equipment', Decimal('299.99'), Decimal('449.99'), 25),
            ('Floor Scrubber', 'EQP-002', 'Equipment', Decimal('599.99'), Decimal('899.99'), 15),
            ('Window Squeegee', 'EQP-003', 'Equipment', Decimal('24.99'), Decimal('34.99'), 50),
            ('Safety Goggles', 'SF-001', 'Safety Gear', Decimal('9.99'), Decimal('14.99'), 80),
            ('Rubber Gloves', 'SF-002', 'Safety Gear', Decimal('12.99'), Decimal('18.99'), 120),
            ('Face Masks', 'SF-003', 'Safety Gear', Decimal('19.99'), Decimal('29.99'), 300),
        ]
        
        for name, sku, category_name, cost_price, selling_price, stock in products_data:
            Product.objects.get_or_create(
                sku=sku,
                defaults={
                    'name': name,
                    'description': f'High-quality {name.lower()} for professional cleaning',
                    'category': categories[category_name],
                    'cost_price': cost_price,
                    'selling_price': selling_price,
                    'current_stock': stock,
                    'min_stock_level': stock // 5,
                    'max_stock_level': stock * 2,
                }
            )

    def create_finance_data(self, organization, admin_user):
        """Create comprehensive finance data."""
        # Chart of accounts for cleaning business
        accounts_data = [
            ('Cash', 'CASH001', 'asset'),
            ('Accounts Receivable', 'AR001', 'asset'),
            ('Equipment', 'EQ001', 'asset'),
            ('Accounts Payable', 'AP001', 'liability'),
            ('Cleaning Revenue', 'REV001', 'revenue'),
            ('Equipment Rental Revenue', 'REV002', 'revenue'),
            ('Cleaning Supplies', 'EXP001', 'expense'),
            ('Equipment Maintenance', 'EXP002', 'expense'),
            ('Freelancer Payments', 'EXP003', 'expense'),
        ]
        
        for name, code, account_type in accounts_data:
            Account.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'account_type': account_type,
                    'balance': Decimal(str(random.randint(5000, 100000))),
                }
            )

        # Create finance customers first
        customers = []
        for i in range(5):
            customer, created = FinanceCustomer.objects.get_or_create(
                name=f'Finance Demo Customer {i+1}',
                defaults={
                    'email': f'finance_customer{i+1}@demo.com',
                    'phone': f'+1-555-{random.randint(3000, 3999)}',
                    'credit_limit': Decimal(str(random.randint(5000, 50000))),
                }
            )
            customers.append(customer)

        # Sample invoices
        for i in range(10):
            customer = random.choice(customers)
            Invoice.objects.get_or_create(
                invoice_number=f'INV-{date.today().year}-{i+1:04d}',
                defaults={
                    'customer': customer,
                    'status': random.choice(['draft', 'sent', 'paid', 'overdue']),
                    'issue_date': date.today() - timedelta(days=random.randint(1, 30)),
                    'due_date': date.today() + timedelta(days=random.randint(1, 45)),
                    'total_amount': Decimal(str(random.randint(150, 2500))),
                    'created_by': admin_user
                }
            )

    def create_hr_data(self, organization, admin_user):
        """Create HR data."""
        departments_data = [
            ('Operations', 'Cleaning operations and field services'),
            ('HR', 'Human resources and people management'),
            ('Finance', 'Financial management and accounting'),
            ('Sales', 'Sales and customer acquisition'),
            ('IT', 'Information technology and systems'),
        ]
        
        departments = {}
        for name, description in departments_data:
            department, created = Department.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            departments[name] = department

        # Create positions first
        positions_data = [
            ('Operations Manager', 'Manages cleaning operations and field services', 'Operations'),
            ('HR Manager', 'Manages human resources and people operations', 'HR'),
            ('Finance Manager', 'Manages financial operations and accounting', 'Finance'),
            ('Sales Director', 'Directs sales and customer acquisition', 'Sales'),
        ]
        
        positions = {}
        for name, description, dept_name in positions_data:
            department = departments.get(dept_name)
            if department:
                position, created = Position.objects.get_or_create(
                    title=name,
                    defaults={
                        'description': description,
                        'department': department
                    }
                )
                positions[name] = position

        # Sample employees - create users first, then employee profiles
        employees_data = [
            ('John', 'Smith', 'john.smith@tidygen.com', 'Operations', 'Operations Manager'),
            ('Jane', 'Doe', 'jane.doe@tidygen.com', 'HR', 'HR Manager'),
            ('Mike', 'Johnson', 'mike.johnson@tidygen.com', 'Finance', 'Finance Manager'),
            ('Sarah', 'Wilson', 'sarah.wilson@tidygen.com', 'Sales', 'Sales Director'),
        ]
        
        for first_name, last_name, email, dept_name, position_name in employees_data:
            # Create user first
            user, user_created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email.split('@')[0],
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_active': True,
                }
            )
            if user_created:
                user.set_password('employee123')
                user.save()
            
            # Create employee profile
            Employee.objects.get_or_create(
                user=user,
                defaults={
                    'employee_id': f'EMP-{random.randint(1000, 9999)}',
                    'department': departments.get(dept_name),
                    'position': positions.get(position_name),
                    'salary': Decimal(str(random.randint(45000, 95000))),
                    'hire_date': date.today() - timedelta(days=random.randint(30, 1095)),
                    'employment_status': 'active',
                }
            )

    def create_sales_data(self, organization, admin_user):
        """Create sales data."""
        clients_data = [
            ('TechCorp Office', 'contact@techcorp.com', '+1-555-1001', 'corporate'),
            ('Residential Complex A', 'manager@rescomplexa.com', '+1-555-1002', 'corporate'),
            ('Shopping Mall Downtown', 'operations@mall.com', '+1-555-1003', 'corporate'),
            ('Medical Center', 'admin@medcenter.com', '+1-555-1004', 'corporate'),
        ]
        
        clients = {}
        for name, email, phone, client_type in clients_data:
            client, created = Client.objects.get_or_create(
                client_type=client_type,
                defaults={
                    'email': email,
                    'phone': phone,
                    'status': 'active',
                }
            )
            if created and client_type == 'corporate':
                CorporateClient.objects.create(
                    client=client,
                    company_name=name
                )
            clients[name] = client

    def create_purchasing_data(self, organization, admin_user):
        """Create purchasing data."""
        suppliers_data = [
            ('Cleaning Supplies Co', 'orders@cleaningsupplies.com', '+1-555-2001'),
            ('Equipment Rentals Inc', 'sales@equipmentrentals.com', '+1-555-2002'),
            ('Safety First Supplies', 'purchase@safetyfirst.com', '+1-555-2003'),
        ]
        
        suppliers = {}
        for name, email, phone in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                name=name,
                defaults={
                    'email': email,
                    'phone': phone,
                    'contact_person': f'{name} Sales Team',
                    'address': f'123 {name} Street, San Francisco, CA 94105',
                    'payment_terms': 'net_30',
                }
            )
            suppliers[name] = supplier

        # Create sample purchase orders
        for i in range(5):
            supplier = random.choice(list(suppliers.values()))
            PurchaseOrder.objects.get_or_create(
                po_number=f'PO-{date.today().year}-{i+1:04d}',
                defaults={
                    'supplier': supplier,
                    'requested_by': admin_user,
                    'status': random.choice(['draft', 'pending_approval', 'approved', 'sent']),
                    'total_amount': Decimal(str(random.randint(1000, 10000))),
                    'expected_delivery_date': date.today() + timedelta(days=random.randint(7, 30)),
                }
            )

    def create_freelancers_data(self, organization, users_data):
        """Create comprehensive freelancer data."""
        # Create sample freelancers
        for i in range(1, 11):
            user = users_data[f'freelancer{i}']
            
            freelancer, created = Freelancer.objects.get_or_create(
                user=user,
                defaults={
                    'freelancer_id': f'FREE-{i:04d}',
                    'first_name': f'Freelancer{i}',
                    'last_name': 'Cleaner',
                    'date_of_birth': date.today() - timedelta(days=random.randint(7000, 12000)),
                    'gender': random.choice(['male', 'female']),
                    'personal_email': f'freelancer{i}@tidygen.com',
                    'personal_phone': f'+1-555-{random.randint(1000, 9999)}',
                    'address_line1': f'{random.randint(100, 999)} Demo Street',
                    'city': 'San Francisco',
                    'state': 'CA',
                    'postal_code': '94105',
                    'country': 'USA',
                    'status': random.choice(['verified', 'active']),
                    'verification_status': 'verified',
                    'hourly_rate': Decimal(str(random.randint(18, 35))),
                    'is_available': random.choice([True, False]),
                    'payment_method': random.choice(['bank_transfer', 'crypto_wallet']),
                    'wallet_address': f'0x{"".join(random.choices("0123456789abcdef", k=40))}',
                    'emergency_contact_name': f'Emergency Contact {i}',
                    'emergency_contact_phone': f'+1-555-{random.randint(1000, 9999)}',
                    'bio': f'Experienced and reliable freelancer {i} specializing in various cleaning services.',
                }
            )

        # Create freelancer skills
        skill_names = ['Residential Cleaning', 'Commercial Cleaning', 'Window Cleaning', 
                      'Carpet Cleaning', 'Deep Cleaning', 'Move-in/Move-out Cleaning',
                      'Post-Construction Cleanup', 'Medical Facility Cleaning']
        
        for skill_name in skill_names:
            FreelancerSkill.objects.get_or_create(
                name=skill_name,
                defaults={'description': f'Professional {skill_name.lower()} services'}
            )

    def create_gig_management_data(self, organization, users_data):
        """Create gig management data."""
        # Create gig categories
        categories_data = [
            ('Residential Cleaning', 'Home cleaning services', '🏠', '#3B82F6'),
            ('Commercial Cleaning', 'Office and business cleaning', '🏢', '#10B981'),
            ('Deep Cleaning', 'Comprehensive deep cleaning', '🧽', '#F59E0B'),
            ('Move Cleaning', 'Move-in/move-out cleaning', '📦', '#8B5CF6'),
            ('Window Cleaning', 'Window and glass cleaning', '🪟', '#06B6D4'),
        ]
        
        categories = {}
        for name, description, icon, color in categories_data:
            category, created = GigCategory.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'icon': icon,
                    'color': color,
                    'default_hourly_rate_min': Decimal('20.00'),
                    'default_hourly_rate_max': Decimal('45.00'),
                }
            )
            categories[name] = category

        # Create sample gig jobs
        jobs_data = [
            ('Weekly Office Cleaning', 'Regular weekly cleaning for downtown office', 
             'Commercial Cleaning', Decimal('150.00'), 'published'),
            ('Deep Clean Apartment', 'Move-out deep cleaning for 2BR apartment',
             'Deep Cleaning', Decimal('200.00'), 'assigned'),
            ('Residential Weekly Service', 'Weekly house cleaning service',
             'Residential Cleaning', Decimal('120.00'), 'completed'),
            ('Window Cleaning Service', 'Clean all windows in 3-story building',
             'Window Cleaning', Decimal('180.00'), 'in_progress'),
        ]
        
        jobs = []
        for title, description, category_name, budget, status in jobs_data:
            # Get a random client user for the job
            client_user = random.choice(list(users_data.values()))
            
            job, created = GigJob.objects.get_or_create(
                title=title,
                defaults={
                    'job_id': f'GJ-{date.today().year}-{random.randint(1000, 9999)}',
                    'description': description,
                    'category': categories[category_name],
                    'client': client_user,
                    'client_type': 'corporate',
                    'service_address': f'{random.randint(100, 999)} Client Street',
                    'city': 'San Francisco',
                    'state': 'CA',
                    'postal_code': '94105',
                    'country': 'US',
                    'service_type': 'regular_cleaning',
                    'property_type': 'office',
                    'fixed_price': budget,
                    'estimated_duration_hours': Decimal(str(random.randint(2, 8))),
                    'status': status,
                    'preferred_start_date': datetime.now() + timedelta(days=random.randint(1, 30)),
                    'special_requirements': 'Please bring own cleaning supplies if needed',
                }
            )
            jobs.append(job)

        # Create applications for jobs
        freelancers = Freelancer.objects.all()[:5]
        for job in jobs[:2]:
            for freelancer in freelancers:
                GigApplication.objects.get_or_create(
                    job=job,
                    freelancer=freelancer,
                    defaults={
                        'proposed_rate': (job.fixed_price or job.hourly_rate or Decimal('25.00')) + Decimal(str(random.randint(-20, 20))),
                        'cover_letter': f'Interested in this {job.title.lower()} position',
                        'status': random.choice(['submitted', 'accepted', 'rejected']),
                    }
                )

    def create_contractor_payments_data(self, organization, users_data):
        """Create contractor payment data."""
        # Create payment methods first
        payment_methods_data = [
            ('Bank Transfer', 'bank_transfer'),
            ('Crypto Wallet', 'crypto_wallet'),
            ('Stripe', 'stripe'),
        ]
        
        payment_methods = {}
        for name, method_type in payment_methods_data:
            method, created = PaymentMethod.objects.get_or_create(
                name=name,
                defaults={
                    'payment_type': method_type,
                    'is_active': True,
                    'processing_fee_percentage': Decimal('2.5'),
                    'min_payment_amount': Decimal('10.00'),
                    'web3_enabled': method_type in ['crypto_wallet'],
                }
            )
            payment_methods[name] = method

        # Create payment transactions for freelancers
        freelancers = Freelancer.objects.all()[:5]
        if freelancers and payment_methods:
            for i in range(10):
                freelancer = random.choice(freelancers)
                method = random.choice(list(payment_methods.values()))
                ContractorPayment.objects.get_or_create(
                    payment_id=f'PAY-{date.today().year}-{i+1:04d}',
                    defaults={
                        'freelancer': freelancer,
                        'payment_method': method,
                        'amount': Decimal(str(random.randint(100, 800))),
                        'currency': 'USD',
                        'processing_fee': Decimal(str(random.randint(2, 20))),
                        'net_amount': Decimal(str(random.randint(90, 780))),
                        'payment_trigger': 'job_completion',
                        'status': random.choice(['pending', 'processing', 'completed', 'failed']),
                        'transaction_reference': f'REF-{random.randint(100000, 999999)}',
                    }
                )

    def create_freelancer_web3_data(self, organization, users_data):
        """Create Web3-related freelancer data."""
        # Create NFT Badges
        badge_data = [
            ('VERIFIED_CLEANER_001', 'Verified Cleaner', 'NFT badge for verified professional cleaners', 'completion_milestone'),
            ('TOP_PERFORMER_001', 'Top Performer', 'NFT badge for top-rated freelancers', 'quality_rating'),
            ('RELIABLE_WORKER_001', 'Reliable Worker', 'NFT badge for consistent and reliable workers', 'quality_rating'),
        ]
        
        badges = {}
        for badge_id, name, description, badge_type in badge_data:
            badge, created = FreelancerNFTBadge.objects.get_or_create(
                badge_id=badge_id,
                defaults={
                    'name': name,
                    'description': description,
                    'badge_type': badge_type,
                    'rarity': random.choice(['common', 'uncommon', 'rare']),
                    'image_url': f'https://example.com/{badge_id.lower()}.png',
                    'color_hex': '#3B82F6',
                }
            )
            badges[name] = badge

        # Create reputation tokens for freelancers
        freelancers = Freelancer.objects.all()[:5]
        token_types = ['quality', 'reliability', 'communication', 'punctuality', 'overall']
        for freelancer in freelancers:
            for token_type in token_types:
                FreelancerReputationToken.objects.get_or_create(
                    freelancer=freelancer,
                    token_type=token_type,
                    defaults={
                        'token_amount': Decimal(str(random.randint(10, 1000))),
                        'token_contract_address': f'0x{"".join(random.choices("0123456789abcdef", k=40))}',
                        'blockchain_network': 'ethereum',
                    }
                )

    def create_analytics_data(self, organization, admin_user):
        """Create analytics data."""
        # Create KPIs
        kpi_data = [
            ('Revenue Growth', 'Monthly revenue growth percentage', 'financial'),
            ('Freelancer Satisfaction', 'Average freelancer satisfaction score', 'employee'),
            ('Client Retention Rate', 'Percentage of clients retained', 'customer'),
            ('Job Completion Rate', 'Percentage of jobs completed on time', 'operational'),
        ]
        
        for name, description, kpi_type in kpi_data:
            KPI.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'kpi_type': kpi_type,
                    'calculation_method': f'Calculate {name.lower()} based on system data',
                    'data_source': 'system_database',
                    'target_value': Decimal(str(random.randint(80, 95))),
                    'current_value': Decimal(str(random.randint(70, 90))),
                    'unit': '%' if 'rate' in name.lower() or 'percentage' in name.lower() else '',
                }
            )

    def create_audit_trail_data(self, organization, users_data):
        """Create audit trail data."""
        events = ['user_login', 'freelancer_created', 'payment_processed', 'job_completed']
        modules = ['system', 'freelancers', 'contractor_payments', 'gig_management']
        
        for i in range(50):
            user = random.choice(list(users_data.values()))
            AuditEvent.objects.create(
                event_type=random.choice(events),
                module=random.choice(modules),
                object_id=str(random.randint(1, 100)),
                object_type='DemoObject',
                data={'demo': True, 'value': random.randint(1, 100)},
                metadata={'source': 'demo_seed'},
                user=user,
                status='hashed',
            )

    def create_facility_management_data(self, organization, admin_user):
        """Create facility management data."""
        facilities_data = [
            ('Main Office', 'office', '123 Main St, San Francisco, CA 94105'),
            ('Equipment Depot', 'depot', '456 Depot Ave, San Francisco, CA 94110'),
            ('Storage Facility', 'storage', '789 Storage Blvd, San Francisco, CA 94115'),
        ]
        
        for name, facility_type, address in facilities_data:
            Facility.objects.get_or_create(
                name=name,
                defaults={
                    'facility_type': facility_type,
                    'address': address,
                    'city': 'San Francisco',
                    'state': 'CA',
                    'postal_code': '94105',
                    'country': 'USA',
                    'total_area': Decimal(str(random.randint(5000, 20000))),
                    'is_active': True,
                }
            )

    def create_field_operations_data(self, organization, users_data):
        """Create field operations data."""
        # Create field teams
        for i in range(3):
            FieldTeam.objects.get_or_create(
                name=f'Team Alpha-{i+1}',
                defaults={
                    'description': f'Field operation team {i+1}',
                    'team_type': 'cleaning',
                    'max_capacity': 5,
                    'status': 'active',
                }
            )

    def create_payroll_data(self, organization, users_data):
        """Create payroll data."""
        # Create a default payroll configuration if one doesn't exist
        if not PayrollConfiguration.objects.exists():
            PayrollConfiguration.objects.create(
                pay_frequency='monthly',
                currency='USD',
                overtime_multiplier=Decimal('1.5'),
                federal_tax_rate=Decimal('0.22'),
                state_tax_rate=Decimal('0.05'),
            )

    def create_scheduling_data(self, organization, users_data):
        """Create scheduling data."""
        # Create resources (vehicles, equipment)
        for i in range(5):
            Resource.objects.get_or_create(
                name=f'Vehicle {i+1}',
                defaults={
                    'resource_type': 'vehicle',
                    'description': f'Cleaning vehicle {i+1}',
                    'capacity': random.randint(2, 5),
                    'is_active': True,
                }
            )

    def create_ledger_data(self, organization, admin_user):
        """Create ledger data."""
        # Create ledger configuration
        LedgerConfiguration.objects.get_or_create(
            organization=organization,
            defaults={
                'blockchain_network': 'ethereum',
                'rpc_endpoint': 'http://localhost:8545',
                'contract_address': f'0x{"".join(random.choices("0123456789abcdef", k=40))}',
                'is_active': True,
            }
        )

    def create_wallet_data(self, organization, users_data):
        """Create wallet data."""
        for user in list(users_data.values())[:3]:
            Wallet.objects.get_or_create(
                user=user,
                defaults={
                    'address': f'0x{"".join(random.choices("0123456789abcdef", k=40))}',
                    'wallet_type': 'ethereum',
                    'is_verified': True,
                    'is_active': True,
                }
            )

    def create_did_auth_data(self, organization, users_data):
        """Create DID authentication data."""
        for i, user in enumerate(list(users_data.values())[:3]):
            did = f'did:tidygen:{uuid.uuid4()}'
            DIDDocument.objects.get_or_create(
                did=did,
                defaults={
                    'document': {
                        '@context': ['https://www.w3.org/ns/did/v1'],
                        'id': did,
                        'verificationMethod': [{
                            'id': f'{did}#keys-1',
                            'type': 'Ed25519VerificationKey2020',
                            'controller': did,
                            'publicKeyMultibase': f'z{"".join(random.choices("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz", k=44))}'
                        }]
                    },
                    'controller': did,
                    'status': 'active',
                }
            )
