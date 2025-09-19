"""
DID Authentication Signals

Django signals for DID-based authentication system.
"""

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
import logging

from .models import DIDDocument, DIDRole, DIDCredential, DIDSession

logger = logging.getLogger(__name__)


@receiver(post_save, sender=DIDDocument)
def did_document_created(sender, instance, created, **kwargs):
    """
    Signal handler for when a DID document is created or updated.
    """
    if created:
        logger.info(f"New DID document created: {instance.did}")
        # Log the creation in audit trail
        from apps.audit_trail.services import AuditService
        audit_service = AuditService()
        audit_service.capture_event(
            event_type='did_created',
            module='did_auth',
            object_type='DIDDocument',
            object_id=instance.did,
            data={
                'did': instance.did,
                'controller': instance.controller,
                'status': instance.status
            }
        )
    else:
        logger.info(f"DID document updated: {instance.did}")
        # Log the update in audit trail
        from apps.audit_trail.services import AuditService
        audit_service = AuditService()
        audit_service.capture_event(
            event_type='did_updated',
            module='did_auth',
            object_type='DIDDocument',
            object_id=instance.did,
            data={
                'did': instance.did,
                'controller': instance.controller,
                'status': instance.status,
                'updated_at': instance.updated_at.isoformat()
            }
        )


@receiver(post_save, sender=DIDRole)
def did_role_created(sender, instance, created, **kwargs):
    """
    Signal handler for when a DID role is created or updated.
    """
    if created:
        logger.info(f"New DID role created: {instance.did.did} - {instance.role_name}")
        # Log the role creation in audit trail
        from apps.audit_trail.services import AuditService
        audit_service = AuditService()
        audit_service.capture_event(
            event_type='did_role_created',
            module='did_auth',
            object_type='DIDRole',
            object_id=str(instance.id),
            data={
                'did': instance.did.did,
                'role_name': instance.role_name,
                'granted_by': instance.granted_by,
                'permissions': instance.permissions
            }
        )


@receiver(post_save, sender=DIDCredential)
def did_credential_created(sender, instance, created, **kwargs):
    """
    Signal handler for when a DID credential is created or updated.
    """
    if created:
        logger.info(f"New DID credential created: {instance.did.did} - {instance.credential_type}")
        # Log the credential creation in audit trail
        from apps.audit_trail.services import AuditService
        audit_service = AuditService()
        audit_service.capture_event(
            event_type='did_credential_created',
            module='did_auth',
            object_type='DIDCredential',
            object_id=str(instance.id),
            data={
                'did': instance.did.did,
                'credential_type': instance.credential_type,
                'issuer': instance.issuer
            }
        )


@receiver(post_save, sender=DIDSession)
def did_session_created(sender, instance, created, **kwargs):
    """
    Signal handler for when a DID session is created.
    """
    if created:
        logger.info(f"New DID session created: {instance.did.did}")
        # Log the session creation in audit trail
        from apps.audit_trail.services import AuditService
        audit_service = AuditService()
        audit_service.capture_event(
            event_type='did_session_created',
            module='did_auth',
            object_type='DIDSession',
            object_id=str(instance.id),
            data={
                'did': instance.did.did,
                'ip_address': str(instance.ip_address) if instance.ip_address else None,
                'user_agent': instance.user_agent,
                'expires_at': instance.expires_at.isoformat()
            }
        )


@receiver(pre_delete, sender=DIDDocument)
def did_document_deleted(sender, instance, **kwargs):
    """
    Signal handler for when a DID document is deleted.
    """
    logger.info(f"DID document deleted: {instance.did}")
    # Log the deletion in audit trail
    from apps.audit_trail.services import AuditService
    audit_service = AuditService()
    audit_service.log_event(
        event_type='did_deleted',
        actor=None,  # System event
        entity_type='DIDDocument',
        entity_id=instance.did,
        event_data={
            'did': instance.did,
            'controller': instance.controller,
            'status': instance.status,
            'deleted_at': timezone.now().isoformat()
        }
    )


@receiver(pre_delete, sender=DIDRole)
def did_role_deleted(sender, instance, **kwargs):
    """
    Signal handler for when a DID role is deleted.
    """
    logger.info(f"DID role deleted: {instance.did.did} - {instance.role_name}")
    # Log the role deletion in audit trail
    from apps.audit_trail.services import AuditService
    audit_service = AuditService()
    audit_service.log_event(
        event_type='did_role_deleted',
        actor=None,  # System event
        entity_type='DIDRole',
        entity_id=str(instance.id),
        event_data={
            'did': instance.did.did,
            'role_name': instance.role_name,
            'granted_by': instance.granted_by,
            'deleted_at': timezone.now().isoformat()
        }
    )


@receiver(pre_delete, sender=DIDCredential)
def did_credential_deleted(sender, instance, **kwargs):
    """
    Signal handler for when a DID credential is deleted.
    """
    logger.info(f"DID credential deleted: {instance.did.did} - {instance.credential_type}")
    # Log the credential deletion in audit trail
    from apps.audit_trail.services import AuditService
    audit_service = AuditService()
    audit_service.log_event(
        event_type='did_credential_deleted',
        actor=None,  # System event
        entity_type='DIDCredential',
        entity_id=str(instance.id),
        event_data={
            'did': instance.did.did,
            'credential_type': instance.credential_type,
            'issuer': instance.issuer,
            'deleted_at': timezone.now().isoformat()
        }
    )


@receiver(pre_delete, sender=DIDSession)
def did_session_deleted(sender, instance, **kwargs):
    """
    Signal handler for when a DID session is deleted.
    """
    logger.info(f"DID session deleted: {instance.did.did}")
    # Log the session deletion in audit trail
    from apps.audit_trail.services import AuditService
    audit_service = AuditService()
    audit_service.log_event(
        event_type='did_session_deleted',
        actor=None,  # System event
        entity_type='DIDSession',
        entity_id=str(instance.id),
        event_data={
            'did': instance.did.did,
            'ip_address': str(instance.ip_address) if instance.ip_address else None,
            'deleted_at': timezone.now().isoformat()
        }
    )
