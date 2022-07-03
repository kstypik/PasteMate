import datetime
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from ..models import Paste, Report

User = get_user_model()

REPORT_CHANGELIST_URL = reverse("admin:pastes_report_changelist")


class ReportAdminTest(TestCase):
    def setUp(self):
        self.paste = Paste.objects.create(
            content="Hello World", title="Should be linked"
        )
        self.user = User.objects.create_superuser(
            username="Test", email="test@test.com"
        )
        self.report = Report.objects.create(
            paste=self.paste,
            reason="For testing",
            reporter_name="Random person",
        )
        self.additional_report = Report.objects.create(
            paste=self.paste,
            reason="For better testing",
            reporter_name="Who knows",
        )

        self.client.force_login(self.user)

    def test_shows_link_to_paste_on_list(self):
        response = self.client.get(REPORT_CHANGELIST_URL)

        html = f"""
<td class="field-linked_paste">
    Should be linked <a href="{self.paste.get_absolute_url()}">(view)</a>
</td>"""
        self.assertInHTML(html, response.content.decode("utf-8"))

    @patch.object(
        timezone,
        "now",
        return_value=datetime.datetime(
            2022, 6, 24, 12, 00, tzinfo=datetime.timezone.utc
        ),
    )
    def test_mark_reports_as_moderated(self, mocked_now):
        data = {
            "action": "mark_as_moderated",
            "_selected_action": [self.report.id, self.additional_report.id],
        }
        response = self.client.post(REPORT_CHANGELIST_URL, data, follow=True)
        self.report.refresh_from_db()
        self.additional_report.refresh_from_db()

        self.assertTrue(self.report.moderated)
        self.assertTrue(self.additional_report.moderated)
        self.assertEqual(self.report.moderated_by, self.user)
        self.assertEqual(self.additional_report.moderated_by, self.user)
        self.assertEqual(
            self.report.moderated_at,
            datetime.datetime(2022, 6, 24, 12, 0, tzinfo=datetime.timezone.utc),
        )
        self.assertEqual(
            self.additional_report.moderated_at,
            datetime.datetime(2022, 6, 24, 12, 0, tzinfo=datetime.timezone.utc),
        )
        self.assertContains(
            response,
            "2 reports were successfully marked as moderated.",
        )

    def test_mark_reports_as_unmoderated(self):
        data = {
            "action": "mark_as_unmoderated",
            "_selected_action": [self.report.id, self.additional_report.id],
        }
        response = self.client.post(REPORT_CHANGELIST_URL, data, follow=True)
        self.report.refresh_from_db()
        self.additional_report.refresh_from_db()

        self.assertFalse(self.report.moderated)
        self.assertFalse(self.additional_report.moderated)
        self.assertContains(
            response,
            "2 reports were successfully marked as unmoderated.",
        )

    @patch.object(
        timezone,
        "now",
        return_value=datetime.datetime(
            2022, 6, 24, 12, 00, tzinfo=datetime.timezone.utc
        ),
    )
    def test_deactivate_reported_pastes(self, mocked_now):
        data = {
            "action": "deactivate_reported_pastes",
            "_selected_action": [self.report.id, self.additional_report.id],
        }
        response = self.client.post(REPORT_CHANGELIST_URL, data, follow=True)
        self.report.refresh_from_db()
        self.additional_report.refresh_from_db()

        self.assertFalse(self.report.paste.is_active)
        self.assertFalse(self.additional_report.paste.is_active)
        self.assertEqual(self.report.moderated_by, self.user)
        self.assertEqual(self.additional_report.moderated_by, self.user)
        self.assertEqual(
            self.report.moderated_at,
            datetime.datetime(2022, 6, 24, 12, 0, tzinfo=datetime.timezone.utc),
        )
        self.assertEqual(
            self.additional_report.moderated_at,
            datetime.datetime(2022, 6, 24, 12, 0, tzinfo=datetime.timezone.utc),
        )
        self.assertContains(
            response,
            "2 reported pastes were successfully deactivated.",
        )
