import datetime
import os
import tempfile
from unittest import mock

from django.test import TestCase
from django.utils import timezone
from django.utils.text import slugify

from pastemate.accounts.models import User
from pastemate.pastes.models import Folder, Paste, Report


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
            content="""Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque sit amet leo neque. Duis mauris quam, lobortis quis urna vel, vestibulum placerat nisl. Aenean rutrum nibh sed cursus aliquet. Sed nec elit at ex malesuada laoreet vel non purus. Aenean faucibus, est in egestas efficitur, neque est lobortis lectus, eget sollicitudin sapien enim vel lacus. Quisque efficitur scelerisque placerat. Donec quis ante sit amet nulla auctor posuere. Aliquam aliquam vestibulum tempus. In placerat nunc eu porttitor gravida. Pellentesque dui felis, molestie vitae efficitur eget, sodales nec enim. Suspendisse ut consequat quam. Phasellus a semper metus, vel imperdiet turpis. Aliquam nunc velit, vulputate at est ac, porta faucibus nisl. Nam faucibus sit amet diam at ultricies. Interdum et malesuada fames ac ante ipsum primis in faucibus. """  # noqa
        )

        self.assertEqual(paste_short.calculate_filesize(), 16)
        self.assertEqual(paste_long.calculate_filesize(), 833)

    def test_highlight_syntax_html(self):
        paste = Paste.objects.create(
            content='<div class="container">Hello world!</div>',
            syntax="html",
        )

        self.assertIn(
            '<div class="highlight">',
            paste.highlight_syntax(format="html"),
        )

    def test_highlight_syntax_image(self):
        paste = Paste.objects.create(content="Hello")
        expected_image = b"""\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00Z\x00\x00\x00#\x08\x02\x00\x00\x00\x9b\xe7\x8a\\\x00\x00\x02\xa4IDATx\x9c\xed\x99OH\"Q\x18\xc0\xc7Ei\x0e\x89\xe4D\x86\xb3)\x0c{\xd0\x8b\x87\x98\x08\x96\x06\xf6`\xa7\xf0\xe4IO\x03J\xb1s\xd0n!\x1e\xba\x0cD\xd1!v\x90d\xdcK\xb28\x10\x91\xb4t\x115\xd9\xab\x82\xa7\xb6\x880\xd0Bqh\x07A\x02\xff\x0c\xb4\x07)zKL2)\xba\xf0~\xa7y\x1f\xdf\xf7\xbd\x8f\x1f\xbc\x99aF#I%d\x98\xf0\xfc\xf6\xfa\xfa\xb7\xa1n1@>\x8cz\x80\xf1\x02\xea\x00\x80:\x00\xa0\x0e\x00\xa8\x03\x00\xea\x00\x80:\x00\xa0\x0e\x00\xa8\x03\x00\xea\x00\x80:\x00\xfe\x1b\x1d\x82 \xa0(\x8a\xa2\xa8\xd9l\xee'\xae\x8ew\xe9\xa8TJ''?x~\xfb\xfa\xfaw\xffU\x8dF\x03E\xd1\xe3\xe3\xe3\xe7\x08A\x10,\xcb*Wy<\x9eV\xab\x15\x8f\xc7\xfb\x8c\xabC\xbd\x8e|\xfeW6\xfbsv\xf6\xe3@\xe6\x18\x13\xd4\xeb\xb0Z?y\xbd_\x17\x17\xbf\x0cn\x18\x04A\x10\x8e\xe3l6\xdb\xd4\xd4\x14EQ\x85B\xe1=\xaddY\x0e\x85Bsss\x06\x83\xc1\xe9t\x9e\x9f\x9f\xbfY\xa2^\x87\xc9\x84OL\xa0\xaa\xcb_%\x16\x8b\xed\xee\xee\xc6b\xb1\xdb\xdb[\x9f\xcf\xb7\xb2\xb2R\xab\xd5Tw\xe38N\x10\x84d2yssc\xb5Z\xddnw\xb7\xdbU.\x19\xd9\xad\xd4\xeb\xf5\xa2OT\xab\xd5^\x90e\xd9\xcd\xcdM\x8a\xa2&''i\x9a&I\xf2\xe0\xe0@\xf5\x16<\xcf3\x0cC\x92$\x86a;;;www\xe9tZ\xb9dd:\x12\x89D\xeb\x89\xdeC\xe1\xfe\xfe\xbe^\xaf3\x0c\xf3\xac\xe9\xec\xec\xec\xea\xeaJ]\x7fY\x96+\x95\x8a\xddn\xef-1\x0c3\x99L\xa5\xd2\x1b\x9f\xfe\xb4\xea6\x1b\x1e\x99Lfiii\x18\x9d\x1f\x1f\x1f5\x1a\x8dr\xce\x18\xbdwLOO\xcf\xcc\xcc\\\\\\(\xe4\xe8\xf5\xfaN\xa7\xd3O\\\xab\xd5Z,\x96\xcb\xcb\xcb\xdeR\x92$Q\x14\t\x82P\x9ea\x8ct \x08\x12\x0e\x87\xb7\xb6\xb6\xb2\xd9\xec\xc3\xc3C\xb9\\\x8eD\"\xf9|\xfee\x82\xc3\xe1h\xb7\xdb\xa9T\xea\x9f\xc2W\xe3~\xbf\x7f\x7f\x7f\xbfX,J\x92\xb4\xb1\xb1\x81\xe3\xf8\xf2\xf2\xb2\xf2\x00\xea\x0fK\xa3\xf1\xe7\xf0\xf0{\xef:\x97;\xcd\xe5NI\x92\x9a\x9f\xff\xac\xba!\x82 kkk\xb2,\x07\x83\xc1r\xb9l4\x1a\x17\x16\x16\x9cN\xe7\xcb\x04\x1c\xc7\xf7\xf6\xf6VWW\xeb\xf5:M\xd3\xd1hT!\x1e\x08\x04DQt\xb9\\\xcdf\x93$\xc9\xa3\xa3#\x9dN\xa7<\x80\x06\xfeXx\xc9x\x1d\x96\x91\x03u\x00@\x1d\x00P\x07\x00\xd4\x01\x00u\x00@\x1d\x00P\x07\x00\xd4\x01\x00u\x00@\x1d\x00\x7f\x01\xcf\x01\xfd\x93\xd3&\x90g\x00\x00\x00\x00IEND\xaeB`\x82"""  # noqa

        self.assertEqual(paste.highlight_syntax(format="image"), expected_image)

    def test_highlight_syntax_not_supported_options(self):
        paste = Paste.objects.create(content="Hello")

        self.assertEqual(paste.highlight_syntax(format="video"), NotImplemented)
        self.assertEqual(paste.highlight_syntax(format="chart"), NotImplemented)

    def test_make_embeddable_image(self):
        paste = Paste()
        paste.content = "Hello World"
        self.assertEqual(paste.make_embeddable_image(), f"embed/{paste.uuid}.png")

    def test_make_backup_archive(self):
        user = User.objects.create_user(username="Gabe", email="gabe@valve.com")
        paste1 = Paste.objects.create(content="Hi", title="p1", author=user)
        paste2 = Paste.objects.create(content="Hello", title="p2", author=user)
        paste3 = Paste.objects.create(content="Morning", title="p3", author=user)

        previous_cwd = os.getcwd()
        with tempfile.TemporaryFile() as fp:
            backup_archive = Paste.make_backup_archive(fp, user)
            with tempfile.TemporaryDirectory() as temp_dir:
                os.chdir(temp_dir)

                backup_archive.extract(f"{paste1.title}-{paste1.uuid}.txt")
                with open(f"{paste1.title}-{paste1.uuid}.txt") as fh:
                    self.assertEqual("Hi", fh.read())

                backup_archive.extract(f"{paste2.title}-{paste2.uuid}.txt")
                with open(f"{paste2.title}-{paste2.uuid}.txt") as fh:
                    self.assertEqual("Hello", fh.read())

                backup_archive.extract(f"{paste3.title}-{paste3.uuid}.txt")
                with open(f"{paste3.title}-{paste3.uuid}.txt") as fh:
                    self.assertEqual("Morning", fh.read())

                backup_archive.close()
        os.chdir(previous_cwd)

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
            expiration_symbol=Paste.NEVER,
        )
        paste_expiring_in_10_minutes = Paste.objects.create(
            content="I will expire in 10 minutes",
            expiration_symbol=Paste.TEN_MINUTES,
        )
        paste_expiring_in_1_hour = Paste.objects.create(
            content="I will expire in 1 hour",
            expiration_symbol=Paste.ONE_HOUR,
        )
        paste_expiring_in_1_day = Paste.objects.create(
            content="I will expire in 1 day",
            expiration_symbol=Paste.ONE_DAY,
        )
        paste_expiring_in_1_week = Paste.objects.create(
            content="I will expire in 1 week",
            expiration_symbol=Paste.ONE_WEEK,
        )
        paste_expiring_in_2_weeks = Paste.objects.create(
            content="I will expire in 2 weeks",
            expiration_symbol=Paste.TWO_WEEKS,
        )
        paste_expiring_in_1_month = Paste.objects.create(
            content="I will expire in 1 month",
            expiration_symbol=Paste.ONE_MONTH,
        )
        paste_expiring_in_6_months = Paste.objects.create(
            content="I will expire in 6 months",
            expiration_symbol=Paste.SIX_MONTHS,
        )
        paste_expiring_in_1_year = Paste.objects.create(
            content="I will expire in 1 year",
            expiration_symbol=Paste.ONE_YEAR,
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
