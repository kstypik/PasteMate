import datetime
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from ..models import Paste


class ExpirePastesCommandTest(TestCase):
    def setUp(self):
        self.paste_to_delete = Paste.objects.create(
            content="Hi",
            expiration_date=datetime.datetime(
                2020, 1, 1, 12, 00, tzinfo=datetime.timezone.utc
            ),
        )
        self.paste_to_delete2 = Paste.objects.create(
            content="Hi",
            expiration_date=datetime.datetime(
                2020, 1, 1, 12, 00, tzinfo=datetime.timezone.utc
            ),
        )
        self.paste_to_delete3 = Paste.objects.create(
            content="Hi",
            expiration_date=datetime.datetime(
                2020, 1, 1, 12, 00, tzinfo=datetime.timezone.utc
            ),
        )

        self.paste_not_for_deletion = Paste.objects.create(content="Hi")
        self.paste_not_for_deletion2 = Paste.objects.create(content="Hi")

    def test_show_pastes_scheduled_for_expiring(self):
        out = StringIO()
        call_command("expire_pastes", only_show=True, stdout=out)

        self.assertIn(
            f"{self.paste_to_delete.uuid} - {self.paste_to_delete.title}",
            out.getvalue(),
        )
        self.assertIn(
            f"{self.paste_to_delete2.uuid} - {self.paste_to_delete2.title}",
            out.getvalue(),
        )
        self.assertIn(
            f"{self.paste_to_delete3.uuid} - {self.paste_to_delete3.title}",
            out.getvalue(),
        )
        self.assertNotIn(
            f"{self.paste_not_for_deletion.uuid} - {self.paste_not_for_deletion.title}",
            out.getvalue(),
        )
        self.assertNotIn(
            f"{self.paste_not_for_deletion2.uuid} - {self.paste_not_for_deletion2.title}",
            out.getvalue(),
        )

    def test_delete_pastes_scheduled_for_expiring(self):
        out = StringIO()
        call_command("expire_pastes", stdout=out)

        self.assertIn("Successfully deleted 3 expired pastes", out.getvalue())

    def test_shows_info_when_nothing_to_remove(self):
        Paste.objects.all().delete()
        out = StringIO()
        call_command("expire_pastes", stdout=out)

        self.assertIn("No expired pastes to remove", out.getvalue())
