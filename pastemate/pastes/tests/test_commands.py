import datetime
from io import StringIO

import pytest
from django.core.management import call_command

from pastes.models import Paste

pytestmark = pytest.mark.django_db


def test_show_pastes_scheduled_for_expiring(create_paste):
    paste_to_delete = create_paste(
        title="First",
        expiration_date=datetime.datetime(
            2020, 1, 1, 12, 00, tzinfo=datetime.UTC
        ),
    )
    paste_to_delete2 = create_paste(
        title="Second",
        expiration_date=datetime.datetime(
            2020, 1, 1, 12, 00, tzinfo=datetime.UTC
        ),
    )
    paste_to_delete3 = create_paste(
        title="Third",
        expiration_date=datetime.datetime(
            2020, 1, 1, 12, 00, tzinfo=datetime.UTC
        ),
    )
    paste_not_for_deletion = create_paste(title="This one not")
    paste_not_for_deletion2 = create_paste(title="This one also not")

    out = StringIO()
    call_command("expire_pastes", only_show=True, stdout=out)

    assert f"{paste_to_delete.uuid} - {paste_to_delete.title}" in out.getvalue()
    assert f"{paste_to_delete2.uuid} - {paste_to_delete2.title}" in out.getvalue()
    assert f"{paste_to_delete3.uuid} - {paste_to_delete3.title}" in out.getvalue()
    assert (
        f"{paste_not_for_deletion.uuid} - {paste_not_for_deletion.title}"
        not in out.getvalue()
    )
    assert (
        f"{paste_not_for_deletion2.uuid} - {paste_not_for_deletion2.title}"
        not in out.getvalue()
    )


def test_delete_pastes_scheduled_for_expiring(create_paste):
    create_paste(
        title="First",
        expiration_date=datetime.datetime(
            2020, 1, 1, 12, 00, tzinfo=datetime.UTC
        ),
    )
    create_paste(
        title="Second",
        expiration_date=datetime.datetime(
            2020, 1, 1, 12, 00, tzinfo=datetime.UTC
        ),
    )
    create_paste(
        title="Third",
        expiration_date=datetime.datetime(
            2020, 1, 1, 12, 00, tzinfo=datetime.UTC
        ),
    )
    create_paste(title="This one not")
    create_paste(title="This one also not")

    out = StringIO()
    call_command("expire_pastes", stdout=out)

    assert "Successfully deleted 3 expired pastes" in out.getvalue()


def test_shows_info_when_nothing_to_remove(create_paste):
    create_paste(
        title="First",
        expiration_date=datetime.datetime(
            2020, 1, 1, 12, 00, tzinfo=datetime.UTC
        ),
    )
    create_paste(
        title="Second",
        expiration_date=datetime.datetime(
            2020, 1, 1, 12, 00, tzinfo=datetime.UTC
        ),
    )
    create_paste(
        title="Third",
        expiration_date=datetime.datetime(
            2020, 1, 1, 12, 00, tzinfo=datetime.UTC
        ),
    )
    Paste.objects.all().delete()
    out = StringIO()
    call_command("expire_pastes", stdout=out)

    assert "No expired pastes to remove" in out.getvalue()
