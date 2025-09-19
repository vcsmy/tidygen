"""
Smart Contract Ledger Admin Interface

This module defines the Django admin interface for the Smart Contract Ledger,
providing administrative access to ledger transactions, events, and configuration.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Q
from django.utils import timezone

from .models import (
    LedgerTransaction,
    LedgerEvent,
    LedgerBatch,
    LedgerConfiguration
)


@admin.register(LedgerTransaction)
class LedgerTransactionAdmin(admin.ModelAdmin):
    """Admin interface for LedgerTransaction model."""
    
    list_display = [
        'id',
        'transaction_type',
        'source_module',
        'source_id',
        'organization',
        'status',
        'hash_short',
        'blockchain_hash_short',
        'amount_display',
        'created_at',
        'confirmed_at',
        'retry_count'
    ]
    
    list_filter = [
        'transaction_type',
        'status',
        'source_module',
        'organization',
        'created_at',
        'confirmed_at'
    ]
    
    search_fields = [
        'source_id',
        'hash',
        'blockchain_hash',
        'organization__name',
        'transaction_data'
    ]
    
    readonly_fields = [
        'id',
        'hash',
        'created_at',
        'submitted_at',
        'confirmed_at',
        'failed_at',
        'retry_count',
        'gas_used',
        'gas_price',
        'block_number',
        'transaction_index',
        'hash_verification',
        'transaction_data_display'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id',
                'transaction_type',
                'source_module',
                'source_id',
                'organization',
                'created_by'
            )
        }),
        ('Transaction Data', {
            'fields': (
                'transaction_data_display',
                'hash',
                'hash_verification'
            )
        }),
        ('Blockchain Information', {
            'fields': (
                'blockchain_hash',
                'status',
                'block_number',
                'transaction_index',
                'gas_used',
                'gas_price'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'submitted_at',
                'confirmed_at',
                'failed_at'
            )
        }),
        ('Error Information', {
            'fields': (
                'error_message',
                'retry_count'
            ),
            'classes': ('collapse',)
        })
    )
    
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    def hash_short(self, obj):
        """Display short version of hash."""
        if obj.hash:
            return f"{obj.hash[:8]}...{obj.hash[-8:]}"
        return '-'
    hash_short.short_description = 'Hash'
    
    def blockchain_hash_short(self, obj):
        """Display short version of blockchain hash."""
        if obj.blockchain_hash:
            return f"{obj.blockchain_hash[:8]}...{obj.blockchain_hash[-8:]}"
        return '-'
    blockchain_hash_short.short_description = 'Blockchain Hash'
    
    def amount_display(self, obj):
        """Display transaction amount."""
        try:
            amount = obj.transaction_data.get('amount', 0)
            currency = obj.transaction_data.get('currency', 'USD')
            return f"{amount} {currency}"
        except (AttributeError, KeyError):
            return '-'
    amount_display.short_description = 'Amount'
    
    def hash_verification(self, obj):
        """Display hash verification status."""
        if obj.hash:
            is_valid = obj.verify_hash()
            if is_valid:
                return format_html(
                    '<span style="color: green;">✓ Valid</span>'
                )
            else:
                return format_html(
                    '<span style="color: red;">✗ Invalid</span>'
                )
        return '-'
    hash_verification.short_description = 'Hash Verification'
    
    def transaction_data_display(self, obj):
        """Display formatted transaction data."""
        if obj.transaction_data:
            import json
            formatted_data = json.dumps(obj.transaction_data, indent=2)
            return format_html('<pre>{}</pre>', formatted_data)
        return '-'
    transaction_data_display.short_description = 'Transaction Data'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'organization',
            'created_by'
        )
    
    actions = ['submit_to_blockchain', 'verify_transactions', 'retry_failed']
    
    def submit_to_blockchain(self, request, queryset):
        """Submit selected transactions to blockchain."""
        from .services import TransactionService
        
        submitted_count = 0
        failed_count = 0
        
        for transaction in queryset.filter(status='pending'):
            try:
                service = TransactionService(
                    organization_id=str(transaction.organization.id)
                )
                if service.submit_transaction(transaction):
                    submitted_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                failed_count += 1
        
        self.message_user(
            request,
            f"Submitted {submitted_count} transactions, {failed_count} failed."
        )
    submit_to_blockchain.short_description = "Submit to blockchain"
    
    def verify_transactions(self, request, queryset):
        """Verify selected transactions."""
        from .services import TransactionService
        
        verified_count = 0
        failed_count = 0
        
        for transaction in queryset:
            try:
                service = TransactionService(
                    organization_id=str(transaction.organization.id)
                )
                result = service.verify_transaction(transaction)
                if result.get('hash_valid') and result.get('blockchain_confirmed'):
                    verified_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                failed_count += 1
        
        self.message_user(
            request,
            f"Verified {verified_count} transactions, {failed_count} failed."
        )
    verify_transactions.short_description = "Verify transactions"
    
    def retry_failed(self, request, queryset):
        """Retry failed transactions."""
        from .services import TransactionService
        
        retried_count = 0
        failed_count = 0
        
        for transaction in queryset.filter(status='failed'):
            try:
                service = TransactionService(
                    organization_id=str(transaction.organization.id)
                )
                if service.submit_transaction(transaction, force_submit=True):
                    retried_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                failed_count += 1
        
        self.message_user(
            request,
            f"Retried {retried_count} transactions, {failed_count} failed."
        )
    retry_failed.short_description = "Retry failed transactions"


@admin.register(LedgerEvent)
class LedgerEventAdmin(admin.ModelAdmin):
    """Admin interface for LedgerEvent model."""
    
    list_display = [
        'id',
        'transaction_link',
        'event_type',
        'blockchain_event_id',
        'created_at'
    ]
    
    list_filter = [
        'event_type',
        'created_at',
        'transaction__organization'
    ]
    
    search_fields = [
        'transaction__source_id',
        'blockchain_event_id',
        'event_data'
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'event_data_display'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id',
                'transaction',
                'event_type',
                'blockchain_event_id'
            )
        }),
        ('Event Data', {
            'fields': (
                'event_data_display',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
            )
        })
    )
    
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    def transaction_link(self, obj):
        """Display link to related transaction."""
        if obj.transaction:
            url = reverse('admin:ledger_ledgertransaction_change', args=[obj.transaction.id])
            return format_html(
                '<a href="{}">{}</a>',
                url,
                f"{obj.transaction.transaction_type} - {obj.transaction.source_id}"
            )
        return '-'
    transaction_link.short_description = 'Transaction'
    
    def event_data_display(self, obj):
        """Display formatted event data."""
        if obj.event_data:
            import json
            formatted_data = json.dumps(obj.event_data, indent=2)
            return format_html('<pre>{}</pre>', formatted_data)
        return '-'
    event_data_display.short_description = 'Event Data'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'transaction',
            'transaction__organization'
        )


@admin.register(LedgerBatch)
class LedgerBatchAdmin(admin.ModelAdmin):
    """Admin interface for LedgerBatch model."""
    
    list_display = [
        'id',
        'batch_hash_short',
        'organization',
        'status',
        'transaction_count',
        'blockchain_hash_short',
        'created_at',
        'confirmed_at'
    ]
    
    list_filter = [
        'status',
        'organization',
        'created_at',
        'confirmed_at'
    ]
    
    search_fields = [
        'batch_hash',
        'blockchain_hash',
        'organization__name'
    ]
    
    readonly_fields = [
        'id',
        'batch_hash',
        'created_at',
        'submitted_at',
        'confirmed_at',
        'failed_at',
        'gas_used',
        'block_number',
        'transaction_list'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id',
                'batch_hash',
                'organization',
                'status'
            )
        }),
        ('Blockchain Information', {
            'fields': (
                'blockchain_hash',
                'block_number',
                'gas_used'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'submitted_at',
                'confirmed_at',
                'failed_at'
            )
        }),
        ('Transactions', {
            'fields': (
                'transaction_list',
            )
        }),
        ('Error Information', {
            'fields': (
                'error_message',
            ),
            'classes': ('collapse',)
        })
    )
    
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    def batch_hash_short(self, obj):
        """Display short version of batch hash."""
        if obj.batch_hash:
            return f"{obj.batch_hash[:8]}...{obj.batch_hash[-8:]}"
        return '-'
    batch_hash_short.short_description = 'Batch Hash'
    
    def blockchain_hash_short(self, obj):
        """Display short version of blockchain hash."""
        if obj.blockchain_hash:
            return f"{obj.blockchain_hash[:8]}...{obj.blockchain_hash[-8:]}"
        return '-'
    blockchain_hash_short.short_description = 'Blockchain Hash'
    
    def transaction_list(self, obj):
        """Display list of transactions in the batch."""
        transactions = obj.transactions.all()
        if transactions:
            links = []
            for tx in transactions:
                url = reverse('admin:ledger_ledgertransaction_change', args=[tx.id])
                links.append(
                    f'<a href="{url}">{tx.transaction_type} - {tx.source_id}</a>'
                )
            return format_html('<br>'.join(links))
        return '-'
    transaction_list.short_description = 'Transactions'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related and prefetch_related."""
        return super().get_queryset(request).select_related(
            'organization'
        ).prefetch_related(
            'transactions'
        )
    
    actions = ['submit_to_blockchain']
    
    def submit_to_blockchain(self, request, queryset):
        """Submit selected batches to blockchain."""
        from .services import TransactionService
        
        submitted_count = 0
        failed_count = 0
        
        for batch in queryset.filter(status='pending'):
            try:
                service = TransactionService(
                    organization_id=str(batch.organization.id)
                )
                if service.submit_batch(batch):
                    submitted_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                failed_count += 1
        
        self.message_user(
            request,
            f"Submitted {submitted_count} batches, {failed_count} failed."
        )
    submit_to_blockchain.short_description = "Submit to blockchain"


@admin.register(LedgerConfiguration)
class LedgerConfigurationAdmin(admin.ModelAdmin):
    """Admin interface for LedgerConfiguration model."""
    
    list_display = [
        'organization',
        'blockchain_network',
        'rpc_endpoint_short',
        'contract_address_short',
        'is_active',
        'batch_size',
        'created_at'
    ]
    
    list_filter = [
        'blockchain_network',
        'is_active',
        'auto_confirm',
        'created_at'
    ]
    
    search_fields = [
        'organization__name',
        'rpc_endpoint',
        'contract_address'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'connection_test'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'organization',
                'blockchain_network',
                'is_active'
            )
        }),
        ('Blockchain Connection', {
            'fields': (
                'rpc_endpoint',
                'contract_address',
                'connection_test'
            )
        }),
        ('Security', {
            'fields': (
                'private_key',
            ),
            'classes': ('collapse',)
        }),
        ('Configuration', {
            'fields': (
                'batch_size',
                'batch_timeout',
                'retry_attempts',
                'gas_limit',
                'gas_price',
                'auto_confirm'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            )
        })
    )
    
    ordering = ['-created_at']
    
    def rpc_endpoint_short(self, obj):
        """Display short version of RPC endpoint."""
        if obj.rpc_endpoint:
            return obj.rpc_endpoint[:50] + '...' if len(obj.rpc_endpoint) > 50 else obj.rpc_endpoint
        return '-'
    rpc_endpoint_short.short_description = 'RPC Endpoint'
    
    def contract_address_short(self, obj):
        """Display short version of contract address."""
        if obj.contract_address:
            return f"{obj.contract_address[:8]}...{obj.contract_address[-8:]}"
        return '-'
    contract_address_short.short_description = 'Contract Address'
    
    def connection_test(self, obj):
        """Display connection test button."""
        if obj.id:
            return format_html(
                '<a href="{}" class="button">Test Connection</a>',
                reverse('admin:ledger_ledgerconfiguration_test_connection', args=[obj.id])
            )
        return '-'
    connection_test.short_description = 'Connection Test'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('organization')
    
    def save_model(self, request, obj, form, change):
        """Save model with additional validation."""
        # Ensure only one configuration per organization
        if not change:  # Creating new configuration
            if LedgerConfiguration.objects.filter(organization=obj.organization).exists():
                from django.core.exceptions import ValidationError
                raise ValidationError("Configuration already exists for this organization")
        
        super().save_model(request, obj, form, change)


# Customize admin site
admin.site.site_header = "TidyGen ERP - Smart Contract Ledger"
admin.site.site_title = "Ledger Admin"
admin.site.index_title = "Smart Contract Ledger Administration"
