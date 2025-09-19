"""
Smart Contract Ledger Models

This module defines the database models for the Smart Contract Ledger functionality,
enabling tamper-proof logging of financial transactions to blockchain.
"""

import uuid
import hashlib
import json
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class LedgerTransaction(models.Model):
    """
    Model representing a transaction logged to the blockchain ledger.
    
    This model stores all financial transactions (invoices, payments, etc.)
    that are logged to the smart contract for tamper-proof audit trails.
    """
    
    TRANSACTION_TYPES = [
        ('invoice', 'Invoice'),
        ('payment', 'Payment'),
        ('expense', 'Expense'),
        ('refund', 'Refund'),
        ('adjustment', 'Adjustment'),
        ('transfer', 'Transfer'),
        ('payroll', 'Payroll'),
        ('tax', 'Tax'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Unique identifier for the ledger transaction"
    )
    
    transaction_type = models.CharField(
        max_length=50,
        choices=TRANSACTION_TYPES,
        help_text="Type of financial transaction"
    )
    
    source_module = models.CharField(
        max_length=50,
        help_text="Django app/module that created this transaction (e.g., finance, sales)"
    )
    
    source_id = models.CharField(
        max_length=100,
        help_text="ID of the original transaction in the source module"
    )
    
    transaction_data = models.JSONField(
        help_text="Complete transaction data as JSON"
    )
    
    hash = models.CharField(
        max_length=64,
        unique=True,
        help_text="SHA256 hash of the transaction data"
    )
    
    blockchain_hash = models.CharField(
        max_length=66,
        null=True,
        blank=True,
        help_text="Hash of the blockchain transaction (0x...)"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the blockchain transaction"
    )
    
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        related_name='ledger_transactions',
        help_text="Organization that owns this transaction"
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_ledger_transactions',
        help_text="User who created this transaction"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the transaction was created"
    )
    
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the transaction was submitted to blockchain"
    )
    
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the transaction was confirmed on blockchain"
    )
    
    failed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the transaction failed"
    )
    
    error_message = models.TextField(
        null=True,
        blank=True,
        help_text="Error message if transaction failed"
    )
    
    retry_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this transaction has been retried"
    )
    
    gas_used = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Gas used for the blockchain transaction"
    )
    
    gas_price = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Gas price for the blockchain transaction"
    )
    
    block_number = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Block number where transaction was confirmed"
    )
    
    transaction_index = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Index of transaction within the block"
    )
    
    class Meta:
        db_table = 'ledger_transaction'
        verbose_name = 'Ledger Transaction'
        verbose_name_plural = 'Ledger Transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['hash']),
            models.Index(fields=['status']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['source_module', 'source_id']),
            models.Index(fields=['organization', 'created_at']),
            models.Index(fields=['blockchain_hash']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['source_module', 'source_id', 'organization'],
                name='unique_source_transaction'
            )
        ]
    
    def __str__(self):
        return f"{self.transaction_type.title()} - {self.source_id} ({self.status})"
    
    def clean(self):
        """Validate the transaction data."""
        super().clean()
        
        if not self.transaction_data:
            raise ValidationError("Transaction data is required")
        
        if not isinstance(self.transaction_data, dict):
            raise ValidationError("Transaction data must be a dictionary")
        
        # Validate required fields in transaction data
        required_fields = ['amount', 'currency', 'description']
        for field in required_fields:
            if field not in self.transaction_data:
                raise ValidationError(f"Transaction data must contain '{field}' field")
    
    def save(self, *args, **kwargs):
        """Override save to generate hash if not provided."""
        if not self.hash:
            self.hash = self.generate_hash()
        super().save(*args, **kwargs)
    
    def generate_hash(self):
        """Generate SHA256 hash of the transaction data."""
        # Create a deterministic string from transaction data
        data_string = json.dumps(
            self.transaction_data, 
            sort_keys=True, 
            separators=(',', ':')
        )
        
        # Include other identifying information
        hash_input = f"{self.transaction_type}:{self.source_module}:{self.source_id}:{data_string}"
        
        return hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
    
    def verify_hash(self):
        """Verify that the stored hash matches the current transaction data."""
        expected_hash = self.generate_hash()
        return self.hash == expected_hash
    
    def mark_submitted(self, blockchain_hash=None):
        """Mark transaction as submitted to blockchain."""
        self.status = 'submitted'
        self.submitted_at = timezone.now()
        if blockchain_hash:
            self.blockchain_hash = blockchain_hash
        self.save(update_fields=['status', 'submitted_at', 'blockchain_hash'])
    
    def mark_confirmed(self, block_number=None, transaction_index=None, gas_used=None, gas_price=None):
        """Mark transaction as confirmed on blockchain."""
        self.status = 'confirmed'
        self.confirmed_at = timezone.now()
        if block_number is not None:
            self.block_number = block_number
        if transaction_index is not None:
            self.transaction_index = transaction_index
        if gas_used is not None:
            self.gas_used = gas_used
        if gas_price is not None:
            self.gas_price = gas_price
        self.save(update_fields=[
            'status', 'confirmed_at', 'block_number', 
            'transaction_index', 'gas_used', 'gas_price'
        ])
    
    def mark_failed(self, error_message=None):
        """Mark transaction as failed."""
        self.status = 'failed'
        self.failed_at = timezone.now()
        if error_message:
            self.error_message = error_message
        self.retry_count += 1
        self.save(update_fields=['status', 'failed_at', 'error_message', 'retry_count'])
    
    @property
    def is_confirmed(self):
        """Check if transaction is confirmed on blockchain."""
        return self.status == 'confirmed'
    
    @property
    def is_pending(self):
        """Check if transaction is pending."""
        return self.status in ['pending', 'submitted']
    
    @property
    def is_failed(self):
        """Check if transaction has failed."""
        return self.status == 'failed'
    
    @property
    def can_retry(self):
        """Check if transaction can be retried."""
        return self.is_failed and self.retry_count < 3


class LedgerEvent(models.Model):
    """
    Model representing events related to ledger transactions.
    
    This model stores events emitted by the smart contract and other
    system events for comprehensive audit trails.
    """
    
    EVENT_TYPES = [
        ('transaction_logged', 'Transaction Logged'),
        ('transaction_confirmed', 'Transaction Confirmed'),
        ('transaction_failed', 'Transaction Failed'),
        ('hash_verified', 'Hash Verified'),
        ('retry_attempted', 'Retry Attempted'),
        ('batch_processed', 'Batch Processed'),
        ('error_occurred', 'Error Occurred'),
    ]
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Unique identifier for the ledger event"
    )
    
    transaction = models.ForeignKey(
        LedgerTransaction,
        on_delete=models.CASCADE,
        related_name='events',
        help_text="Related ledger transaction"
    )
    
    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPES,
        help_text="Type of event"
    )
    
    event_data = models.JSONField(
        default=dict,
        help_text="Event-specific data as JSON"
    )
    
    blockchain_event_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="ID of the event on blockchain"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the event occurred"
    )
    
    class Meta:
        db_table = 'ledger_event'
        verbose_name = 'Ledger Event'
        verbose_name_plural = 'Ledger Events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type']),
            models.Index(fields=['transaction', 'created_at']),
            models.Index(fields=['blockchain_event_id']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.transaction.source_id}"


class LedgerBatch(models.Model):
    """
    Model representing batches of transactions submitted together.
    
    This model tracks batches of transactions that are submitted
    to the blockchain in a single operation for efficiency.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
        ('partial', 'Partially Confirmed'),
    ]
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Unique identifier for the batch"
    )
    
    batch_hash = models.CharField(
        max_length=64,
        unique=True,
        help_text="Hash of the batch data"
    )
    
    transactions = models.ManyToManyField(
        LedgerTransaction,
        related_name='batches',
        help_text="Transactions in this batch"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the batch"
    )
    
    blockchain_hash = models.CharField(
        max_length=66,
        null=True,
        blank=True,
        help_text="Hash of the batch transaction on blockchain"
    )
    
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        related_name='ledger_batches',
        help_text="Organization that owns this batch"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the batch was created"
    )
    
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the batch was submitted to blockchain"
    )
    
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the batch was confirmed on blockchain"
    )
    
    failed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the batch failed"
    )
    
    error_message = models.TextField(
        null=True,
        blank=True,
        help_text="Error message if batch failed"
    )
    
    gas_used = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Total gas used for the batch"
    )
    
    block_number = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Block number where batch was confirmed"
    )
    
    class Meta:
        db_table = 'ledger_batch'
        verbose_name = 'Ledger Batch'
        verbose_name_plural = 'Ledger Batches'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['batch_hash']),
            models.Index(fields=['status']),
            models.Index(fields=['organization', 'created_at']),
        ]
    
    def __str__(self):
        return f"Batch {self.id} ({self.status}) - {self.transactions.count()} transactions"
    
    @property
    def transaction_count(self):
        """Get the number of transactions in this batch."""
        return self.transactions.count()
    
    @property
    def is_confirmed(self):
        """Check if batch is confirmed on blockchain."""
        return self.status == 'confirmed'
    
    @property
    def is_failed(self):
        """Check if batch has failed."""
        return self.status == 'failed'


class LedgerConfiguration(models.Model):
    """
    Model for storing ledger configuration settings.
    
    This model stores configuration settings for the ledger system,
    including blockchain connection details and operational parameters.
    """
    
    organization = models.OneToOneField(
        'core.Organization',
        on_delete=models.CASCADE,
        related_name='ledger_config',
        help_text="Organization this configuration belongs to"
    )
    
    blockchain_network = models.CharField(
        max_length=50,
        default='substrate',
        help_text="Blockchain network to use (substrate, ethereum, etc.)"
    )
    
    rpc_endpoint = models.URLField(
        help_text="RPC endpoint for blockchain connection"
    )
    
    contract_address = models.CharField(
        max_length=66,
        null=True,
        blank=True,
        help_text="Address of the deployed smart contract"
    )
    
    private_key = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Private key for signing transactions (encrypted)"
    )
    
    batch_size = models.PositiveIntegerField(
        default=10,
        help_text="Maximum number of transactions per batch"
    )
    
    batch_timeout = models.PositiveIntegerField(
        default=300,
        help_text="Timeout in seconds for batch processing"
    )
    
    retry_attempts = models.PositiveIntegerField(
        default=3,
        help_text="Maximum number of retry attempts"
    )
    
    gas_limit = models.BigIntegerField(
        default=1000000,
        help_text="Gas limit for transactions"
    )
    
    gas_price = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Gas price for transactions"
    )
    
    auto_confirm = models.BooleanField(
        default=True,
        help_text="Automatically confirm transactions"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether ledger is active for this organization"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the configuration was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the configuration was last updated"
    )
    
    class Meta:
        db_table = 'ledger_configuration'
        verbose_name = 'Ledger Configuration'
        verbose_name_plural = 'Ledger Configurations'
    
    def __str__(self):
        return f"Ledger Config - {self.organization.name}"
    
    def clean(self):
        """Validate configuration settings."""
        super().clean()
        
        if self.batch_size <= 0:
            raise ValidationError("Batch size must be greater than 0")
        
        if self.batch_timeout <= 0:
            raise ValidationError("Batch timeout must be greater than 0")
        
        if self.retry_attempts <= 0:
            raise ValidationError("Retry attempts must be greater than 0")
