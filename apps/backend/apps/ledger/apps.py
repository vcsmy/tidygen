"""
Smart Contract Ledger Django App Configuration

This module configures the ledger Django app and sets up signal handlers
for automatic transaction logging from other modules.
"""

from django.apps import AppConfig
from django.db.models.signals import post_save, post_delete


class LedgerConfig(AppConfig):
    """Configuration for the ledger Django app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ledger'
    verbose_name = 'Smart Contract Ledger'
    
    def ready(self):
        """Initialize the app when Django starts."""
        # Import signal handlers
        from . import signals
        
        # Register signal handlers for automatic transaction logging
        self._register_signal_handlers()
    
    def _register_signal_handlers(self):
        """Register signal handlers for automatic transaction logging."""
        try:
            # Import models to avoid circular imports
            from apps.finance.models import Invoice, Payment
            from apps.sales.models import SalesOrder
            from apps.purchasing.models import PurchaseOrder
            
            # Connect signal handlers
            post_save.connect(
                signals.log_finance_transaction,
                sender=Invoice,
                dispatch_uid='ledger_invoice_save'
            )
            
            post_save.connect(
                signals.log_finance_transaction,
                sender=Payment,
                dispatch_uid='ledger_payment_save'
            )
            
            post_save.connect(
                signals.log_sales_transaction,
                sender=SalesOrder,
                dispatch_uid='ledger_sales_save'
            )
            
            post_save.connect(
                signals.log_purchasing_transaction,
                sender=PurchaseOrder,
                dispatch_uid='ledger_purchasing_save'
            )
            
        except ImportError:
            # Models not available yet, signals will be registered later
            pass
