"""
Admin configuration for contractor_payments app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    PaymentMethod, ContractorPayment, EscrowAccount,
    PaymentSchedule, DisputeResolution
)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'payment_type', 'is_active', 'processing_fee_percentage',
        'min_payment_amount', 'max_payment_amount', 'web3_enabled'
    ]
    list_filter = ['payment_type', 'is_active', 'web3_enabled', 'requires_kyc']
    search_fields = ['name', 'payment_type']
    readonly_fields = ['created', 'modified']


@admin.register(ContractorPayment)
class ContractorPaymentAdmin(admin.ModelAdmin):
    list_display = [
        'payment_id', 'freelancer_name', 'amount_display', 'status',
        'payment_method', 'created_date', 'processed_date'
    ]
    list_filter = [
        'status', 'payment_trigger', 'payment_method', 'currency',
        'created', 'processed_date'
    ]
    search_fields = [
        'payment_id', 'freelancer__first_name', 'freelancer__last_name',
        'transaction_reference', 'processor_transaction_id'
    ]
    readonly_fields = ['payment_id', 'created', 'modified']
    
    fieldsets = (
        ('Payment Information', {
            'fields': (
                'payment_id', 'transaction_reference', 'freelancer', 'job', 'milestone',
                'amount', 'currency', 'processing_fee', 'net_amount'
            )
        }),
        ('Payment Method & Status', {
            'fields': (
                'payment_method', 'status', 'payment_trigger', 'failure_reason',
                'retry_count', 'max_retries'
            )
        }),
        ('Timing', {
            'fields': (
                'scheduled_date', 'processed_date'
            )
        }),
        ('Bank Details', {
            'fields': (
                'bank_account_number', 'bank_routing_number', 'bank_name', 'account_holder_name'
            ),
            'classes': ('collapse',)
        }),
        ('Crypto Details', {
            'fields': (
                'wallet_address', 'crypto_currency', 'blockchain_network'
            ),
            'classes': ('collapse',)
        }),
        ('Web3 Integration', {
            'fields': (
                'smart_contract_address', 'blockchain_transaction_hash', 'gas_fee'
            ),
            'classes': ('collapse',)
        }),
        ('Processor Details', {
            'fields': (
                'processor_transaction_id', 'processor_response'
            ),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': (
                'notes', 'created_by', 'approved_by', 'created', 'modified'
            )
        }),
    )
    
    def freelancer_name(self, obj):
        return obj.freelancer.full_name
    freelancer_name.short_description = 'Freelancer'
    
    def amount_display(self, obj):
        return f"{obj.amount} {obj.currency}"
    amount_display.short_description = 'Amount'
    
    def created_date(self, obj):
        return obj.created.strftime('%Y-%m-%d')
    created_date.short_description = 'Created'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'freelancer', 'payment_method', 'job', 'created_by'
        )


@admin.register(EscrowAccount)
class EscrowAccountAdmin(admin.ModelAdmin):
    list_display = [
        'escrow_id', 'job_title', 'client_name', 'freelancer_name',
        'total_amount_display', 'status', 'funded_date', 'release_date'
    ]
    list_filter = [
        'status', 'currency', 'requires_client_approval', 'created',
        'funded_date', 'release_date'
    ]
    search_fields = [
        'escrow_id', 'job__title', 'client__first_name', 'client__last_name',
        'freelancer__first_name', 'freelancer__last_name', 'smart_contract_address'
    ]
    readonly_fields = ['escrow_id', 'created', 'modified']
    
    fieldsets = (
        ('Escrow Information', {
            'fields': (
                'escrow_id', 'job', 'client', 'freelancer', 'status'
            )
        }),
        ('Financial Details', {
            'fields': (
                'total_amount', 'currency', 'platform_fee', 'net_amount'
            )
        }),
        ('Timeline', {
            'fields': (
                'funded_date', 'release_date', 'release_trigger'
            )
        }),
        ('Release Conditions', {
            'fields': (
                'auto_release_hours', 'requires_client_approval', 'requires_freelancer_confirmation'
            )
        }),
        ('Web3 Integration', {
            'fields': (
                'smart_contract_address', 'blockchain_transaction_hash', 'contract_deployed_at'
            ),
            'classes': ('collapse',)
        }),
        ('Traditional Escrow', {
            'fields': (
                'escrow_provider', 'escrow_account_number'
            ),
            'classes': ('collapse',)
        }),
        ('Dispute Information', {
            'fields': (
                'dispute_reason', 'dispute_raised_by', 'dispute_raised_at'
            ),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': (
                'created', 'modified'
            )
        }),
    )
    
    def job_title(self, obj):
        return obj.job.title if obj.job else 'N/A'
    job_title.short_description = 'Job'
    
    def client_name(self, obj):
        return obj.client.get_full_name()
    client_name.short_description = 'Client'
    
    def freelancer_name(self, obj):
        return obj.freelancer.full_name
    freelancer_name.short_description = 'Freelancer'
    
    def total_amount_display(self, obj):
        return f"{obj.total_amount} {obj.currency}"
    total_amount_display.short_description = 'Amount'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'job', 'client', 'freelancer'
        )


@admin.register(PaymentSchedule)
class PaymentScheduleAdmin(admin.ModelAdmin):
    list_display = [
        'freelancer_name', 'schedule_type', 'is_active', 'next_payment_date',
        'fixed_amount_display', 'currency', 'accumulated_amount_display'
    ]
    list_filter = [
        'schedule_type', 'is_active', 'currency', 'created'
    ]
    search_fields = [
        'freelancer__first_name', 'freelancer__last_name'
    ]
    readonly_fields = ['created', 'modified']
    
    def freelancer_name(self, obj):
        return obj.freelancer.full_name
    freelancer_name.short_description = 'Freelancer'
    
    def fixed_amount_display(self, obj):
        return f"{obj.fixed_amount} {obj.currency}" if obj.fixed_amount else 'Variable'
    fixed_amount_display.short_description = 'Fixed Amount'
    
    def accumulated_amount_display(self, obj):
        return f"{obj.accumulated_amount} {obj.currency}"
    accumulated_amount_display.short_description = 'Accumulated'


@admin.register(DisputeResolution)
class DisputeResolutionAdmin(admin.ModelAdmin):
    list_display = [
        'payment_payment_id', 'dispute_type', 'raised_by_name', 'status',
        'created_date', 'resolved_at_date', 'resolution_amount_display'
    ]
    list_filter = [
        'dispute_type', 'status', 'created', 'resolved_at'
    ]
    search_fields = [
        'payment__payment_id', 'raised_by__first_name', 'raised_by__last_name',
        'description'
    ]
    readonly_fields = ['created', 'modified']
    
    def payment_payment_id(self, obj):
        return obj.payment.payment_id
    payment_payment_id.short_description = 'Payment ID'
    
    def raised_by_name(self, obj):
        return obj.raised_by.get_full_name()
    raised_by_name.short_description = 'Raised By'
    
    def created_date(self, obj):
        return obj.created.strftime('%Y-%m-%d')
    created_date.short_description = 'Created'
    
    def resolved_at_date(self, obj):
        return obj.resolved_at.strftime('%Y-%m-%d') if obj.resolved_at else '-'
    resolved_at_date.short_description = 'Resolved'
    
    def resolution_amount_display(self, obj):
        return f"{obj.resolution_amount} {obj.payment.currency}" if obj.resolution_amount else '-'
    resolution_amount_display.short_description = 'Resolution Amount'
