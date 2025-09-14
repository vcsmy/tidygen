"""
Scheduling app configuration for TidyGen ERP platform.
"""
from django.apps import AppConfig


class SchedulingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.scheduling'
    verbose_name = 'Scheduling Management'

    def ready(self):
        import apps.scheduling.signals
