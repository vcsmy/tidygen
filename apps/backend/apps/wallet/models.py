"""
Wallet Models

This module defines the database models for wallet-based authentication,
including wallet management, signature verification, and permission systems.
"""

import uuid
import hashlib
import secrets
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class Wallet(models.Model):
    """
    Model representing a connected wallet for user authentication.
    
    This model stores wallet information including address, type, and
    connection details for both MetaMask and Polkadot.js wallets.
    """
    
    WALLET_TYPES = [
        ('metamask', 'MetaMask'),
        ('polkadot', 'Polkadot.js'),
        ('walletconnect', 'WalletConnect'),
        ('other', 'Other'),
    ]
    
    CHAIN_TYPES = [
        ('ethereum', 'Ethereum'),
        ('polygon', 'Polygon'),
        ('bsc', 'Binance Smart Chain'),
        ('substrate', 'Substrate'),
        ('polkadot', 'Polkadot'),
        ('kusama', 'Kusama'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Unique identifier for the wallet"
    )
    
    address = models.CharField(
        max_length=100,
        unique=True,
        help_text="Wallet address (0x... for EVM, 5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY for Substrate)"
    )
    
    wallet_type = models.CharField(
        max_length=20,
        choices=WALLET_TYPES,
        help_text="Type of wallet (MetaMask, Polkadot.js, etc.)"
    )
    
    chain_type = models.CharField(
        max_length=20,
        choices=CHAIN_TYPES,
        help_text="Type of blockchain network"
    )
    
    chain_id = models.CharField(
        max_length=50,
        help_text="Network chain ID (1 for Ethereum mainnet, 137 for Polygon, etc.)"
    )
    
    network_name = models.CharField(
        max_length=100,
        help_text="Human-readable network name (Ethereum Mainnet, Polkadot, etc.)"
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wallet_connections',
        help_text="User who owns this wallet"
    )
    
    is_primary = models.BooleanField(
        default=False,
        help_text="Whether this is the user's primary wallet"
    )
    
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether this wallet has been verified through signature"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this wallet is currently active"
    )
    
    public_key = models.TextField(
        null=True,
        blank=True,
        help_text="Public key for Substrate wallets"
    )
    
    metadata = models.JSONField(
        default=dict,
        help_text="Additional wallet metadata (SS58 format, etc.)"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the wallet was first connected"
    )
    
    last_used = models.DateTimeField(
        auto_now=True,
        help_text="When the wallet was last used for authentication"
    )
    
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the wallet was verified"
    )
    
    class Meta:
        db_table = 'wallet'
        verbose_name = 'Wallet'
        verbose_name_plural = 'Wallets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['address']),
            models.Index(fields=['wallet_type']),
            models.Index(fields=['chain_type']),
            models.Index(fields=['user', 'is_primary']),
            models.Index(fields=['is_verified', 'is_active']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'is_primary'],
                condition=models.Q(is_primary=True),
                name='unique_primary_wallet_per_user'
            )
        ]
    
    def __str__(self):
        return f"{self.wallet_type.title()} - {self.address[:10]}...{self.address[-6:]}"
    
    def clean(self):
        """Validate wallet data."""
        super().clean()
        
        # Validate address format based on wallet type
        if self.wallet_type == 'metamask':
            if not self.address.startswith('0x') or len(self.address) != 42:
                raise ValidationError("Invalid Ethereum address format")
        elif self.wallet_type == 'polkadot':
            if not self.address or len(self.address) < 40:
                raise ValidationError("Invalid Substrate address format")
        
        # Validate chain ID
        if not self.chain_id:
            raise ValidationError("Chain ID is required")
    
    def save(self, *args, **kwargs):
        """Override save to handle primary wallet logic."""
        # If this is being set as primary, unset other primary wallets
        if self.is_primary:
            Wallet.objects.filter(
                user=self.user,
                is_primary=True
            ).exclude(id=self.id).update(is_primary=False)
        
        super().save(*args, **kwargs)
    
    @property
    def short_address(self):
        """Get shortened address for display."""
        if len(self.address) > 20:
            return f"{self.address[:10]}...{self.address[-6:]}"
        return self.address
    
    @property
    def display_name(self):
        """Get display name for the wallet."""
        return f"{self.wallet_type.title()} ({self.short_address})"
    
    def generate_verification_message(self):
        """Generate a message for wallet verification."""
        nonce = secrets.token_hex(16)
        timestamp = int(timezone.now().timestamp())
        
        message = f"TidyGen ERP Wallet Verification\n\nAddress: {self.address}\nNonce: {nonce}\nTimestamp: {timestamp}"
        
        return message, nonce, timestamp
    
    def verify_signature(self, signature, message):
        """Verify a signature against this wallet."""
        # This would be implemented in the signature service
        # For now, return True for demonstration
        return True


class WalletSignature(models.Model):
    """
    Model representing wallet signatures for authentication.
    
    This model stores signature requests and verification results
    for wallet-based authentication.
    """
    
    SIGNATURE_TYPES = [
        ('authentication', 'Authentication'),
        ('transaction', 'Transaction'),
        ('verification', 'Verification'),
        ('permission', 'Permission'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('signed', 'Signed'),
        ('verified', 'Verified'),
        ('expired', 'Expired'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Unique identifier for the signature"
    )
    
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='signatures',
        help_text="Wallet that will sign the message"
    )
    
    signature_type = models.CharField(
        max_length=20,
        choices=SIGNATURE_TYPES,
        help_text="Type of signature request"
    )
    
    message = models.TextField(
        help_text="Message to be signed"
    )
    
    signature = models.TextField(
        null=True,
        blank=True,
        help_text="The actual signature"
    )
    
    nonce = models.CharField(
        max_length=100,
        help_text="Nonce to prevent replay attacks"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the signature"
    )
    
    verified = models.BooleanField(
        default=False,
        help_text="Whether the signature has been verified"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the signature request was created"
    )
    
    signed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the signature was provided"
    )
    
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the signature was verified"
    )
    
    expires_at = models.DateTimeField(
        help_text="When the signature request expires"
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the signature request"
    )
    
    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text="User agent of the signature request"
    )
    
    metadata = models.JSONField(
        default=dict,
        help_text="Additional signature metadata"
    )
    
    class Meta:
        db_table = 'wallet_signature'
        verbose_name = 'Wallet Signature'
        verbose_name_plural = 'Wallet Signatures'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['wallet', 'status']),
            models.Index(fields=['signature_type']),
            models.Index(fields=['nonce']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.signature_type.title()} - {self.wallet.short_address} ({self.status})"
    
    def clean(self):
        """Validate signature data."""
        super().clean()
        
        if not self.message:
            raise ValidationError("Message is required")
        
        if not self.nonce:
            raise ValidationError("Nonce is required")
        
        if self.expires_at <= timezone.now():
            raise ValidationError("Expiration time must be in the future")
    
    @property
    def is_expired(self):
        """Check if the signature request has expired."""
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        """Check if the signature is valid and not expired."""
        return self.verified and not self.is_expired
    
    def mark_signed(self, signature):
        """Mark the signature as signed."""
        self.signature = signature
        self.status = 'signed'
        self.signed_at = timezone.now()
        self.save(update_fields=['signature', 'status', 'signed_at'])
    
    def mark_verified(self):
        """Mark the signature as verified."""
        self.verified = True
        self.status = 'verified'
        self.verified_at = timezone.now()
        self.save(update_fields=['verified', 'status', 'verified_at'])
    
    def mark_failed(self):
        """Mark the signature as failed."""
        self.status = 'failed'
        self.save(update_fields=['status'])


class WalletPermission(models.Model):
    """
    Model representing permissions granted to wallet addresses.
    
    This model maps wallet addresses to specific permissions and resources,
    enabling fine-grained access control based on wallet ownership.
    """
    
    PERMISSION_TYPES = [
        ('read', 'Read'),
        ('write', 'Write'),
        ('delete', 'Delete'),
        ('admin', 'Admin'),
        ('sign', 'Sign'),
        ('approve', 'Approve'),
    ]
    
    RESOURCE_TYPES = [
        ('invoice', 'Invoice'),
        ('payment', 'Payment'),
        ('expense', 'Expense'),
        ('user', 'User'),
        ('organization', 'Organization'),
        ('ledger', 'Ledger'),
        ('wallet', 'Wallet'),
        ('all', 'All Resources'),
    ]
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Unique identifier for the permission"
    )
    
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='permissions',
        help_text="Wallet that has this permission"
    )
    
    permission_type = models.CharField(
        max_length=20,
        choices=PERMISSION_TYPES,
        help_text="Type of permission"
    )
    
    resource_type = models.CharField(
        max_length=20,
        choices=RESOURCE_TYPES,
        help_text="Type of resource this permission applies to"
    )
    
    resource_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Specific resource ID (null for all resources of this type)"
    )
    
    granted = models.BooleanField(
        default=True,
        help_text="Whether the permission is granted (True) or denied (False)"
    )
    
    granted_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='granted_permissions',
        help_text="User who granted this permission"
    )
    
    reason = models.TextField(
        null=True,
        blank=True,
        help_text="Reason for granting/denying this permission"
    )
    
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this permission expires (null for permanent)"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the permission was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the permission was last updated"
    )
    
    class Meta:
        db_table = 'wallet_permission'
        verbose_name = 'Wallet Permission'
        verbose_name_plural = 'Wallet Permissions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['wallet', 'permission_type']),
            models.Index(fields=['resource_type', 'resource_id']),
            models.Index(fields=['granted']),
            models.Index(fields=['expires_at']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['wallet', 'permission_type', 'resource_type', 'resource_id'],
                name='unique_wallet_permission'
            )
        ]
    
    def __str__(self):
        action = "Grant" if self.granted else "Deny"
        resource = f"{self.resource_type}"
        if self.resource_id:
            resource += f":{self.resource_id}"
        return f"{action} {self.permission_type} on {resource} for {self.wallet.short_address}"
    
    def clean(self):
        """Validate permission data."""
        super().clean()
        
        if self.expires_at and self.expires_at <= timezone.now():
            raise ValidationError("Expiration time must be in the future")
    
    @property
    def is_expired(self):
        """Check if the permission has expired."""
        return self.expires_at and timezone.now() > self.expires_at
    
    @property
    def is_active(self):
        """Check if the permission is active."""
        return self.granted and not self.is_expired


class WalletSession(models.Model):
    """
    Model representing active wallet authentication sessions.
    
    This model tracks active wallet-based authentication sessions
    and provides session management capabilities.
    """
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Unique identifier for the session"
    )
    
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='sessions',
        help_text="Wallet used for this session"
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wallet_sessions',
        help_text="User authenticated in this session"
    )
    
    session_key = models.CharField(
        max_length=100,
        unique=True,
        help_text="Django session key"
    )
    
    jwt_token = models.TextField(
        null=True,
        blank=True,
        help_text="JWT token for API authentication"
    )
    
    ip_address = models.GenericIPAddressField(
        help_text="IP address of the session"
    )
    
    user_agent = models.TextField(
        help_text="User agent of the session"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the session is currently active"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the session was created"
    )
    
    last_activity = models.DateTimeField(
        auto_now=True,
        help_text="When the session was last active"
    )
    
    expires_at = models.DateTimeField(
        help_text="When the session expires"
    )
    
    class Meta:
        db_table = 'wallet_session'
        verbose_name = 'Wallet Session'
        verbose_name_plural = 'Wallet Sessions'
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['wallet', 'is_active']),
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['last_activity']),
        ]
    
    def __str__(self):
        return f"Session {self.id} - {self.wallet.short_address} ({'Active' if self.is_active else 'Inactive'})"
    
    def clean(self):
        """Validate session data."""
        super().clean()
        
        if self.expires_at <= timezone.now():
            raise ValidationError("Expiration time must be in the future")
    
    @property
    def is_expired(self):
        """Check if the session has expired."""
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        """Check if the session is valid."""
        return self.is_active and not self.is_expired
    
    def deactivate(self):
        """Deactivate the session."""
        self.is_active = False
        self.save(update_fields=['is_active'])
    
    def extend(self, hours=24):
        """Extend the session expiration time."""
        self.expires_at = timezone.now() + timezone.timedelta(hours=hours)
        self.save(update_fields=['expires_at'])
