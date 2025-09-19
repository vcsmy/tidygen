from django.apps import AppConfig


class DidAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.did_auth'
    verbose_name = 'DID Authentication'

    def ready(self):
        import apps.did_auth.signals  # noqa