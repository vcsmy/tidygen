from django.apps import AppConfig


class Web3Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.web3'
    verbose_name = 'Web3 & Blockchain Integration'

    def ready(self):
        import apps.web3.signals
