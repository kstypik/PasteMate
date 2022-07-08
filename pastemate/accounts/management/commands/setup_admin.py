from django.core.management.base import BaseCommand

from config.settings.base import env
from pastemate.accounts.models import User


class Command(BaseCommand):
    help = "Sets up admin account"

    def handle(self, *args, **options):
        User.objects.create_superuser(
            username="Admin",
            email="admin@example.com",
            password=env("DJANGO_DEMO_ADMIN_PASS"),
        )

        self.stdout.write("Admin account created.")
