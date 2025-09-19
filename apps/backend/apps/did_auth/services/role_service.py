"""
DID Role Service

Service for managing DID roles and permissions.
"""

from typing import Dict, Any, Optional, List
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError

from ..models import DIDDocument, DIDRole, DIDPermission


class DIDRoleService:
    """
    Service for managing DID roles and permissions.
    """

    @staticmethod
    def assign_role(
        did: str,
        role_name: str,
        granted_by: str,
        permissions: Optional[List[str]] = None,
        expires_at: Optional[timezone.datetime] = None,
        custom_role_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[DIDRole]:
        """
        Assign a role to a DID.
        
        Args:
            did: The DID identifier
            role_name: The name of the role
            granted_by: DID of the entity granting the role
            permissions: List of permissions for the role
            expires_at: Optional expiration date
            custom_role_name: Custom name for custom roles
            metadata: Additional metadata
            
        Returns:
            DIDRole instance or None
        """
        try:
            did_doc = DIDDocument.objects.get(did=did)
            
            # Check if role already exists
            existing_role = DIDRole.objects.filter(
                did=did_doc,
                role_name=role_name
            ).first()
            
            if existing_role:
                # Update existing role
                existing_role.is_active = True
                existing_role.granted_by = granted_by
                existing_role.granted_at = timezone.now()
                existing_role.expires_at = expires_at
                existing_role.permissions = permissions or []
                existing_role.custom_role_name = custom_role_name or ""
                existing_role.metadata = metadata or {}
                existing_role.save()
                return existing_role
            else:
                # Create new role
                role = DIDRole.objects.create(
                    did=did_doc,
                    role_name=role_name,
                    custom_role_name=custom_role_name or "",
                    permissions=permissions or [],
                    granted_by=granted_by,
                    expires_at=expires_at,
                    metadata=metadata or {}
                )
                return role
                
        except DIDDocument.DoesNotExist:
            return None

    @staticmethod
    def revoke_role(did: str, role_name: str, revoked_by: str) -> bool:
        """
        Revoke a role from a DID.
        
        Args:
            did: The DID identifier
            role_name: The name of the role to revoke
            revoked_by: DID of the entity revoking the role
            
        Returns:
            True if successful, False otherwise
        """
        try:
            did_doc = DIDDocument.objects.get(did=did)
            role = DIDRole.objects.get(did=did_doc, role_name=role_name)
            
            role.is_active = False
            role.save()
            
            return True
        except (DIDDocument.DoesNotExist, DIDRole.DoesNotExist):
            return False

    @staticmethod
    def get_did_roles(did: str, active_only: bool = True) -> List[DIDRole]:
        """
        Get all roles for a DID.
        
        Args:
            did: The DID identifier
            active_only: Whether to return only active roles
            
        Returns:
            List of DIDRole instances
        """
        try:
            did_doc = DIDDocument.objects.get(did=did)
            queryset = did_doc.roles.all()
            
            if active_only:
                queryset = queryset.filter(is_active=True)
            
            return list(queryset)
        except DIDDocument.DoesNotExist:
            return []

    @staticmethod
    def check_role_permission(did: str, role_name: str, permission: str) -> bool:
        """
        Check if a DID has a specific permission through a role.
        
        Args:
            did: The DID identifier
            role_name: The role name
            permission: The permission to check
            
        Returns:
            True if role has permission, False otherwise
        """
        try:
            did_doc = DIDDocument.objects.get(did=did)
            role = DIDRole.objects.get(
                did=did_doc,
                role_name=role_name,
                is_active=True
            )
            
            return role.is_valid() and role.has_permission(permission)
        except (DIDDocument.DoesNotExist, DIDRole.DoesNotExist):
            return False

    @staticmethod
    def get_all_permissions(did: str) -> List[str]:
        """
        Get all permissions for a DID across all roles.
        
        Args:
            did: The DID identifier
            
        Returns:
            List of unique permissions
        """
        roles = DIDRoleService.get_did_roles(did, active_only=True)
        permissions = set()
        
        for role in roles:
            if role.is_valid():
                permissions.update(role.permissions)
        
        return list(permissions)

    @staticmethod
    def create_permission(
        name: str,
        display_name: str,
        description: str,
        category: str,
        resource: str,
        action: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DIDPermission:
        """
        Create a new permission.
        
        Args:
            name: Unique permission name
            display_name: Human-readable display name
            description: Description of the permission
            category: Permission category
            resource: Resource this permission applies to
            action: Action this permission allows
            metadata: Additional metadata
            
        Returns:
            DIDPermission instance
        """
        permission = DIDPermission.objects.create(
            name=name,
            display_name=display_name,
            description=description,
            category=category,
            resource=resource,
            action=action,
            metadata=metadata or {}
        )
        
        return permission

    @staticmethod
    def get_permissions_by_category(category: str) -> List[DIDPermission]:
        """
        Get all permissions in a category.
        
        Args:
            category: The permission category
            
        Returns:
            List of DIDPermission instances
        """
        return list(DIDPermission.objects.filter(
            category=category,
            is_active=True
        ))

    @staticmethod
    def get_all_permissions() -> List[DIDPermission]:
        """
        Get all active permissions.
        
        Returns:
            List of all active DIDPermission instances
        """
        return list(DIDPermission.objects.filter(is_active=True))

    @staticmethod
    def create_default_permissions():
        """
        Create default permissions for the system.
        """
        default_permissions = [
            # Finance permissions
            {
                'name': 'finance:read',
                'display_name': 'View Financial Data',
                'description': 'View financial reports and data',
                'category': 'finance',
                'resource': 'finance',
                'action': 'read'
            },
            {
                'name': 'finance:write',
                'display_name': 'Manage Financial Data',
                'description': 'Create and update financial records',
                'category': 'finance',
                'resource': 'finance',
                'action': 'write'
            },
            {
                'name': 'finance:approve',
                'display_name': 'Approve Financial Transactions',
                'description': 'Approve financial transactions and payments',
                'category': 'finance',
                'resource': 'finance',
                'action': 'approve'
            },
            
            # HR permissions
            {
                'name': 'hr:read',
                'display_name': 'View HR Data',
                'description': 'View employee and HR information',
                'category': 'hr',
                'resource': 'hr',
                'action': 'read'
            },
            {
                'name': 'hr:write',
                'display_name': 'Manage HR Data',
                'description': 'Create and update employee records',
                'category': 'hr',
                'resource': 'hr',
                'action': 'write'
            },
            
            # Inventory permissions
            {
                'name': 'inventory:read',
                'display_name': 'View Inventory',
                'description': 'View inventory levels and items',
                'category': 'inventory',
                'resource': 'inventory',
                'action': 'read'
            },
            {
                'name': 'inventory:write',
                'display_name': 'Manage Inventory',
                'description': 'Update inventory levels and items',
                'category': 'inventory',
                'resource': 'inventory',
                'action': 'write'
            },
            
            # Admin permissions
            {
                'name': 'admin:full_access',
                'display_name': 'Full System Access',
                'description': 'Complete access to all system functions',
                'category': 'admin',
                'resource': 'system',
                'action': 'full_access'
            },
            {
                'name': 'admin:user_management',
                'display_name': 'User Management',
                'description': 'Manage users and their permissions',
                'category': 'admin',
                'resource': 'users',
                'action': 'manage'
            },
            
            # Audit permissions
            {
                'name': 'audit:read',
                'display_name': 'View Audit Logs',
                'description': 'View system audit logs and trails',
                'category': 'audit',
                'resource': 'audit',
                'action': 'read'
            },
            {
                'name': 'audit:export',
                'display_name': 'Export Audit Data',
                'description': 'Export audit logs and reports',
                'category': 'audit',
                'resource': 'audit',
                'action': 'export'
            }
        ]
        
        for perm_data in default_permissions:
            permission, created = DIDPermission.objects.get_or_create(
                name=perm_data['name'],
                defaults=perm_data
            )
            
            if created:
                print(f"Created permission: {permission.name}")

    @staticmethod
    def create_default_roles():
        """
        Create default roles with their permissions.
        """
        # Ensure permissions exist
        DIDRoleService.create_default_permissions()
        
        default_roles = [
            {
                'role_name': 'admin',
                'permissions': [
                    'admin:full_access',
                    'admin:user_management',
                    'finance:read',
                    'finance:write',
                    'finance:approve',
                    'hr:read',
                    'hr:write',
                    'inventory:read',
                    'inventory:write',
                    'audit:read',
                    'audit:export'
                ]
            },
            {
                'role_name': 'finance_manager',
                'permissions': [
                    'finance:read',
                    'finance:write',
                    'finance:approve',
                    'audit:read'
                ]
            },
            {
                'role_name': 'hr_manager',
                'permissions': [
                    'hr:read',
                    'hr:write',
                    'audit:read'
                ]
            },
            {
                'role_name': 'auditor',
                'permissions': [
                    'audit:read',
                    'audit:export',
                    'finance:read',
                    'hr:read',
                    'inventory:read'
                ]
            },
            {
                'role_name': 'field_supervisor',
                'permissions': [
                    'inventory:read',
                    'inventory:write'
                ]
            },
            {
                'role_name': 'cleaner',
                'permissions': [
                    'inventory:read'
                ]
            }
        ]
        
        # Note: These are template roles - actual role assignment
        # happens when assigning roles to specific DIDs
        print("Default role templates created:")
        for role_data in default_roles:
            print(f"- {role_data['role_name']}: {len(role_data['permissions'])} permissions")
