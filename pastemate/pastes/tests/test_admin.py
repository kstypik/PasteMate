import datetime
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from pytest_django.asserts import assertContains, assertInHTML

pytestmark = pytest.mark.django_db

User = get_user_model()

REPORT_CHANGELIST_URL = reverse("admin:pastes_report_changelist")


def test_shows_link_to_paste_on_list(admin_client, create_report):
    report = create_report()
    response = admin_client.get(REPORT_CHANGELIST_URL)
    print(response.content.decode("utf-8"))
    html = f"""
<td class="field-linked_paste">
Paste For Testing <a href="{report.paste.get_absolute_url()}">(view)</a>
</td>"""
    assertInHTML(html, response.content.decode("utf-8"))


@patch.object(
    timezone,
    "now",
    return_value=datetime.datetime(2022, 6, 24, 12, 00, tzinfo=datetime.timezone.utc),
)
def test_mark_reports_as_moderated(mocked_now, admin_client, admin_user, create_report):
    report = create_report()
    additional_report = create_report(reason="Additional", reporter_name="Someone else")
    data = {
        "action": "mark_as_moderated",
        "_selected_action": [report.id, additional_report.id],
    }
    response = admin_client.post(REPORT_CHANGELIST_URL, data, follow=True)
    report.refresh_from_db()
    additional_report.refresh_from_db()

    assert report.moderated
    assert additional_report.moderated
    assert report.moderated_by == admin_user
    assert additional_report.moderated_by == admin_user
    assert report.moderated_at == datetime.datetime(
        2022, 6, 24, 12, 0, tzinfo=datetime.timezone.utc
    )
    assert additional_report.moderated_at == datetime.datetime(
        2022, 6, 24, 12, 0, tzinfo=datetime.timezone.utc
    )
    assertContains(
        response,
        "2 reports were successfully marked as moderated.",
    )


def test_mark_reports_as_unmoderated(admin_client, create_report):
    report = create_report()
    additional_report = create_report()
    data = {
        "action": "mark_as_unmoderated",
        "_selected_action": [report.id, additional_report.id],
    }
    response = admin_client.post(REPORT_CHANGELIST_URL, data, follow=True)
    report.refresh_from_db()
    additional_report.refresh_from_db()

    assert not report.moderated
    assert not additional_report.moderated
    assertContains(
        response,
        "2 reports were successfully marked as unmoderated.",
    )


@patch.object(
    timezone,
    "now",
    return_value=datetime.datetime(2022, 6, 24, 12, 00, tzinfo=datetime.timezone.utc),
)
def test_deactivate_reported_pastes(
    mocked_now, admin_client, admin_user, create_report
):
    report = create_report()
    additional_report = create_report()
    data = {
        "action": "deactivate_reported_pastes",
        "_selected_action": [report.id, additional_report.id],
    }
    response = admin_client.post(REPORT_CHANGELIST_URL, data, follow=True)
    report.refresh_from_db()
    additional_report.refresh_from_db()

    assert not report.paste.is_active
    assert not additional_report.paste.is_active
    assert report.moderated_by == admin_user
    assert additional_report.moderated_by == admin_user
    assert report.moderated_at == datetime.datetime(
        2022, 6, 24, 12, 0, tzinfo=datetime.timezone.utc
    )
    assert additional_report.moderated_at == datetime.datetime(
        2022, 6, 24, 12, 0, tzinfo=datetime.timezone.utc
    )
    assertContains(
        response,
        "2 reported pastes were successfully deactivated.",
    )
