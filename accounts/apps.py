from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    
    def ready(self):
        try:
            import accounts.signals  # noqa
        except ImportError:
            # During initial setup/migration, this might fail
            # as models aren't created yet, which is fine
            pass