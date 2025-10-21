"""
Signals for automated client management operations in TidyGen ERP platform.
"""
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

from apps.sales.models import (
    Client, IndividualClient, CorporateClient, ClientContact, ClientNote,
    ClientDocument, ClientInteraction, ClientTag, ClientTagAssignment, ClientSegmentAssignment
)


@receiver(post_save, sender=Client)
def update_client_activity(sender, instance, created, **kwargs):
    """Update client activity date when client is modified."""
    if not created:
        instance.last_activity_date = timezone.now()
        # Save without triggering signals again
        Client.objects.filter(pk=instance.pk).update(last_activity_date=timezone.now())


@receiver(post_save, sender=ClientInteraction)
def update_client_contact_date(sender, instance, created, **kwargs):
    """Update client's last contact date when interaction is created."""
    if created:
        client = instance.client
        client.last_contact_date = timezone.now()
        client.last_activity_date = timezone.now()
        # Save without triggering signals again
        Client.objects.filter(pk=client.pk).update(
            last_contact_date=timezone.now(),
            last_activity_date=timezone.now()
        )


@receiver(post_save, sender=ClientNote)
def update_client_activity_on_note(sender, instance, created, **kwargs):
    """Update client's last activity date when note is created."""
    if created:
        client = instance.client
        client.last_activity_date = timezone.now()
        # Save without triggering signals again
        Client.objects.filter(pk=client.pk).update(last_activity_date=timezone.now())


@receiver(post_save, sender=ClientDocument)
def update_client_activity_on_document(sender, instance, created, **kwargs):
    """Update client's last activity date when document is uploaded."""
    if created:
        client = instance.client
        client.last_activity_date = timezone.now()
        # Save without triggering signals again
        Client.objects.filter(pk=client.pk).update(last_activity_date=timezone.now())


@receiver(post_save, sender=ClientContact)
def update_client_activity_on_contact(sender, instance, created, **kwargs):
    """Update client's last activity date when contact is added."""
    if created:
        client = instance.client
        client.last_activity_date = timezone.now()
        # Save without triggering signals again
        Client.objects.filter(pk=client.pk).update(last_activity_date=timezone.now())


@receiver(post_save, sender=ClientTagAssignment)
def update_client_activity_on_tag_assignment(sender, instance, created, **kwargs):
    """Update client's last activity date when tag is assigned."""
    if created:
        client = instance.client
        client.last_activity_date = timezone.now()
        # Save without triggering signals again
        Client.objects.filter(pk=client.pk).update(last_activity_date=timezone.now())


@receiver(post_save, sender=ClientSegmentAssignment)
def update_client_activity_on_segment_assignment(sender, instance, created, **kwargs):
    """Update client's last activity date when segment is assigned."""
    if created:
        client = instance.client
        client.last_activity_date = timezone.now()
        # Save without triggering signals again
        Client.objects.filter(pk=client.pk).update(last_activity_date=timezone.now())


@receiver(pre_save, sender=ClientContact)
def ensure_single_primary_contact(sender, instance, **kwargs):
    """Ensure only one primary contact per client."""
    if instance.is_primary:
        # Remove primary status from other contacts of the same client
        ClientContact.objects.filter(
            client=instance.client,
            is_primary=True
        ).exclude(pk=instance.pk).update(is_primary=False)


@receiver(pre_save, sender=Client)
def set_default_assigned_to(sender, instance, **kwargs):
    """Set default assigned_to if not provided."""
    if not instance.assigned_to and instance.created_by:
        instance.assigned_to = instance.created_by


@receiver(pre_save, sender=Client)
def validate_client_type_data(sender, instance, **kwargs):
    """Validate that client has appropriate type-specific data."""
    if instance.client_type == 'individual':
        # Ensure individual client data exists
        if not hasattr(instance, 'individual_client') or not instance.individual_client:
            # This will be handled by the serializer or view
            pass
    elif instance.client_type == 'corporate':
        # Ensure corporate client data exists
        if not hasattr(instance, 'corporate_client') or not instance.corporate_client:
            # This will be handled by the serializer or view
            pass


@receiver(post_save, sender=Client)
def create_type_specific_client(sender, instance, created, **kwargs):
    """Create type-specific client data if it doesn't exist."""
    if created:
        if instance.client_type == 'individual':
            # Check if individual client data already exists
            if not hasattr(instance, 'individual_client'):
                # This will be handled by the serializer
                pass
        elif instance.client_type == 'corporate':
            # Check if corporate client data already exists
            if not hasattr(instance, 'corporate_client'):
                # This will be handled by the serializer
                pass


@receiver(post_save, sender=ClientInteraction)
def create_follow_up_note(sender, instance, created, **kwargs):
    """Create a follow-up note if interaction requires follow-up."""
    if created and instance.requires_follow_up and instance.follow_up_date:
        # Create a note for the follow-up
        ClientNote.objects.create(
            client=instance.client,
            note_type='follow_up',
            title=f'Follow-up required: {instance.subject}',
            content=f'Follow-up required for interaction: {instance.subject}\n'
                   f'Follow-up date: {instance.follow_up_date}\n'
                   f'Notes: {instance.follow_up_notes}',
            related_date=instance.follow_up_date
        )


@receiver(post_save, sender=ClientDocument)
def check_document_expiry(sender, instance, created, **kwargs):
    """Check if document is expiring soon and create a note."""
    if created and instance.expiry_date:
        # Check if document expires within 30 days
        if instance.expiry_date <= timezone.now().date() + timedelta(days=30):
            ClientNote.objects.create(
                client=instance.client,
                note_type='general',
                title=f'Document expiring soon: {instance.title}',
                content=f'Document "{instance.title}" expires on {instance.expiry_date}. '
                       f'Please review and renew if necessary.',
                related_date=instance.expiry_date
            )


@receiver(pre_save, sender=Client)
def update_client_status_based_on_activity(sender, instance, **kwargs):
    """Update client status based on activity."""
    if not instance.pk:  # New client
        return
    
    # Get the original instance from database
    try:
        original = Client.objects.get(pk=instance.pk)
    except Client.DoesNotExist:
        return
    
    # If client was inactive and has recent activity, consider making them active
    if (original.status == 'inactive' and 
        instance.last_activity_date and 
        instance.last_activity_date > timezone.now() - timedelta(days=30)):
        # Don't automatically change status, but could add logic here
        pass


@receiver(post_save, sender=ClientNote)
def notify_important_notes(sender, instance, created, **kwargs):
    """Create notifications for important notes."""
    if created:
        # Check if note is marked as important (contains keywords)
        important_keywords = ['urgent', 'important', 'critical', 'asap', 'emergency']
        note_content = instance.content.lower()
        
        if any(keyword in note_content for keyword in important_keywords):
            # Create a high-priority note or notification
            # This could be extended to send emails or create notifications
            pass


@receiver(post_save, sender=Client)
def assign_default_tags(sender, instance, created, **kwargs):
    """Assign default tags based on client type and status."""
    if created:
        # Assign client type tag
        type_tag, _ = ClientTag.objects.get_or_create(
            name=f"{instance.client_type.title()} Client",
            defaults={
                'color': '#007bff' if instance.client_type == 'individual' else '#28a745',
                'description': f'Default tag for {instance.client_type} clients'
            }
        )
        
        # Assign status tag
        status_tag, _ = ClientTag.objects.get_or_create(
            name=f"{instance.status.title()} Status",
            defaults={
                'color': '#ffc107' if instance.status == 'prospect' else '#28a745',
                'description': f'Default tag for {instance.status} clients'
            }
        )
        
        # Create tag assignments
        ClientTagAssignment.objects.get_or_create(
            client=instance,
            tag=type_tag,
            defaults={'assigned_by': instance.created_by}
        )
        
        ClientTagAssignment.objects.get_or_create(
            client=instance,
            tag=status_tag,
            defaults={'assigned_by': instance.created_by}
        )


@receiver(post_save, sender=Client)
def create_welcome_interaction(sender, instance, created, **kwargs):
    """Create a welcome interaction for new clients."""
    if created:
        ClientInteraction.objects.create(
            client=instance,
            interaction_type='other',
            subject='Welcome to our services',
            description=f'New {instance.client_type} client added to the system.',
            initiated_by=instance.created_by,
            outcome='Client onboarded successfully'
        )


@receiver(post_delete, sender=ClientTagAssignment)
def update_client_activity_on_tag_removal(sender, instance, **kwargs):
    """Update client's last activity date when tag is removed."""
    client = instance.client
    client.last_activity_date = timezone.now()
    # Save without triggering signals again
    Client.objects.filter(pk=client.pk).update(last_activity_date=timezone.now())


@receiver(post_delete, sender=ClientSegmentAssignment)
def update_client_activity_on_segment_removal(sender, instance, **kwargs):
    """Update client's last activity date when segment is removed."""
    client = instance.client
    client.last_activity_date = timezone.now()
    # Save without triggering signals again
    Client.objects.filter(pk=client.pk).update(last_activity_date=timezone.now())


@receiver(post_delete, sender=ClientContact)
def update_client_activity_on_contact_removal(sender, instance, **kwargs):
    """Update client's last activity date when contact is removed."""
    client = instance.client
    client.last_activity_date = timezone.now()
    # Save without triggering signals again
    Client.objects.filter(pk=client.pk).update(last_activity_date=timezone.now())


@receiver(post_delete, sender=ClientNote)
def update_client_activity_on_note_removal(sender, instance, **kwargs):
    """Update client's last activity date when note is removed."""
    client = instance.client
    client.last_activity_date = timezone.now()
    # Save without triggering signals again
    Client.objects.filter(pk=client.pk).update(last_activity_date=timezone.now())


@receiver(post_delete, sender=ClientDocument)
def update_client_activity_on_document_removal(sender, instance, **kwargs):
    """Update client's last activity date when document is removed."""
    client = instance.client
    client.last_activity_date = timezone.now()
    # Save without triggering signals again
    Client.objects.filter(pk=client.pk).update(last_activity_date=timezone.now())
