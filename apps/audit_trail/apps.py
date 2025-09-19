"""
Audit Trail App Configuration

Django app configuration for the audit trail system.
"""

from django.apps import AppConfig


class AuditTrailConfig(AppConfig):
    """Configuration for the audit trail app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.audit_trail'
    verbose_name = 'Audit Trail'
    
    def ready(self):
        """Import signals when the app is ready."""
        try:
            import apps.audit_trail.signals
        except ImportError:
            pass
