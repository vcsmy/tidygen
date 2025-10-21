"""
Signals for contractor_payments app.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal
from .models import ContractorPayment


@receiver(pre_save, sender=ContractorPayment)
def generate_payment_id(sender, instance, **kwargs):
    """
    Generate payment ID if not provided.
    """
    if not instance.payment_id:
        import uuid
        instance.payment_id = f"PAY{str(uuid.uuid4())[:8].upper()}"


@receiver(pre_save, sender=ContractorPayment)
def calculate_net_amount(sender, instance, **kwargs):
    """
    Calculate net amount before saving.
    """
    if instance.amount and instance.processing_fee is not None:
        instance.net_amount = instance.amount - instance.processing_fee
