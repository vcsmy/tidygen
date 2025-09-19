"""
Smart Contract Ledger Signal Handlers

This module defines signal handlers for automatically logging transactions
from other ERP modules to the blockchain ledger.
"""

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings

logger = logging.getLogger(__name__)


@receiver(post_save, sender=None)
def log_finance_transaction(sender, instance, created, **kwargs):
    """
    Signal handler for logging finance transactions.
    
    This handler automatically logs invoices and payments to the blockchain ledger.
    """
    try:
        # Check if this is a finance-related model
        if not hasattr(instance, '_meta') or not instance._meta.app_label == 'finance':
            return
        
        # Skip if ledger logging is disabled
        if not getattr(settings, 'LEDGER_AUTO_LOG_ENABLED', True):
            return
        
        # Import here to avoid circular imports
        from .services import TransactionService
        from .models import LedgerTransaction
        
        # Determine transaction type and data
        if instance._meta.model_name == 'invoice':
            transaction_type = 'invoice'
            transaction_data = {
                'amount': float(instance.total_amount or 0),
                'currency': instance.currency or 'USD',
                'description': f"Invoice {instance.invoice_number}",
                'invoice_number': instance.invoice_number,
                'client_name': instance.client.name if hasattr(instance, 'client') and instance.client else None,
                'due_date': instance.due_date.isoformat() if instance.due_date else None,
                'status': instance.status,
                'created_by': instance.created_by.username if hasattr(instance, 'created_by') and instance.created_by else None
            }
        elif instance._meta.model_name == 'payment':
            transaction_type = 'payment'
            transaction_data = {
                'amount': float(instance.amount or 0),
                'currency': instance.currency or 'USD',
                'description': f"Payment for {instance.invoice.invoice_number if hasattr(instance, 'invoice') and instance.invoice else 'Unknown'}",
                'payment_method': instance.payment_method,
                'payment_date': instance.payment_date.isoformat() if instance.payment_date else None,
                'reference_number': instance.reference_number,
                'status': instance.status,
                'created_by': instance.created_by.username if hasattr(instance, 'created_by') and instance.created_by else None
            }
        else:
            # Skip other finance models
            return
        
        # Get organization from instance
        organization_id = None
        if hasattr(instance, 'organization'):
            organization_id = str(instance.organization.id)
        elif hasattr(instance, 'client') and hasattr(instance.client, 'organization'):
            organization_id = str(instance.client.organization.id)
        
        if not organization_id:
            logger.warning(f"No organization found for {instance._meta.model_name} {instance.id}")
            return
        
        # Check if transaction already exists
        existing_transaction = LedgerTransaction.objects.filter(
            source_module='finance',
            source_id=str(instance.id),
            organization_id=organization_id
        ).first()
        
        if existing_transaction:
            logger.info(f"Transaction already exists for {instance._meta.model_name} {instance.id}")
            return
        
        # Create ledger transaction
        transaction_service = TransactionService(organization_id=organization_id)
        
        ledger_transaction = transaction_service.create_transaction(
            transaction_type=transaction_type,
            source_module='finance',
            source_id=str(instance.id),
            transaction_data=transaction_data,
            organization_id=organization_id
        )
        
        logger.info(f"Logged {transaction_type} transaction {instance.id} to ledger")
        
    except Exception as e:
        logger.error(f"Failed to log finance transaction: {e}")


@receiver(post_save, sender=None)
def log_sales_transaction(sender, instance, created, **kwargs):
    """
    Signal handler for logging sales transactions.
    
    This handler automatically logs sales orders to the blockchain ledger.
    """
    try:
        # Check if this is a sales-related model
        if not hasattr(instance, '_meta') or not instance._meta.app_label == 'sales':
            return
        
        # Skip if ledger logging is disabled
        if not getattr(settings, 'LEDGER_AUTO_LOG_ENABLED', True):
            return
        
        # Import here to avoid circular imports
        from .services import TransactionService
        from .models import LedgerTransaction
        
        # Determine transaction type and data
        if instance._meta.model_name == 'salesorder':
            transaction_type = 'sales_order'
            transaction_data = {
                'amount': float(instance.total_amount or 0),
                'currency': instance.currency or 'USD',
                'description': f"Sales Order {instance.order_number}",
                'order_number': instance.order_number,
                'client_name': instance.client.name if hasattr(instance, 'client') and instance.client else None,
                'order_date': instance.order_date.isoformat() if instance.order_date else None,
                'status': instance.status,
                'created_by': instance.created_by.username if hasattr(instance, 'created_by') and instance.created_by else None
            }
        else:
            # Skip other sales models
            return
        
        # Get organization from instance
        organization_id = None
        if hasattr(instance, 'organization'):
            organization_id = str(instance.organization.id)
        elif hasattr(instance, 'client') and hasattr(instance.client, 'organization'):
            organization_id = str(instance.client.organization.id)
        
        if not organization_id:
            logger.warning(f"No organization found for {instance._meta.model_name} {instance.id}")
            return
        
        # Check if transaction already exists
        existing_transaction = LedgerTransaction.objects.filter(
            source_module='sales',
            source_id=str(instance.id),
            organization_id=organization_id
        ).first()
        
        if existing_transaction:
            logger.info(f"Transaction already exists for {instance._meta.model_name} {instance.id}")
            return
        
        # Create ledger transaction
        transaction_service = TransactionService(organization_id=organization_id)
        
        ledger_transaction = transaction_service.create_transaction(
            transaction_type=transaction_type,
            source_module='sales',
            source_id=str(instance.id),
            transaction_data=transaction_data,
            organization_id=organization_id
        )
        
        logger.info(f"Logged {transaction_type} transaction {instance.id} to ledger")
        
    except Exception as e:
        logger.error(f"Failed to log sales transaction: {e}")


@receiver(post_save, sender=None)
def log_purchasing_transaction(sender, instance, created, **kwargs):
    """
    Signal handler for logging purchasing transactions.
    
    This handler automatically logs purchase orders to the blockchain ledger.
    """
    try:
        # Check if this is a purchasing-related model
        if not hasattr(instance, '_meta') or not instance._meta.app_label == 'purchasing':
            return
        
        # Skip if ledger logging is disabled
        if not getattr(settings, 'LEDGER_AUTO_LOG_ENABLED', True):
            return
        
        # Import here to avoid circular imports
        from .services import TransactionService
        from .models import LedgerTransaction
        
        # Determine transaction type and data
        if instance._meta.model_name == 'purchaseorder':
            transaction_type = 'purchase_order'
            transaction_data = {
                'amount': float(instance.total_amount or 0),
                'currency': instance.currency or 'USD',
                'description': f"Purchase Order {instance.po_number}",
                'po_number': instance.po_number,
                'supplier_name': instance.supplier.name if hasattr(instance, 'supplier') and instance.supplier else None,
                'order_date': instance.order_date.isoformat() if instance.order_date else None,
                'status': instance.status,
                'created_by': instance.created_by.username if hasattr(instance, 'created_by') and instance.created_by else None
            }
        else:
            # Skip other purchasing models
            return
        
        # Get organization from instance
        organization_id = None
        if hasattr(instance, 'organization'):
            organization_id = str(instance.organization.id)
        elif hasattr(instance, 'supplier') and hasattr(instance.supplier, 'organization'):
            organization_id = str(instance.supplier.organization.id)
        
        if not organization_id:
            logger.warning(f"No organization found for {instance._meta.model_name} {instance.id}")
            return
        
        # Check if transaction already exists
        existing_transaction = LedgerTransaction.objects.filter(
            source_module='purchasing',
            source_id=str(instance.id),
            organization_id=organization_id
        ).first()
        
        if existing_transaction:
            logger.info(f"Transaction already exists for {instance._meta.model_name} {instance.id}")
            return
        
        # Create ledger transaction
        transaction_service = TransactionService(organization_id=organization_id)
        
        ledger_transaction = transaction_service.create_transaction(
            transaction_type=transaction_type,
            source_module='purchasing',
            source_id=str(instance.id),
            transaction_data=transaction_data,
            organization_id=organization_id
        )
        
        logger.info(f"Logged {transaction_type} transaction {instance.id} to ledger")
        
    except Exception as e:
        logger.error(f"Failed to log purchasing transaction: {e}")


@receiver(post_save, sender=None)
def log_payroll_transaction(sender, instance, created, **kwargs):
    """
    Signal handler for logging payroll transactions.
    
    This handler automatically logs payroll records to the blockchain ledger.
    """
    try:
        # Check if this is a payroll-related model
        if not hasattr(instance, '_meta') or not instance._meta.app_label == 'payroll':
            return
        
        # Skip if ledger logging is disabled
        if not getattr(settings, 'LEDGER_AUTO_LOG_ENABLED', True):
            return
        
        # Import here to avoid circular imports
        from .services import TransactionService
        from .models import LedgerTransaction
        
        # Determine transaction type and data
        if instance._meta.model_name == 'payroll':
            transaction_type = 'payroll'
            transaction_data = {
                'amount': float(instance.gross_pay or 0),
                'currency': instance.currency or 'USD',
                'description': f"Payroll for {instance.employee.name if hasattr(instance, 'employee') and instance.employee else 'Unknown'}",
                'employee_name': instance.employee.name if hasattr(instance, 'employee') and instance.employee else None,
                'pay_period_start': instance.pay_period_start.isoformat() if instance.pay_period_start else None,
                'pay_period_end': instance.pay_period_end.isoformat() if instance.pay_period_end else None,
                'status': instance.status,
                'created_by': instance.created_by.username if hasattr(instance, 'created_by') and instance.created_by else None
            }
        else:
            # Skip other payroll models
            return
        
        # Get organization from instance
        organization_id = None
        if hasattr(instance, 'organization'):
            organization_id = str(instance.organization.id)
        elif hasattr(instance, 'employee') and hasattr(instance.employee, 'organization'):
            organization_id = str(instance.employee.organization.id)
        
        if not organization_id:
            logger.warning(f"No organization found for {instance._meta.model_name} {instance.id}")
            return
        
        # Check if transaction already exists
        existing_transaction = LedgerTransaction.objects.filter(
            source_module='payroll',
            source_id=str(instance.id),
            organization_id=organization_id
        ).first()
        
        if existing_transaction:
            logger.info(f"Transaction already exists for {instance._meta.model_name} {instance.id}")
            return
        
        # Create ledger transaction
        transaction_service = TransactionService(organization_id=organization_id)
        
        ledger_transaction = transaction_service.create_transaction(
            transaction_type=transaction_type,
            source_module='payroll',
            source_id=str(instance.id),
            transaction_data=transaction_data,
            organization_id=organization_id
        )
        
        logger.info(f"Logged {transaction_type} transaction {instance.id} to ledger")
        
    except Exception as e:
        logger.error(f"Failed to log payroll transaction: {e}")


def register_ledger_signals():
    """
    Register all ledger signal handlers.
    
    This function can be called to manually register signal handlers
    if automatic registration fails.
    """
    try:
        # Import models to register signals
        from apps.finance.models import Invoice, Payment
        from apps.sales.models import SalesOrder
        from apps.purchasing.models import PurchaseOrder
        from apps.payroll.models import Payroll
        
        # Connect signal handlers
        post_save.connect(
            log_finance_transaction,
            sender=Invoice,
            dispatch_uid='ledger_invoice_save_manual'
        )
        
        post_save.connect(
            log_finance_transaction,
            sender=Payment,
            dispatch_uid='ledger_payment_save_manual'
        )
        
        post_save.connect(
            log_sales_transaction,
            sender=SalesOrder,
            dispatch_uid='ledger_sales_save_manual'
        )
        
        post_save.connect(
            log_purchasing_transaction,
            sender=PurchaseOrder,
            dispatch_uid='ledger_purchasing_save_manual'
        )
        
        post_save.connect(
            log_payroll_transaction,
            sender=Payroll,
            dispatch_uid='ledger_payroll_save_manual'
        )
        
        logger.info("Ledger signal handlers registered successfully")
        
    except ImportError as e:
        logger.warning(f"Could not register ledger signals: {e}")
    except Exception as e:
        logger.error(f"Failed to register ledger signals: {e}")
