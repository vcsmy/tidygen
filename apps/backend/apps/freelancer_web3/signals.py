"""
Signals for freelancer_web3 app.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import (
    FreelancerNFTBadge, FreelancerNFTInstance, FreelancerSmartContract,
    FreelancerReputationToken, FreelancerWalletConnection
)


@receiver(pre_save, sender=FreelancerNFTBadge)
def generate_badge_id(sender, instance, **kwargs):
    """
    Generate badge ID if not provided.
    """
    if not instance.badge_id:
        import uuid
        instance.badge_id = f"BADGE{str(uuid.uuid4())[:8].upper()}"


@receiver(pre_save, sender=FreelancerSmartContract)
def generate_contract_id(sender, instance, **kwargs):
    """
    Generate contract ID if not provided.
    """
    if not instance.contract_id:
        import uuid
        instance.contract_id = f"CONTRACT{str(uuid.uuid4())[:8].upper()}"


@receiver(post_save, sender=FreelancerWalletConnection)
def update_primary_wallet(sender, instance, created, **kwargs):
    """
    Ensure only one primary wallet per freelancer.
    """
    if instance.is_primary:
        FreelancerWalletConnection.objects.filter(
            freelancer=instance.freelancer,
            is_primary=True
        ).exclude(id=instance.id).update(is_primary=False)
