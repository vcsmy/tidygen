"""
Admin configuration for freelancer_web3 app.
"""
from django.contrib import admin
from .models import (
    FreelancerNFTBadge, FreelancerNFTInstance, FreelancerSmartContract,
    FreelancerReputationToken, FreelancerWalletConnection, FreelancerWeb3Transaction
)


@admin.register(FreelancerNFTBadge)
class FreelancerNFTBadgeAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'badge_type', 'rarity', 'required_completed_jobs',
        'required_rating', 'is_active', 'is_transferable'
    ]
    list_filter = ['badge_type', 'rarity', 'is_active', 'is_transferable']
    search_fields = ['name', 'description', 'badge_id']
    readonly_fields = ['badge_id', 'created', 'modified']


@admin.register(FreelancerNFTInstance)
class FreelancerNFTInstanceAdmin(admin.ModelAdmin):
    list_display = [
        'freelancer_name', 'badge_name', 'token_id', 'status',
        'current_owner_address_short', 'minted_at'
    ]
    list_filter = ['status', 'blockchain_network', 'created']
    search_fields = [
        'freelancer__first_name', 'freelancer__last_name',
        'badge__name', 'token_id', 'nft_contract_address'
    ]
    readonly_fields = ['created', 'modified']
    
    def freelancer_name(self, obj):
        return obj.freelancer.full_name
    freelancer_name.short_description = 'Freelancer'
    
    def badge_name(self, obj):
        return obj.badge.name
    badge_name.short_description = 'Badge'
    
    def current_owner_address_short(self, obj):
        return f"{obj.current_owner_address[:10]}..." if obj.current_owner_address else ''
    current_owner_address_short.short_description = 'Owner'


@admin.register(FreelancerSmartContract)
class FreelancerSmartContractAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'freelancer_name', 'contract_type', 'status',
        'contract_address_short', 'is_verified', 'deployed_at'
    ]
    list_filter = ['contract_type', 'status', 'is_verified', 'blockchain_network']
    search_fields = [
        'name', 'contract_id', 'freelancer__first_name', 'freelancer__last_name',
        'contract_address'
    ]
    readonly_fields = ['contract_id', 'created', 'modified']
    
    def freelancer_name(self, obj):
        return obj.freelancer.full_name
    freelancer_name.short_description = 'Freelancer'
    
    def contract_address_short(self, obj):
        return f"{obj.contract_address[:10]}..." if obj.contract_address else ''
    contract_address_short.short_description = 'Contract'


@admin.register(FreelancerReputationToken)
class FreelancerReputationTokenAdmin(admin.ModelAdmin):
    list_display = [
        'freelancer_name', 'token_type', 'token_amount',
        'token_contract_address_short', 'last_update_hash_short'
    ]
    list_filter = ['token_type', 'blockchain_network', 'created']
    search_fields = [
        'freelancer__first_name', 'freelancer__last_name',
        'token_contract_address'
    ]
    readonly_fields = ['created', 'modified']
    
    def freelancer_name(self, obj):
        return obj.freelancer.full_name
    freelancer_name.short_description = 'Freelancer'
    
    def token_contract_address_short(self, obj):
        return f"{obj.token_contract_address[:10]}..." if obj.token_contract_address else ''
    token_contract_address_short.short_description = 'Contract'
    
    def last_update_hash_short(self, obj):
        return f"{obj.last_update_hash[:10]}..." if obj.last_update_hash else ''
    last_update_hash_short.short_description = 'Last Update'


@admin.register(FreelancerWalletConnection)
class FreelancerWalletConnectionAdmin(admin.ModelAdmin):
    list_display = [
        'freelancer_name', 'wallet_type', 'wallet_address_short',
        'connection_status', 'is_primary', 'connected_at'
    ]
    list_filter = ['wallet_type', 'connection_status', 'is_primary', 'blockchain_network']
    search_fields = [
        'freelancer__first_name', 'freelancer__last_name',
        'wallet_address', 'wallet_name'
    ]
    readonly_fields = ['created', 'modified']
    
    def freelancer_name(self, obj):
        return obj.freelancer.full_name
    freelancer_name.short_description = 'Freelancer'
    
    def wallet_address_short(self, obj):
        return f"{obj.wallet_address[:10]}..." if obj.wallet_address else ''
    wallet_address_short.short_description = 'Wallet'


@admin.register(FreelancerWeb3Transaction)
class FreelancerWeb3TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'freelancer_name', 'transaction_type', 'status',
        'transaction_hash_short', 'value_display', 'confirmed_at'
    ]
    list_filter = ['transaction_type', 'status', 'blockchain_network', 'created']
    search_fields = [
        'freelancer__first_name', 'freelancer__last_name',
        'transaction_hash', 'from_address', 'to_address'
    ]
    readonly_fields = ['created', 'modified', 'confirmed_at']
    
    def freelancer_name(self, obj):
        return obj.freelancer.full_name
    freelancer_name.short_description = 'Freelancer'
    
    def transaction_hash_short(self, obj):
        return f"{obj.transaction_hash[:10]}..." if obj.transaction_hash else ''
    transaction_hash_short.short_description = 'Transaction'
    
    def value_display(self, obj):
        return f"{obj.value_wei} wei" if obj.value_wei else '0'
    value_display.short_description = 'Value'
