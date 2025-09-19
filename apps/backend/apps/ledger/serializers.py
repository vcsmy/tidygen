"""
Smart Contract Ledger Serializers

This module defines the serializers for the Smart Contract Ledger API,
providing data validation and transformation for blockchain transaction operations.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import LedgerTransaction, LedgerEvent, LedgerBatch, LedgerConfiguration

User = get_user_model()


class LedgerTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for LedgerTransaction model.
    
    Handles serialization and validation of ledger transactions,
    including hash generation and status management.
    """
    
    hash = serializers.CharField(read_only=True)
    blockchain_hash = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    submitted_at = serializers.DateTimeField(read_only=True)
    confirmed_at = serializers.DateTimeField(read_only=True)
    failed_at = serializers.DateTimeField(read_only=True)
    retry_count = serializers.IntegerField(read_only=True)
    gas_used = serializers.IntegerField(read_only=True)
    gas_price = serializers.IntegerField(read_only=True)
    block_number = serializers.IntegerField(read_only=True)
    transaction_index = serializers.IntegerField(read_only=True)
    
    # Computed fields
    is_confirmed = serializers.BooleanField(read_only=True)
    is_pending = serializers.BooleanField(read_only=True)
    is_failed = serializers.BooleanField(read_only=True)
    can_retry = serializers.BooleanField(read_only=True)
    
    # Related fields
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = LedgerTransaction
        fields = [
            'id',
            'transaction_type',
            'source_module',
            'source_id',
            'transaction_data',
            'hash',
            'blockchain_hash',
            'status',
            'organization',
            'organization_name',
            'created_by',
            'created_by_username',
            'created_at',
            'submitted_at',
            'confirmed_at',
            'failed_at',
            'error_message',
            'retry_count',
            'gas_used',
            'gas_price',
            'block_number',
            'transaction_index',
            'is_confirmed',
            'is_pending',
            'is_failed',
            'can_retry',
        ]
        read_only_fields = [
            'id', 'hash', 'blockchain_hash', 'status', 'created_at',
            'submitted_at', 'confirmed_at', 'failed_at', 'retry_count',
            'gas_used', 'gas_price', 'block_number', 'transaction_index',
            'is_confirmed', 'is_pending', 'is_failed', 'can_retry'
        ]
    
    def validate_transaction_data(self, value):
        """Validate transaction data structure."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Transaction data must be a dictionary")
        
        # Check required fields
        required_fields = ['amount', 'currency', 'description']
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"Transaction data must contain '{field}' field")
        
        # Validate amount
        amount = value.get('amount')
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise serializers.ValidationError("Amount must be a positive number")
        
        # Validate currency
        currency = value.get('currency')
        if not isinstance(currency, str) or len(currency) != 3:
            raise serializers.ValidationError("Currency must be a 3-character string")
        
        return value
    
    def validate_source_id(self, value):
        """Validate source ID format."""
        if not value or not isinstance(value, str):
            raise serializers.ValidationError("Source ID must be a non-empty string")
        
        if len(value) > 100:
            raise serializers.ValidationError("Source ID must be 100 characters or less")
        
        return value
    
    def create(self, validated_data):
        """Create a new ledger transaction."""
        # Set organization from context if not provided
        if 'organization' not in validated_data:
            request = self.context.get('request')
            if request and hasattr(request, 'user') and request.user.is_authenticated:
                validated_data['organization'] = request.user.organization
        
        # Set created_by from context
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        
        return super().create(validated_data)


class LedgerTransactionCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for creating ledger transactions.
    
    This serializer is used specifically for the /api/ledger/push endpoint
    and focuses on the essential fields needed for transaction creation.
    """
    
    class Meta:
        model = LedgerTransaction
        fields = [
            'transaction_type',
            'source_module',
            'source_id',
            'transaction_data',
        ]
    
    def validate_transaction_data(self, value):
        """Validate transaction data structure."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Transaction data must be a dictionary")
        
        # Check required fields
        required_fields = ['amount', 'currency', 'description']
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"Transaction data must contain '{field}' field")
        
        return value


class LedgerTransactionUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating ledger transaction status.
    
    This serializer is used for updating transaction status and blockchain data.
    """
    
    class Meta:
        model = LedgerTransaction
        fields = [
            'status',
            'blockchain_hash',
            'error_message',
            'gas_used',
            'gas_price',
            'block_number',
            'transaction_index',
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_status(self, value):
        """Validate status transitions."""
        instance = self.instance
        if instance:
            valid_transitions = {
                'pending': ['submitted', 'failed'],
                'submitted': ['confirmed', 'failed'],
                'confirmed': [],  # Final state
                'failed': ['pending'],  # Can retry
                'rejected': [],  # Final state
            }
            
            current_status = instance.status
            if value not in valid_transitions.get(current_status, []):
                raise serializers.ValidationError(
                    f"Invalid status transition from '{current_status}' to '{value}'"
                )
        
        return value


class LedgerEventSerializer(serializers.ModelSerializer):
    """
    Serializer for LedgerEvent model.
    
    Handles serialization of ledger events for audit trail purposes.
    """
    
    transaction_source_id = serializers.CharField(source='transaction.source_id', read_only=True)
    transaction_type = serializers.CharField(source='transaction.transaction_type', read_only=True)
    
    class Meta:
        model = LedgerEvent
        fields = [
            'id',
            'transaction',
            'transaction_source_id',
            'transaction_type',
            'event_type',
            'event_data',
            'blockchain_event_id',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class LedgerBatchSerializer(serializers.ModelSerializer):
    """
    Serializer for LedgerBatch model.
    
    Handles serialization of transaction batches for efficient blockchain operations.
    """
    
    transaction_count = serializers.IntegerField(read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    is_confirmed = serializers.BooleanField(read_only=True)
    is_failed = serializers.BooleanField(read_only=True)
    
    # Nested transaction data
    transactions = LedgerTransactionSerializer(many=True, read_only=True)
    
    class Meta:
        model = LedgerBatch
        fields = [
            'id',
            'batch_hash',
            'transactions',
            'transaction_count',
            'status',
            'blockchain_hash',
            'organization',
            'organization_name',
            'created_at',
            'submitted_at',
            'confirmed_at',
            'failed_at',
            'error_message',
            'gas_used',
            'block_number',
            'is_confirmed',
            'is_failed',
        ]
        read_only_fields = [
            'id', 'batch_hash', 'status', 'blockchain_hash',
            'created_at', 'submitted_at', 'confirmed_at',
            'failed_at', 'gas_used', 'block_number',
            'transaction_count', 'is_confirmed', 'is_failed'
        ]


class LedgerBatchCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating ledger batches.
    
    This serializer is used for creating new batches of transactions.
    """
    
    transaction_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        help_text="List of transaction IDs to include in the batch"
    )
    
    class Meta:
        model = LedgerBatch
        fields = [
            'transaction_ids',
        ]
    
    def validate_transaction_ids(self, value):
        """Validate transaction IDs."""
        if not value:
            raise serializers.ValidationError("At least one transaction ID is required")
        
        # Check if transactions exist and belong to the same organization
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            organization = request.user.organization
            
            from .models import LedgerTransaction
            transactions = LedgerTransaction.objects.filter(
                id__in=value,
                organization=organization,
                status='pending'
            )
            
            if transactions.count() != len(value):
                raise serializers.ValidationError(
                    "Some transactions not found or not in pending status"
                )
        
        return value
    
    def create(self, validated_data):
        """Create a new ledger batch."""
        transaction_ids = validated_data.pop('transaction_ids')
        
        # Set organization from context
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['organization'] = request.user.organization
        
        # Create batch
        batch = super().create(validated_data)
        
        # Add transactions to batch
        from .models import LedgerTransaction
        transactions = LedgerTransaction.objects.filter(id__in=transaction_ids)
        batch.transactions.set(transactions)
        
        return batch


class LedgerConfigurationSerializer(serializers.ModelSerializer):
    """
    Serializer for LedgerConfiguration model.
    
    Handles serialization of ledger configuration settings.
    """
    
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = LedgerConfiguration
        fields = [
            'id',
            'organization',
            'organization_name',
            'blockchain_network',
            'rpc_endpoint',
            'contract_address',
            'batch_size',
            'batch_timeout',
            'retry_attempts',
            'gas_limit',
            'gas_price',
            'auto_confirm',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'private_key': {'write_only': True},  # Never expose private key
        }
    
    def validate_batch_size(self, value):
        """Validate batch size."""
        if value <= 0:
            raise serializers.ValidationError("Batch size must be greater than 0")
        if value > 100:
            raise serializers.ValidationError("Batch size cannot exceed 100")
        return value
    
    def validate_batch_timeout(self, value):
        """Validate batch timeout."""
        if value <= 0:
            raise serializers.ValidationError("Batch timeout must be greater than 0")
        if value > 3600:  # 1 hour
            raise serializers.ValidationError("Batch timeout cannot exceed 3600 seconds")
        return value
    
    def validate_retry_attempts(self, value):
        """Validate retry attempts."""
        if value <= 0:
            raise serializers.ValidationError("Retry attempts must be greater than 0")
        if value > 10:
            raise serializers.ValidationError("Retry attempts cannot exceed 10")
        return value


class LedgerTransactionVerifySerializer(serializers.Serializer):
    """
    Serializer for transaction verification requests.
    
    This serializer is used for the /api/ledger/verify/{id}/ endpoint
    to verify transactions on the blockchain.
    """
    
    transaction_id = serializers.UUIDField()
    verify_hash = serializers.BooleanField(default=True)
    verify_blockchain = serializers.BooleanField(default=True)
    
    def validate_transaction_id(self, value):
        """Validate transaction ID exists."""
        from .models import LedgerTransaction
        try:
            LedgerTransaction.objects.get(id=value)
        except LedgerTransaction.DoesNotExist:
            raise serializers.ValidationError("Transaction not found")
        return value


class LedgerTransactionVerifyResponseSerializer(serializers.Serializer):
    """
    Serializer for transaction verification responses.
    
    This serializer is used to return verification results.
    """
    
    transaction_id = serializers.UUIDField()
    hash_valid = serializers.BooleanField()
    blockchain_confirmed = serializers.BooleanField()
    blockchain_hash = serializers.CharField(allow_null=True)
    block_number = serializers.IntegerField(allow_null=True)
    verification_timestamp = serializers.DateTimeField()
    error_message = serializers.CharField(allow_null=True)


class LedgerAuditTrailSerializer(serializers.Serializer):
    """
    Serializer for audit trail requests.
    
    This serializer is used for the /api/ledger/audit/ endpoint
    to retrieve audit trail information.
    """
    
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    transaction_type = serializers.ChoiceField(
        choices=LedgerTransaction.TRANSACTION_TYPES,
        required=False
    )
    status = serializers.ChoiceField(
        choices=LedgerTransaction.STATUS_CHOICES,
        required=False
    )
    source_module = serializers.CharField(required=False)
    limit = serializers.IntegerField(default=100, min_value=1, max_value=1000)
    offset = serializers.IntegerField(default=0, min_value=0)


class LedgerAuditTrailResponseSerializer(serializers.Serializer):
    """
    Serializer for audit trail responses.
    
    This serializer is used to return audit trail data.
    """
    
    transactions = LedgerTransactionSerializer(many=True)
    total_count = serializers.IntegerField()
    has_next = serializers.BooleanField()
    has_previous = serializers.BooleanField()
    next_offset = serializers.IntegerField(allow_null=True)
    previous_offset = serializers.IntegerField(allow_null=True)


class LedgerStatsSerializer(serializers.Serializer):
    """
    Serializer for ledger statistics.
    
    This serializer is used to return ledger statistics and metrics.
    """
    
    total_transactions = serializers.IntegerField()
    pending_transactions = serializers.IntegerField()
    confirmed_transactions = serializers.IntegerField()
    failed_transactions = serializers.IntegerField()
    total_batches = serializers.IntegerField()
    successful_batches = serializers.IntegerField()
    failed_batches = serializers.IntegerField()
    total_gas_used = serializers.IntegerField()
    average_confirmation_time = serializers.DurationField(allow_null=True)
    last_updated = serializers.DateTimeField()
