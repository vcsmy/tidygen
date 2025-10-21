"""
Freelancer Web3 app configuration for TidyGen ERP Community Edition.
Handles advanced Web3 features for freelancers including NFT badges, smart contracts, and decentralized reputation.
"""
from django.apps import AppConfig


class FreelancerWeb3Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.freelancer_web3'
    verbose_name = 'Freelancer Web3'

    def ready(self):
        import apps.freelancer_web3.signals
