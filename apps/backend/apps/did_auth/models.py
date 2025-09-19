"""
DID-Based Access Control Models

Models for decentralized identity management including DID documents,
roles, credentials, and authentication.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
import json
import uuid
from typing import Dict, Any, List

User = get_user_model()


class DIDDocument(models.Model):
    """
    Represents a Decentralized Identity (DID) document.
    """
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('revoked', 'Revoked'),
        ('expired', 'Expired'),
    ]
    
    did = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="The DID identifier (e.g., did:ethr:0x123...)"
    )
    document = models.JSONField(
        help_text="The complete DID document as per W3C DID specification"
    )
    controller = models.CharField(
        max_length=255,
        help_text="The DID of the controller of this DID document"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this DID document was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this DID document was last updated"
    )
    on_chain_tx_hash = models.CharField(
        max_length=66,
        blank=True,
        null=True,
        help_text="Transaction hash if stored on-chain"
    )
    on_chain_block_number = models.BigIntegerField(
        blank=True,
        null=True,
        help_text="Block number where the transaction was included"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        help_text="Current status of the DID document"
    )
    expires_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Optional expiration date for the DID document"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata for the DID document"
    )

    class Meta:
        verbose_name = "DID Document"
        verbose_name_plural = "DID Documents"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['did']),
            models.Index(fields=['controller']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.did} ({self.status})"

    def clean(self):
        """Validate DID document structure."""
        if not self.did.startswith('did:'):
            raise ValidationError("DID must start with 'did:'")
        
        # Validate DID document structure
        required_fields = ['@context', 'id', 'verificationMethod']
        for field in required_fields:
            if field not in self.document:
                raise ValidationError(f"DID document must contain '{field}' field")

    def is_expired(self):
        """Check if the DID document has expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def is_active(self):
        """Check if the DID document is active and not expired."""
        return self.status == 'active' and not self.is_expired()

    def get_verification_methods(self):
        """Get all verification methods from the DID document."""
        return self.document.get('verificationMethod', [])

    def get_public_keys(self):
        """Extract public keys from verification methods."""
        keys = []
        for vm in self.get_verification_methods():
            if 'publicKeyMultibase' in vm:
                keys.append(vm['publicKeyMultibase'])
            elif 'publicKeyJwk' in vm:
                keys.append(vm['publicKeyJwk'])
        return keys


class DIDRole(models.Model):
    """
    Represents a role assigned to a DID.
    """
    
    ROLE_TYPES = [
        ('admin', 'Administrator'),
        ('finance_manager', 'Finance Manager'),
        ('auditor', 'Auditor'),
        ('hr_manager', 'HR Manager'),
        ('field_supervisor', 'Field Supervisor'),
        ('cleaner', 'Cleaner'),
        ('client', 'Client'),
        ('supplier', 'Supplier'),
        ('custom', 'Custom Role'),
    ]
    
    did = models.ForeignKey(
        DIDDocument,
        on_delete=models.CASCADE,
        related_name='roles',
        help_text="The DID this role is assigned to"
    )
    role_name = models.CharField(
        max_length=100,
        choices=ROLE_TYPES,
        help_text="The name of the role"
    )
    custom_role_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Custom role name if role_type is 'custom'"
    )
    permissions = models.JSONField(
        default=list,
        help_text="List of permissions granted by this role"
    )
    granted_by = models.CharField(
        max_length=255,
        help_text="DID of the entity that granted this role"
    )
    granted_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this role was granted"
    )
    expires_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Optional expiration date for this role"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this role is currently active"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata for this role"
    )

    class Meta:
        verbose_name = "DID Role"
        verbose_name_plural = "DID Roles"
        ordering = ['-granted_at']
        unique_together = ['did', 'role_name']
        indexes = [
            models.Index(fields=['did']),
            models.Index(fields=['role_name']),
            models.Index(fields=['is_active']),
            models.Index(fields=['granted_at']),
        ]

    def __str__(self):
        role_display = self.custom_role_name if self.role_name == 'custom' else self.get_role_name_display()
        return f"{self.did.did} - {role_display}"

    def is_expired(self):
        """Check if the role has expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def is_valid(self):
        """Check if the role is valid (active and not expired)."""
        return self.is_active and not self.is_expired()

    def has_permission(self, permission):
        """Check if this role has a specific permission."""
        return permission in self.permissions


class DIDCredential(models.Model):
    """
    Represents a verifiable credential issued to a DID.
    """
    
    CREDENTIAL_TYPES = [
        ('identity', 'Identity Credential'),
        ('employment', 'Employment Credential'),
        ('certification', 'Certification Credential'),
        ('membership', 'Membership Credential'),
        ('custom', 'Custom Credential'),
    ]
    
    did = models.ForeignKey(
        DIDDocument,
        on_delete=models.CASCADE,
        related_name='credentials',
        help_text="The DID this credential is issued to"
    )
    credential_type = models.CharField(
        max_length=100,
        choices=CREDENTIAL_TYPES,
        help_text="The type of credential"
    )
    credential_data = models.JSONField(
        help_text="The credential data as per W3C VC specification"
    )
    issuer = models.CharField(
        max_length=255,
        help_text="DID of the entity that issued this credential"
    )
    issued_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this credential was issued"
    )
    expires_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Optional expiration date for this credential"
    )
    revoked = models.BooleanField(
        default=False,
        help_text="Whether this credential has been revoked"
    )
    revoked_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When this credential was revoked"
    )
    revoked_by = models.CharField(
        max_length=255,
        blank=True,
        help_text="DID of the entity that revoked this credential"
    )
    on_chain_tx_hash = models.CharField(
        max_length=66,
        blank=True,
        null=True,
        help_text="Transaction hash if stored on-chain"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata for this credential"
    )

    class Meta:
        verbose_name = "DID Credential"
        verbose_name_plural = "DID Credentials"
        ordering = ['-issued_at']
        indexes = [
            models.Index(fields=['did']),
            models.Index(fields=['credential_type']),
            models.Index(fields=['issuer']),
            models.Index(fields=['issued_at']),
            models.Index(fields=['revoked']),
        ]

    def __str__(self):
        return f"{self.did.did} - {self.get_credential_type_display()}"

    def is_expired(self):
        """Check if the credential has expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def is_valid(self):
        """Check if the credential is valid (not revoked and not expired)."""
        return not self.revoked and not self.is_expired()

    def revoke(self, revoked_by):
        """Revoke this credential."""
        self.revoked = True
        self.revoked_at = timezone.now()
        self.revoked_by = revoked_by
        self.save()


class DIDSession(models.Model):
    """
    Represents an active DID-based authentication session.
    """
    
    did = models.ForeignKey(
        DIDDocument,
        on_delete=models.CASCADE,
        related_name='sessions',
        help_text="The DID associated with this session"
    )
    session_token = models.CharField(
        max_length=255,
        unique=True,
        help_text="Unique session token"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this session was created"
    )
    expires_at = models.DateTimeField(
        help_text="When this session expires"
    )
    last_activity = models.DateTimeField(
        auto_now=True,
        help_text="Last activity timestamp"
    )
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text="IP address of the session"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="User agent string"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this session is active"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional session metadata"
    )

    class Meta:
        verbose_name = "DID Session"
        verbose_name_plural = "DID Sessions"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['did']),
            models.Index(fields=['session_token']),
            models.Index(fields=['is_active']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.did.did} - {self.session_token[:8]}..."

    def is_expired(self):
        """Check if the session has expired."""
        return timezone.now() > self.expires_at

    def is_valid(self):
        """Check if the session is valid (active and not expired)."""
        return self.is_active and not self.is_expired()

    def extend(self, duration_hours=24):
        """Extend the session expiration time."""
        from datetime import timedelta
        self.expires_at = timezone.now() + timedelta(hours=duration_hours)
        self.save()

    def terminate(self):
        """Terminate this session."""
        self.is_active = False
        self.save()


class DIDPermission(models.Model):
    """
    Represents a permission that can be granted to DID roles.
    """
    
    PERMISSION_CATEGORIES = [
        ('finance', 'Finance'),
        ('hr', 'Human Resources'),
        ('inventory', 'Inventory'),
        ('scheduling', 'Scheduling'),
        ('analytics', 'Analytics'),
        ('admin', 'Administration'),
        ('audit', 'Audit'),
        ('custom', 'Custom'),
    ]
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique name for this permission"
    )
    display_name = models.CharField(
        max_length=200,
        help_text="Human-readable display name"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of what this permission allows"
    )
    category = models.CharField(
        max_length=50,
        choices=PERMISSION_CATEGORIES,
        help_text="Category this permission belongs to"
    )
    resource = models.CharField(
        max_length=100,
        help_text="Resource this permission applies to"
    )
    action = models.CharField(
        max_length=50,
        help_text="Action this permission allows (read, write, delete, etc.)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this permission is active"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this permission was created"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata for this permission"
    )

    class Meta:
        verbose_name = "DID Permission"
        verbose_name_plural = "DID Permissions"
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.display_name} ({self.category})"

    def get_full_permission(self):
        """Get the full permission string (resource:action)."""
        return f"{self.resource}:{self.action}"