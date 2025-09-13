"""
Web3 and blockchain integration models.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.core.models import BaseModel
import hashlib
import json

User = get_user_model()


class Wallet(BaseModel):
    """User wallet for blockchain interactions."""
    WALLET_TYPES = [
        ('metamask', 'MetaMask'),
        ('walletconnect', 'WalletConnect'),
        ('coinbase', 'Coinbase Wallet'),
        ('trust', 'Trust Wallet'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallets')
    address = models.CharField(max_length=42, unique=True)  # Ethereum address
    wallet_type = models.CharField(max_length=20, choices=WALLET_TYPES)
    is_primary = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    verification_signature = models.TextField(blank=True)
    last_used = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Wallet'
        verbose_name_plural = 'Wallets'
        unique_together = ['user', 'address']
    
    def __str__(self):
        return f"{self.user.username} - {self.address[:10]}..."


class BlockchainTransaction(BaseModel):
    """Record of blockchain transactions."""
    TRANSACTION_TYPES = [
        ('payment', 'Payment'),
        ('contract_deploy', 'Contract Deployment'),
        ('contract_call', 'Contract Call'),
        ('token_transfer', 'Token Transfer'),
        ('nft_mint', 'NFT Mint'),
        ('nft_transfer', 'NFT Transfer'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blockchain_transactions')
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_hash = models.CharField(max_length=66, unique=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Transaction details
    from_address = models.CharField(max_length=42)
    to_address = models.CharField(max_length=42)
    value = models.DecimalField(max_digits=36, decimal_places=18, default=0)
    gas_used = models.BigIntegerField(null=True, blank=True)
    gas_price = models.BigIntegerField(null=True, blank=True)
    block_number = models.BigIntegerField(null=True, blank=True)
    block_hash = models.CharField(max_length=66, blank=True)
    
    # Additional data
    contract_address = models.CharField(max_length=42, blank=True)
    token_address = models.CharField(max_length=42, blank=True)
    token_symbol = models.CharField(max_length=20, blank=True)
    token_decimals = models.IntegerField(null=True, blank=True)
    
    # Metadata
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = 'Blockchain Transaction'
        verbose_name_plural = 'Blockchain Transactions'
        ordering = ['-created']
        indexes = [
            models.Index(fields=['transaction_hash']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['wallet', 'transaction_type']),
        ]
    
    def __str__(self):
        return f"{self.transaction_type} - {self.transaction_hash[:10]}..."


class SmartContract(BaseModel):
    """Smart contracts deployed by the platform."""
    CONTRACT_TYPES = [
        ('erc20', 'ERC-20 Token'),
        ('erc721', 'ERC-721 NFT'),
        ('erc1155', 'ERC-1155 Multi-Token'),
        ('custom', 'Custom Contract'),
    ]
    
    name = models.CharField(max_length=100)
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPES)
    address = models.CharField(max_length=42, unique=True)
    abi = models.JSONField()
    bytecode = models.TextField(blank=True)
    source_code = models.TextField(blank=True)
    
    # Deployment details
    deployer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deployed_contracts')
    deployment_transaction = models.ForeignKey(
        BlockchainTransaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deployed_contract'
    )
    deployment_block = models.BigIntegerField(null=True, blank=True)
    
    # Contract state
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    total_supply = models.DecimalField(max_digits=36, decimal_places=18, null=True, blank=True)
    
    # Metadata
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    documentation = models.URLField(blank=True)
    
    class Meta:
        verbose_name = 'Smart Contract'
        verbose_name_plural = 'Smart Contracts'
        ordering = ['-created']
    
    def __str__(self):
        return f"{self.name} ({self.address[:10]}...)"


class Token(BaseModel):
    """Tokens managed by the platform."""
    TOKEN_TYPES = [
        ('native', 'Native Token (ETH)'),
        ('erc20', 'ERC-20 Token'),
        ('erc721', 'ERC-721 NFT'),
        ('erc1155', 'ERC-1155 Token'),
    ]
    
    contract = models.ForeignKey(SmartContract, on_delete=models.CASCADE, related_name='tokens')
    token_id = models.CharField(max_length=100, blank=True)  # For NFTs
    symbol = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    decimals = models.IntegerField(default=18)
    total_supply = models.DecimalField(max_digits=36, decimal_places=18, null=True, blank=True)
    
    # Token metadata
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    external_url = models.URLField(blank=True)
    attributes = models.JSONField(default=dict, blank=True)
    
    # Pricing (if available)
    price_usd = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    market_cap = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Token'
        verbose_name_plural = 'Tokens'
        unique_together = ['contract', 'token_id']
        ordering = ['symbol', 'name']
    
    def __str__(self):
        if self.token_id:
            return f"{self.name} #{self.token_id}"
        return f"{self.name} ({self.symbol})"


class WalletBalance(BaseModel):
    """Wallet token balances."""
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='balances')
    token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name='balances')
    balance = models.DecimalField(max_digits=36, decimal_places=18, default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Wallet Balance'
        verbose_name_plural = 'Wallet Balances'
        unique_together = ['wallet', 'token']
        ordering = ['-balance']
    
    def __str__(self):
        return f"{self.wallet.address[:10]}... - {self.balance} {self.token.symbol}"


class DeFiProtocol(BaseModel):
    """DeFi protocols integration."""
    PROTOCOL_TYPES = [
        ('dex', 'Decentralized Exchange'),
        ('lending', 'Lending Protocol'),
        ('yield', 'Yield Farming'),
        ('staking', 'Staking'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    protocol_type = models.CharField(max_length=20, choices=PROTOCOL_TYPES)
    contract_address = models.CharField(max_length=42)
    website = models.URLField(blank=True)
    documentation = models.URLField(blank=True)
    
    # Integration details
    is_active = models.BooleanField(default=True)
    supported_tokens = models.ManyToManyField(Token, blank=True)
    apy = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    
    # Metadata
    description = models.TextField(blank=True)
    risk_level = models.CharField(
        max_length=10,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
        ],
        default='medium'
    )
    
    class Meta:
        verbose_name = 'DeFi Protocol'
        verbose_name_plural = 'DeFi Protocols'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.protocol_type})"


# ==================== CORE WEB3 FEATURES ====================

class DecentralizedIdentity(BaseModel):
    """Decentralized Identity (DID) management."""
    DID_METHODS = [
        ('did:ethr', 'Ethereum DID'),
        ('did:key', 'Key DID'),
        ('did:web', 'Web DID'),
        ('did:polkadot', 'Polkadot DID'),
        ('did:substrate', 'Substrate DID'),
        ('did:ens', 'ENS DID'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('revoked', 'Revoked'),
        ('suspended', 'Suspended'),
        ('expired', 'Expired'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='did')
    did_identifier = models.CharField(max_length=255, unique=True)
    did_method = models.CharField(max_length=20, choices=DID_METHODS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # DID Document
    did_document = models.JSONField(default=dict)
    public_keys = models.JSONField(default=list)
    service_endpoints = models.JSONField(default=list)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verification_method = models.CharField(max_length=100, blank=True)
    verification_timestamp = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Decentralized Identity'
        verbose_name_plural = 'Decentralized Identities'
        unique_together = ['user']
        indexes = [
            models.Index(fields=['did_identifier']),
            models.Index(fields=['user', 'status']),
        ]
    
    def __str__(self):
        return f"{self.did_identifier} ({self.user.username})"
    
    def generate_did_document(self):
        """Generate DID document."""
        self.did_document = {
            "@context": ["https://www.w3.org/ns/did/v1"],
            "id": self.did_identifier,
            "verificationMethod": self.public_keys,
            "service": self.service_endpoints,
            "created": self.created.isoformat(),
            "updated": self.modified.isoformat(),
        }
        self.save()


class OnChainAnchor(BaseModel):
    """On-chain data anchoring for critical transactions."""
    ANCHOR_TYPES = [
        ('transaction', 'Transaction Hash'),
        ('document', 'Document Hash'),
        ('contract', 'Contract Hash'),
        ('payment', 'Payment Hash'),
        ('supply_chain', 'Supply Chain Checkpoint'),
        ('audit_log', 'Audit Log Hash'),
        ('invoice', 'Invoice Hash'),
        ('purchase_order', 'Purchase Order Hash'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('anchored', 'Anchored'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
    ]
    
    anchor_type = models.CharField(max_length=20, choices=ANCHOR_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Data to be anchored
    data_hash = models.CharField(max_length=64)  # SHA-256 hash
    original_data = models.JSONField(default=dict)
    data_type = models.CharField(max_length=50)  # e.g., 'invoice', 'contract', 'payment'
    
    # Blockchain details
    blockchain_network = models.CharField(max_length=50, default='ethereum')
    transaction_hash = models.CharField(max_length=66, blank=True)
    block_number = models.BigIntegerField(null=True, blank=True)
    block_hash = models.CharField(max_length=66, blank=True)
    gas_used = models.BigIntegerField(null=True, blank=True)
    
    # Related entities
    related_invoice = models.ForeignKey('finance.Invoice', on_delete=models.SET_NULL, null=True, blank=True)
    related_contract = models.ForeignKey('SmartContract', on_delete=models.SET_NULL, null=True, blank=True)
    related_payment = models.ForeignKey('finance.Payment', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Metadata
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)
    
    class Meta:
        verbose_name = 'On-Chain Anchor'
        verbose_name_plural = 'On-Chain Anchors'
        ordering = ['-created']
        indexes = [
            models.Index(fields=['data_hash']),
            models.Index(fields=['transaction_hash']),
            models.Index(fields=['anchor_type']),
            models.Index(fields=['status', 'created']),
        ]
    
    def __str__(self):
        return f"{self.anchor_type} - {self.data_hash[:16]}..."
    
    def generate_data_hash(self, data):
        """Generate SHA-256 hash of data."""
        if isinstance(data, dict):
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)
        return hashlib.sha256(data_str.encode()).hexdigest()


class SmartContractModule(BaseModel):
    """Smart contract-driven ERP modules."""
    MODULE_TYPES = [
        ('invoice_escrow', 'Invoice Escrow'),
        ('payment_automation', 'Payment Automation'),
        ('supply_chain', 'Supply Chain Tracking'),
        ('compliance', 'Compliance Monitoring'),
        ('governance', 'Governance Voting'),
        ('rewards', 'Rewards Distribution'),
        ('audit', 'Audit Logging'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('deployed', 'Deployed'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('deprecated', 'Deprecated'),
    ]
    
    name = models.CharField(max_length=100)
    module_type = models.CharField(max_length=30, choices=MODULE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Smart contract details
    contract = models.ForeignKey(SmartContract, on_delete=models.CASCADE, related_name='modules')
    contract_address = models.CharField(max_length=42)
    abi = models.JSONField()
    
    # Configuration
    configuration = models.JSONField(default=dict)
    triggers = models.JSONField(default=list)  # Events that trigger contract execution
    conditions = models.JSONField(default=dict)  # Conditions for execution
    
    # Integration
    integrated_modules = models.JSONField(default=list)  # ERP modules this integrates with
    webhook_endpoints = models.JSONField(default=list)
    
    # Metadata
    description = models.TextField(blank=True)
    version = models.CharField(max_length=20, default='1.0.0')
    documentation = models.URLField(blank=True)
    
    class Meta:
        verbose_name = 'Smart Contract Module'
        verbose_name_plural = 'Smart Contract Modules'
        ordering = ['-created']
        unique_together = ['name', 'version']
    
    def __str__(self):
        return f"{self.name} ({self.module_type})"


class DAOGovernance(BaseModel):
    """DAO-style governance for community version."""
    GOVERNANCE_TYPES = [
        ('proposal', 'Proposal'),
        ('vote', 'Vote'),
        ('execution', 'Execution'),
        ('treasury', 'Treasury Management'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('passed', 'Passed'),
        ('rejected', 'Rejected'),
        ('executed', 'Executed'),
        ('expired', 'Expired'),
    ]
    
    governance_type = models.CharField(max_length=20, choices=GOVERNANCE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Proposal details
    title = models.CharField(max_length=200)
    description = models.TextField()
    proposer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proposals')
    
    # Voting
    voting_power_required = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    voting_duration = models.DurationField()
    voting_start = models.DateTimeField(null=True, blank=True)
    voting_end = models.DateTimeField(null=True, blank=True)
    
    # Results
    votes_for = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    votes_against = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    total_votes = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    
    # Execution
    execution_data = models.JSONField(default=dict)
    executed_at = models.DateTimeField(null=True, blank=True)
    executed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='executed_proposals')
    
    # Blockchain integration
    on_chain_proposal_id = models.CharField(max_length=100, blank=True)
    transaction_hash = models.CharField(max_length=66, blank=True)
    
    class Meta:
        verbose_name = 'DAO Governance'
        verbose_name_plural = 'DAO Governance'
        ordering = ['-created']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['proposer', 'status']),
            models.Index(fields=['voting_start', 'voting_end']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.governance_type})"


class GovernanceVote(BaseModel):
    """Individual votes in DAO governance."""
    VOTE_CHOICES = [
        ('for', 'For'),
        ('against', 'Against'),
        ('abstain', 'Abstain'),
    ]
    
    governance = models.ForeignKey(DAOGovernance, on_delete=models.CASCADE, related_name='votes')
    voter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='governance_votes')
    vote_choice = models.CharField(max_length=10, choices=VOTE_CHOICES)
    voting_power = models.DecimalField(max_digits=20, decimal_places=8)
    
    # Blockchain integration
    transaction_hash = models.CharField(max_length=66, blank=True)
    block_number = models.BigIntegerField(null=True, blank=True)
    
    # Metadata
    reason = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)
    
    class Meta:
        verbose_name = 'Governance Vote'
        verbose_name_plural = 'Governance Votes'
        unique_together = ['governance', 'voter']
        ordering = ['-created']
    
    def __str__(self):
        return f"{self.voter.username} - {self.vote_choice} ({self.voting_power})"


class TokenizedReward(BaseModel):
    """Tokenized rewards for community contributions."""
    REWARD_TYPES = [
        ('bug_report', 'Bug Report'),
        ('feature_request', 'Feature Request'),
        ('code_contribution', 'Code Contribution'),
        ('documentation', 'Documentation'),
        ('testing', 'Testing'),
        ('support', 'Support'),
        ('translation', 'Translation'),
        ('design', 'Design'),
        ('marketing', 'Marketing'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
    ]
    
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Recipient
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokenized_rewards')
    recipient_wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='rewards')
    
    # Reward details
    title = models.CharField(max_length=200)
    description = models.TextField()
    token_amount = models.DecimalField(max_digits=20, decimal_places=8)
    token_contract = models.ForeignKey(SmartContract, on_delete=models.CASCADE, related_name='rewards')
    
    # Evaluation
    evaluator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='evaluated_rewards')
    evaluation_notes = models.TextField(blank=True)
    evaluation_score = models.IntegerField(null=True, blank=True)  # 1-10 scale
    
    # Payment
    payment_transaction = models.ForeignKey(BlockchainTransaction, on_delete=models.SET_NULL, null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    contribution_url = models.URLField(blank=True)  # Link to PR, issue, etc.
    metadata = models.JSONField(default=dict)
    
    class Meta:
        verbose_name = 'Tokenized Reward'
        verbose_name_plural = 'Tokenized Rewards'
        ordering = ['-created']
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['reward_type']),
            models.Index(fields=['status', 'created']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username} ({self.token_amount})"


class DecentralizedStorage(BaseModel):
    """Decentralized file storage integration."""
    STORAGE_TYPES = [
        ('ipfs', 'IPFS'),
        ('arweave', 'Arweave'),
        ('swarm', 'Swarm'),
        ('sia', 'Sia'),
    ]
    
    STATUS_CHOICES = [
        ('uploading', 'Uploading'),
        ('uploaded', 'Uploaded'),
        ('pinned', 'Pinned'),
        ('failed', 'Failed'),
    ]
    
    storage_type = models.CharField(max_length=20, choices=STORAGE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploading')
    
    # File details
    original_filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    content_type = models.CharField(max_length=100)
    file_hash = models.CharField(max_length=64)  # SHA-256 hash
    
    # Storage details
    storage_hash = models.CharField(max_length=255)  # IPFS hash, Arweave ID, etc.
    storage_url = models.URLField(blank=True)
    pin_status = models.BooleanField(default=False)
    
    # Related entities
    related_invoice = models.ForeignKey('finance.Invoice', on_delete=models.SET_NULL, null=True, blank=True)
    related_contract = models.ForeignKey('SmartContract', on_delete=models.SET_NULL, null=True, blank=True)
    related_document = models.ForeignKey('hr.Document', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Metadata
    description = models.TextField(blank=True)
    tags = models.JSONField(default=list)
    metadata = models.JSONField(default=dict)
    
    class Meta:
        verbose_name = 'Decentralized Storage'
        verbose_name_plural = 'Decentralized Storage'
        ordering = ['-created']
        indexes = [
            models.Index(fields=['storage_hash']),
            models.Index(fields=['file_hash']),
            models.Index(fields=['storage_type']),
            models.Index(fields=['status', 'created']),
        ]
    
    def __str__(self):
        return f"{self.original_filename} ({self.storage_type})"


class BlockchainAuditLog(BaseModel):
    """Blockchain-based audit logs for transparency."""
    LOG_TYPES = [
        ('user_action', 'User Action'),
        ('system_event', 'System Event'),
        ('transaction', 'Transaction'),
        ('data_change', 'Data Change'),
        ('access_attempt', 'Access Attempt'),
        ('security_event', 'Security Event'),
    ]
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    log_type = models.CharField(max_length=20, choices=LOG_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='medium')
    
    # Event details
    event_name = models.CharField(max_length=100)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    
    # Data
    old_data = models.JSONField(default=dict, blank=True)
    new_data = models.JSONField(default=dict, blank=True)
    affected_models = models.JSONField(default=list)
    
    # Blockchain anchoring
    is_anchored = models.BooleanField(default=False)
    anchor = models.ForeignKey(OnChainAnchor, on_delete=models.SET_NULL, null=True, blank=True)
    transaction_hash = models.CharField(max_length=66, blank=True)
    block_number = models.BigIntegerField(null=True, blank=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(default=dict)
    
    class Meta:
        verbose_name = 'Blockchain Audit Log'
        verbose_name_plural = 'Blockchain Audit Logs'
        ordering = ['-created']
        indexes = [
            models.Index(fields=['log_type']),
            models.Index(fields=['user', 'created']),
            models.Index(fields=['severity', 'created']),
            models.Index(fields=['is_anchored', 'created']),
        ]
    
    def __str__(self):
        return f"{self.event_name} - {self.user.username if self.user else 'System'}"
