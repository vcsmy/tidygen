"""
Wallet Signals

This module defines Django signals for wallet-related events,
enabling automatic processing and logging of wallet activities.
"""

import logging
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from .models import Wallet, WalletSignature, WalletPermission, WalletSession

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Wallet)
def wallet_post_save(sender, instance, created, **kwargs):
    """
    Handle wallet post-save events.
    
    Args:
        sender: The model class
        instance: The actual instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    if created:
        logger.info(f"New wallet connected: {instance.wallet_type} - {instance.address}")
        
        # Log wallet connection event
        # This could trigger notifications, analytics, etc.
        
    else:
        # Wallet was updated
        if instance.is_verified and not instance.verified_at:
            instance.verified_at = timezone.now()
            instance.save(update_fields=['verified_at'])
            logger.info(f"Wallet verified: {instance.address}")


@receiver(pre_save, sender=Wallet)
def wallet_pre_save(sender, instance, **kwargs):
    """
    Handle wallet pre-save events.
    
    Args:
        sender: The model class
        instance: The actual instance being saved
        **kwargs: Additional keyword arguments
    """
    # Ensure only one primary wallet per user
    if instance.is_primary and instance.user:
        Wallet.objects.filter(
            user=instance.user,
            is_primary=True
        ).exclude(id=instance.id).update(is_primary=False)


@receiver(post_save, sender=WalletSignature)
def wallet_signature_post_save(sender, instance, created, **kwargs):
    """
    Handle wallet signature post-save events.
    
    Args:
        sender: The model class
        instance: The actual instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    if created:
        logger.info(f"New signature request: {instance.signature_type} for {instance.wallet.address}")
        
        # Log signature request event
        # This could trigger notifications, rate limiting checks, etc.
        
    else:
        # Signature was updated
        if instance.status == 'verified' and instance.verified:
            logger.info(f"Signature verified: {instance.signature_type} for {instance.wallet.address}")
            
            # Log successful verification
            # This could trigger user notifications, session creation, etc.


@receiver(post_save, sender=WalletPermission)
def wallet_permission_post_save(sender, instance, created, **kwargs):
    """
    Handle wallet permission post-save events.
    
    Args:
        sender: The model class
        instance: The actual instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    if created:
        action = "granted" if instance.granted else "denied"
        logger.info(f"Permission {action}: {instance.permission_type} on {instance.resource_type} for {instance.wallet.address}")
        
        # Log permission change event
        # This could trigger access control updates, notifications, etc.


@receiver(post_save, sender=WalletSession)
def wallet_session_post_save(sender, instance, created, **kwargs):
    """
    Handle wallet session post-save events.
    
    Args:
        sender: The model class
        instance: The actual instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    if created:
        logger.info(f"New wallet session created: {instance.wallet.address} for user {instance.user.username}")
        
        # Log session creation event
        # This could trigger session monitoring, security alerts, etc.
        
    else:
        # Session was updated
        if not instance.is_active:
            logger.info(f"Wallet session deactivated: {instance.wallet.address}")
            
            # Log session deactivation
            # This could trigger cleanup tasks, security monitoring, etc.


@receiver(post_delete, sender=Wallet)
def wallet_post_delete(sender, instance, **kwargs):
    """
    Handle wallet post-delete events.
    
    Args:
        sender: The model class
        instance: The actual instance being deleted
        **kwargs: Additional keyword arguments
    """
    logger.info(f"Wallet deleted: {instance.wallet_type} - {instance.address}")
    
    # Log wallet deletion event
    # This could trigger cleanup tasks, security monitoring, etc.


@receiver(post_delete, sender=WalletSession)
def wallet_session_post_delete(sender, instance, **kwargs):
    """
    Handle wallet session post-delete events.
    
    Args:
        sender: The model class
        instance: The actual instance being deleted
        **kwargs: Additional keyword arguments
    """
    logger.info(f"Wallet session deleted: {instance.wallet.address}")
    
    # Log session deletion event
    # This could trigger cleanup tasks, security monitoring, etc.
