import datetime
import unittest
from unittest import mock

from accounts.models import User
from django.test import TestCase
from django.utils import timezone
from django.utils.text import slugify
from pastes.models import Folder, Paste, Report


class PasteModelTest(TestCase):
    def test___str__(self):
        paste_with_title = Paste.objects.create(
            content="Hello, world!",
            title="Paste with a title",
        )
        paste_without_title = Paste.objects.create(
            content="Paste with no title",
        )

        self.assertEqual(paste_with_title.__str__(), paste_with_title.title)
        self.assertEqual(str(paste_with_title), paste_with_title.title)

        self.assertEqual(paste_without_title.__str__(), "Untitled")
        self.assertEqual(str(paste_without_title), "Untitled")

    def test_get_absolute_url(self):
        paste = Paste.objects.create(
            content="Testing the URL",
        )
        url = paste.get_absolute_url()

        self.assertEqual(url, f"/{paste.uuid}/")

    def test_calculate_filesize(self):
        paste_short = Paste.objects.create(
            content="Filesize of this",
        )
        paste_long = Paste.objects.create(
            content="""Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque sit amet leo neque. Duis mauris quam, lobortis quis urna vel, vestibulum placerat nisl. Aenean rutrum nibh sed cursus aliquet. Sed nec elit at ex malesuada laoreet vel non purus. Aenean faucibus, est in egestas efficitur, neque est lobortis lectus, eget sollicitudin sapien enim vel lacus. Quisque efficitur scelerisque placerat. Donec quis ante sit amet nulla auctor posuere. Aliquam aliquam vestibulum tempus. In placerat nunc eu porttitor gravida. Pellentesque dui felis, molestie vitae efficitur eget, sodales nec enim. Suspendisse ut consequat quam. Phasellus a semper metus, vel imperdiet turpis. Aliquam nunc velit, vulputate at est ac, porta faucibus nisl. Nam faucibus sit amet diam at ultricies. Interdum et malesuada fames ac ante ipsum primis in faucibus. """
        )

        self.assertEqual(paste_short.calculate_filesize(), 16)
        self.assertEqual(paste_long.calculate_filesize(), 833)

    @unittest.skip
    def test_highlight_syntax(self):
        paste = Paste.objects.create(
            content='<div class="container">Hello world!</div>',
            syntax="html",
        )

        self.assertInHTML(
            '<div class="highlight"></div>',
            paste.highlight_syntax(format="html"),
        )

    @unittest.skip
    def test_make_embeddable_image(self):
        paste = Paste.objects.create(
            content='<div class="container">Hello world!</div>',
            syntax="html",
        )

    @unittest.skip
    def test_make_backup_archive(self):
        user = User.objects.create_user(name="Gabe")

    @mock.patch.object(
        timezone,
        "now",
        return_value=datetime.datetime(
            2022, 6, 24, 12, 00, tzinfo=datetime.timezone.utc
        ),
    )
    def test_calculate_expiration_date(self, mock_timezone_now):
        paste_never_expiring = Paste.objects.create(
            content="I should never expire",
            expiration_interval_symbol=Paste.NEVER,
        )
        paste_expiring_in_10_minutes = Paste.objects.create(
            content="I will expire in 10 minutes",
            expiration_interval_symbol=Paste.TEN_MINUTES,
        )
        paste_expiring_in_1_hour = Paste.objects.create(
            content="I will expire in 1 hour",
            expiration_interval_symbol=Paste.ONE_HOUR,
        )
        paste_expiring_in_1_day = Paste.objects.create(
            content="I will expire in 1 day",
            expiration_interval_symbol=Paste.ONE_DAY,
        )
        paste_expiring_in_1_week = Paste.objects.create(
            content="I will expire in 1 week",
            expiration_interval_symbol=Paste.ONE_WEEK,
        )
        paste_expiring_in_2_weeks = Paste.objects.create(
            content="I will expire in 2 weeks",
            expiration_interval_symbol=Paste.TWO_WEEKS,
        )
        paste_expiring_in_1_month = Paste.objects.create(
            content="I will expire in 1 month",
            expiration_interval_symbol=Paste.ONE_MONTH,
        )
        paste_expiring_in_6_months = Paste.objects.create(
            content="I will expire in 6 months",
            expiration_interval_symbol=Paste.SIX_MONTHS,
        )
        paste_expiring_in_1_year = Paste.objects.create(
            content="I will expire in 1 year",
            expiration_interval_symbol=Paste.ONE_YEAR,
        )

        self.assertIsNone(paste_never_expiring.calculate_expiration_date())
        self.assertEqual(
            paste_expiring_in_10_minutes.calculate_expiration_date(),
            timezone.now() + datetime.timedelta(minutes=10),
        )
        self.assertEqual(
            paste_expiring_in_1_hour.calculate_expiration_date(),
            timezone.now() + datetime.timedelta(hours=1),
        )
        self.assertEqual(
            paste_expiring_in_1_day.calculate_expiration_date(),
            timezone.now() + datetime.timedelta(days=1),
        )
        self.assertEqual(
            paste_expiring_in_1_week.calculate_expiration_date(),
            timezone.now() + datetime.timedelta(weeks=1),
        )
        self.assertEqual(
            paste_expiring_in_2_weeks.calculate_expiration_date(),
            timezone.now() + datetime.timedelta(weeks=2),
        )
        self.assertEqual(
            paste_expiring_in_1_month.calculate_expiration_date(),
            timezone.now() + datetime.timedelta(days=30),
        )
        self.assertEqual(
            paste_expiring_in_6_months.calculate_expiration_date(),
            timezone.now() + datetime.timedelta(days=180),
        )
        self.assertEqual(
            paste_expiring_in_1_year.calculate_expiration_date(),
            timezone.now() + datetime.timedelta(days=365),
        )

    def test_get_full_language_name(self):
        self.assertEqual(Paste.get_full_language_name("python"), "Python")
        self.assertEqual(Paste.get_full_language_name("javascript"), "JavaScript")
        self.assertEqual(Paste.get_full_language_name("cpp"), "C++")
        self.assertEqual(Paste.get_full_language_name("plpgsql"), "PL/pgSQL")

    def test_save_with_title(self):
        paste = Paste.objects.create(content="Hello world", title="Custom Title")

        self.assertEqual(paste.title, "Custom Title")

    def test_save_without_title_gives_untitled_for_it(self):
        paste = Paste.objects.create(content="Hello world")

        self.assertEqual(paste.title, "Untitled")

    def test_save_content_html_not_empty(self):
        paste = Paste.objects.create(content="Hello world")

        self.assertNotEqual(paste.content_html, "")

    def test_save_add_embeddable_image(self):
        paste = Paste.objects.create(content="Hello world")

        self.assertTrue(bool(paste.embeddable_image))

    def test_save_do_not_add_embeddable_image_when_pass_burn_or_private(self):
        paste_with_password = Paste.objects.create(
            content="I have a password", password="topsecret"
        )
        paste_that_will_burn = Paste.objects.create(
            content="I will burn soon", burn_after_read=True
        )
        private_paste = Paste.objects.create(
            content="I am very private", exposure=Paste.Exposure.PRIVATE
        )
        paste_with_all_three_conditions = Paste.objects.create(
            content="I am private, will burn and have a password",
            password="topsecret",
            burn_after_read=True,
            exposure=Paste.Exposure.PRIVATE,
        )

        self.assertFalse(bool(paste_with_password.embeddable_image))
        self.assertFalse(bool(paste_that_will_burn.embeddable_image))
        self.assertFalse(bool(private_paste.embeddable_image))
        self.assertFalse(bool(paste_with_all_three_conditions.embeddable_image))


class FolderModelTest(TestCase):
    def test___str__(self):
        user = User.objects.create(username="test")
        folder = Folder.objects.create(name="Testing folder", created_by=user)

        self.assertEqual(folder.__str__(), folder.name)
        self.assertEqual(str(folder), folder.name)

    def test_get_absolute_url(self):
        user = User.objects.create(username="test")
        folder = Folder.objects.create(name="Testing folder", created_by=user)
        url = folder.get_absolute_url()

        self.assertEqual(url, f"/user/{user.username}/folder/{folder.slug}/")

    def test_save_sets_slug(self):
        user = User.objects.create(username="test")
        folder = Folder.objects.create(name="Testing folder", created_by=user)

        self.assertEqual(folder.slug, slugify(folder.name))


class ReportModelTest(TestCase):
    def test___str__(self):
        paste = Paste.objects.create(content="Hello")
        report = Report.objects.create(
            paste=paste, reason="Just for testing", reporter_name="Johnny"
        )

        self.assertEqual(report.__str__(), f"Report by {report.reporter_name}")
        self.assertEqual(str(report), f"Report by {report.reporter_name}")
