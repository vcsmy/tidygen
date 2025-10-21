"""
Contractor Payments models for TidyGen ERP Community Edition.
Handles payment processing, escrow, and Web3 payments for individual contractors.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from apps.core.models import BaseModel

User = get_user_model()


class PaymentMethod(BaseModel):
    """
    Supported payment methods for contractor payments.
    """
    PAYMENT_TYPES = [
        ('bank_transfer', 'Bank Transfer'),
        ('crypto_wallet', 'Crypto Wallet'),
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('escrow_crypto', 'Escrow Crypto'),
        ('escrow_traditional', 'Escrow Traditional'),
    ]
    
    name = models.CharField(_('payment method name'), max_length=50, unique=True)
    payment_type = models.CharField(_('payment type'), max_length=30, choices=PAYMENT_TYPES)
    is_active = models.BooleanField(_('is active'), default=True)
    processing_fee_percentage = models.DecimalField(
        _('processing fee percentage'), 
        max_digits=5, decimal_places=2, default=0,
        validators=[MinValueValidator(0)]
    )
    min_payment_amount = models.DecimalField(_('min payment amount'), max_digits=10, decimal_places=2, default=0)
    max_payment_amount = models.DecimalField(_('max payment amount'), max_digits=15, decimal_places=2, default=999999999.99)
    supported_currencies = models.JSONField(_('supported currencies'), default=list)
    
    # Configuration
    requires_kyc = models.BooleanField(_('requires KYC'), default=False)
    settlement_time_hours = models.IntegerField(_('settlement time hours'), default=24)
    web3_enabled = models.BooleanField(_('Web3 enabled'), default=False)
    
    class Meta:
        verbose_name = _('Payment Method')
        verbose_name_plural = _('Payment Methods')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ContractorPayment(BaseModel):
    """
    Payment transactions for contractors/freelancers.
    """
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('disputed', 'Disputed'),
    ]
    
    PAYMENT_TRIGGER_CHOICES = [
        ('job_completion', 'Job Completion'),
        ('milestone_completion', 'Milestone Completion'),
        ('scheduled', 'Scheduled Payment'),
        ('manual', 'Manual Payment'),
        ('dispute_resolution', 'Dispute Resolution'),
    ]
    
    # Payment identification
    payment_id = models.CharField(_('payment ID'), max_length=50, unique=True)
    transaction_reference = models.CharField(_('transaction reference'), max_length=200, blank=True)
    
    # Related entities
    freelancer = models.ForeignKey('freelancers.Freelancer', on_delete=models.CASCADE, related_name='payments')
    job = models.ForeignKey('gig_management.GigJob', on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    milestone = models.ForeignKey('gig_management.JobMilestone', on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    
    # Payment details
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, related_name='payments')
    amount = models.DecimalField(_('amount'), max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    currency = models.CharField(_('currency'), max_length=10, default='USD')
    processing_fee = models.DecimalField(_('processing fee'), max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(_('net amount'), max_digits=15, decimal_places=2)
    
    # Payment trigger and timing
    payment_trigger = models.CharField(_('payment trigger'), max_length=20, choices=PAYMENT_TRIGGER_CHOICES)
    scheduled_date = models.DateTimeField(_('scheduled date'), null=True, blank=True)
    processed_date = models.DateTimeField(_('processed date'), null=True, blank=True)
    
    # Status and workflow
    status = models.CharField(_('status'), max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    failure_reason = models.TextField(_('failure reason'), blank=True)
    retry_count = models.IntegerField(_('retry count'), default=0)
    max_retries = models.IntegerField(_('max retries'), default=3)
    
    # Bank/Account details (encrypted)
    bank_account_number = models.CharField(_('bank account number'), max_length=100, blank=True)
    bank_routing_number = models.CharField(_('bank routing number'), max_length=50, blank=True)
    bank_name = models.CharField(_('bank name'), max_length=200, blank=True)
    account_holder_name = models.CharField(_('account holder name'), max_length=200, blank=True)
    
    # Crypto wallet details
    wallet_address = models.CharField(_('wallet address'), max_length=100, blank=True)
    crypto_currency = models.CharField(_('crypto currency'), max_length=20, blank=True)
    blockchain_network = models.CharField(_('blockchain network'), max_length=50, blank=True)
    
    # External payment processor details
    processor_transaction_id = models.CharField(_('processor transaction ID'), max_length=200, blank=True)
    processor_response = models.JSONField(_('processor response'), default=dict)
    
    # Web3 integration
    smart_contract_address = models.CharField(_('smart contract address'), max_length=42, blank=True)
    blockchain_transaction_hash = models.CharField(_('blockchain transaction hash'), max_length=66, blank=True)
    gas_fee = models.DecimalField(_('gas fee'), max_digits=10, decimal_places=8, default=0)
    
    # Additional information
    notes = models.TextField(_('notes'), blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_payments')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_payments')
    
    class Meta:
        verbose_name = _('Contractor Payment')
        verbose_name_plural = _('Contractor Payments')
        ordering = ['-created']
        indexes = [
            models.Index(fields=['payment_id']),
            models.Index(fields=['freelancer', 'status']),
            models.Index(fields=['status', 'scheduled_date']),
            models.Index(fields=['created']),
        ]
    
    def __str__(self):
        return f"{self.payment_id}: {self.freelancer.full_name} - {self.amount} {self.currency}"
    
    def save(self, *args, **kwargs):
        """Calculate net amount before saving."""
        if not self.net_amount:
            self.net_amount = self.amount - self.processing_fee
        super().save(*args, **kwargs)


class EscrowAccount(BaseModel):
    """
    Escrow accounts for secure payment holding.
    """
    ESCROW_STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending_deposit', 'Pending Deposit'),
        ('funded', 'Funded'),
        ('released', 'Released'),
        ('disputed', 'Disputed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Escrow identification
    escrow_id = models.CharField(_('escrow ID'), max_length=50, unique=True)
    
    # Related entities
    job = models.ForeignKey('gig_management.GigJob', on_delete=models.CASCADE, related_name='escrow_accounts')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='escrow_accounts')
    freelancer = models.ForeignKey('freelancers.Freelancer', on_delete=models.CASCADE, related_name='escrow_accounts')
    
    # Financial details
    total_amount = models.DecimalField(_('total amount'), max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    currency = models.CharField(_('currency'), max_length=10, default='USD')
    platform_fee = models.DecimalField(_('platform fee'), max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(_('net amount for freelancer'), max_digits=15, decimal_places=2)
    
    # Escrow workflow
    status = models.CharField(_('status'), max_length=20, choices=ESCROW_STATUS_CHOICES, default='pending_deposit')
    funded_date = models.DateTimeField(_('funded date'), null=True, blank=True)
    release_date = models.DateTimeField(_('release date'), null=True, blank=True)
    release_trigger = models.CharField(_('release trigger'), max_length=50, blank=True)  # e.g., 'job_completion', 'client_approval'
    
    # Web3/Escrow contract details
    smart_contract_address = models.CharField(_('smart contract address'), max_length=42, blank=True)
    blockchain_transaction_hash = models.CharField(_('blockchain transaction hash'), max_length=66, blank=True)
    contract_deployed_at = models.DateTimeField(_('contract deployed at'), null=True, blank=True)
    
    # Traditional escrow details
    escrow_provider = models.CharField(_('escrow provider'), max_length=100, blank=True)
    escrow_account_number = models.CharField(_('escrow account number'), max_length=100, blank=True)
    
    # Dispute handling
    dispute_reason = models.TextField(_('dispute reason'), blank=True)
    dispute_raised_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='raised_disputes')
    dispute_raised_at = models.DateTimeField(_('dispute raised at'), null=True, blank=True)
    
    # Release conditions
    auto_release_hours = models.IntegerField(_('auto release hours'), default=72)  # Auto-release after 72 hours unless disputed
    requires_client_approval = models.BooleanField(_('requires client approval'), default=True)
    requires_freelancer_confirmation = models.BooleanField(_('requires freelancer confirmation'), default=False)
    
    class Meta:
        verbose_name = _('Escrow Account')
        verbose_name_plural = _('Escrow Accounts')
        ordering = ['-created']
        indexes = [
            models.Index(fields=['escrow_id']),
            models.Index(fields=['status', 'created']),
            models.Index(fields=['job', 'status']),
        ]
    
    def __str__(self):
        return f"Escrow {self.escrow_id}: {self.job.title if self.job else 'Unknown Job'}"
    
    @property
    def is_funded(self):
        """Check if escrow is funded and ready for release."""
        return self.status in ['funded', 'released'] and self.blockchain_transaction_hash


class PaymentSchedule(BaseModel):
    """
    Scheduled payment plans for contractors.
    """
    SCHEDULE_TYPES = [
        ('weekly', 'Weekly'),
        ('bi_weekly', 'Bi-weekly'),
        ('monthly', 'Monthly'),
        ('per_job', 'Per Job'),
        ('milestone_based', 'Milestone Based'),
    ]
    
    freelancer = models.ForeignKey('freelancers.Freelancer', on_delete=models.CASCADE, related_name='payment_schedules')
    schedule_type = models.CharField(_('schedule type'), max_length=20, choices=SCHEDULE_TYPES)
    
    # Schedule configuration
    is_active = models.BooleanField(_('is active'), default=True)
    next_payment_date = models.DateTimeField(_('next payment date'))
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, related_name='schedules')
    
    # Amount configuration
    fixed_amount = models.DecimalField(_('fixed amount'), max_digits=15, decimal_places=2, null=True, blank=True)
    currency = models.CharField(_('currency'), max_length=10, default='USD')
    
    # Accumulated amounts for variable schedules
    accumulated_amount = models.DecimalField(_('accumulated amount'), max_digits=15, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = _('Payment Schedule')
        verbose_name_plural = _('Payment Schedules')
        ordering = ['next_payment_date']
    
    def __str__(self):
        return f"{self.freelancer.full_name} - {self.get_schedule_type_display()}"


class DisputeResolution(BaseModel):
    """
    Dispute resolution for payment issues.
    """
    DISPUTE_TYPES = [
        ('payment_quality', 'Payment vs Quality'),
        ('payment_timing', 'Payment Timing'),
        ('payment_amount', 'Payment Amount'),
        ('cancelled_job', 'Cancelled Job'),
        ('other', 'Other'),
    ]
    
    RESOLUTION_STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('resolved', 'Resolved'),
        ('escalated', 'Escalated'),
        ('closed', 'Closed'),
    ]
    
    # Related entities
    payment = models.ForeignKey(ContractorPayment, on_delete=models.CASCADE, related_name='disputes')
    escrow_account = models.ForeignKey(EscrowAccount, on_delete=models.CASCADE, null=True, blank=True, related_name='disputes')
    
    # Dispute information
    dispute_type = models.CharField(_('dispute type'), max_length=30, choices=DISPUTE_TYPES)
    description = models.TextField(_('description'))
    raised_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_disputes')
    
    # Resolution workflow
    status = models.CharField(_('status'), max_length=20, choices=RESOLUTION_STATUS_CHOICES, default='submitted')
    resolution_notes = models.TextField(_('resolution notes'), blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_disputes')
    resolved_at = models.DateTimeField(_('resolved at'), null=True, blank=True)
    
    # Resolution outcome
    resolution_amount = models.DecimalField(_('resolution amount'), max_digits=15, decimal_places=2, null=True, blank=True)
    resolution_type = models.CharField(_('resolution type'), max_length=50, blank=True)  # e.g., 'partial_refund', 'full_payment'
    
    class Meta:
        verbose_name = _('Dispute Resolution')
        verbose_name_plural = _('Dispute Resolutions')
        ordering = ['-created']
    
    def __str__(self):
        return f"Dispute for {self.payment.payment_id} - {self.get_status_display()}"
