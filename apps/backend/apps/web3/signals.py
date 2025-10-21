"""
Web3 and blockchain integration signals.
"""
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

from .models import (
    Wallet, BlockchainTransaction, SmartContract, Token,
    WalletBalance, DeFiProtocol, DecentralizedIdentity, OnChainAnchor,
    SmartContractModule, DAOGovernance, GovernanceVote, TokenizedReward,
    DecentralizedStorage, BlockchainAuditLog
)


# ==================== WALLET SIGNALS ====================

@receiver(post_save, sender=Wallet)
def update_wallet_primary_status(sender, instance, created, **kwargs):
    """Ensure only one primary wallet per user."""
    if instance.is_primary:
        # Unset other primary wallets for this user
        Wallet.objects.filter(
            user=instance.user,
            is_primary=True
        ).exclude(id=instance.id).update(is_primary=False)


@receiver(post_save, sender=Wallet)
def log_wallet_creation(sender, instance, created, **kwargs):
    """Log wallet creation in audit log."""
    if created:
        BlockchainAuditLog.objects.create(
            organization=instance.user.organization_memberships.first().organization,
            log_type='user_action',
            severity='low',
            event_name='wallet_created',
            description=f'Wallet {instance.address[:10]}... created',
            user=instance.user,
            affected_models=['Wallet'],
            metadata={
                'wallet_type': instance.wallet_type,
                'address': instance.address,
                'is_primary': instance.is_primary
            }
        )


# ==================== BLOCKCHAIN TRANSACTION SIGNALS ====================

@receiver(post_save, sender=BlockchainTransaction)
def update_wallet_last_used(sender, instance, created, **kwargs):
    """Update wallet last used timestamp."""
    if created:
        instance.wallet.last_used = timezone.now()
        instance.wallet.save(update_fields=['last_used'])


@receiver(post_save, sender=BlockchainTransaction)
def log_transaction_creation(sender, instance, created, **kwargs):
    """Log transaction creation in audit log."""
    if created:
        BlockchainAuditLog.objects.create(
            organization=instance.user.organization_memberships.first().organization,
            log_type='transaction',
            severity='medium',
            event_name='transaction_created',
            description=f'Transaction {instance.transaction_type} created',
            user=instance.user,
            affected_models=['BlockchainTransaction'],
            metadata={
                'transaction_type': instance.transaction_type,
                'transaction_hash': instance.transaction_hash,
                'value': str(instance.value),
                'status': instance.status
            }
        )


# ==================== DECENTRALIZED IDENTITY SIGNALS ====================

@receiver(post_save, sender=DecentralizedIdentity)
def generate_did_document_on_creation(sender, instance, created, **kwargs):
    """Generate DID document when DID is created."""
    if created and not instance.did_document:
        instance.generate_did_document()


@receiver(post_save, sender=DecentralizedIdentity)
def log_did_creation(sender, instance, created, **kwargs):
    """Log DID creation in audit log."""
    if created:
        BlockchainAuditLog.objects.create(
            log_type='user_action',
            severity='medium',
            event_name='did_created',
            description=f'DID {instance.did_identifier} created',
            user=instance.user,
            affected_models=['DecentralizedIdentity'],
            metadata={
                'did_method': instance.did_method,
                'did_identifier': instance.did_identifier,
                'status': instance.status
            }
        )


@receiver(post_save, sender=DecentralizedIdentity)
def log_did_verification(sender, instance, **kwargs):
    """Log DID verification in audit log."""
    if instance.is_verified and instance.verification_timestamp:
        BlockchainAuditLog.objects.create(
            log_type='user_action',
            severity='medium',
            event_name='did_verified',
            description=f'DID {instance.did_identifier} verified',
            user=instance.user,
            affected_models=['DecentralizedIdentity'],
            metadata={
                'did_method': instance.did_method,
                'verification_method': instance.verification_method,
                'verification_timestamp': instance.verification_timestamp.isoformat()
            }
        )


# ==================== ON-CHAIN ANCHOR SIGNALS ====================

@receiver(post_save, sender=OnChainAnchor)
def log_anchor_creation(sender, instance, created, **kwargs):
    """Log anchor creation in audit log."""
    if created and not kwargs.get('raw', False):
        # Prevent recursion by checking if this is an auto-generated anchor
        if instance.metadata.get('auto_anchored', False):
            # Skip logging for auto-anchored items to prevent recursion
            return
            
        BlockchainAuditLog.objects.create(
            log_type='system_event',
            severity='high',
            event_name='anchor_created',
            description=f'On-chain anchor {instance.anchor_type} created',
            user=None,  # System event
            affected_models=['OnChainAnchor'],
            metadata={
                'anchor_type': instance.anchor_type,
                'data_hash': instance.data_hash,
                'data_type': instance.data_type,
                'blockchain_network': instance.blockchain_network
            }
        )


@receiver(post_save, sender=OnChainAnchor)
def log_anchor_status_change(sender, instance, **kwargs):
    """Log anchor status changes in audit log."""
    if (instance.status in ['anchored', 'confirmed'] and 
        not kwargs.get('raw', False) and 
        not instance.metadata.get('auto_anchored', False)):
        BlockchainAuditLog.objects.create(
            log_type='system_event',
            severity='high',
            event_name='anchor_status_changed',
            description=f'Anchor {instance.anchor_type} status changed to {instance.status}',
            user=None,  # System event
            affected_models=['OnChainAnchor'],
            metadata={
                'anchor_type': instance.anchor_type,
                'status': instance.status,
                'transaction_hash': instance.transaction_hash,
                'block_number': instance.block_number
            }
        )


# ==================== SMART CONTRACT MODULE SIGNALS ====================

@receiver(post_save, sender=SmartContractModule)
def log_module_deployment(sender, instance, **kwargs):
    """Log smart contract module deployment."""
    if instance.status == 'deployed':
        BlockchainAuditLog.objects.create(
            log_type='system_event',
            severity='high',
            event_name='smart_contract_deployed',
            description=f'Smart contract module {instance.name} deployed',
            user=None,  # System event
            affected_models=['SmartContractModule'],
            metadata={
                'module_name': instance.name,
                'module_type': instance.module_type,
                'contract_address': instance.contract_address,
                'version': instance.version
            }
        )


@receiver(post_save, sender=SmartContractModule)
def log_module_activation(sender, instance, **kwargs):
    """Log smart contract module activation."""
    if instance.status == 'active':
        BlockchainAuditLog.objects.create(
            log_type='system_event',
            severity='medium',
            event_name='smart_contract_activated',
            description=f'Smart contract module {instance.name} activated',
            user=None,  # System event
            affected_models=['SmartContractModule'],
            metadata={
                'module_name': instance.name,
                'module_type': instance.module_type,
                'integrated_modules': instance.integrated_modules
            }
        )


# ==================== DAO GOVERNANCE SIGNALS ====================

@receiver(post_save, sender=DAOGovernance)
def log_proposal_creation(sender, instance, created, **kwargs):
    """Log governance proposal creation."""
    if created:
        BlockchainAuditLog.objects.create(
            log_type='user_action',
            severity='medium',
            event_name='governance_proposal_created',
            description=f'Governance proposal "{instance.title}" created',
            user=instance.proposer,
            affected_models=['DAOGovernance'],
            metadata={
                'governance_type': instance.governance_type,
                'title': instance.title,
                'voting_duration': str(instance.voting_duration)
            }
        )


@receiver(post_save, sender=DAOGovernance)
def log_voting_start(sender, instance, **kwargs):
    """Log voting period start."""
    if instance.status == 'active' and instance.voting_start:
        BlockchainAuditLog.objects.create(
            log_type='system_event',
            severity='medium',
            event_name='voting_started',
            description=f'Voting started for proposal "{instance.title}"',
            user=None,  # System event
            affected_models=['DAOGovernance'],
            metadata={
                'proposal_id': instance.id,
                'voting_start': instance.voting_start.isoformat(),
                'voting_end': instance.voting_end.isoformat() if instance.voting_end else None
            }
        )


@receiver(post_save, sender=DAOGovernance)
def log_proposal_execution(sender, instance, **kwargs):
    """Log proposal execution."""
    if instance.status == 'executed':
        BlockchainAuditLog.objects.create(
            log_type='system_event',
            severity='high',
            event_name='proposal_executed',
            description=f'Proposal "{instance.title}" executed',
            user=instance.executed_by,
            affected_models=['DAOGovernance'],
            metadata={
                'proposal_id': instance.id,
                'votes_for': str(instance.votes_for),
                'votes_against': str(instance.votes_against),
                'executed_at': instance.executed_at.isoformat() if instance.executed_at else None
            }
        )


@receiver(post_save, sender=GovernanceVote)
def log_vote_cast(sender, instance, created, **kwargs):
    """Log vote casting."""
    if created:
        BlockchainAuditLog.objects.create(
            organization=instance.governance.organization,
            log_type='user_action',
            severity='medium',
            event_name='vote_cast',
            description=f'Vote {instance.vote_choice} cast for proposal "{instance.governance.title}"',
            user=instance.voter,
            affected_models=['GovernanceVote'],
            metadata={
                'proposal_id': instance.governance.id,
                'vote_choice': instance.vote_choice,
                'voting_power': str(instance.voting_power),
                'reason': instance.reason
            }
        )


# ==================== TOKENIZED REWARD SIGNALS ====================

@receiver(post_save, sender=TokenizedReward)
def log_reward_creation(sender, instance, created, **kwargs):
    """Log tokenized reward creation."""
    if created:
        BlockchainAuditLog.objects.create(
            log_type='user_action',
            severity='low',
            event_name='reward_created',
            description=f'Tokenized reward "{instance.title}" created',
            user=instance.recipient,
            affected_models=['TokenizedReward'],
            metadata={
                'reward_type': instance.reward_type,
                'token_amount': str(instance.token_amount),
                'recipient': instance.recipient.username
            }
        )


@receiver(post_save, sender=TokenizedReward)
def log_reward_approval(sender, instance, **kwargs):
    """Log reward approval."""
    if instance.status == 'approved':
        BlockchainAuditLog.objects.create(
            log_type='user_action',
            severity='medium',
            event_name='reward_approved',
            description=f'Reward "{instance.title}" approved',
            user=instance.evaluator,
            affected_models=['TokenizedReward'],
            metadata={
                'reward_id': instance.id,
                'evaluation_score': instance.evaluation_score,
                'evaluator': instance.evaluator.username if instance.evaluator else None
            }
        )


@receiver(post_save, sender=TokenizedReward)
def log_reward_payment(sender, instance, **kwargs):
    """Log reward payment."""
    if instance.status == 'paid':
        BlockchainAuditLog.objects.create(
            log_type='transaction',
            severity='medium',
            event_name='reward_paid',
            description=f'Reward "{instance.title}" paid',
            user=instance.recipient,
            affected_models=['TokenizedReward'],
            metadata={
                'reward_id': instance.id,
                'token_amount': str(instance.token_amount),
                'paid_at': instance.paid_at.isoformat() if instance.paid_at else None
            }
        )


# ==================== DECENTRALIZED STORAGE SIGNALS ====================

@receiver(post_save, sender=DecentralizedStorage)
def log_storage_upload(sender, instance, created, **kwargs):
    """Log file upload to decentralized storage."""
    if created:
        BlockchainAuditLog.objects.create(
            log_type='user_action',
            severity='low',
            event_name='file_uploaded',
            description=f'File "{instance.original_filename}" uploaded to {instance.storage_type}',
            user=None,  # Could be system or user
            affected_models=['DecentralizedStorage'],
            metadata={
                'storage_type': instance.storage_type,
                'file_size': instance.file_size,
                'content_type': instance.content_type,
                'file_hash': instance.file_hash
            }
        )


@receiver(post_save, sender=DecentralizedStorage)
def log_storage_pin(sender, instance, **kwargs):
    """Log file pinning."""
    if instance.pin_status and instance.status == 'pinned':
        BlockchainAuditLog.objects.create(
            log_type='system_event',
            severity='low',
            event_name='file_pinned',
            description=f'File "{instance.original_filename}" pinned to {instance.storage_type}',
            user=None,  # System event
            affected_models=['DecentralizedStorage'],
            metadata={
                'storage_type': instance.storage_type,
                'storage_hash': instance.storage_hash,
                'storage_url': instance.storage_url
            }
        )


# ==================== BLOCKCHAIN AUDIT LOG SIGNALS ====================

@receiver(post_save, sender=BlockchainAuditLog)
def auto_anchor_critical_logs(sender, instance, created, **kwargs):
    """Automatically anchor critical audit logs to blockchain."""
    if (created and instance.severity in ['high', 'critical'] and 
        instance.event_name != 'anchor_created' and not kwargs.get('raw', False)):
        # Create on-chain anchor for critical logs
        original_data = {
            'log_id': instance.id,
            'event_name': instance.event_name,
            'description': instance.description,
            'severity': instance.severity,
            'user': instance.user.username if instance.user else None,
            'timestamp': instance.created.isoformat()
        }
        anchor = OnChainAnchor.objects.create(
            anchor_type='audit_log',
            data_hash=OnChainAnchor().generate_data_hash(original_data),
            original_data=original_data,
            data_type='audit_log',
            description=f'Audit log anchor for {instance.event_name}',
            metadata={
                'log_id': instance.id,
                'severity': instance.severity,
                'auto_anchored': True
            }
        )
        
        # Link the anchor to the audit log
        instance.anchor = anchor
        instance.is_anchored = True
        instance.save(update_fields=['anchor', 'is_anchored'])


# ==================== INTEGRATION SIGNALS ====================

@receiver(post_save, sender='finance.Invoice')
def auto_anchor_invoice(sender, instance, created, **kwargs):
    """Automatically anchor invoices to blockchain."""
    if created:
        # Create on-chain anchor for invoice
        original_data = {
            'invoice_id': instance.id,
            'invoice_number': instance.invoice_number,
            'amount': str(instance.total_amount),
            'customer': instance.customer.name if instance.customer else None,
            'status': instance.status,
            'created_at': instance.created.isoformat()
        }
        anchor = OnChainAnchor.objects.create(
            anchor_type='invoice',
            data_hash=OnChainAnchor().generate_data_hash(original_data),
            original_data=original_data,
            data_type='invoice',
            description=f'Invoice {instance.invoice_number} anchor',
            related_invoice=instance,
            metadata={
                'invoice_id': instance.id,
                'auto_anchored': True
            }
        )


@receiver(post_save, sender='finance.Payment')
def auto_anchor_payment(sender, instance, created, **kwargs):
    """Automatically anchor payments to blockchain."""
    if created:
        # Create on-chain anchor for payment
        original_data = {
            'payment_id': instance.id,
            'amount': str(instance.amount),
            'payment_method': instance.payment_method,
            'created_at': instance.created.isoformat()
        }
        anchor = OnChainAnchor.objects.create(
            anchor_type='payment',
            data_hash=OnChainAnchor().generate_data_hash(original_data),
            original_data=original_data,
            data_type='payment',
            description=f'Payment {instance.id} anchor',
            related_payment=instance,
            metadata={
                'payment_id': instance.id,
                'auto_anchored': True
            }
        )


@receiver(post_save, sender='hr.Employee')
def auto_anchor_employee_hire(sender, instance, created, **kwargs):
    """Automatically anchor employee hiring to blockchain."""
    if created:
        # Create on-chain anchor for employee hire
        original_data = {
            'employee_id': instance.id,
            'employee_number': instance.employee_id,
            'hire_date': instance.hire_date.isoformat() if instance.hire_date else None,
            'position': instance.position.title if instance.position else None,
            'department': instance.department.name if instance.department else None,
            'salary': str(instance.salary) if instance.salary else None
        }
        anchor = OnChainAnchor.objects.create(
            anchor_type='supply_chain',
            data_hash=OnChainAnchor().generate_data_hash(original_data),
            original_data=original_data,
            data_type='employee_hire',
            description=f'Employee {instance.employee_id} hire anchor',
            metadata={
                'employee_id': instance.id,
                'auto_anchored': True
            }
        )
