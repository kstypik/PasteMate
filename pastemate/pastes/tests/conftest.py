import pytest
from django.urls import reverse

from pastemate.pastes.models import Folder, Report


@pytest.fixture
def create_report(create_paste):
    paste = create_paste()

    def report(reason="For testing", reporter_name="Tester"):
        return Report.objects.create(
            paste=paste,
            reason=reason,
            reporter_name=reporter_name,
        )

    return report


@pytest.fixture
def folder(user):
    return Folder.objects.create(name="Testing folder", created_by=user)


@pytest.fixture
def create_folder(user):
    def folder(name="Testing folder", created_by=None):
        if created_by is None:
            created_by = user
        return Folder.objects.create(name=name, created_by=created_by)

    return folder


@pytest.fixture
def create_paste_with_url(create_paste):
    def make_paste_with_url(viewname, **kwargs):
        paste = create_paste(**kwargs)
        url = reverse(viewname, args=[paste.uuid])
        return paste, url

    return make_paste_with_url
