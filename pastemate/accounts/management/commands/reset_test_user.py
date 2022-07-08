from django.core.management.base import BaseCommand

from pastemate.accounts.models import User


class Command(BaseCommand):
    help = "Resets test account"

    def handle(self, *args, **options):
        test_account, created = User.objects.get_or_create(id=2)
        if not created:
            test_account.username = "test"
            test_account.email = "test@example.com"
            test_account.set_password("test12")
            test_account.location = "Testland"
            test_account.website = "https://example.com"
            test_account.avatar = "default_avatar.png"

        test_account.save()

        self.stdout.write("Test account reset.")
