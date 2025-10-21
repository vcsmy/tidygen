"""
Gig Management app configuration for TidyGen ERP Community Edition.
Handles job posting, assignment, and tracking for freelancers.
"""
from django.apps import AppConfig


class GigManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.gig_management'
    verbose_name = 'Gig Management'

    def ready(self):
        import apps.gig_management.signals
