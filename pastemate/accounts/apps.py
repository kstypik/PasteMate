from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pastemate.accounts"

    def ready(self):
        import pastemate.accounts.signals  # noqa
