"""
Serializers for contractor_payments app API.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    PaymentMethod, ContractorPayment, EscrowAccount,
    PaymentSchedule, DisputeResolution
)

User = get_user_model()


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for payment methods."""
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'name', 'payment_type', 'payment_type_display', 'is_active',
            'processing_fee_percentage', 'min_payment_amount', 'max_payment_amount',
            'supported_currencies', 'requires_kyc', 'settlement_time_hours',
            'web3_enabled', 'created', 'modified'
        ]


class ContractorPaymentListSerializer(serializers.ModelSerializer):
    """Serializer for contractor payment list view."""
    freelancer_name = serializers.CharField(source='freelancer.full_name', read_only=True)
    payment_method_name = serializers.CharField(source='payment_method.name', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    amount_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ContractorPayment
        fields = [
            'id', 'payment_id', 'freelancer', 'freelancer_name', 'job', 'job_title',
            'amount', 'amount_display', 'currency', 'status', 'status_display',
            'payment_method', 'payment_method_name', 'payment_trigger',
            'scheduled_date', 'processed_date', 'created', 'modified'
        ]
    
    def get_amount_display(self, obj):
        return f"{obj.amount} {obj.currency}"


class ContractorPaymentDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed contractor payment view."""
    freelancer_name = serializers.CharField(source='freelancer.full_name', read_only=True)
    payment_method = PaymentMethodSerializer(read_only=True)
    payment_method_id = serializers.IntegerField(write_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = ContractorPayment
        fields = [
            'id', 'payment_id', 'transaction_reference', 'freelancer', 'freelancer_name',
            'job', 'job_title', 'milestone', 'payment_method', 'payment_method_id',
            'amount', 'currency', 'processing_fee', 'net_amount', 'payment_trigger',
            'scheduled_date', 'processed_date', 'status', 'failure_reason',
            'retry_count', 'max_retries', 'bank_account_number', 'bank_routing_number',
            'bank_name', 'account_holder_name', 'wallet_address', 'crypto_currency',
            'blockchain_network', 'processor_transaction_id', 'smart_contract_address',
            'blockchain_transaction_hash', 'gas_fee', 'notes', 'created_by',
            'created_by_name', 'approved_by', 'approved_by_name', 'created', 'modified'
        ]
        read_only_fields = [
            'id', 'payment_id', 'created', 'modified', 'net_amount', 'processed_date'
        ]


class EscrowAccountSerializer(serializers.ModelSerializer):
    """Serializer for escrow accounts."""
    freelancer_name = serializers.CharField(source='freelancer.full_name', read_only=True)
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_funded = serializers.ReadOnlyField()
    
    class Meta:
        model = EscrowAccount
        fields = [
            'id', 'escrow_id', 'job', 'job_title', 'client', 'client_name',
            'freelancer', 'freelancer_name', 'total_amount', 'currency',
            'platform_fee', 'net_amount', 'status', 'status_display',
            'funded_date', 'release_date', 'release_trigger', 'smart_contract_address',
            'blockchain_transaction_hash', 'contract_deployed_at', 'escrow_provider',
            'escrow_account_number', 'dispute_reason', 'auto_release_hours',
            'requires_client_approval', 'requires_freelancer_confirmation',
            'is_funded', 'created', 'modified'
        ]
        read_only_fields = ['id', 'escrow_id', 'created', 'modified']


class PaymentScheduleSerializer(serializers.ModelSerializer):
    """Serializer for payment schedules."""
    freelancer_name = serializers.CharField(source='freelancer.full_name', read_only=True)
    payment_method_name = serializers.CharField(source='payment_method.name', read_only=True)
    
    class Meta:
        model = PaymentSchedule
        fields = [
            'id', 'freelancer', 'freelancer_name', 'schedule_type',
            'is_active', 'next_payment_date', 'payment_method', 'payment_method_name',
            'fixed_amount', 'currency', 'accumulated_amount', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class DisputeResolutionSerializer(serializers.ModelSerializer):
    """Serializer for dispute resolutions."""
    payment_payment_id = serializers.CharField(source='payment.payment_id', read_only=True)
    raised_by_name = serializers.CharField(source='raised_by.get_full_name', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = DisputeResolution
        fields = [
            'id', 'payment', 'payment_payment_id', 'escrow_account', 'dispute_type',
            'description', 'raised_by', 'raised_by_name', 'status', 'status_display',
            'resolution_notes', 'resolved_by', 'resolved_by_name', 'resolved_at',
            'resolution_amount', 'resolution_type', 'created', 'modified'
        ]
        read_only_fields = ['id', 'raised_by', 'created', 'modified', 'resolved_at']
