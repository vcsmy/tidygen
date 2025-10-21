"""
Freelancer Web3 models for TidyGen ERP Community Edition.
Handles advanced Web3 features for freelancers including NFT badges, smart contracts, and decentralized reputation.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel

User = get_user_model()


class FreelancerNFTBadge(BaseModel):
    """
    NFT badges for freelancer achievements and milestones.
    """
    BADGE_TYPES = [
        ('completion_milestone', 'Completion Milestone'),
        ('quality_rating', 'Quality Rating'),
        ('experience_level', 'Experience Level'),
        ('specialization', 'Specialization'),
        ('certification', 'Certification'),
        ('community_service', 'Community Service'),
        ('platform_loyalty', 'Platform Loyalty'),
    ]
    
    RARITY_LEVELS = [
        ('common', 'Common'),
        ('uncommon', 'Uncommon'),
        ('rare', 'Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary'),
    ]
    
    # Badge identification
    badge_id = models.CharField(_('badge ID'), max_length=50, unique=True)
    name = models.CharField(_('badge name'), max_length=200)
    description = models.TextField(_('description'))
    badge_type = models.CharField(_('badge type'), max_length=30, choices=BADGE_TYPES)
    rarity = models.CharField(_('rarity'), max_length=20, choices=RARITY_LEVELS, default='common')
    
    # Visual representation
    image_url = models.URLField(_('image URL'), blank=True)
    icon_class = models.CharField(_('icon class'), max_length=100, blank=True)
    color_hex = models.CharField(_('color hex'), max_length=7, default='#000000')
    
    # Requirements for earning
    required_completed_jobs = models.IntegerField(_('required completed jobs'), default=0)
    required_rating = models.DecimalField(_('required rating'), max_digits=3, decimal_places=2, default=0,
                                        validators=[MinValueValidator(0), MaxValueValidator(5)])
    required_years_experience = models.IntegerField(_('required years experience'), default=0)
    required_specialization = models.CharField(_('required specialization'), max_length=100, blank=True)
    
    # Web3 metadata
    nft_contract_address = models.CharField(_('NFT contract address'), max_length=42, blank=True)
    token_id = models.IntegerField(_('token ID'), null=True, blank=True)
    metadata_uri = models.URLField(_('metadata URI'), blank=True)
    
    # Badge status
    is_active = models.BooleanField(_('is active'), default=True)
    is_transferable = models.BooleanField(_('is transferable'), default=False)
    mint_cost_wei = models.DecimalField(_('mint cost wei'), max_digits=20, decimal_places=0, default=0)
    
    class Meta:
        verbose_name = _('Freelancer NFT Badge')
        verbose_name_plural = _('Freelancer NFT Badges')
        ordering = ['rarity', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_rarity_display()})"


class FreelancerNFTInstance(BaseModel):
    """
    Individual NFT badge instances owned by freelancers.
    """
    STATUS_CHOICES = [
        ('minting', 'Minting'),
        ('minted', 'Minted'),
        ('transferred', 'Transferred'),
        ('burned', 'Burned'),
    ]
    
    # Related entities
    freelancer = models.ForeignKey('freelancers.Freelancer', on_delete=models.CASCADE, related_name='nft_badges')
    badge = models.ForeignKey(FreelancerNFTBadge, on_delete=models.CASCADE, related_name='instances')
    
    # NFT details
    token_id = models.IntegerField(_('token ID'), unique=True)
    nft_contract_address = models.CharField(_('NFT contract address'), max_length=42)
    blockchain_network = models.CharField(_('blockchain network'), max_length=50, default='ethereum')
    
    # Ownership tracking
    current_owner_address = models.CharField(_('current owner address'), max_length=42)
    original_owner_address = models.CharField(_('original owner address'), max_length=42)
    
    # Transaction details
    mint_transaction_hash = models.CharField(_('mint transaction hash'), max_length=66, blank=True)
    last_transfer_hash = models.CharField(_('last transfer hash'), max_length=66, blank=True)
    
    # Status and metadata
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='minting')
    minted_at = models.DateTimeField(_('minted at'), null=True, blank=True)
    metadata_uri = models.URLField(_('metadata URI'), blank=True)
    
    # Achievement context
    earned_for_job = models.ForeignKey('gig_management.GigJob', on_delete=models.SET_NULL, null=True, blank=True)
    earned_for_milestone = models.ForeignKey('gig_management.JobMilestone', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = _('Freelancer NFT Instance')
        verbose_name_plural = _('Freelancer NFT Instances')
        ordering = ['-minted_at']
        unique_together = ['freelancer', 'badge', 'token_id']
        indexes = [
            models.Index(fields=['token_id']),
            models.Index(fields=['freelancer', 'status']),
            models.Index(fields=['nft_contract_address', 'token_id']),
        ]
    
    def __str__(self):
        return f"{self.freelancer.full_name} - {self.badge.name} (Token #{self.token_id})"


class FreelancerSmartContract(BaseModel):
    """
    Smart contract instances for freelancer services and agreements.
    """
    CONTRACT_TYPES = [
        ('service_agreement', 'Service Agreement'),
        ('payment_escrow', 'Payment Escrow'),
        ('reputation_token', 'Reputation Token'),
        ('insurance_coverage', 'Insurance Coverage'),
        ('performance_bond', 'Performance Bond'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('deployed', 'Deployed'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('disputed', 'Disputed'),
    ]
    
    # Contract identification
    contract_id = models.CharField(_('contract ID'), max_length=50, unique=True)
    name = models.CharField(_('contract name'), max_length=200)
    contract_type = models.CharField(_('contract type'), max_length=30, choices=CONTRACT_TYPES)
    
    # Related entities
    freelancer = models.ForeignKey('freelancers.Freelancer', on_delete=models.CASCADE, related_name='smart_contracts')
    job = models.ForeignKey('gig_management.GigJob', on_delete=models.CASCADE, null=True, blank=True, related_name='smart_contracts')
    
    # Contract details
    contract_address = models.CharField(_('contract address'), max_length=42, blank=True)
    blockchain_network = models.CharField(_('blockchain network'), max_length=50, default='ethereum')
    contract_abi = models.JSONField(_('contract ABI'), default=dict)
    
    # Deployment information
    deployer_address = models.CharField(_('deployer address'), max_length=42)
    deployment_transaction_hash = models.CharField(_('deployment transaction hash'), max_length=66, blank=True)
    gas_used = models.IntegerField(_('gas used'), default=0)
    deployment_cost_wei = models.DecimalField(_('deployment cost wei'), max_digits=20, decimal_places=0, default=0)
    
    # Contract state
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='draft')
    is_verified = models.BooleanField(_('is verified'), default=False)
    deployed_at = models.DateTimeField(_('deployed at'), null=True, blank=True)
    
    # Contract parameters
    contract_parameters = models.JSONField(_('contract parameters'), default=dict)
    upgradeable = models.BooleanField(_('upgradeable'), default=False)
    
    class Meta:
        verbose_name = _('Freelancer Smart Contract')
        verbose_name_plural = _('Freelancer Smart Contracts')
        ordering = ['-created']
        indexes = [
            models.Index(fields=['contract_id']),
            models.Index(fields=['contract_address']),
            models.Index(fields=['freelancer', 'status']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.freelancer.full_name}"


class FreelancerReputationToken(BaseModel):
    """
    Reputation tokens for freelancers on-chain.
    """
    TOKEN_TYPES = [
        ('quality', 'Quality'),
        ('reliability', 'Reliability'),
        ('communication', 'Communication'),
        ('punctuality', 'Punctuality'),
        ('overall', 'Overall'),
    ]
    
    # Related entities
    freelancer = models.ForeignKey('freelancers.Freelancer', on_delete=models.CASCADE, related_name='reputation_tokens')
    
    # Token details
    token_type = models.CharField(_('token type'), max_length=20, choices=TOKEN_TYPES)
    token_amount = models.DecimalField(_('token amount'), max_digits=20, decimal_places=8, default=0)
    
    # Smart contract integration
    token_contract_address = models.CharField(_('token contract address'), max_length=42)
    blockchain_network = models.CharField(_('blockchain network'), max_length=50, default='ethereum')
    
    # Source of reputation
    source_job = models.ForeignKey('gig_management.GigJob', on_delete=models.SET_NULL, null=True, blank=True)
    source_review = models.ForeignKey('freelancers.FreelancerReview', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Transaction details
    mint_transaction_hash = models.CharField(_('mint transaction hash'), max_length=66, blank=True)
    last_update_hash = models.CharField(_('last update hash'), max_length=66, blank=True)
    
    # Metadata
    reputation_metadata = models.JSONField(_('reputation metadata'), default=dict)
    
    class Meta:
        verbose_name = _('Freelancer Reputation Token')
        verbose_name_plural = _('Freelancer Reputation Tokens')
        ordering = ['-created']
        unique_together = ['freelancer', 'token_type']
        indexes = [
            models.Index(fields=['freelancer', 'token_type']),
            models.Index(fields=['token_contract_address']),
        ]
    
    def __str__(self):
        return f"{self.freelancer.full_name} - {self.get_token_type_display()} ({self.token_amount})"


class FreelancerWalletConnection(BaseModel):
    """
    Web3 wallet connections for freelancers.
    """
    WALLET_TYPES = [
        ('metamask', 'MetaMask'),
        ('walletconnect', 'WalletConnect'),
        ('coinbase', 'Coinbase Wallet'),
        ('trust', 'Trust Wallet'),
        ('ledger', 'Ledger'),
        ('trezor', 'Trezor'),
    ]
    
    CONNECTION_STATUS = [
        ('pending', 'Pending'),
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('expired', 'Expired'),
    ]
    
    # Related entities
    freelancer = models.ForeignKey('freelancers.Freelancer', on_delete=models.CASCADE, related_name='wallet_connections')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='freelancer_wallet_connections')
    
    # Wallet details
    wallet_type = models.CharField(_('wallet type'), max_length=20, choices=WALLET_TYPES)
    wallet_address = models.CharField(_('wallet address'), max_length=42)
    wallet_name = models.CharField(_('wallet name'), max_length=100, blank=True)
    
    # Connection details
    connection_status = models.CharField(_('connection status'), max_length=20, choices=CONNECTION_STATUS, default='pending')
    signature = models.TextField(_('signature'), blank=True)
    nonce = models.CharField(_('nonce'), max_length=100, blank=True)
    
    # Blockchain information
    blockchain_network = models.CharField(_('blockchain network'), max_length=50, default='ethereum')
    chain_id = models.IntegerField(_('chain ID'), default=1)
    
    # Timestamps
    connected_at = models.DateTimeField(_('connected at'), null=True, blank=True)
    last_used_at = models.DateTimeField(_('last used at'), null=True, blank=True)
    expires_at = models.DateTimeField(_('expires at'), null=True, blank=True)
    
    # Security
    is_primary = models.BooleanField(_('is primary wallet'), default=False)
    ip_address = models.GenericIPAddressField(_('IP address'), null=True, blank=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    
    class Meta:
        verbose_name = _('Freelancer Wallet Connection')
        verbose_name_plural = _('Freelancer Wallet Connections')
        ordering = ['-connected_at']
        unique_together = ['freelancer', 'wallet_address', 'wallet_type']
        indexes = [
            models.Index(fields=['wallet_address']),
            models.Index(fields=['freelancer', 'is_primary']),
        ]
    
    def __str__(self):
        return f"{self.freelancer.full_name} - {self.get_wallet_type_display()} ({self.wallet_address[:10]}...)"


class FreelancerWeb3Transaction(BaseModel):
    """
    Web3 transaction history for freelancers.
    """
    TRANSACTION_TYPES = [
        ('nft_mint', 'NFT Mint'),
        ('nft_transfer', 'NFT Transfer'),
        ('contract_deploy', 'Contract Deploy'),
        ('contract_interaction', 'Contract Interaction'),
        ('payment', 'Payment'),
        ('reputation_mint', 'Reputation Mint'),
        ('wallet_connection', 'Wallet Connection'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Related entities
    freelancer = models.ForeignKey('freelancers.Freelancer', on_delete=models.CASCADE, related_name='web3_transactions')
    
    # Transaction details
    transaction_type = models.CharField(_('transaction type'), max_length=30, choices=TRANSACTION_TYPES)
    transaction_hash = models.CharField(_('transaction hash'), max_length=66, unique=True)
    blockchain_network = models.CharField(_('blockchain network'), max_length=50, default='ethereum')
    block_number = models.IntegerField(_('block number'), null=True, blank=True)
    
    # Transaction parameters
    from_address = models.CharField(_('from address'), max_length=42)
    to_address = models.CharField(_('to address'), max_length=42, blank=True)
    value_wei = models.DecimalField(_('value wei'), max_digits=20, decimal_places=0, default=0)
    gas_price_wei = models.DecimalField(_('gas price wei'), max_digits=20, decimal_places=0, default=0)
    gas_used = models.IntegerField(_('gas used'), default=0)
    
    # Status and confirmation
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    confirmation_count = models.IntegerField(_('confirmation count'), default=0)
    confirmed_at = models.DateTimeField(_('confirmed at'), null=True, blank=True)
    
    # Related Web3 entities
    related_nft = models.ForeignKey(FreelancerNFTInstance, on_delete=models.SET_NULL, null=True, blank=True)
    related_contract = models.ForeignKey(FreelancerSmartContract, on_delete=models.SET_NULL, null=True, blank=True)
    related_reputation_token = models.ForeignKey(FreelancerReputationToken, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Metadata
    transaction_metadata = models.JSONField(_('transaction metadata'), default=dict)
    
    class Meta:
        verbose_name = _('Freelancer Web3 Transaction')
        verbose_name_plural = _('Freelancer Web3 Transactions')
        ordering = ['-created']
        indexes = [
            models.Index(fields=['transaction_hash']),
            models.Index(fields=['freelancer', 'transaction_type']),
            models.Index(fields=['status', 'created']),
        ]
    
    def __str__(self):
        return f"{self.freelancer.full_name} - {self.transaction_type} ({self.transaction_hash[:10]}...)"
