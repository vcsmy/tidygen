"""
Wallet App Configuration

This module configures the wallet Django application,
including app metadata and signal registration.
"""

from django.apps import AppConfig


class WalletConfig(AppConfig):
    """
    Configuration for the wallet application.
    
    This class configures the wallet app with proper metadata
    and handles signal registration for wallet-related events.
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.wallet'
    verbose_name = 'Wallet Management'
    
    def ready(self):
        """
        Initialize the wallet app.
        
        This method is called when Django starts up and is used
        to register signals and perform other initialization tasks.
        """
        # Import signals to ensure they are registered
        try:
            import apps.wallet.signals
        except ImportError:
            pass
