from django.core.management.base import BaseCommand

from accounts.models import User


class Command(BaseCommand):
    help = "Resets test account"

    def handle(self, *args, **options):
        defaults = {
            "username": "test",
            "email": "test@example.com",
            "location": "Testland",
            "website": "https://example.com",
        }
        test_account, created = User.objects.get_or_create(id=2, defaults=defaults)
        test_account.set_password("test12")
        test_account.save()

        self.stdout.write("Test account reset.")
