"""
Web3 and blockchain integration serializers.
"""
from rest_framework import serializers
import hashlib
from .models import (
    Wallet, BlockchainTransaction, SmartContract, Token,
    WalletBalance, DeFiProtocol, DecentralizedIdentity, OnChainAnchor,
    SmartContractModule, DAOGovernance, GovernanceVote, TokenizedReward,
    DecentralizedStorage, BlockchainAuditLog
)


class WalletSerializer(serializers.ModelSerializer):
    """Serializer for wallet model."""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Wallet
        fields = [
            'id', 'user', 'user_name', 'address', 'wallet_type',
            'is_primary', 'is_verified', 'last_used', 'created'
        ]
        read_only_fields = ['id', 'created', 'last_used']


class WalletCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating wallets."""
    
    class Meta:
        model = Wallet
        fields = ['address', 'wallet_type', 'is_primary']
    
    def create(self, validated_data):
        """Create wallet and set as primary if specified."""
        user = self.context['request'].user
        wallet = Wallet.objects.create(user=user, **validated_data)
        
        # If this is set as primary, unset other primary wallets
        if wallet.is_primary:
            Wallet.objects.filter(user=user, is_primary=True).exclude(id=wallet.id).update(is_primary=False)
        
        return wallet


class BlockchainTransactionSerializer(serializers.ModelSerializer):
    """Serializer for blockchain transactions."""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    wallet_address = serializers.CharField(source='wallet.address', read_only=True)
    
    class Meta:
        model = BlockchainTransaction
        fields = [
            'id', 'user', 'user_name', 'wallet', 'wallet_address',
            'transaction_hash', 'transaction_type', 'status',
            'from_address', 'to_address', 'value', 'gas_used', 'gas_price',
            'block_number', 'block_hash', 'contract_address',
            'token_address', 'token_symbol', 'token_decimals',
            'description', 'metadata', 'created'
        ]
        read_only_fields = ['id', 'created']


class SmartContractSerializer(serializers.ModelSerializer):
    """Serializer for smart contracts."""
    deployer_name = serializers.CharField(source='deployer.get_full_name', read_only=True)
    
    class Meta:
        model = SmartContract
        fields = [
            'id', 'name', 'contract_type', 'address', 'abi', 'bytecode',
            'source_code', 'deployer', 'deployer_name', 'deployment_transaction',
            'deployment_block', 'is_verified', 'is_active', 'total_supply',
            'description', 'website', 'documentation', 'created'
        ]
        read_only_fields = ['id', 'created']


class TokenSerializer(serializers.ModelSerializer):
    """Serializer for tokens."""
    contract_name = serializers.CharField(source='contract.name', read_only=True)
    contract_address = serializers.CharField(source='contract.address', read_only=True)
    
    class Meta:
        model = Token
        fields = [
            'id', 'contract', 'contract_name', 'contract_address',
            'token_id', 'symbol', 'name', 'decimals', 'total_supply',
            'description', 'image_url', 'external_url', 'attributes',
            'price_usd', 'market_cap', 'created'
        ]
        read_only_fields = ['id', 'created']


class WalletBalanceSerializer(serializers.ModelSerializer):
    """Serializer for wallet balances."""
    wallet_address = serializers.CharField(source='wallet.address', read_only=True)
    token_name = serializers.CharField(source='token.name', read_only=True)
    token_symbol = serializers.CharField(source='token.symbol', read_only=True)
    token_image = serializers.URLField(source='token.image_url', read_only=True)
    
    class Meta:
        model = WalletBalance
        fields = [
            'id', 'wallet', 'wallet_address', 'token', 'token_name',
            'token_symbol', 'token_image', 'balance', 'last_updated'
        ]
        read_only_fields = ['id', 'last_updated']


class DeFiProtocolSerializer(serializers.ModelSerializer):
    """Serializer for DeFi protocols."""
    supported_tokens_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DeFiProtocol
        fields = [
            'id', 'name', 'protocol_type', 'contract_address',
            'website', 'documentation', 'is_active', 'supported_tokens',
            'supported_tokens_count', 'apy', 'description', 'risk_level',
            'created'
        ]
        read_only_fields = ['id', 'created']
    
    def get_supported_tokens_count(self, obj):
        """Get count of supported tokens."""
        return obj.supported_tokens.count()


class WalletVerificationSerializer(serializers.Serializer):
    """Serializer for wallet verification."""
    address = serializers.CharField(max_length=42)
    signature = serializers.CharField()
    message = serializers.CharField()
    
    def validate_address(self, value):
        """Validate Ethereum address format."""
        if not value.startswith('0x') or len(value) != 42:
            raise serializers.ValidationError('Invalid Ethereum address format.')
        return value.lower()


class TransactionRequestSerializer(serializers.Serializer):
    """Serializer for transaction requests."""
    to_address = serializers.CharField(max_length=42)
    value = serializers.DecimalField(max_digits=36, decimal_places=18)
    gas_limit = serializers.IntegerField(required=False)
    gas_price = serializers.IntegerField(required=False)
    data = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    
    def validate_to_address(self, value):
        """Validate Ethereum address format."""
        if not value.startswith('0x') or len(value) != 42:
            raise serializers.ValidationError('Invalid Ethereum address format.')
        return value.lower()
    
    def validate_value(self, value):
        """Validate transaction value."""
        if value < 0:
            raise serializers.ValidationError('Transaction value cannot be negative.')
        return value


class TokenTransferSerializer(serializers.Serializer):
    """Serializer for token transfers."""
    token_address = serializers.CharField(max_length=42)
    to_address = serializers.CharField(max_length=42)
    amount = serializers.DecimalField(max_digits=36, decimal_places=18)
    token_id = serializers.CharField(required=False, allow_blank=True)  # For NFTs
    
    def validate_token_address(self, value):
        """Validate Ethereum address format."""
        if not value.startswith('0x') or len(value) != 42:
            raise serializers.ValidationError('Invalid token address format.')
        return value.lower()
    
    def validate_to_address(self, value):
        """Validate Ethereum address format."""
        if not value.startswith('0x') or len(value) != 42:
            raise serializers.ValidationError('Invalid recipient address format.')
        return value.lower()
    
    def validate_amount(self, value):
        """Validate transfer amount."""
        if value <= 0:
            raise serializers.ValidationError('Transfer amount must be positive.')
        return value


class MessageSigningSerializer(serializers.Serializer):
    """Serializer for message signing requests."""
    address = serializers.CharField(max_length=42)
    
    def validate_address(self, value):
        """Validate Ethereum address format."""
        if not value.startswith('0x') or len(value) != 42:
            raise serializers.ValidationError('Invalid Ethereum address format.')
        return value.lower()


class SignatureVerificationSerializer(serializers.Serializer):
    """Serializer for signature verification."""
    address = serializers.CharField(max_length=42)
    signature = serializers.CharField()
    message = serializers.CharField()
    
    def validate_address(self, value):
        """Validate Ethereum address format."""
        if not value.startswith('0x') or len(value) != 42:
            raise serializers.ValidationError('Invalid Ethereum address format.')
        return value.lower()
    
    def validate_signature(self, value):
        """Validate signature format."""
        if not value.startswith('0x') or len(value) != 132:
            raise serializers.ValidationError('Invalid signature format.')
        return value


# ==================== CORE WEB3 SERIALIZERS ====================

class DecentralizedIdentitySerializer(serializers.ModelSerializer):
    """Serializer for Decentralized Identity."""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = DecentralizedIdentity
        fields = [
            'id', 'user', 'user_name',
            'did_identifier', 'did_method', 'status', 'did_document',
            'public_keys', 'service_endpoints', 'is_verified',
            'verification_method', 'verification_timestamp', 'metadata',
            'expires_at', 'is_expired', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']
    
    def get_is_expired(self, obj):
        """Check if DID is expired."""
        if obj.expires_at:
            from django.utils import timezone
            return timezone.now() > obj.expires_at
        return False


class OnChainAnchorSerializer(serializers.ModelSerializer):
    """Serializer for On-Chain Anchor."""
    related_invoice_number = serializers.CharField(source='related_invoice.invoice_number', read_only=True)
    related_contract_name = serializers.CharField(source='related_contract.name', read_only=True)
    related_payment_amount = serializers.DecimalField(source='related_payment.amount', max_digits=20, decimal_places=8, read_only=True)
    
    class Meta:
        model = OnChainAnchor
        fields = [
            'id', 'anchor_type', 'status',
            'data_hash', 'original_data', 'data_type', 'blockchain_network',
            'transaction_hash', 'block_number', 'block_hash', 'gas_used',
            'related_invoice', 'related_invoice_number', 'related_contract',
            'related_contract_name', 'related_payment', 'related_payment_amount',
            'description', 'metadata', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class SmartContractModuleSerializer(serializers.ModelSerializer):
    """Serializer for Smart Contract Module."""
    contract_name = serializers.CharField(source='contract.name', read_only=True)
    contract_address = serializers.CharField(source='contract.address', read_only=True)
    
    class Meta:
        model = SmartContractModule
        fields = [
            'id', 'name', 'module_type', 'status', 'contract', 
            'contract_name', 'contract_address', 'abi', 'configuration', 
            'triggers', 'conditions', 'integrated_modules', 'webhook_endpoints', 
            'description', 'version', 'documentation', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class DAOGovernanceSerializer(serializers.ModelSerializer):
    """Serializer for DAO Governance."""
    proposer_name = serializers.CharField(source='proposer.get_full_name', read_only=True)
    executed_by_name = serializers.CharField(source='executed_by.get_full_name', read_only=True)
    votes_count = serializers.SerializerMethodField()
    is_voting_active = serializers.SerializerMethodField()
    can_vote = serializers.SerializerMethodField()
    
    class Meta:
        model = DAOGovernance
        fields = [
            'id', 'governance_type', 'status', 'title', 'description', 'proposer', 
            'proposer_name', 'voting_power_required', 'voting_duration', 'voting_start', 
            'voting_end', 'votes_for', 'votes_against', 'total_votes', 'execution_data', 
            'executed_at', 'executed_by', 'executed_by_name', 'on_chain_proposal_id', 
            'transaction_hash', 'votes_count', 'is_voting_active', 'can_vote', 
            'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']
    
    def get_votes_count(self, obj):
        """Get total number of votes."""
        return obj.votes.count()
    
    def get_is_voting_active(self, obj):
        """Check if voting is currently active."""
        from django.utils import timezone
        now = timezone.now()
        return (obj.status == 'active' and 
                obj.voting_start and obj.voting_end and
                obj.voting_start <= now <= obj.voting_end)
    
    def get_can_vote(self, obj):
        """Check if current user can vote."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        # Check if user has already voted
        if obj.votes.filter(voter=request.user).exists():
            return False
        
        # Check if voting is active
        return self.get_is_voting_active(obj)


class GovernanceVoteSerializer(serializers.ModelSerializer):
    """Serializer for Governance Vote."""
    voter_name = serializers.CharField(source='voter.get_full_name', read_only=True)
    governance_title = serializers.CharField(source='governance.title', read_only=True)
    
    class Meta:
        model = GovernanceVote
        fields = [
            'id', 'governance', 'governance_title', 'voter', 'voter_name',
            'vote_choice', 'voting_power', 'transaction_hash', 'block_number',
            'reason', 'metadata', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class TokenizedRewardSerializer(serializers.ModelSerializer):
    """Serializer for Tokenized Reward."""
    recipient_name = serializers.CharField(source='recipient.get_full_name', read_only=True)
    evaluator_name = serializers.CharField(source='evaluator.get_full_name', read_only=True)
    token_symbol = serializers.CharField(source='token_contract.name', read_only=True)
    wallet_address = serializers.CharField(source='recipient_wallet.address', read_only=True)
    
    class Meta:
        model = TokenizedReward
        fields = [
            'id', 'reward_type', 'status', 'recipient', 'recipient_name', 
            'recipient_wallet', 'wallet_address', 'title', 'description', 
            'token_amount', 'token_contract', 'token_symbol', 'evaluator', 
            'evaluator_name', 'evaluation_notes', 'evaluation_score', 
            'payment_transaction', 'paid_at', 'contribution_url', 'metadata',
            'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class DecentralizedStorageSerializer(serializers.ModelSerializer):
    """Serializer for Decentralized Storage."""
    file_size_mb = serializers.SerializerMethodField()
    related_invoice_number = serializers.CharField(source='related_invoice.invoice_number', read_only=True)
    related_contract_name = serializers.CharField(source='related_contract.name', read_only=True)
    related_document_name = serializers.CharField(source='related_document.name', read_only=True)
    
    class Meta:
        model = DecentralizedStorage
        fields = [
            'id', 'storage_type', 'status', 'original_filename', 'file_size', 
            'file_size_mb', 'content_type', 'file_hash', 'storage_hash', 
            'storage_url', 'pin_status', 'related_invoice', 'related_invoice_number', 
            'related_contract', 'related_contract_name', 'related_document', 
            'related_document_name', 'description', 'tags', 'metadata', 
            'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']
    
    def get_file_size_mb(self, obj):
        """Get file size in MB."""
        return round(obj.file_size / (1024 * 1024), 2)


class BlockchainAuditLogSerializer(serializers.ModelSerializer):
    """Serializer for Blockchain Audit Log."""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    anchor_status = serializers.CharField(source='anchor.status', read_only=True)
    
    class Meta:
        model = BlockchainAuditLog
        fields = [
            'id', 'log_type', 'severity',
            'event_name', 'description', 'user', 'user_name', 'old_data',
            'new_data', 'affected_models', 'is_anchored', 'anchor', 'anchor_status',
            'transaction_hash', 'block_number', 'ip_address', 'user_agent',
            'session_id', 'metadata', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


# ==================== SPECIALIZED SERIALIZERS ====================

class DIDCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating DID."""
    
    class Meta:
        model = DecentralizedIdentity
        fields = ['did_method', 'public_keys', 'service_endpoints', 'metadata', 'expires_at']
    
    def create(self, validated_data):
        """Create DID with auto-generated identifier."""
        user = self.context['request'].user
        
        # Generate DID identifier based on method
        did_method = validated_data['did_method']
        if did_method == 'did:ethr':
            # Use Ethereum address-based DID
            wallet = user.wallets.filter(is_primary=True).first()
            if not wallet:
                raise serializers.ValidationError('No primary wallet found for Ethereum DID.')
            did_identifier = f"did:ethr:{wallet.address}"
        elif did_method == 'did:key':
            # Use key-based DID (simplified)
            did_identifier = f"did:key:{hashlib.sha256(f'{user.id}'.encode()).hexdigest()[:32]}"
        else:
            # Default to web DID
            did_identifier = f"did:web:tidygen.com:{user.username}"
        
        validated_data['user'] = user
        validated_data['did_identifier'] = did_identifier
        
        return super().create(validated_data)


class AnchorCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating on-chain anchors."""
    
    class Meta:
        model = OnChainAnchor
        fields = ['anchor_type', 'original_data', 'data_type', 'blockchain_network', 'description']
    
    def create(self, validated_data):
        """Create anchor with auto-generated hash."""
        # Generate data hash
        data_hash = OnChainAnchor().generate_data_hash(validated_data['original_data'])
        validated_data['data_hash'] = data_hash
        
        return super().create(validated_data)


class GovernanceProposalSerializer(serializers.ModelSerializer):
    """Serializer for creating governance proposals."""
    
    class Meta:
        model = DAOGovernance
        fields = ['governance_type', 'title', 'description', 'voting_duration', 'execution_data']
    
    def create(self, validated_data):
        """Create governance proposal."""
        user = self.context['request'].user
        
        validated_data['proposer'] = user
        validated_data['status'] = 'draft'
        
        return super().create(validated_data)


class RewardCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tokenized rewards."""
    
    class Meta:
        model = TokenizedReward
        fields = ['reward_type', 'title', 'description', 'token_amount', 'token_contract', 'contribution_url']
    
    def create(self, validated_data):
        """Create tokenized reward."""
        user = self.context['request'].user
        
        validated_data['recipient'] = user
        validated_data['recipient_wallet'] = user.wallets.filter(is_primary=True).first()
        
        return super().create(validated_data)
