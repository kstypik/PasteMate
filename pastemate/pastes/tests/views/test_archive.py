import pytest
from django.test import override_settings
from django.urls import reverse
from pytest_django.asserts import assertInHTML, assertTemplateUsed

from pastes.models import Paste

pytestmark = pytest.mark.django_db

PASTES_ARCHIVE_URL = reverse("pastes:archive")


def test_template_name_correct(client):
    response = client.get(PASTES_ARCHIVE_URL)

    assertTemplateUsed(response, "pastes/archive.html")


@override_settings(PASTES_ARCHIVE_LENGTH=2)
def test_can_view_archive(client, create_paste):
    first_added_paste = create_paste()
    second_added_paste = create_paste()
    last_added_paste = create_paste()

    response = client.get(PASTES_ARCHIVE_URL)

    assert first_added_paste not in response.context["pastes"]
    assert second_added_paste in response.context["pastes"]
    assert last_added_paste in response.context["pastes"]


def test_can_view_archive_of_specific_language(client, create_paste):
    first_added_paste = create_paste(syntax="python")
    second_added_paste = create_paste()
    last_added_paste = create_paste(syntax="python")

    response = client.get(reverse("pastes:syntax_archive", args=["python"]))

    assert first_added_paste in response.context["pastes"]
    assert second_added_paste not in response.context["pastes"]
    assert last_added_paste in response.context["pastes"]


def test_syntax_in_context_of_language_archive(client):
    response = client.get(reverse("pastes:syntax_archive", args=["python"]))

    assert response.context["syntax"] == "Python"


def test_displays_message_when_no_pastes(client):
    Paste.objects.all().delete()

    response = client.get(PASTES_ARCHIVE_URL)

    assertInHTML("<p>There are no pastes yet.</p>", response.content.decode("utf-8"))
