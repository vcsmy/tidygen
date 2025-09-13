"""
Signals for core app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Organization

User = get_user_model()


@receiver(post_save, sender=User)
def assign_user_to_organization(sender, instance, created, **kwargs):
    """
    Automatically assign new users to the single organization in community edition.
    """
    if created:
        # Get the single organization
        org = Organization.objects.first()
        if org:
            # In community edition, all users are implicitly part of the single organization
            # We don't need to create explicit membership records
            # The organization context is handled at the application level
            pass
