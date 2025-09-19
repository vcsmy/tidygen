"""
Wallet Serializers

This module defines Django REST Framework serializers for wallet-related models,
providing data validation and transformation for API endpoints.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Wallet, WalletSignature, WalletPermission, WalletSession
from .services import WalletService

User = get_user_model()


class WalletSerializer(serializers.ModelSerializer):
    """
    Serializer for Wallet model.
    
    Provides serialization and validation for wallet data,
    including address validation and metadata handling.
    """
    
    short_address = serializers.ReadOnlyField()
    display_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Wallet
        fields = [
            'id',
            'address',
            'short_address',
            'display_name',
            'wallet_type',
            'chain_type',
            'chain_id',
            'network_name',
            'is_primary',
            'is_verified',
            'is_active',
            'public_key',
            'metadata',
            'created_at',
            'last_used',
            'verified_at'
        ]
        read_only_fields = [
            'id',
            'short_address',
            'display_name',
            'is_verified',
            'created_at',
            'last_used',
            'verified_at'
        ]
    
    def validate_address(self, value):
        """Validate wallet address format."""
        wallet_type = self.initial_data.get('wallet_type')
        
        if wallet_type == 'metamask':
            if not value.startswith('0x') or len(value) != 42:
                raise serializers.ValidationError("Invalid Ethereum address format")
        elif wallet_type == 'polkadot':
            if not value or len(value) < 40:
                raise serializers.ValidationError("Invalid Substrate address format")
        
        return value
    
    def validate_wallet_type(self, value):
        """Validate wallet type."""
        supported_types = ['metamask', 'polkadot', 'walletconnect', 'other']
        if value not in supported_types:
            raise serializers.ValidationError(f"Unsupported wallet type: {value}")
        return value
    
    def validate_chain_type(self, value):
        """Validate chain type."""
        supported_chains = ['ethereum', 'polygon', 'bsc', 'substrate', 'polkadot', 'kusama', 'other']
        if value not in supported_chains:
            raise serializers.ValidationError(f"Unsupported chain type: {value}")
        return value


class WalletCreateSerializer(serializers.Serializer):
    """
    Serializer for creating new wallets.
    
    Handles wallet connection and initial setup.
    """
    
    wallet_type = serializers.ChoiceField(choices=Wallet.WALLET_TYPES)
    address = serializers.CharField(max_length=100)
    chain_id = serializers.CharField(max_length=50)
    network_name = serializers.CharField(max_length=100)
    public_key = serializers.CharField(required=False, allow_blank=True)
    metadata = serializers.JSONField(required=False, default=dict)
    
    def validate_address(self, value):
        """Validate wallet address based on type."""
        wallet_type = self.initial_data.get('wallet_type')
        
        if wallet_type == 'metamask':
            if not value.startswith('0x') or len(value) != 42:
                raise serializers.ValidationError("Invalid Ethereum address format")
        elif wallet_type == 'polkadot':
            if not value or len(value) < 40:
                raise serializers.ValidationError("Invalid Substrate address format")
        
        return value
    
    def create(self, validated_data):
        """Create wallet using WalletService."""
        wallet_service = WalletService()
        
        result = wallet_service.connect_wallet(
            wallet_type=validated_data['wallet_type'],
            address=validated_data['address'],
            chain_id=validated_data['chain_id'],
            network_name=validated_data['network_name'],
            public_key=validated_data.get('public_key'),
            metadata=validated_data.get('metadata', {})
        )
        
        if 'error' in result:
            raise serializers.ValidationError(result['error'])
        
        # Return the created wallet
        wallet = Wallet.objects.get(id=result['wallet_id'])
        return wallet


class WalletSignatureSerializer(serializers.ModelSerializer):
    """
    Serializer for WalletSignature model.
    
    Provides serialization for signature requests and verification.
    """
    
    is_expired = serializers.ReadOnlyField()
    is_valid = serializers.ReadOnlyField()
    wallet_address = serializers.CharField(source='wallet.address', read_only=True)
    wallet_type = serializers.CharField(source='wallet.wallet_type', read_only=True)
    
    class Meta:
        model = WalletSignature
        fields = [
            'id',
            'wallet',
            'wallet_address',
            'wallet_type',
            'signature_type',
            'message',
            'signature',
            'nonce',
            'status',
            'verified',
            'is_expired',
            'is_valid',
            'created_at',
            'signed_at',
            'verified_at',
            'expires_at',
            'ip_address',
            'user_agent',
            'metadata'
        ]
        read_only_fields = [
            'id',
            'wallet_address',
            'wallet_type',
            'signature',
            'status',
            'verified',
            'is_expired',
            'is_valid',
            'created_at',
            'signed_at',
            'verified_at',
            'ip_address',
            'user_agent'
        ]


class WalletSignatureRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting wallet signatures.
    
    Handles signature request creation and validation.
    """
    
    wallet_id = serializers.UUIDField()
    signature_type = serializers.ChoiceField(choices=WalletSignature.SIGNATURE_TYPES)
    user_id = serializers.UUIDField(required=False)
    
    def validate_wallet_id(self, value):
        """Validate wallet exists and is active."""
        try:
            wallet = Wallet.objects.get(id=value, is_active=True)
            return value
        except Wallet.DoesNotExist:
            raise serializers.ValidationError("Wallet not found or inactive")
    
    def create(self, validated_data):
        """Create signature request using WalletService."""
        wallet_service = WalletService()
        
        if validated_data['signature_type'] == 'authentication':
            result = wallet_service.request_authentication(
                wallet_id=str(validated_data['wallet_id']),
                user_id=str(validated_data.get('user_id')) if validated_data.get('user_id') else None,
                ip_address=self.context.get('request').META.get('REMOTE_ADDR'),
                user_agent=self.context.get('request').META.get('HTTP_USER_AGENT')
            )
        else:
            raise serializers.ValidationError(f"Unsupported signature type: {validated_data['signature_type']}")
        
        if 'error' in result:
            raise serializers.ValidationError(result['error'])
        
        return result


class WalletSignatureVerifySerializer(serializers.Serializer):
    """
    Serializer for verifying wallet signatures.
    
    Handles signature verification and authentication.
    """
    
    signature_id = serializers.UUIDField()
    signature = serializers.CharField()
    user_id = serializers.UUIDField(required=False)
    
    def validate_signature_id(self, value):
        """Validate signature request exists."""
        try:
            signature_request = WalletSignature.objects.get(id=value)
            if signature_request.is_expired:
                raise serializers.ValidationError("Signature request has expired")
            return value
        except WalletSignature.DoesNotExist:
            raise serializers.ValidationError("Signature request not found")
    
    def validate_signature(self, value):
        """Validate signature format."""
        if not value or len(value) < 10:
            raise serializers.ValidationError("Invalid signature format")
        return value
    
    def create(self, validated_data):
        """Verify signature using WalletService."""
        wallet_service = WalletService()
        
        result = wallet_service.verify_authentication(
            signature_id=str(validated_data['signature_id']),
            signature=validated_data['signature'],
            user_id=str(validated_data.get('user_id')) if validated_data.get('user_id') else None
        )
        
        if 'error' in result:
            raise serializers.ValidationError(result['error'])
        
        return result


class WalletPermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for WalletPermission model.
    
    Provides serialization for wallet permissions and access control.
    """
    
    is_expired = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    wallet_address = serializers.CharField(source='wallet.address', read_only=True)
    granted_by_username = serializers.CharField(source='granted_by.username', read_only=True)
    
    class Meta:
        model = WalletPermission
        fields = [
            'id',
            'wallet',
            'wallet_address',
            'permission_type',
            'resource_type',
            'resource_id',
            'granted',
            'is_expired',
            'is_active',
            'reason',
            'expires_at',
            'granted_by',
            'granted_by_username',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'wallet_address',
            'is_expired',
            'is_active',
            'granted_by_username',
            'created_at',
            'updated_at'
        ]
    
    def validate_permission_type(self, value):
        """Validate permission type."""
        supported_types = ['read', 'write', 'delete', 'admin', 'sign', 'approve']
        if value not in supported_types:
            raise serializers.ValidationError(f"Unsupported permission type: {value}")
        return value
    
    def validate_resource_type(self, value):
        """Validate resource type."""
        supported_types = ['invoice', 'payment', 'expense', 'user', 'organization', 'ledger', 'wallet', 'all']
        if value not in supported_types:
            raise serializers.ValidationError(f"Unsupported resource type: {value}")
        return value


class WalletSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for WalletSession model.
    
    Provides serialization for wallet authentication sessions.
    """
    
    is_expired = serializers.ReadOnlyField()
    is_valid = serializers.ReadOnlyField()
    wallet_address = serializers.CharField(source='wallet.address', read_only=True)
    wallet_type = serializers.CharField(source='wallet.wallet_type', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = WalletSession
        fields = [
            'id',
            'wallet',
            'wallet_address',
            'wallet_type',
            'user',
            'username',
            'session_key',
            'is_active',
            'is_expired',
            'is_valid',
            'ip_address',
            'user_agent',
            'created_at',
            'last_activity',
            'expires_at'
        ]
        read_only_fields = [
            'id',
            'wallet_address',
            'wallet_type',
            'username',
            'session_key',
            'is_expired',
            'is_valid',
            'created_at',
            'last_activity'
        ]


class WalletConnectSerializer(serializers.Serializer):
    """
    Serializer for wallet connection requests.
    
    Handles the initial wallet connection process.
    """
    
    wallet_type = serializers.ChoiceField(choices=Wallet.WALLET_TYPES)
    address = serializers.CharField(max_length=100)
    chain_id = serializers.CharField(max_length=50)
    network_name = serializers.CharField(max_length=100)
    public_key = serializers.CharField(required=False, allow_blank=True)
    metadata = serializers.JSONField(required=False, default=dict)
    
    def validate_address(self, value):
        """Validate wallet address format."""
        wallet_type = self.initial_data.get('wallet_type')
        
        if wallet_type == 'metamask':
            if not value.startswith('0x') or len(value) != 42:
                raise serializers.ValidationError("Invalid Ethereum address format")
        elif wallet_type == 'polkadot':
            if not value or len(value) < 40:
                raise serializers.ValidationError("Invalid Substrate address format")
        
        return value


class WalletDisconnectSerializer(serializers.Serializer):
    """
    Serializer for wallet disconnection requests.
    
    Handles wallet disconnection and cleanup.
    """
    
    wallet_id = serializers.UUIDField()
    
    def validate_wallet_id(self, value):
        """Validate wallet exists and belongs to user."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required")
        
        try:
            wallet = Wallet.objects.get(id=value, user=request.user)
            return value
        except Wallet.DoesNotExist:
            raise serializers.ValidationError("Wallet not found or access denied")


class TransactionSignatureRequestSerializer(serializers.Serializer):
    """
    Serializer for transaction signature requests.
    
    Handles requests for signing transactions with wallet.
    """
    
    wallet_id = serializers.UUIDField()
    transaction_type = serializers.CharField(max_length=50)
    amount = serializers.DecimalField(max_digits=20, decimal_places=8)
    currency = serializers.CharField(max_length=10)
    description = serializers.CharField(max_length=500)
    recipient = serializers.CharField(max_length=100, required=False)
    metadata = serializers.JSONField(required=False, default=dict)
    
    def validate_wallet_id(self, value):
        """Validate wallet exists and is verified."""
        try:
            wallet = Wallet.objects.get(id=value, is_active=True, is_verified=True)
            return value
        except Wallet.DoesNotExist:
            raise serializers.ValidationError("Wallet not found, inactive, or unverified")
    
    def validate_amount(self, value):
        """Validate transaction amount."""
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value


class WalletStatusSerializer(serializers.Serializer):
    """
    Serializer for wallet connection status.
    
    Provides information about wallet connection and network status.
    """
    
    connected = serializers.BooleanField()
    wallet_type = serializers.CharField()
    address = serializers.CharField()
    network_name = serializers.CharField()
    chain_id = serializers.CharField()
    balance = serializers.JSONField(required=False)
    is_verified = serializers.BooleanField()
    last_used = serializers.DateTimeField()


class SupportedWalletsSerializer(serializers.Serializer):
    """
    Serializer for supported wallet types.
    
    Provides information about available wallet integrations.
    """
    
    type = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    supported_chains = serializers.ListField(child=serializers.CharField())
    icon = serializers.CharField()
    enabled = serializers.BooleanField()
