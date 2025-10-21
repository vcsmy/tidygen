"""
Contractor Payments app configuration for TidyGen ERP Community Edition.
Handles payment processing, escrow, and Web3 payments for freelancers.
"""
from django.apps import AppConfig


class ContractorPaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.contractor_payments'
    verbose_name = 'Contractor Payments'

    def ready(self):
        import apps.contractor_payments.signals
