"""
Management command to initialize the DID authentication system.
"""

from django.core.management.base import BaseCommand
from apps.did_auth.services import DIDRoleService, DIDService


class Command(BaseCommand):
    help = 'Initialize the DID authentication system with default permissions and roles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-sample-did',
            action='store_true',
            help='Create a sample DID document for testing'
        )
        parser.add_argument(
            '--assign-sample-roles',
            action='store_true',
            help='Assign sample roles to the sample DID'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Initializing DID authentication system...'))
        
        # Create default permissions
        self.stdout.write('Creating default permissions...')
        DIDRoleService.create_default_permissions()
        self.stdout.write(self.style.SUCCESS('✓ Default permissions created'))
        
        # Create default role templates
        self.stdout.write('Creating default role templates...')
        DIDRoleService.create_default_roles()
        self.stdout.write(self.style.SUCCESS('✓ Default role templates created'))
        
        # Create sample DID if requested
        if options['create_sample_did']:
            self.stdout.write('Creating sample DID...')
            sample_did = DIDService.generate_did()
            
            # Create DID document template
            did_document = DIDService.create_did_document_template(
                did=sample_did,
                controller=sample_did
            )
            
            # Create the DID document
            did_doc = DIDService.create_did_document(
                did=sample_did,
                document=did_document,
                controller=sample_did
            )
            
            self.stdout.write(self.style.SUCCESS(f'✓ Sample DID created: {sample_did}'))
            
            # Assign sample roles if requested
            if options['assign_sample_roles']:
                self.stdout.write('Assigning sample roles...')
                
                # Assign admin role
                admin_role = DIDRoleService.assign_role(
                    did=sample_did,
                    role_name='admin',
                    granted_by='did:system:admin',
                    permissions=['admin:full_access', 'admin:user_management']
                )
                
                if admin_role:
                    self.stdout.write(self.style.SUCCESS('✓ Admin role assigned'))
                
                # Assign finance manager role
                finance_role = DIDRoleService.assign_role(
                    did=sample_did,
                    role_name='finance_manager',
                    granted_by='did:system:admin',
                    permissions=['finance:read', 'finance:write', 'finance:approve']
                )
                
                if finance_role:
                    self.stdout.write(self.style.SUCCESS('✓ Finance manager role assigned'))
        
        self.stdout.write(self.style.SUCCESS('DID authentication system initialized successfully!'))
        
        # Display summary
        from apps.did_auth.models import DIDPermission, DIDDocument, DIDRole
        
        permission_count = DIDPermission.objects.count()
        did_count = DIDDocument.objects.count()
        role_count = DIDRole.objects.count()
        
        self.stdout.write(f'\nSystem Summary:')
        self.stdout.write(f'- Permissions: {permission_count}')
        self.stdout.write(f'- DID Documents: {did_count}')
        self.stdout.write(f'- Roles: {role_count}')
        
        if options['create_sample_did']:
            self.stdout.write(f'\nSample DID: {sample_did}')
            self.stdout.write('You can use this DID for testing the authentication system.')
