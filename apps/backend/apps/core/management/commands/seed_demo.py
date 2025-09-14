"""
Django management command to seed the database with essential demo data.
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

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with essential demo data for presentation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()

        self.stdout.write('Starting to seed database with demo data...')
        
        with transaction.atomic():
            # Create organization
            organization = self.create_organization()
            
            # Create core data
            self.create_roles_and_permissions(organization)
            admin_user = self.create_demo_users(organization)
            
        self.stdout.write(
            self.style.SUCCESS('Successfully seeded database with demo data!')
        )
        self.stdout.write(f'Admin user: admin / admin123')
        self.stdout.write(f'Demo users: demo1, demo2, demo3 / password123')
        self.stdout.write(f'Organization: {organization.name}')

    def clear_data(self):
        """Clear existing data (except superusers)."""
        # Clear non-superuser users and related data
        User.objects.filter(is_superuser=False).delete()
        Organization.objects.all().delete()
        Permission.objects.all().delete()
        Role.objects.all().delete()

    def create_organization(self):
        """Create the demo organization."""
        organization, created = Organization.objects.get_or_create(
            name='TidyGen Demo Corp',
            defaults={
                'slug': 'tidygen-demo-corp',
                'description': 'TidyGen ERP System - Demonstration Organization',
                'industry': 'Technology',
                'size': 'medium',
                'website': 'https://tidygen-demo.com',
                'phone': '+1-555-DEMO',
                'email': 'demo@tidygen-corp.com',
                'address': '123 Demo Street',
                'city': 'San Francisco',
                'state': 'CA',
                'country': 'USA',
                'postal_code': '94105'
            }
        )
        return organization

    def create_roles_and_permissions(self, organization):
        """Create essential roles and permissions."""
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

    def create_demo_users(self, organization):
        """Create demo users for presentation."""
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@tidygen-demo.com',
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

        # Create demo users for different roles
        demo_users_data = [
            ('demo1', 'demo1@tidygen-demo.com', 'John', 'Doe', 'finance', 'Finance Manager'),
            ('demo2', 'demo2@tidygen-demo.com', 'Jane', 'Smith', 'sales', 'Sales Manager'),
            ('demo3', 'demo3@tidygen-demo.com', 'Mike', 'Johnson', 'hr', 'HR Manager'),
        ]
        
        for username, email, first_name, last_name, role_name, position in demo_users_data:
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
