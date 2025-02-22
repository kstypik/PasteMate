import datetime
import os
from pathlib import Path
import tempfile
from unittest import mock

import pytest
from django.utils import timezone
from django.utils.text import slugify

from pastes.models import Paste

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
            content="""Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque sit amet leo neque. Duis mauris quam, lobortis quis urna vel, vestibulum placerat nisl. Aenean rutrum nibh sed cursus aliquet. Sed nec elit at ex malesuada laoreet vel non purus. Aenean faucibus, est in egestas efficitur, neque est lobortis lectus, eget sollicitudin sapien enim vel lacus. Quisque efficitur scelerisque placerat. Donec quis ante sit amet nulla auctor posuere. Aliquam aliquam vestibulum tempus. In placerat nunc eu porttitor gravida. Pellentesque dui felis, molestie vitae efficitur eget, sodales nec enim. Suspendisse ut consequat quam. Phasellus a semper metus, vel imperdiet turpis. Aliquam nunc velit, vulputate at est ac, porta faucibus nisl. Nam faucibus sit amet diam at ultricies. Interdum et malesuada fames ac ante ipsum primis in faucibus. """
        )

        assert paste_short.calculate_filesize() == 16
        assert paste_long.calculate_filesize() == 833

    def test_highlight_syntax_html(self, create_paste):
        paste = create_paste(
            content='<div class="container">Hello world!</div>',
            syntax="html",
        )

        assert '<div class="highlight">' in paste.highlight_syntax(format_type="html")

    def test_highlight_syntax_not_supported_options(self, create_paste):
        paste = create_paste()

        assert paste.highlight_syntax(format_type="video") == NotImplemented
        assert paste.highlight_syntax(format_type="chart") == NotImplemented

    def test_make_embeddable_image(self, create_paste):
        paste = Paste()

        assert paste.create_embeddable_image() == f"embed/{paste.uuid}.png"

    def test_make_backup_archive(self, user, create_paste):
        paste1 = create_paste(content="Hi", author=user)
        paste2 = create_paste(content="Hello", author=user)
        paste3 = create_paste(content="Morning", author=user)

        previous_cwd = Path.cwd()
        with tempfile.TemporaryFile() as fp:
            backup_archive = Paste.make_backup_archive(fp, user)
            with tempfile.TemporaryDirectory() as temp_dir:
                os.chdir(temp_dir)

                backup_archive.extract(f"{paste1.title}-{paste1.uuid}.txt")
                with Path(f"{paste1.title}-{paste1.uuid}.txt").open() as fh:
                    assert fh.read() == "Hi"

                backup_archive.extract(f"{paste2.title}-{paste2.uuid}.txt")
                with Path(f"{paste2.title}-{paste2.uuid}.txt").open() as fh:
                    assert fh.read() == "Hello"

                backup_archive.extract(f"{paste3.title}-{paste3.uuid}.txt")
                with Path(f"{paste3.title}-{paste3.uuid}.txt").open() as fh:
                    assert fh.read() == "Morning"

                backup_archive.close()
        os.chdir(previous_cwd)

    @pytest.mark.parametrize(
        ("test_input", "expected"),
        [
            (Paste.NEVER, None),
            (
                Paste.TEN_MINUTES,
                datetime.datetime(2022, 6, 24, 12, 10, tzinfo=datetime.UTC),
            ),
            (
                Paste.ONE_HOUR,
                datetime.datetime(2022, 6, 24, 13, 00, tzinfo=datetime.UTC),
            ),
            (
                Paste.ONE_DAY,
                datetime.datetime(2022, 6, 25, 12, 00, tzinfo=datetime.UTC),
            ),
            (
                Paste.ONE_WEEK,
                datetime.datetime(2022, 7, 1, 12, 00, tzinfo=datetime.UTC),
            ),
            (
                Paste.TWO_WEEKS,
                datetime.datetime(2022, 7, 8, 12, 00, tzinfo=datetime.UTC),
            ),
            (
                Paste.ONE_MONTH,
                datetime.datetime(2022, 7, 24, 12, 00, tzinfo=datetime.UTC),
            ),
            (
                Paste.SIX_MONTHS,
                datetime.datetime(2022, 12, 21, 12, 00, tzinfo=datetime.UTC),
            ),
            (
                Paste.ONE_YEAR,
                datetime.datetime(2023, 6, 24, 12, 00, tzinfo=datetime.UTC),
            ),
        ],
    )
    @mock.patch.object(
        timezone,
        "now",
        return_value=datetime.datetime(2022, 6, 24, 12, 00, tzinfo=datetime.UTC),
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
