"""
Custom permissions for TidyGen ERP platform.
"""

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        return obj == request.user


class IsSystemAdmin(permissions.BasePermission):
    """
    Custom permission to only allow system administrators.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_staff
        )


class IsOrganizationAdmin(permissions.BasePermission):
    """
    Custom permission to only allow organization administrators.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user is organization admin
        organization = getattr(request, 'organization', None)
        if not organization:
            return False
        
        # Check if user is owner or admin of the organization
        membership = request.user.organization_memberships.filter(
            organization=organization,
            is_active=True
        ).first()
        
        return membership and (membership.is_owner or membership.role.name == 'Admin')


class IsOrganizationMember(permissions.BasePermission):
    """
    Custom permission to only allow organization members.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user is organization member
        organization = getattr(request, 'organization', None)
        if not organization:
            return False
        
        # Check if user is member of the organization
        membership = request.user.organization_memberships.filter(
            organization=organization,
            is_active=True
        ).exists()
        
        return membership


class HasPermission(permissions.BasePermission):
    """
    Custom permission to check for specific permissions.
    """
    
    def __init__(self, permission_codename):
        self.permission_codename = permission_codename
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user has the specific permission
        return request.user.has_perm(self.permission_codename)


class IsWeb3Verified(permissions.BasePermission):
    """
    Custom permission to only allow Web3 verified users.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.wallet_verified
        )


class IsReadOnlyOrAuthenticated(permissions.BasePermission):
    """
    Custom permission to allow read-only access to unauthenticated users,
    but require authentication for write operations.
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated
