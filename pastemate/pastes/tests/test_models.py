import datetime
import os
import tempfile
from unittest import mock

import pytest
from django.utils import timezone
from django.utils.text import slugify

from pastemate.pastes.models import Paste

pytestmark = pytest.mark.django_db


class TestPaste:
    def test___str__(self, create_paste):
        paste_with_title = create_paste()
        paste_without_title = create_paste(title="")

        assert paste_with_title.__str__() == paste_with_title.title
        assert str(paste_with_title) == paste_with_title.title

        assert paste_without_title.__str__() == "Untitled"
        assert str(paste_without_title) == "Untitled"

    def test_get_absolute_url(self, create_paste):
        paste = create_paste()
        url = paste.get_absolute_url()

        assert url == f"/{paste.uuid}/"

    def test_calculate_filesize(self, create_paste):
        paste_short = create_paste(
            content="Filesize of this",
        )
        paste_long = create_paste(
            content="""Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque sit amet leo neque. Duis mauris quam, lobortis quis urna vel, vestibulum placerat nisl. Aenean rutrum nibh sed cursus aliquet. Sed nec elit at ex malesuada laoreet vel non purus. Aenean faucibus, est in egestas efficitur, neque est lobortis lectus, eget sollicitudin sapien enim vel lacus. Quisque efficitur scelerisque placerat. Donec quis ante sit amet nulla auctor posuere. Aliquam aliquam vestibulum tempus. In placerat nunc eu porttitor gravida. Pellentesque dui felis, molestie vitae efficitur eget, sodales nec enim. Suspendisse ut consequat quam. Phasellus a semper metus, vel imperdiet turpis. Aliquam nunc velit, vulputate at est ac, porta faucibus nisl. Nam faucibus sit amet diam at ultricies. Interdum et malesuada fames ac ante ipsum primis in faucibus. """  # noqa
        )

        assert paste_short.calculate_filesize() == 16
        assert paste_long.calculate_filesize() == 833

    def test_highlight_syntax_html(self, create_paste):
        paste = create_paste(
            content='<div class="container">Hello world!</div>',
            syntax="html",
        )

        assert '<div class="highlight">' in paste.highlight_syntax(format="html")

    def test_highlight_syntax_image(self, create_paste):
        paste = create_paste(content="Hello")
        expected_image = b"""\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00Z\x00\x00\x00#\x08\x02\x00\x00\x00\x9b\xe7\x8a\\\x00\x00\x02\xa4IDATx\x9c\xed\x99OH\"Q\x18\xc0\xc7Ei\x0e\x89\xe4D\x86\xb3)\x0c{\xd0\x8b\x87\x98\x08\x96\x06\xf6`\xa7\xf0\xe4IO\x03J\xb1s\xd0n!\x1e\xba\x0cD\xd1!v\x90d\xdcK\xb28\x10\x91\xb4t\x115\xd9\xab\x82\xa7\xb6\x880\xd0Bqh\x07A\x02\xff\x0c\xb4\x07)zKL2)\xba\xf0~\xa7y\x1f\xdf\xf7\xbd\x8f\x1f\xbc\x99aF#I%d\x98\xf0\xfc\xf6\xfa\xfa\xb7\xa1n1@>\x8cz\x80\xf1\x02\xea\x00\x80:\x00\xa0\x0e\x00\xa8\x03\x00\xea\x00\x80:\x00\xa0\x0e\x00\xa8\x03\x00\xea\x00\x80:\x00\xfe\x1b\x1d\x82 \xa0(\x8a\xa2\xa8\xd9l\xee'\xae\x8ew\xe9\xa8TJ''?x~\xfb\xfa\xfaw\xffU\x8dF\x03E\xd1\xe3\xe3\xe3\xe7\x08A\x10,\xcb*Wy<\x9eV\xab\x15\x8f\xc7\xfb\x8c\xabC\xbd\x8e|\xfeW6\xfbsv\xf6\xe3@\xe6\x18\x13\xd4\xeb\xb0Z?y\xbd_\x17\x17\xbf\x0cn\x18\x04A\x10\x8e\xe3l6\xdb\xd4\xd4\x14EQ\x85B\xe1=\xaddY\x0e\x85Bsss\x06\x83\xc1\xe9t\x9e\x9f\x9f\xbfY\xa2^\x87\xc9\x84OL\xa0\xaa\xcb_%\x16\x8b\xed\xee\xee\xc6b\xb1\xdb\xdb[\x9f\xcf\xb7\xb2\xb2R\xab\xd5Tw\xe38N\x10\x84d2yssc\xb5Z\xddnw\xb7\xdbU.\x19\xd9\xad\xd4\xeb\xf5\xa2OT\xab\xd5^\x90e\xd9\xcd\xcdM\x8a\xa2&''i\x9a&I\xf2\xe0\xe0@\xf5\x16<\xcf3\x0cC\x92$\x86a;;;www\xe9tZ\xb9dd:\x12\x89D\xeb\x89\xdeC\xe1\xfe\xfe\xbe^\xaf3\x0c\xf3\xac\xe9\xec\xec\xec\xea\xeaJ]\x7fY\x96+\x95\x8a\xddn\xef-1\x0c3\x99L\xa5\xd2\x1b\x9f\xfe\xb4\xea6\x1b\x1e\x99Lfiii\x18\x9d\x1f\x1f\x1f5\x1a\x8dr\xce\x18\xbdwLOO\xcf\xcc\xcc\\\\\\(\xe4\xe8\xf5\xfaN\xa7\xd3O\\\xab\xd5Z,\x96\xcb\xcb\xcb\xdeR\x92$Q\x14\t\x82P\x9ea\x8ct \x08\x12\x0e\x87\xb7\xb6\xb6\xb2\xd9\xec\xc3\xc3C\xb9\\\x8eD\"\xf9|\xfee\x82\xc3\xe1h\xb7\xdb\xa9T\xea\x9f\xc2W\xe3~\xbf\x7f\x7f\x7f\xbfX,J\x92\xb4\xb1\xb1\x81\xe3\xf8\xf2\xf2\xb2\xf2\x00\xea\x0fK\xa3\xf1\xe7\xf0\xf0{\xef:\x97;\xcd\xe5NI\x92\x9a\x9f\xff\xac\xba!\x82 kkk\xb2,\x07\x83\xc1r\xb9l4\x1a\x17\x16\x16\x9cN\xe7\xcb\x04\x1c\xc7\xf7\xf6\xf6VWW\xeb\xf5:M\xd3\xd1hT!\x1e\x08\x04DQt\xb9\\\xcdf\x93$\xc9\xa3\xa3#\x9dN\xa7<\x80\x06\xfeXx\xc9x\x1d\x96\x91\x03u\x00@\x1d\x00P\x07\x00\xd4\x01\x00u\x00@\x1d\x00P\x07\x00\xd4\x01\x00u\x00@\x1d\x00\x7f\x01\xcf\x01\xfd\x93\xd3&\x90g\x00\x00\x00\x00IEND\xaeB`\x82"""  # noqa

        assert paste.highlight_syntax(format="image") == expected_image

    def test_highlight_syntax_not_supported_options(self, create_paste):
        paste = create_paste()

        assert paste.highlight_syntax(format="video") == NotImplemented
        assert paste.highlight_syntax(format="chart") == NotImplemented

    def test_make_embeddable_image(self, create_paste):
        paste = Paste()

        assert paste.make_embeddable_image() == f"embed/{paste.uuid}.png"

    def test_make_backup_archive(self, user, create_paste):
        paste1 = create_paste(content="Hi", author=user)
        paste2 = create_paste(content="Hello", author=user)
        paste3 = create_paste(content="Morning", author=user)

        previous_cwd = os.getcwd()
        with tempfile.TemporaryFile() as fp:
            backup_archive = Paste.make_backup_archive(fp, user)
            with tempfile.TemporaryDirectory() as temp_dir:
                os.chdir(temp_dir)

                backup_archive.extract(f"{paste1.title}-{paste1.uuid}.txt")
                with open(f"{paste1.title}-{paste1.uuid}.txt") as fh:
                    assert "Hi" == fh.read()

                backup_archive.extract(f"{paste2.title}-{paste2.uuid}.txt")
                with open(f"{paste2.title}-{paste2.uuid}.txt") as fh:
                    assert "Hello" == fh.read()

                backup_archive.extract(f"{paste3.title}-{paste3.uuid}.txt")
                with open(f"{paste3.title}-{paste3.uuid}.txt") as fh:
                    assert "Morning" == fh.read()

                backup_archive.close()
        os.chdir(previous_cwd)

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            (Paste.NEVER, None),
            (
                Paste.TEN_MINUTES,
                datetime.datetime(2022, 6, 24, 12, 10, tzinfo=datetime.timezone.utc),
            ),
            (
                Paste.ONE_HOUR,
                datetime.datetime(2022, 6, 24, 13, 00, tzinfo=datetime.timezone.utc),
            ),
            (
                Paste.ONE_DAY,
                datetime.datetime(2022, 6, 25, 12, 00, tzinfo=datetime.timezone.utc),
            ),
            (
                Paste.ONE_WEEK,
                datetime.datetime(2022, 7, 1, 12, 00, tzinfo=datetime.timezone.utc),
            ),
            (
                Paste.TWO_WEEKS,
                datetime.datetime(2022, 7, 8, 12, 00, tzinfo=datetime.timezone.utc),
            ),
            (
                Paste.ONE_MONTH,
                datetime.datetime(2022, 7, 24, 12, 00, tzinfo=datetime.timezone.utc),
            ),
            (
                Paste.SIX_MONTHS,
                datetime.datetime(2022, 12, 21, 12, 00, tzinfo=datetime.timezone.utc),
            ),
            (
                Paste.ONE_YEAR,
                datetime.datetime(2023, 6, 24, 12, 00, tzinfo=datetime.timezone.utc),
            ),
        ],
    )
    @mock.patch.object(
        timezone,
        "now",
        return_value=datetime.datetime(
            2022, 6, 24, 12, 00, tzinfo=datetime.timezone.utc
        ),
    )
    def test_calculate_expiration_date(
        self, mock_timezone_now, test_input, expected, create_paste
    ):
        assert create_paste(expiration_symbol=test_input).expiration_date == expected

    def test_get_full_language_name(self):
        assert Paste.get_full_language_name("python") == "Python"
        assert Paste.get_full_language_name("javascript") == "JavaScript"
        assert Paste.get_full_language_name("cpp") == "C++"
        assert Paste.get_full_language_name("plpgsql") == "PL/pgSQL"

    def test_save_with_title(self, create_paste):
        paste = create_paste(title="Custom Title")

        assert paste.title == "Custom Title"

    def test_save_without_title_gives_untitled_for_it(self, create_paste):
        paste = create_paste(title="")

        assert paste.title == "Untitled"

    def test_save_content_html_not_empty(self, create_paste):
        paste = create_paste()

        assert paste.content_html

    def test_save_add_embeddable_image(self, create_paste):
        paste = create_paste()

        assert bool(paste.embeddable_image)

    def test_save_do_not_add_embeddable_image_when_password_or_burn_or_private(
        self, create_paste
    ):
        paste_with_password = create_paste(password="topsecret")
        paste_that_will_burn = create_paste(burn_after_read=True)
        private_paste = create_paste(exposure=Paste.Exposure.PRIVATE)
        paste_with_all_three_conditions = create_paste(
            password="topsecret",
            burn_after_read=True,
            exposure=Paste.Exposure.PRIVATE,
        )

        assert not bool(paste_with_password.embeddable_image)
        assert not bool(paste_that_will_burn.embeddable_image)
        assert not bool(private_paste.embeddable_image)
        assert not bool(paste_with_all_three_conditions.embeddable_image)


class TestFolder:
    def test___str__(self, folder):
        assert folder.__str__() == folder.name
        assert str(folder) == folder.name

    def test_get_absolute_url(self, folder):
        url = folder.get_absolute_url()

        assert url == f"/user/{folder.created_by.username}/folder/{folder.slug}/"

    def test_save_sets_slug(self, folder):
        assert folder.slug == slugify(folder.name)


class TestReport:
    def test___str__(self, create_report):
        report = create_report()

        assert report.__str__() == f"Report by {report.reporter_name}"
        assert str(report) == f"Report by {report.reporter_name}"
