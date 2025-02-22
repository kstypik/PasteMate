import datetime
from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils import timezone
from pytest_django.asserts import assertRedirects

from core.utils import login_redirect_url

pytestmark = pytest.mark.django_db

BACKUP_URL = reverse("pastes:backup")


def test_login_required(client):
    response = client.get(BACKUP_URL)

    assertRedirects(response, login_redirect_url(BACKUP_URL))


@patch.object(
    timezone,
    "now",
    return_value=datetime.datetime(2022, 6, 24, 12, 00, tzinfo=datetime.UTC),
)
def test_backup_archive_with_correct_name(mock, auto_login_user, create_paste):
    client, user = auto_login_user()
    create_paste(content="Hi", author=user)

    response = client.post(BACKUP_URL)

    assert (
        response.headers["Content-Disposition"]
        == "attachment; filename=pastemate_backup_20220624.zip"
    )
