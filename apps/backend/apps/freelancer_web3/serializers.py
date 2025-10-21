"""
Serializers for freelancer_web3 app API.
"""
from rest_framework import serializers
from .models import (
    FreelancerNFTBadge, FreelancerNFTInstance, FreelancerSmartContract,
    FreelancerReputationToken, FreelancerWalletConnection, FreelancerWeb3Transaction
)


class FreelancerNFTBadgeSerializer(serializers.ModelSerializer):
    """Serializer for NFT badge templates."""
    badge_type_display = serializers.CharField(source='get_badge_type_display', read_only=True)
    rarity_display = serializers.CharField(source='get_rarity_display', read_only=True)
    
    class Meta:
        model = FreelancerNFTBadge
        fields = [
            'id', 'badge_id', 'name', 'description', 'badge_type', 'badge_type_display',
            'rarity', 'rarity_display', 'image_url', 'icon_class', 'color_hex',
            'required_completed_jobs', 'required_rating', 'required_years_experience',
            'required_specialization', 'nft_contract_address', 'token_id', 'metadata_uri',
            'is_active', 'is_transferable', 'mint_cost_wei', 'created', 'modified'
        ]


class FreelancerNFTInstanceSerializer(serializers.ModelSerializer):
    """Serializer for NFT badge instances."""
    freelancer_name = serializers.CharField(source='freelancer.full_name', read_only=True)
    badge_name = serializers.CharField(source='badge.name', read_only=True)
    badge_details = FreelancerNFTBadgeSerializer(source='badge', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = FreelancerNFTInstance
        fields = [
            'id', 'freelancer', 'freelancer_name', 'badge', 'badge_name', 'badge_details',
            'token_id', 'nft_contract_address', 'blockchain_network', 'current_owner_address',
            'original_owner_address', 'mint_transaction_hash', 'last_transfer_hash',
            'status', 'status_display', 'minted_at', 'metadata_uri', 'earned_for_job',
            'earned_for_milestone', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class FreelancerSmartContractSerializer(serializers.ModelSerializer):
    """Serializer for smart contracts."""
    freelancer_name = serializers.CharField(source='freelancer.full_name', read_only=True)
    contract_type_display = serializers.CharField(source='get_contract_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = FreelancerSmartContract
        fields = [
            'id', 'contract_id', 'name', 'contract_type', 'contract_type_display',
            'freelancer', 'freelancer_name', 'job', 'contract_address', 'blockchain_network',
            'contract_abi', 'deployer_address', 'deployment_transaction_hash', 'gas_used',
            'deployment_cost_wei', 'status', 'status_display', 'is_verified', 'deployed_at',
            'contract_parameters', 'upgradeable', 'created', 'modified'
        ]
        read_only_fields = ['id', 'contract_id', 'created', 'modified']


class FreelancerReputationTokenSerializer(serializers.ModelSerializer):
    """Serializer for reputation tokens."""
    freelancer_name = serializers.CharField(source='freelancer.full_name', read_only=True)
    token_type_display = serializers.CharField(source='get_token_type_display', read_only=True)
    
    class Meta:
        model = FreelancerReputationToken
        fields = [
            'id', 'freelancer', 'freelancer_name', 'token_type', 'token_type_display',
            'token_amount', 'token_contract_address', 'blockchain_network',
            'source_job', 'source_review', 'mint_transaction_hash', 'last_update_hash',
            'reputation_metadata', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class FreelancerWalletConnectionSerializer(serializers.ModelSerializer):
    """Serializer for wallet connections."""
    freelancer_name = serializers.CharField(source='freelancer.full_name', read_only=True)
    wallet_type_display = serializers.CharField(source='get_wallet_type_display', read_only=True)
    connection_status_display = serializers.CharField(source='get_connection_status_display', read_only=True)
    
    class Meta:
        model = FreelancerWalletConnection
        fields = [
            'id', 'freelancer', 'freelancer_name', 'user', 'wallet_type', 'wallet_type_display',
            'wallet_address', 'wallet_name', 'connection_status', 'connection_status_display',
            'signature', 'nonce', 'blockchain_network', 'chain_id', 'connected_at',
            'last_used_at', 'expires_at', 'is_primary', 'ip_address', 'user_agent',
            'created', 'modified'
        ]
        read_only_fields = [
            'id', 'user', 'signature', 'connected_at', 'last_used_at', 'created', 'modified'
        ]


class FreelancerWeb3TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Web3 transactions."""
    freelancer_name = serializers.CharField(source='freelancer.full_name', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = FreelancerWeb3Transaction
        fields = [
            'id', 'freelancer', 'freelancer_name', 'transaction_type', 'transaction_type_display',
            'transaction_hash', 'blockchain_network', 'block_number', 'from_address', 'to_address',
            'value_wei', 'gas_price_wei', 'gas_used', 'status', 'status_display',
            'confirmation_count', 'confirmed_at', 'related_nft', 'related_contract',
            'related_reputation_token', 'transaction_metadata', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified', 'confirmed_at']
