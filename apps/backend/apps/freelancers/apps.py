"""
Freelancers app configuration for TidyGen ERP Community Edition.
"""
from django.apps import AppConfig


class FreelancersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.freelancers'
    verbose_name = 'Freelancers & Contractors'

    def ready(self):
        import apps.freelancers.signals
