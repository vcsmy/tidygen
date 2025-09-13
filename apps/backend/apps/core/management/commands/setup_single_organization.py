"""
Management command to set up the single organization for community edition.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.core.models import Organization

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up the single organization for community edition'

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            type=str,
            default='My Organization',
            help='Organization name'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@example.com',
            help='Organization email'
        )
        parser.add_argument(
            '--create-admin',
            action='store_true',
            help='Create an admin user if none exists'
        )

    def handle(self, *args, **options):
        # Create or get the single organization
        org, created = Organization.objects.get_or_create(
            defaults={
                'name': options['name'],
                'email': options['email'],
                'description': 'Default organization for community edition',
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created organization: {org.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Organization already exists: {org.name}')
            )
        
        # Create admin user if requested and none exists
        if options['create_admin']:
            admin_user, admin_created = User.objects.get_or_create(
                username='admin',
                defaults={
                    'email': 'admin@example.com',
                    'first_name': 'Admin',
                    'last_name': 'User',
                    'is_staff': True,
                    'is_superuser': True,
                    'is_verified': True,
                }
            )
            
            if admin_created:
                admin_user.set_password('admin123')
                admin_user.save()
                self.stdout.write(
                    self.style.SUCCESS('Created admin user: admin/admin123')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Admin user already exists')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Single organization setup completed!')
        )
