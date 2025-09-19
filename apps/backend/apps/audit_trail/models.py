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


# Additional models will be added in separate files to avoid timeout
