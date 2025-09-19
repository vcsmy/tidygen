"""
Audit Trail Models

Models for decentralized audit trail system including AuditEvent, AuditHash,
MerkleTree, and OnChainRecord models for tamper-proof logging.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
import hashlib
import json
from typing import Dict, Any, List

User = get_user_model()


class AuditEvent(models.Model):
    """
    Represents an audit event in the system.
    Each financial or system event is captured as an AuditEvent.
    """
    
    EVENT_TYPE_CHOICES = [
        # Financial Events
        ('invoice_created', 'Invoice Created'),
        ('invoice_updated', 'Invoice Updated'),
        ('invoice_deleted', 'Invoice Deleted'),
        ('payment_created', 'Payment Created'),
        ('payment_processed', 'Payment Processed'),
        ('payment_failed', 'Payment Failed'),
        ('expense_created', 'Expense Created'),
        ('expense_approved', 'Expense Approved'),
        ('expense_rejected', 'Expense Rejected'),
        
        # Sales Events
        ('sale_created', 'Sale Created'),
        ('sale_updated', 'Sale Updated'),
        ('client_created', 'Client Created'),
        ('client_updated', 'Client Updated'),
        ('contract_created', 'Contract Created'),
        ('contract_updated', 'Contract Updated'),
        
        # HR Events
        ('employee_created', 'Employee Created'),
        ('employee_updated', 'Employee Updated'),
        ('payroll_processed', 'Payroll Processed'),
        ('leave_approved', 'Leave Approved'),
        ('leave_rejected', 'Leave Rejected'),
        
        # System Events
        ('user_login', 'User Login'),
        ('user_logout', 'User Logout'),
        ('permission_granted', 'Permission Granted'),
        ('permission_revoked', 'Permission Revoked'),
        ('data_export', 'Data Export'),
        ('data_import', 'Data Import'),
        ('system_backup', 'System Backup'),
        ('system_restore', 'System Restore'),
    ]
    
    MODULE_CHOICES = [
        ('finance', 'Finance'),
        ('sales', 'Sales'),
        ('hr', 'Human Resources'),
        ('inventory', 'Inventory'),
        ('purchasing', 'Purchasing'),
        ('scheduling', 'Scheduling'),
        ('analytics', 'Analytics'),
        ('system', 'System'),
        ('wallet', 'Wallet'),
        ('audit_trail', 'Audit Trail'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('hashed', 'Hashed'),
        ('on_chain', 'On-Chain'),
        ('verified', 'Verified'),
        ('failed', 'Failed'),
    ]
    
    # Basic event information
    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPE_CHOICES,
        db_index=True,
        help_text="Type of audit event"
    )
    module = models.CharField(
        max_length=20,
        choices=MODULE_CHOICES,
        db_index=True,
        help_text="Module that generated the event"
    )
    object_id = models.CharField(
        max_length=100,
        db_index=True,
        help_text="ID of the object that triggered the event"
    )
    object_type = models.CharField(
        max_length=100,
        help_text="Type of the object that triggered the event"
    )
    
    # Event data and metadata
    data = models.JSONField(
        help_text="Event data payload"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional event metadata"
    )
    
    # User and session information
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_events',
        help_text="User who triggered the event"
    )
    session_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Session ID when event occurred"
    )
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text="IP address of the user"
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        help_text="User agent string"
    )
    
    # Timestamps
    timestamp = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="When the event occurred"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the audit record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the audit record was last updated"
    )
    
    # Hash and verification
    hash = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text="SHA256 hash of the event data"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
        help_text="Current status of the audit event"
    )
    
    # On-chain information
    on_chain_hash = models.CharField(
        max_length=66,
        blank=True,
        null=True,
        db_index=True,
        help_text="On-chain hash (with 0x prefix)"
    )
    on_chain_tx_hash = models.CharField(
        max_length=66,
        blank=True,
        null=True,
        db_index=True,
        help_text="Blockchain transaction hash"
    )
    on_chain_block_number = models.BigIntegerField(
        blank=True,
        null=True,
        help_text="Block number where event was stored"
    )
    on_chain_timestamp = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Blockchain timestamp"
    )
    
    # IPFS information
    ipfs_hash = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True,
        help_text="IPFS hash for decentralized storage"
    )
    
    class Meta:
        verbose_name = "Audit Event"
        verbose_name_plural = "Audit Events"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['module', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['status', 'timestamp']),
            models.Index(fields=['on_chain_tx_hash']),
            models.Index(fields=['ipfs_hash']),
        ]
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.module} - {self.timestamp}"
    
    def clean(self):
        """Validate the audit event."""
        super().clean()
        
        # Validate that data is not empty
        if not self.data:
            raise ValidationError("Event data cannot be empty")
        
        # Validate object_id is provided
        if not self.object_id:
            raise ValidationError("Object ID is required")
    
    def save(self, *args, **kwargs):
        """Override save to generate hash if not provided."""
        if not self.hash:
            self.hash = self.generate_hash()
        super().save(*args, **kwargs)
    
    def generate_hash(self) -> str:
        """Generate SHA256 hash for the audit event."""
        hash_data = {
            'event_type': self.event_type,
            'module': self.module,
            'object_id': self.object_id,
            'object_type': self.object_type,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user.id if self.user else None,
        }
        
        # Create deterministic JSON string
        json_string = json.dumps(hash_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_string.encode('utf-8')).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit event to dictionary for serialization."""
        return {
            'id': str(self.id),
            'event_type': self.event_type,
            'module': self.module,
            'object_id': self.object_id,
            'object_type': self.object_type,
            'data': self.data,
            'metadata': self.metadata,
            'user_id': self.user.id if self.user else None,
            'session_id': self.session_id,
            'ip_address': str(self.ip_address) if self.ip_address else None,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'hash': self.hash,
            'status': self.status,
            'on_chain_hash': self.on_chain_hash,
            'on_chain_tx_hash': self.on_chain_tx_hash,
            'on_chain_block_number': self.on_chain_block_number,
            'on_chain_timestamp': self.on_chain_timestamp.isoformat() if self.on_chain_timestamp else None,
            'ipfs_hash': self.ipfs_hash,
        }
    
    def mark_hashed(self):
        """Mark event as hashed."""
        self.status = 'hashed'
        self.save(update_fields=['status', 'updated_at'])
    
    def mark_on_chain(self, tx_hash: str, block_number: int, on_chain_timestamp: timezone.datetime):
        """Mark event as stored on-chain."""
        self.status = 'on_chain'
        self.on_chain_tx_hash = tx_hash
        self.on_chain_block_number = block_number
        self.on_chain_timestamp = on_chain_timestamp
        self.save(update_fields=['status', 'on_chain_tx_hash', 'on_chain_block_number', 'on_chain_timestamp', 'updated_at'])
    
    def mark_verified(self):
        """Mark event as verified."""
        self.status = 'verified'
        self.save(update_fields=['status', 'updated_at'])
    
    def mark_failed(self):
        """Mark event as failed."""
        self.status = 'failed'
        self.save(update_fields=['status', 'updated_at'])


class AuditHash(models.Model):
    """
    Represents a hash record for audit events.
    Used for tracking hash generation and verification.
    """
    
    HASH_TYPE_CHOICES = [
        ('sha256', 'SHA256'),
        ('keccak256', 'Keccak256'),
        ('merkle_root', 'Merkle Root'),
    ]
    
    # Hash information
    hash_value = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text="The hash value"
    )
    hash_type = models.CharField(
        max_length=20,
        choices=HASH_TYPE_CHOICES,
        default='sha256',
        help_text="Type of hash algorithm used"
    )
    
    # Related audit event
    audit_event = models.ForeignKey(
        AuditEvent,
        on_delete=models.CASCADE,
        related_name='hashes',
        help_text="Related audit event"
    )
    
    # Hash metadata
    data_hash = models.CharField(
        max_length=64,
        help_text="Hash of the original data"
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        help_text="When the hash was generated"
    )
    
    # Verification status
    verified = models.BooleanField(
        default=False,
        help_text="Whether the hash has been verified"
    )
    verification_timestamp = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the hash was verified"
    )
    
    class Meta:
        verbose_name = "Audit Hash"
        verbose_name_plural = "Audit Hashes"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['hash_value']),
            models.Index(fields=['hash_type', 'timestamp']),
            models.Index(fields=['verified', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.get_hash_type_display()} - {self.hash_value[:16]}..."
    
    def mark_verified(self):
        """Mark hash as verified."""
        self.verified = True
        self.verification_timestamp = timezone.now()
        self.save(update_fields=['verified', 'verification_timestamp'])


class MerkleTree(models.Model):
    """
    Represents a Merkle tree for batch verification of audit events.
    """
    
    # Tree information
    root_hash = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text="Root hash of the Merkle tree"
    )
    leaf_count = models.PositiveIntegerField(
        help_text="Number of leaves in the tree"
    )
    
    # Tree metadata
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="When the tree was created"
    )
    batch_size = models.PositiveIntegerField(
        help_text="Number of events in this batch"
    )
    
    # Tree data
    tree_data = models.JSONField(
        help_text="Serialized tree structure"
    )
    leaf_hashes = models.JSONField(
        help_text="List of leaf hashes"
    )
    
    # On-chain information
    on_chain_tx_hash = models.CharField(
        max_length=66,
        blank=True,
        null=True,
        db_index=True,
        help_text="Blockchain transaction hash"
    )
    on_chain_block_number = models.BigIntegerField(
        blank=True,
        null=True,
        help_text="Block number where tree was stored"
    )
    
    class Meta:
        verbose_name = "Merkle Tree"
        verbose_name_plural = "Merkle Trees"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['root_hash']),
            models.Index(fields=['created_at']),
            models.Index(fields=['on_chain_tx_hash']),
        ]
    
    def __str__(self):
        return f"Merkle Tree - {self.root_hash[:16]}... ({self.leaf_count} leaves)"
    
    def get_events(self) -> List[AuditEvent]:
        """Get all events in this Merkle tree."""
        # This would need to be implemented based on how events are linked to trees
        return AuditEvent.objects.filter(
            timestamp__gte=self.created_at - timezone.timedelta(minutes=1),
            timestamp__lte=self.created_at + timezone.timedelta(minutes=1)
        ).order_by('timestamp')[:self.batch_size]


class OnChainRecord(models.Model):
    """
    Represents a record stored on the blockchain.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
    ]
    
    # Related audit event
    audit_event = models.ForeignKey(
        AuditEvent,
        on_delete=models.CASCADE,
        related_name='on_chain_records',
        help_text="Related audit event"
    )
    
    # Blockchain information
    transaction_hash = models.CharField(
        max_length=66,
        unique=True,
        db_index=True,
        help_text="Blockchain transaction hash"
    )
    block_number = models.BigIntegerField(
        help_text="Block number"
    )
    block_hash = models.CharField(
        max_length=66,
        help_text="Block hash"
    )
    gas_used = models.BigIntegerField(
        help_text="Gas used for the transaction"
    )
    gas_price = models.BigIntegerField(
        help_text="Gas price for the transaction"
    )
    
    # Contract information
    contract_address = models.CharField(
        max_length=42,
        help_text="Smart contract address"
    )
    function_name = models.CharField(
        max_length=100,
        help_text="Function name called"
    )
    
    # Status and timestamps
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="On-chain status"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="When the record was created"
    )
    confirmed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the transaction was confirmed"
    )
    
    class Meta:
        verbose_name = "On-Chain Record"
        verbose_name_plural = "On-Chain Records"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_hash']),
            models.Index(fields=['block_number']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['contract_address']),
        ]
    
    def __str__(self):
        return f"On-Chain Record - {self.transaction_hash[:16]}..."
    
    def mark_confirmed(self):
        """Mark record as confirmed."""
        self.status = 'confirmed'
        self.confirmed_at = timezone.now()
        self.save(update_fields=['status', 'confirmed_at'])
    
    def mark_failed(self):
        """Mark record as failed."""
        self.status = 'failed'
        self.save(update_fields=['status'])


class AuditConfiguration(models.Model):
    """
    Configuration for audit trail system.
    """
    
    # Configuration settings
    auto_hash_events = models.BooleanField(
        default=True,
        help_text="Automatically hash events when created"
    )
    auto_store_on_chain = models.BooleanField(
        default=False,
        help_text="Automatically store events on-chain"
    )
    auto_store_ipfs = models.BooleanField(
        default=False,
        help_text="Automatically store events in IPFS"
    )
    
    # Batch settings
    merkle_batch_size = models.PositiveIntegerField(
        default=100,
        help_text="Number of events per Merkle tree batch"
    )
    on_chain_batch_size = models.PositiveIntegerField(
        default=50,
        help_text="Number of events per on-chain batch"
    )
    
    # Retention settings
    retention_days = models.PositiveIntegerField(
        default=2555,  # 7 years
        help_text="Number of days to retain audit events"
    )
    
    # Blockchain settings
    blockchain_network = models.CharField(
        max_length=50,
        default='ethereum',
        help_text="Blockchain network to use"
    )
    contract_address = models.CharField(
        max_length=42,
        blank=True,
        null=True,
        help_text="Smart contract address"
    )
    
    # IPFS settings
    ipfs_enabled = models.BooleanField(
        default=False,
        help_text="Enable IPFS storage"
    )
    ipfs_gateway = models.URLField(
        blank=True,
        null=True,
        help_text="IPFS gateway URL"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the configuration was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the configuration was last updated"
    )
    
    class Meta:
        verbose_name = "Audit Configuration"
        verbose_name_plural = "Audit Configurations"
    
    def __str__(self):
        return f"Audit Configuration - {self.blockchain_network}"
    
    @classmethod
    def get_config(cls):
        """Get the current audit configuration."""
        config, created = cls.objects.get_or_create(
            defaults={
                'auto_hash_events': True,
                'auto_store_on_chain': False,
                'auto_store_ipfs': False,
                'merkle_batch_size': 100,
                'on_chain_batch_size': 50,
                'retention_days': 2555,
                'blockchain_network': 'ethereum',
                'ipfs_enabled': False,
            }
        )
        return config
