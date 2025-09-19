"""
Audit Trail Signals

Django signals for automatically capturing audit events from other modules.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from apps.audit_trail.services import AuditService

User = get_user_model()


@receiver(post_save, sender=User)
def capture_user_event(sender, instance, created, **kwargs):
    """Capture user-related events."""
    try:
        event_type = 'user_created' if created else 'user_updated'
        AuditService().capture_event(
            event_type=event_type,
            module='system',
            object_id=str(instance.id),
            object_type='User',
            data={
                'user_id': instance.id,
                'username': instance.username,
                'email': instance.email,
                'is_active': instance.is_active,
                'is_staff': instance.is_staff,
                'is_superuser': instance.is_superuser,
            },
            user=instance
        )
    except Exception as e:
        # Log error but don't fail the original operation
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to capture user event: {e}")


@receiver(post_delete, sender=User)
def capture_user_deletion(sender, instance, **kwargs):
    """Capture user deletion events."""
    try:
        AuditService().capture_event(
            event_type='user_deleted',
            module='system',
            object_id=str(instance.id),
            object_type='User',
            data={
                'user_id': instance.id,
                'username': instance.username,
                'email': instance.email,
            }
        )
    except Exception as e:
        # Log error but don't fail the original operation
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to capture user deletion event: {e}")


# Finance module signals
try:
    from apps.finance.models import Invoice, Payment, Expense
    
    @receiver(post_save, sender=Invoice)
    def capture_invoice_event(sender, instance, created, **kwargs):
        """Capture invoice events."""
        try:
            event_type = 'invoice_created' if created else 'invoice_updated'
            AuditService().capture_event(
                event_type=event_type,
                module='finance',
                object_id=str(instance.id),
                object_type='Invoice',
                data={
                    'invoice_id': instance.id,
                    'invoice_number': getattr(instance, 'invoice_number', ''),
                    'amount': getattr(instance, 'amount', 0),
                    'status': getattr(instance, 'status', ''),
                    'client_id': getattr(instance, 'client_id', None),
                },
                user=getattr(instance, 'created_by', None)
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to capture invoice event: {e}")
    
    @receiver(post_save, sender=Payment)
    def capture_payment_event(sender, instance, created, **kwargs):
        """Capture payment events."""
        try:
            event_type = 'payment_created' if created else 'payment_updated'
            AuditService().capture_event(
                event_type=event_type,
                module='finance',
                object_id=str(instance.id),
                object_type='Payment',
                data={
                    'payment_id': instance.id,
                    'amount': getattr(instance, 'amount', 0),
                    'status': getattr(instance, 'status', ''),
                    'payment_method': getattr(instance, 'payment_method', ''),
                    'invoice_id': getattr(instance, 'invoice_id', None),
                },
                user=getattr(instance, 'created_by', None)
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to capture payment event: {e}")
    
    @receiver(post_save, sender=Expense)
    def capture_expense_event(sender, instance, created, **kwargs):
        """Capture expense events."""
        try:
            event_type = 'expense_created' if created else 'expense_updated'
            AuditService().capture_event(
                event_type=event_type,
                module='finance',
                object_id=str(instance.id),
                object_type='Expense',
                data={
                    'expense_id': instance.id,
                    'amount': getattr(instance, 'amount', 0),
                    'status': getattr(instance, 'status', ''),
                    'category': getattr(instance, 'category', ''),
                    'description': getattr(instance, 'description', ''),
                },
                user=getattr(instance, 'created_by', None)
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to capture expense event: {e}")

except ImportError:
    # Finance module not available
    pass


# Sales module signals
try:
    from apps.sales.models import Client, Sale
    
    @receiver(post_save, sender=Client)
    def capture_client_event(sender, instance, created, **kwargs):
        """Capture client events."""
        try:
            event_type = 'client_created' if created else 'client_updated'
            AuditService().capture_event(
                event_type=event_type,
                module='sales',
                object_id=str(instance.id),
                object_type='Client',
                data={
                    'client_id': instance.id,
                    'name': getattr(instance, 'name', ''),
                    'email': getattr(instance, 'email', ''),
                    'phone': getattr(instance, 'phone', ''),
                    'status': getattr(instance, 'status', ''),
                },
                user=getattr(instance, 'created_by', None)
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to capture client event: {e}")
    
    @receiver(post_save, sender=Sale)
    def capture_sale_event(sender, instance, created, **kwargs):
        """Capture sale events."""
        try:
            event_type = 'sale_created' if created else 'sale_updated'
            AuditService().capture_event(
                event_type=event_type,
                module='sales',
                object_id=str(instance.id),
                object_type='Sale',
                data={
                    'sale_id': instance.id,
                    'amount': getattr(instance, 'amount', 0),
                    'status': getattr(instance, 'status', ''),
                    'client_id': getattr(instance, 'client_id', None),
                },
                user=getattr(instance, 'created_by', None)
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to capture sale event: {e}")

except ImportError:
    # Sales module not available
    pass


# HR module signals
try:
    from apps.hr.models import Employee, Payroll
    
    @receiver(post_save, sender=Employee)
    def capture_employee_event(sender, instance, created, **kwargs):
        """Capture employee events."""
        try:
            event_type = 'employee_created' if created else 'employee_updated'
            AuditService().capture_event(
                event_type=event_type,
                module='hr',
                object_id=str(instance.id),
                object_type='Employee',
                data={
                    'employee_id': instance.id,
                    'name': getattr(instance, 'name', ''),
                    'email': getattr(instance, 'email', ''),
                    'position': getattr(instance, 'position', ''),
                    'status': getattr(instance, 'status', ''),
                },
                user=getattr(instance, 'created_by', None)
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to capture employee event: {e}")
    
    @receiver(post_save, sender=Payroll)
    def capture_payroll_event(sender, instance, created, **kwargs):
        """Capture payroll events."""
        try:
            event_type = 'payroll_processed' if created else 'payroll_updated'
            AuditService().capture_event(
                event_type=event_type,
                module='hr',
                object_id=str(instance.id),
                object_type='Payroll',
                data={
                    'payroll_id': instance.id,
                    'amount': getattr(instance, 'amount', 0),
                    'status': getattr(instance, 'status', ''),
                    'employee_id': getattr(instance, 'employee_id', None),
                    'period': getattr(instance, 'period', ''),
                },
                user=getattr(instance, 'created_by', None)
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to capture payroll event: {e}")

except ImportError:
    # HR module not available
    pass


# Wallet module signals
try:
    from apps.wallet.models import Wallet
    
    @receiver(post_save, sender=Wallet)
    def capture_wallet_event(sender, instance, created, **kwargs):
        """Capture wallet events."""
        try:
            event_type = 'wallet_connected' if created else 'wallet_updated'
            AuditService().capture_event(
                event_type=event_type,
                module='wallet',
                object_id=str(instance.id),
                object_type='Wallet',
                data={
                    'wallet_id': instance.id,
                    'address': instance.address,
                    'wallet_type': instance.wallet_type,
                    'chain_type': instance.chain_type,
                    'network_name': instance.network_name,
                    'is_primary': instance.is_primary,
                    'is_verified': instance.is_verified,
                },
                user=instance.user
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to capture wallet event: {e}")

except ImportError:
    # Wallet module not available
    pass
