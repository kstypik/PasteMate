import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_can_view_raw_paste_detail(create_paste, client):
    paste = create_paste()
    response = client.get(reverse("pastes:raw_detail", args=[paste.uuid]))

    assert response.content.decode("utf-8") == paste.content
