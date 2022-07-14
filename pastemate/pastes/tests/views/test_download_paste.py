import pytest
from django.urls import reverse
from pytest_django.asserts import assertContains

pytestmark = pytest.mark.django_db


def test_can_download_paste(client, create_paste):
    paste = create_paste()

    response = client.get(reverse("pastes:paste_download", args=[paste.uuid]))

    assert (
        response.headers["Content-Disposition"]
        == f'attachment; filename="paste-{paste.uuid}.txt"'
    )
    assertContains(response, paste.content)
